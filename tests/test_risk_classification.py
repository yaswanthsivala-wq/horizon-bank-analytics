"""Customer-level risk classification policy and isolation tests."""

import unittest
from dataclasses import FrozenInstanceError
from datetime import date, datetime, timezone

from horizon_pipeline.analytics import (
    ConditionState, EvidenceState, RiskClassification,
    RiskClassificationEngine, RiskConditionResult, RiskRuleCatalogContract,
    RiskRuleCatalogRegistry,
)
from horizon_pipeline.contracts import ContractState, MasterProductionRegistry
from horizon_pipeline.processing.records import ExecutionMode


class RiskClassificationTests(unittest.TestCase):
    IDS = RiskClassificationEngine.CONDITION_IDS
    VERSIONS = {condition: f"{condition}-v1" for condition in IDS}

    def result(self, condition, state, *, version=None, lineage=(), reasons=()):
        return RiskConditionResult(condition, state, ("evidence",), tuple(lineage),
                                   self.VERSIONS[condition] if version is None else version,
                                   tuple(reasons), datetime(2025, 3, 9, tzinfo=timezone.utc))

    def outcomes(self, triggered=0, unknown=0):
        states = ([ConditionState.TRIGGERED] * triggered
                  + [ConditionState.UNKNOWN] * unknown
                  + [ConditionState.NOT_TRIGGERED] * (5 - triggered - unknown))
        return [self.result(condition, state) for condition, state in zip(self.IDS, states)]

    def classify(self, results=None, **overrides):
        registered_versions = overrides.pop("registered_versions", self.VERSIONS)
        catalog_is_fixture = overrides.pop("catalog_is_fixture", True)
        catalog_state = overrides.pop("catalog_state", ContractState.ACTIVE)
        approval_reference = overrides.pop("approval_reference", "")
        values = dict(
            assessment_id="A-1", customer_id="C-1", business_date=date(2025, 3, 9),
            assessment_at=datetime(2025, 3, 10, tzinfo=timezone.utc),
            condition_results=self.outcomes() if results is None else results,
            catalog_version="FIXTURE-CATALOG-v1",
            classification_rule_version="FIXTURE-CLASSIFY-v1",
            execution_mode=ExecutionMode.FIXTURE,
        )
        values.update(overrides)
        registry = values.pop("catalog_registry", RiskRuleCatalogRegistry())
        if values["catalog_version"]:
            registry.register(RiskRuleCatalogContract(
                catalog_version=values["catalog_version"],
                classification_rule_version=values["classification_rule_version"] or "MISSING",
                condition_versions=registered_versions,
                state=catalog_state, is_fixture=catalog_is_fixture,
                approval_reference=approval_reference,
            ))
        values["catalog_registry"] = registry
        return RiskClassificationEngine.classify(**values)

    def test_two_trigger_threshold(self):
        self.assertEqual(self.classify(self.outcomes(triggered=1)).classification, RiskClassification.NOT_HIGH_RISK)
        self.assertEqual(self.classify(self.outcomes(triggered=2)).classification, RiskClassification.PROVISIONAL_HIGH_RISK)

    def test_two_trigger_three_unknown_is_provisional_and_incomplete(self):
        result = self.classify(self.outcomes(triggered=2, unknown=3))
        self.assertEqual(result.classification, RiskClassification.PROVISIONAL_HIGH_RISK)
        self.assertEqual(result.evidence_state, EvidenceState.INCOMPLETE)

    def test_one_trigger_one_unknown_is_incomplete(self):
        self.assertEqual(self.classify(self.outcomes(triggered=1, unknown=1)).classification, RiskClassification.INCOMPLETE_EVIDENCE)

    def test_zero_trigger_one_unknown_not_high_risk_but_incomplete(self):
        result = self.classify(self.outcomes(unknown=1))
        self.assertEqual(result.classification, RiskClassification.NOT_HIGH_RISK)
        self.assertEqual(result.evidence_state, EvidenceState.INCOMPLETE)

    def test_zero_trigger_two_unknown_is_incomplete(self):
        self.assertEqual(self.classify(self.outcomes(unknown=2)).classification, RiskClassification.INCOMPLETE_EVIDENCE)

    def test_all_not_triggered_is_complete(self):
        result = self.classify()
        self.assertEqual(result.classification, RiskClassification.NOT_HIGH_RISK)
        self.assertEqual(result.evidence_state, EvidenceState.COMPLETE)
        self.assertEqual((result.triggered_count, result.unknown_count), (0, 0))

    def test_missing_catalog_overrides_counts_without_fabricating_rows(self):
        result = self.classify(self.outcomes(triggered=5), catalog_version=None)
        self.assertEqual(result.classification, RiskClassification.UNAVAILABLE)
        self.assertIsNone(result.triggered_count)
        self.assertEqual(result.condition_results, ())
        self.assertEqual(result.unavailable_reason, "MISSING_CATALOG_VERSION")

    def test_missing_classification_version_unavailable(self):
        self.assertEqual(self.classify(classification_rule_version=None).unavailable_reason, "MISSING_CLASSIFICATION_RULE_VERSION")

    def test_missing_catalog_members_unavailable(self):
        versions = dict(self.VERSIONS); versions.pop("RC-05")
        self.assertEqual(self.classify(registered_versions=versions).unavailable_reason, "INVALID_CATALOG_CONDITION_MEMBERSHIP")

    def test_duplicate_condition_fails_closed(self):
        results = self.outcomes(); results[-1] = results[0]
        self.assertEqual(self.classify(results).unavailable_reason, "DUPLICATE_CONDITION_RESULT")

    def test_unexpected_condition_fails_closed(self):
        results = self.outcomes(); results[-1] = RiskConditionResult("RC-06", ConditionState.NOT_TRIGGERED, (), (), "RC-06-v1")
        self.assertEqual(self.classify(results).unavailable_reason, "INVALID_CONDITION_RESULT_MEMBERSHIP")

    def test_missing_or_mismatched_condition_version_fails_closed(self):
        results = self.outcomes(); results[0] = self.result("RC-01", ConditionState.TRIGGERED, version="")
        self.assertEqual(self.classify(results).unavailable_reason, "MISSING_RULE_VERSION:RC-01")
        results[0] = self.result("RC-01", ConditionState.TRIGGERED, version="wrong")
        self.assertEqual(self.classify(results).unavailable_reason, "RULE_VERSION_MISMATCH:RC-01")

    def test_condition_evidence_reasons_and_order_are_preserved(self):
        results = list(reversed(self.outcomes(unknown=1)))
        results[-1] = self.result("RC-01", ConditionState.UNKNOWN, reasons=("MISSING",))
        assessment = self.classify(results)
        self.assertEqual(tuple(r.condition_id for r in assessment.condition_results), self.IDS)
        self.assertEqual(assessment.condition_results[0].missing_evidence_reasons, ("MISSING",))

    def test_lineage_is_combined_and_deduplicated(self):
        results = self.outcomes(); results[0] = self.result("RC-01", ConditionState.TRIGGERED, lineage=("L1", "L2"))
        result = self.classify(results, lineage_references=("L0", "L1"))
        self.assertEqual(result.lineage_references, ("L0", "L1", "L2"))

    def test_assessment_is_immutable_and_versions_do_not_rewrite_history(self):
        first = self.classify(catalog_version="FIXTURE-CATALOG-v1")
        second = self.classify(catalog_version="FIXTURE-CATALOG-v2")
        self.assertEqual(first.catalog_version, "FIXTURE-CATALOG-v1")
        self.assertEqual(second.catalog_version, "FIXTURE-CATALOG-v2")
        with self.assertRaises(FrozenInstanceError):
            first.catalog_version = "changed"

    def test_fixture_catalog_is_rejected_in_production(self):
        result = self.classify(execution_mode=ExecutionMode.PRODUCTION, catalog_is_fixture=True)
        self.assertEqual(result.classification, RiskClassification.UNAVAILABLE)
        self.assertEqual(result.unavailable_reason, "CATALOG_NOT_REGISTERED")

    def test_nonfixture_catalog_without_approval_evidence_fails_closed(self):
        result = self.classify(execution_mode=ExecutionMode.PRODUCTION,
                               catalog_is_fixture=False,
                               catalog_version="SUPPLIED-REVIEWED-CATALOG-v1",
                               classification_rule_version="SUPPLIED-CLASSIFY-v1")
        self.assertEqual(result.classification, RiskClassification.UNAVAILABLE)
        self.assertEqual(result.unavailable_reason, "CATALOG_NOT_REGISTERED")

    def test_caller_registry_and_fabricated_approval_cannot_authorize_production(self):
        result = self.classify(
            execution_mode=ExecutionMode.PRODUCTION, catalog_is_fixture=False,
            approval_reference="caller says approved",
            catalog_version="CALLER-CATALOG", classification_rule_version="CALLER-RULE",
        )
        self.assertEqual(result.classification, RiskClassification.UNAVAILABLE)
        self.assertEqual(result.unavailable_reason, "CATALOG_NOT_REGISTERED")

    def test_classifier_and_registry_reject_spoofed_execution_modes(self):
        class FakeMode:
            value = "PRODUCTION"

        class HostileEquality:
            value = "PRODUCTION"
            def __eq__(self, other):
                raise AssertionError("custom equality must not run")

        invalid_modes = (FakeMode(), "PRODUCTION", None, HostileEquality())
        registry = RiskRuleCatalogRegistry()
        registry.register(RiskRuleCatalogContract(
            "CALLER-CATALOG", "CALLER-RULE", self.VERSIONS,
            ContractState.ACTIVE, False, "fabricated approval",
        ))
        for mode in invalid_modes:
            with self.subTest(mode=type(mode).__name__, entry="classifier"):
                with self.assertRaises(TypeError):
                    self.classify(
                        execution_mode=mode, catalog_registry=RiskRuleCatalogRegistry(),
                        catalog_is_fixture=False, catalog_version="CALLER-CATALOG",
                        classification_rule_version="CALLER-RULE",
                        approval_reference="fabricated approval",
                    )
            with self.subTest(mode=type(mode).__name__, entry="registry"):
                with self.assertRaises(TypeError):
                    registry.resolve("CALLER-CATALOG", mode)

    def test_registered_condition_versions_are_defensively_immutable(self):
        versions = dict(self.VERSIONS)
        contract = RiskRuleCatalogContract(
            "FIXTURE-IMMUTABLE", "FIXTURE-RULE", versions,
            ContractState.ACTIVE, True,
        )
        registry = RiskRuleCatalogRegistry()
        registry.register(contract)
        versions["RC-01"] = "MUTATED"
        self.assertEqual(contract.condition_versions["RC-01"], self.VERSIONS["RC-01"])
        with self.assertRaises(TypeError):
            contract.condition_versions["RC-01"] = "MUTATED"

    def test_master_production_registry_has_no_activated_risk_catalog(self):
        master = MasterProductionRegistry()
        result = RiskClassificationEngine.classify(
            assessment_id="A-PROD", customer_id="C1", business_date=date(2025, 3, 9),
            assessment_at=datetime(2025, 3, 10, tzinfo=timezone.utc),
            condition_results=self.outcomes(), catalog_version="UNAPPROVED",
            classification_rule_version="RULE-v1", catalog_registry=master.risk_catalogs,
            execution_mode=ExecutionMode.PRODUCTION,
        )
        self.assertEqual(result.unavailable_reason, "CATALOG_NOT_REGISTERED")

    def test_production_catalog_is_rejected_in_fixture_mode(self):
        result = self.classify(catalog_is_fixture=False)
        self.assertEqual(result.unavailable_reason, "PRODUCTION_CATALOG_PROHIBITED_IN_FIXTURE_MODE")

    def test_multiple_observations_inside_condition_count_once(self):
        results = self.outcomes(triggered=1)
        results[0] = RiskConditionResult("RC-01", ConditionState.TRIGGERED,
            ("event-1", "event-2", "event-3"), (), self.VERSIONS["RC-01"])
        result = self.classify(results)
        self.assertEqual(result.triggered_count, 1)
        self.assertEqual(result.classification, RiskClassification.NOT_HIGH_RISK)


if __name__ == "__main__":
    unittest.main()
