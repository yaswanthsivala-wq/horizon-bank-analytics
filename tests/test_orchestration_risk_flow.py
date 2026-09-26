"""Customer Risk Flow and Classification Aggregation Tests.

CRITICAL NOTICE: TEST FIXTURES ONLY.
Verifies AC-ORCH-05 and AC-ORCH-06:
1. Exact t/u threshold classification logic under DD-04:
   - Customer A: t = 2, u = 1 -> PROVISIONAL_HIGH_RISK (Priority 2)
   - Customer B: t = 1, u = 2 (t < 2, t + u >= 2) -> INCOMPLETE_EVIDENCE (Priority 3)
   - Customer C: t = 0, u = 1 (t < 2, t + u < 2) -> NOT_HIGH_RISK (Priority 4)
   - Customer D: t = 0, u = 0 -> NOT_HIGH_RISK (Priority 4)
2. Incomplete evidence and unavailable populations are segregated and NEVER
   counted in not_high_risk_customer_count in mart_customer_risk_kpis.
3. relationship_exposure_non_additive is True across all records.
"""

from __future__ import annotations

import unittest
from datetime import date, datetime, timezone
from decimal import Decimal

from horizon_pipeline.analytics.kpi import KPIEngine
from horizon_pipeline.analytics.marts import MartBuilder
from horizon_pipeline.analytics.risk_classification import (
    EvidenceState,
    RiskAssessment,
    RiskClassification,
    RiskClassificationEngine,
)
from horizon_pipeline.analytics.risk_conditions import (
    ConditionState,
    RiskConditionResult,
)
from horizon_pipeline.analytics.risk_orchestrator import (
    DEFAULT_CONDITION_VERSIONS,
    CustomerRiskOrchestrator,
    build_default_fixture_risk_catalog,
)
from horizon_pipeline.contracts.risk import RiskRuleCatalogRegistry
from horizon_pipeline.contracts.states import ContractState
from horizon_pipeline.processing.records import ExecutionMode


class OrchestrationRiskFlowTests(unittest.TestCase):
    def setUp(self):
        self.bdate = date(2025, 3, 9)
        self.as_of = datetime(2025, 3, 9, 12, 0, 0, tzinfo=timezone.utc)
        self.registry = RiskRuleCatalogRegistry()
        self.registry.register(build_default_fixture_risk_catalog())

    def _make_condition_result(self, cond_id: str, state: ConditionState) -> RiskConditionResult:
        version = DEFAULT_CONDITION_VERSIONS.get(cond_id, f"{cond_id}-v1")
        return RiskConditionResult(
            condition_id=cond_id,
            state=state,
            evidence=("fixture_evidence",),
            lineage_references=("LIN-TEST",),
            rule_version=version,
            missing_evidence_reasons=("MISSING_EVIDENCE",) if state == ConditionState.UNKNOWN else (),
            as_of=self.as_of,
        )

    def test_risk_classification_t_u_rules_ac_orch_05(self):
        """Exact t/u evaluation under DD-04 policy (AC-ORCH-05)."""
        # Customer A: t = 2, u = 1 -> PROVISIONAL_HIGH_RISK
        conds_a = [
            self._make_condition_result("RC-01", ConditionState.TRIGGERED),
            self._make_condition_result("RC-02", ConditionState.TRIGGERED),
            self._make_condition_result("RC-03", ConditionState.UNKNOWN),
            self._make_condition_result("RC-04", ConditionState.NOT_TRIGGERED),
            self._make_condition_result("RC-05", ConditionState.NOT_TRIGGERED),
        ]
        asm_a = RiskClassificationEngine.classify(
            assessment_id="ASM-A",
            customer_id="CUST-A",
            business_date=self.bdate,
            assessment_at=self.as_of,
            condition_results=conds_a,
            catalog_version="CAT-RISK-2026A-FIXTURE",
            classification_rule_version="DD04-CLASSIFY-v1",
            catalog_registry=self.registry,
            execution_mode=ExecutionMode.FIXTURE,
        )
        self.assertEqual(asm_a.classification, RiskClassification.PROVISIONAL_HIGH_RISK)
        self.assertEqual(asm_a.evidence_state, EvidenceState.INCOMPLETE)

        # Customer B: t = 1, u = 2 (t < 2, t + u = 3 >= 2) -> INCOMPLETE_EVIDENCE
        conds_b = [
            self._make_condition_result("RC-01", ConditionState.TRIGGERED),
            self._make_condition_result("RC-02", ConditionState.UNKNOWN),
            self._make_condition_result("RC-03", ConditionState.UNKNOWN),
            self._make_condition_result("RC-04", ConditionState.NOT_TRIGGERED),
            self._make_condition_result("RC-05", ConditionState.NOT_TRIGGERED),
        ]
        asm_b = RiskClassificationEngine.classify(
            assessment_id="ASM-B",
            customer_id="CUST-B",
            business_date=self.bdate,
            assessment_at=self.as_of,
            condition_results=conds_b,
            catalog_version="CAT-RISK-2026A-FIXTURE",
            classification_rule_version="DD04-CLASSIFY-v1",
            catalog_registry=self.registry,
            execution_mode=ExecutionMode.FIXTURE,
        )
        self.assertEqual(asm_b.classification, RiskClassification.INCOMPLETE_EVIDENCE)
        self.assertEqual(asm_b.evidence_state, EvidenceState.INCOMPLETE)

        # Customer C: t = 0, u = 1 (t < 2, t + u = 1 < 2) -> NOT_HIGH_RISK
        conds_c = [
            self._make_condition_result("RC-01", ConditionState.UNKNOWN),
            self._make_condition_result("RC-02", ConditionState.NOT_TRIGGERED),
            self._make_condition_result("RC-03", ConditionState.NOT_TRIGGERED),
            self._make_condition_result("RC-04", ConditionState.NOT_TRIGGERED),
            self._make_condition_result("RC-05", ConditionState.NOT_TRIGGERED),
        ]
        asm_c = RiskClassificationEngine.classify(
            assessment_id="ASM-C",
            customer_id="CUST-C",
            business_date=self.bdate,
            assessment_at=self.as_of,
            condition_results=conds_c,
            catalog_version="CAT-RISK-2026A-FIXTURE",
            classification_rule_version="DD04-CLASSIFY-v1",
            catalog_registry=self.registry,
            execution_mode=ExecutionMode.FIXTURE,
        )
        self.assertEqual(asm_c.classification, RiskClassification.NOT_HIGH_RISK)
        self.assertEqual(asm_c.evidence_state, EvidenceState.INCOMPLETE)

        # Customer D: t = 0, u = 0 -> NOT_HIGH_RISK
        conds_d = [
            self._make_condition_result("RC-01", ConditionState.NOT_TRIGGERED),
            self._make_condition_result("RC-02", ConditionState.NOT_TRIGGERED),
            self._make_condition_result("RC-03", ConditionState.NOT_TRIGGERED),
            self._make_condition_result("RC-04", ConditionState.NOT_TRIGGERED),
            self._make_condition_result("RC-05", ConditionState.NOT_TRIGGERED),
        ]
        asm_d = RiskClassificationEngine.classify(
            assessment_id="ASM-D",
            customer_id="CUST-D",
            business_date=self.bdate,
            assessment_at=self.as_of,
            condition_results=conds_d,
            catalog_version="CAT-RISK-2026A-FIXTURE",
            classification_rule_version="DD04-CLASSIFY-v1",
            catalog_registry=self.registry,
            execution_mode=ExecutionMode.FIXTURE,
        )
        self.assertEqual(asm_d.classification, RiskClassification.NOT_HIGH_RISK)
        self.assertEqual(asm_d.evidence_state, EvidenceState.COMPLETE)

    def test_customer_risk_mart_segregates_incomplete_evidence(self):
        """Customer risk mart segregates unknown populations from not-high-risk (AC-ORCH-05/06)."""
        # Create assessments for customers A, B, C, D
        conds_a = [self._make_condition_result("RC-01", ConditionState.TRIGGERED), self._make_condition_result("RC-02", ConditionState.TRIGGERED), self._make_condition_result("RC-03", ConditionState.NOT_TRIGGERED), self._make_condition_result("RC-04", ConditionState.NOT_TRIGGERED), self._make_condition_result("RC-05", ConditionState.NOT_TRIGGERED)]
        conds_b = [self._make_condition_result("RC-01", ConditionState.TRIGGERED), self._make_condition_result("RC-02", ConditionState.UNKNOWN), self._make_condition_result("RC-03", ConditionState.UNKNOWN), self._make_condition_result("RC-04", ConditionState.NOT_TRIGGERED), self._make_condition_result("RC-05", ConditionState.NOT_TRIGGERED)]
        conds_c = [self._make_condition_result("RC-01", ConditionState.NOT_TRIGGERED), self._make_condition_result("RC-02", ConditionState.NOT_TRIGGERED), self._make_condition_result("RC-03", ConditionState.NOT_TRIGGERED), self._make_condition_result("RC-04", ConditionState.NOT_TRIGGERED), self._make_condition_result("RC-05", ConditionState.NOT_TRIGGERED)]

        asm_a = RiskClassificationEngine.classify(assessment_id="A", customer_id="CA", business_date=self.bdate, assessment_at=self.as_of, condition_results=conds_a, catalog_version="CAT-RISK-2026A-FIXTURE", classification_rule_version="DD04-CLASSIFY-v1", catalog_registry=self.registry, execution_mode=ExecutionMode.FIXTURE)
        asm_b = RiskClassificationEngine.classify(assessment_id="B", customer_id="CB", business_date=self.bdate, assessment_at=self.as_of, condition_results=conds_b, catalog_version="CAT-RISK-2026A-FIXTURE", classification_rule_version="DD04-CLASSIFY-v1", catalog_registry=self.registry, execution_mode=ExecutionMode.FIXTURE)
        asm_c = RiskClassificationEngine.classify(assessment_id="C", customer_id="CC", business_date=self.bdate, assessment_at=self.as_of, condition_results=conds_c, catalog_version="CAT-RISK-2026A-FIXTURE", classification_rule_version="DD04-CLASSIFY-v1", catalog_registry=self.registry, execution_mode=ExecutionMode.FIXTURE)

        customers = [
            {"customer_id": "CA", "primary_branch_id": "BR-1"},
            {"customer_id": "CB", "primary_branch_id": "BR-1"},
            {"customer_id": "CC", "primary_branch_id": "BR-1"},
        ]

        mart_records = MartBuilder.build_customer_risk_mart(
            assessments=[asm_a, asm_b, asm_c],
            customers=customers,
            as_of_date=self.bdate,
            execution_mode=ExecutionMode.FIXTURE,
        )

        self.assertEqual(len(mart_records), 1)
        r = mart_records[0]
        self.assertEqual(r.total_assessed_customer_count, 3)
        self.assertEqual(r.provisional_high_risk_customer_count, 1)  # Customer A
        self.assertEqual(r.incomplete_evidence_customer_count, 1)    # Customer B
        self.assertEqual(r.not_high_risk_customer_count, 1)          # Customer C (Customer B is NOT here!)
        self.assertTrue(r.relationship_exposure_non_additive)


if __name__ == "__main__":
    unittest.main()
