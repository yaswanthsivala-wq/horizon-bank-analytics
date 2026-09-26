"""Approved RC-01 through RC-05 logical condition tests."""

import unittest
from datetime import date, datetime, timezone

from horizon_pipeline.analytics import ConditionState, PublicationEvidence, RiskConditionEvaluator
from horizon_pipeline.processing.records import ExecutionMode


class RiskConditionTests(unittest.TestCase):
    def setUp(self):
        self.as_of = datetime(2025, 3, 9, 12, tzinfo=timezone.utc)
        self.publication = PublicationEvidence(
            business_date=date(2025, 3, 9), publication_version="FIXTURE-PUB-1",
            revision=1, selected_publication_version="FIXTURE-PUB-1",
            selected_revision=1, manifest_present=True, population_complete=True,
            mapping_versions={
                "SRC-01:transaction_status": "FIXTURE-TX-v1",
                "SRC-01:restriction_status": "FIXTURE-RESTRICTION-v1",
                "SRC-02:loan_status": "FIXTURE-LOAN-v1",
                "SRC-03:fraud_case_status": "FIXTURE-FRAUD-STATUS-v1",
                "SRC-03:fraud_severity": "FIXTURE-FRAUD-SEVERITY-v1",
                "SRC-04:complaint_status": "FIXTURE-COMPLAINT-STATUS-v1",
                "SRC-04:complaint_priority": "FIXTURE-COMPLAINT-PRIORITY-v1",
            },
        )

    def _published(self, row):
        return dict(row, publication_version="FIXTURE-PUB-1", revision=1,
                    lineage_references=("ROW-LIN",))

    @property
    def fixture_args(self):
        return {"execution_mode": ExecutionMode.FIXTURE}

    def _tx(self, amount="10.0000", days=1, status="POSTED", currency="USD"):
        return {"transaction_id": f"PRIOR-{days}-{amount}", "amount": amount,
                "occurred_at": (self.as_of.replace(day=8)).isoformat(),
                "transaction_status": status, "currency": currency,
                "attributed_customer_id": "C1", "publication_version": "HISTORY-PUB",
                "revision": 1, "lineage_references": ("PRIOR-LIN",)}

    def _current(self, **overrides):
        row = {"transaction_id": "CURRENT-1", "amount": "30.0000",
               "occurred_at": self.as_of.isoformat(), "transaction_status": "POSTED",
               "currency": "USD", "publication_version": "FIXTURE-PUB-1", "revision": 1,
               "lineage_references": ("CURRENT-LIN",)}
        row.update(overrides)
        return row

    def test_rc01_exact_threshold_triggers(self):
        prior = [self._tx() for _ in range(5)]
        current = self._current()
        result = RiskConditionEvaluator.rc01(current, prior, customer_id="C1",
            effective_owner_ids=["C1"], initiator_id="C1", window_complete=True,
            mapping_ready=True, publication=self.publication,
            lineage_references=["LIN-1"], **self.fixture_args)
        self.assertEqual(result.state, ConditionState.TRIGGERED)
        self.assertEqual(result.lineage_references, ("LIN-1", "CURRENT-LIN", "PRIOR-LIN"))

    def test_rc01_below_threshold_not_triggered(self):
        current = self._current(amount="29.9999", transaction_status="SUCCESSFUL")
        result = RiskConditionEvaluator.rc01(current, [self._tx() for _ in range(5)],
            customer_id="C1", effective_owner_ids=["C1"], initiator_id=None, window_complete=True,
            mapping_ready=True, publication=self.publication, **self.fixture_args)
        self.assertEqual(result.state, ConditionState.NOT_TRIGGERED)

    def test_rc01_joint_owner_without_initiator_unknown(self):
        current = self._current()
        result = RiskConditionEvaluator.rc01(current, [self._tx() for _ in range(5)],
            customer_id="C1", effective_owner_ids=["C1", "C2"], initiator_id=None, window_complete=True,
            mapping_ready=True, publication=self.publication, **self.fixture_args)
        self.assertEqual(result.state, ConditionState.UNKNOWN)
        self.assertIn("JOINT_ACCOUNT_INITIATOR_UNRESOLVED", result.missing_evidence_reasons)

    def test_rc01_incomplete_or_fewer_than_five_unknown(self):
        current = self._current()
        result = RiskConditionEvaluator.rc01(current, [self._tx() for _ in range(4)],
            customer_id="C1", effective_owner_ids=["C1"], initiator_id="C1", window_complete=False,
            mapping_ready=True, publication=self.publication, **self.fixture_args)
        self.assertEqual(result.state, ConditionState.UNKNOWN)
        self.assertIn("INCOMPLETE_90_DAY_WINDOW", result.missing_evidence_reasons)

    def test_rc01_known_failed_status_is_excluded_not_compared(self):
        current = self._current(amount="100.0000", transaction_status="FAILED")
        result = RiskConditionEvaluator.rc01(current, [self._tx() for _ in range(5)],
            customer_id="C1", effective_owner_ids=["C1"], initiator_id="C1", window_complete=True,
            mapping_ready=True, publication=self.publication, **self.fixture_args)
        self.assertEqual(result.state, ConditionState.NOT_TRIGGERED)
        self.assertIn("recognized_excluded_status=FAILED", result.evidence)

    def test_rc02_positive_negative_and_mapping_unknown(self):
        alert = self._published({"alert_id": "A1", "case_status": "OPEN", "severity": "HIGH",
                 "effective_start": "2025-03-09T10:00:00+00:00"})
        args = dict(as_of=self.as_of, publication=self.publication, **self.fixture_args)
        self.assertEqual(RiskConditionEvaluator.rc02([alert], mapping_ready=True, **args).state, ConditionState.TRIGGERED)
        self.assertEqual(RiskConditionEvaluator.rc02([], mapping_ready=True,
            lineage_references=("DELIVERY-LIN",), **args).state, ConditionState.NOT_TRIGGERED)
        self.assertEqual(RiskConditionEvaluator.rc02([alert], mapping_ready=False, **args).state, ConditionState.UNKNOWN)

    def test_rc02_selects_latest_state_as_of(self):
        history = [
            self._published({"alert_id": "A1", "case_status": "OPEN", "severity": "HIGH", "effective_start": "2025-03-09T08:00:00+00:00"}),
            self._published({"alert_id": "A1", "case_status": "CLOSED", "severity": "HIGH", "effective_start": "2025-03-09T10:00:00+00:00"}),
        ]
        self.assertEqual(RiskConditionEvaluator.rc02(history, as_of=self.as_of, publication=self.publication, mapping_ready=True, **self.fixture_args).state, ConditionState.NOT_TRIGGERED)

    def test_rc03_strictly_greater_than_30_and_historical_as_of(self):
        base = {"loan_id": "L1", "loan_status": "ACTIVE", "business_date": "2025-03-09"}
        at_30 = self._published(dict(base, days_past_due=30))
        at_31 = self._published(dict(base, days_past_due=31))
        args = dict(as_of=self.as_of, publication=self.publication, mapping_ready=True, **self.fixture_args)
        self.assertEqual(RiskConditionEvaluator.rc03([at_30], ["L1"], **args).state, ConditionState.NOT_TRIGGERED)
        result = RiskConditionEvaluator.rc03([at_31], ["L1"], **args)
        self.assertEqual(result.state, ConditionState.TRIGGERED)
        self.assertEqual(result.as_of, self.as_of)

    def test_rc04_strict_sla_boundary_and_reopened_clock(self):
        exact = self._published({"complaint_id": "C1", "priority_at_creation": "Critical", "complaint_status": "REOPENED", "created_at": "2025-03-09T08:00:00+00:00"})
        self.assertEqual(RiskConditionEvaluator.rc04([exact], as_of=self.as_of, publication=self.publication, mapping_ready=True, **self.fixture_args).state, ConditionState.NOT_TRIGGERED)
        later = self.as_of.replace(minute=1)
        self.assertEqual(RiskConditionEvaluator.rc04([exact], as_of=later, publication=self.publication, mapping_ready=True, **self.fixture_args).state, ConditionState.TRIGGERED)

    def test_rc04_missing_priority_mapping_unknown(self):
        complaint = self._published({"complaint_id": "C1", "priority": "URGENT", "complaint_status": "OPEN", "created_at": "2025-03-01T00:00:00+00:00"})
        self.assertEqual(RiskConditionEvaluator.rc04([complaint], as_of=self.as_of, publication=self.publication, mapping_ready=True, **self.fixture_args).state, ConditionState.UNKNOWN)

    def test_rc05_as_of_restriction_and_incomplete_population(self):
        state = self._published({"account_id": "A1", "restriction_status": "FROZEN", "effective_start": "2025-03-09T08:00:00+00:00"})
        args = dict(as_of=self.as_of, mapping_ready=True, **self.fixture_args)
        self.assertEqual(RiskConditionEvaluator.rc05([state], ["A1"], publication=self.publication, **args).state, ConditionState.TRIGGERED)
        incomplete = PublicationEvidence(**{**self.publication.__dict__, "population_complete": False})
        self.assertEqual(RiskConditionEvaluator.rc05([state], ["A1"], publication=incomplete, **args).state, ConditionState.UNKNOWN)

    def test_rc05_selects_latest_restriction_state_as_of(self):
        history = [
            self._published({"account_id": "A1", "restriction_status": "FROZEN", "effective_start": "2025-03-09T08:00:00+00:00"}),
            self._published({"account_id": "A1", "restriction_status": "NONE", "effective_start": "2025-03-09T10:00:00+00:00"}),
        ]
        self.assertEqual(RiskConditionEvaluator.rc05(history, ["A1"], as_of=self.as_of, publication=self.publication, mapping_ready=True, **self.fixture_args).state, ConditionState.NOT_TRIGGERED)

    def test_rc01_window_uses_chicago_calendar_boundary_across_dst(self):
        as_of = datetime.fromisoformat("2025-03-10T00:00:00-05:00")
        current = {"transaction_id": "CURRENT-DST", "amount": "30", "occurred_at": as_of.isoformat(),
                   "transaction_status": "POSTED", "currency": "USD",
                   "publication_version": "FIXTURE-PUB-1", "revision": 1}
        prior = [
            {"transaction_id": "P0", "amount": "10", "occurred_at": "2024-12-10T00:00:00-06:00",
             "transaction_status": "POSTED", "currency": "USD", "attributed_customer_id": "C1",
             "publication_version": "HISTORY", "revision": 1}
        ] + [
            {"transaction_id": f"P{day}", "amount": "10", "occurred_at": f"2025-01-{day:02d}T00:00:00-06:00",
             "transaction_status": "POSTED", "currency": "USD", "attributed_customer_id": "C1",
             "publication_version": "HISTORY", "revision": 1}
            for day in range(1, 5)
        ]
        result = RiskConditionEvaluator.rc01(
            current, prior, customer_id="C1", effective_owner_ids=["C1"],
            initiator_id="C1", window_complete=True, mapping_ready=True,
            publication=self.publication, **self.fixture_args,
        )
        self.assertEqual(result.state, ConditionState.TRIGGERED)
        self.assertIn("prior_count=5", result.evidence)

    def test_rc01_daily_requires_manifest_confirmed_zero(self):
        args = dict(customer_id="C1", as_of=self.as_of, prior_transactions=[],
                    window_complete=True, mapping_ready=True, **self.fixture_args)
        unknown = RiskConditionEvaluator.rc01_customer_day([], publication=self.publication, **args)
        self.assertEqual(unknown.state, ConditionState.UNKNOWN)
        self.assertIn("selected_publication_version=FIXTURE-PUB-1", unknown.evidence)
        self.assertIn("selected_record_count=0", unknown.evidence)
        zero = PublicationEvidence(**{**self.publication.__dict__, "zero_row_confirmed": True})
        negative = RiskConditionEvaluator.rc01_customer_day(
            [], publication=zero, lineage_references=("DELIVERY-LIN",), **args)
        self.assertEqual(negative.state, ConditionState.NOT_TRIGGERED)

    def test_empty_population_without_delivery_lineage_is_unknown(self):
        evaluators = (
            lambda: RiskConditionEvaluator.rc02([], as_of=self.as_of, publication=self.publication,
                                                mapping_ready=True, **self.fixture_args),
            lambda: RiskConditionEvaluator.rc03([], [], as_of=self.as_of, publication=self.publication,
                                                mapping_ready=True, **self.fixture_args),
            lambda: RiskConditionEvaluator.rc04([], as_of=self.as_of, publication=self.publication,
                                                mapping_ready=True, **self.fixture_args),
            lambda: RiskConditionEvaluator.rc05([], [], as_of=self.as_of, publication=self.publication,
                                                mapping_ready=True, **self.fixture_args),
        )
        for evaluate in evaluators:
            with self.subTest(evaluate=evaluate):
                result = evaluate()
                self.assertEqual(result.state, ConditionState.UNKNOWN)
                self.assertIn("DELIVERY_LINEAGE_MISSING", result.missing_evidence_reasons)
                self.assertIn("selected_record_count=0", result.evidence)

    def test_publication_mapping_versions_are_defensively_immutable(self):
        mappings = {"SRC-02:loan_status": "FIXTURE-v1"}
        publication = PublicationEvidence(
            business_date=date(2025, 3, 9), publication_version="P1", revision=1,
            selected_publication_version="P1", selected_revision=1,
            manifest_present=True, population_complete=True, mapping_versions=mappings,
        )
        mappings["SRC-02:loan_status"] = "MUTATED"
        self.assertEqual(publication.mapping_versions["SRC-02:loan_status"], "FIXTURE-v1")
        with self.assertRaises(TypeError):
            publication.mapping_versions["SRC-02:loan_status"] = "MUTATED"

    def test_all_condition_entry_points_reject_spoofed_execution_modes(self):
        class FakeMode:
            value = "PRODUCTION"

        class HostileEquality:
            value = "PRODUCTION"
            def __eq__(self, other):
                raise AssertionError("custom equality must not run")

        invalid_modes = (FakeMode(), "PRODUCTION", None, HostileEquality())
        current = self._current()
        prior = [self._tx() for _ in range(5)]
        for mode in invalid_modes:
            calls = (
                lambda: RiskConditionEvaluator.rc01(
                    current, prior, customer_id="C1", effective_owner_ids=["C1"],
                    initiator_id="C1", window_complete=True, mapping_ready=True,
                    publication=self.publication, execution_mode=mode),
                lambda: RiskConditionEvaluator.rc01_customer_day(
                    [], [], customer_id="C1", as_of=self.as_of, publication=self.publication,
                    window_complete=True, mapping_ready=True, execution_mode=mode),
                lambda: RiskConditionEvaluator.rc02([], as_of=self.as_of, publication=self.publication,
                                                    mapping_ready=True, execution_mode=mode),
                lambda: RiskConditionEvaluator.rc03([], [], as_of=self.as_of, publication=self.publication,
                                                    mapping_ready=True, execution_mode=mode),
                lambda: RiskConditionEvaluator.rc04([], as_of=self.as_of, publication=self.publication,
                                                    mapping_ready=True, execution_mode=mode),
                lambda: RiskConditionEvaluator.rc05([], [], as_of=self.as_of, publication=self.publication,
                                                    mapping_ready=True, execution_mode=mode),
            )
            for call in calls:
                with self.subTest(mode=type(mode).__name__, call=call):
                    with self.assertRaises(TypeError):
                        call()

    def test_rc01_daily_trigger_dominates_unknown_and_counts_condition_once(self):
        prior = [self._tx() for _ in range(5)]
        base = dict(transaction_status="POSTED", currency="USD", customer_id="C1",
                    effective_owner_ids=["C1"], publication_version="FIXTURE-PUB-1", revision=1)
        rows = [
            dict(base, transaction_id="T1", amount="30", occurred_at=self.as_of.isoformat(), initiator_id="C1"),
            dict(base, transaction_id="T2", amount="40", occurred_at=self.as_of.isoformat(), initiator_id=None,
                 effective_owner_ids=["C1", "C2"]),
        ]
        result = RiskConditionEvaluator.rc01_customer_day(
            rows, prior, customer_id="C1", as_of=self.as_of,
            publication=self.publication, window_complete=True, mapping_ready=True,
            **self.fixture_args,
        )
        self.assertEqual(result.state, ConditionState.TRIGGERED)
        self.assertEqual(sum(item.startswith("triggering_transaction=") for item in result.evidence), 1)

    def test_correction_must_use_new_selected_revision(self):
        invalid = PublicationEvidence(**{
            **self.publication.__dict__, "revision": 1, "selected_revision": 1,
            "supersedes_revision": 1,
        })
        result = RiskConditionEvaluator.rc02([], as_of=self.as_of, publication=invalid,
                                             mapping_ready=True, **self.fixture_args)
        self.assertEqual(result.state, ConditionState.UNKNOWN)
        self.assertIn("INVALID_CORRECTION_REVISION", result.missing_evidence_reasons)

    def test_selected_publication_excludes_other_revision(self):
        stale = {"alert_id": "A1", "case_status": "OPEN", "severity": "HIGH",
                 "effective_start": "2025-03-09T10:00:00+00:00",
                 "publication_version": "FIXTURE-PUB-OLD", "revision": 1}
        result = RiskConditionEvaluator.rc02([stale], as_of=self.as_of,
                                             publication=self.publication,
                                             mapping_ready=True,
                                             lineage_references=("DELIVERY-LIN",),
                                             **self.fixture_args)
        self.assertEqual(result.state, ConditionState.NOT_TRIGGERED)

    def test_rc03_through_rc05_ignore_rows_outside_selected_publication(self):
        common = {"publication_version": "FIXTURE-PUB-OLD", "revision": 1}
        rc03 = RiskConditionEvaluator.rc03(
            [dict(common, loan_id="L1", loan_status="ACTIVE", days_past_due=90, business_date="2025-03-09")],
            ["L1"], as_of=self.as_of, publication=self.publication,
            mapping_ready=True, lineage_references=("DELIVERY-LIN",), **self.fixture_args,
        )
        rc04 = RiskConditionEvaluator.rc04(
            [dict(common, complaint_id="C1", priority_at_creation="Critical",
                  complaint_status="OPEN", created_at="2025-03-01T00:00:00+00:00")],
            as_of=self.as_of, publication=self.publication,
            mapping_ready=True, lineage_references=("DELIVERY-LIN",), **self.fixture_args,
        )
        rc05 = RiskConditionEvaluator.rc05(
            [dict(common, account_id="A1", restriction_status="FROZEN",
                  effective_start="2025-03-01T00:00:00+00:00")],
            ["A1"], as_of=self.as_of, publication=self.publication,
            mapping_ready=True, lineage_references=("DELIVERY-LIN",), **self.fixture_args,
        )
        self.assertEqual(
            (rc03.state, rc04.state, rc05.state),
            (ConditionState.NOT_TRIGGERED,) * 3,
        )

    def test_rc01_daily_filters_current_events_by_chicago_business_date(self):
        row = {
            "transaction_id": "T-OLD", "amount": "30", "currency": "USD",
            "transaction_status": "POSTED", "occurred_at": "2025-03-08T23:00:00-06:00",
            "customer_id": "C1", "effective_owner_ids": ["C1"], "initiator_id": "C1",
            "publication_version": "FIXTURE-PUB-1", "revision": 1,
        }
        result = RiskConditionEvaluator.rc01_customer_day(
            [row], [self._tx() for _ in range(5)], customer_id="C1", as_of=self.as_of,
            publication=self.publication, window_complete=True, mapping_ready=True,
            **self.fixture_args,
        )
        self.assertEqual(result.state, ConditionState.UNKNOWN)
        self.assertIn("ZERO_EVENTS_NOT_MANIFEST_CONFIRMED", result.missing_evidence_reasons)

    def test_production_conditions_fail_closed_on_pending_mapping_contracts(self):
        result = RiskConditionEvaluator.rc02(
            [], as_of=self.as_of, publication=self.publication, mapping_ready=True,
            execution_mode=ExecutionMode.PRODUCTION,
        )
        self.assertEqual(result.state, ConditionState.UNKNOWN)
        self.assertIn("MAPPING_UNAVAILABLE", result.missing_evidence_reasons)
        self.assertIn("PRODUCTION_PUBLICATION_AUTHORITY_PENDING", result.missing_evidence_reasons)

    def test_rc03_wrong_or_future_snapshot_date_is_unknown(self):
        wrong = self._published({"loan_id": "L1", "loan_status": "ACTIVE",
                                 "days_past_due": 31, "business_date": "2025-03-10"})
        result = RiskConditionEvaluator.rc03(
            [wrong], ["L1"], as_of=self.as_of, publication=self.publication,
            mapping_ready=True, **self.fixture_args,
        )
        self.assertEqual(result.state, ConditionState.UNKNOWN)
        self.assertIn("SNAPSHOT_BUSINESS_DATE_MISMATCH", result.missing_evidence_reasons)

        future_publication = PublicationEvidence(**{
            **self.publication.__dict__, "business_date": date(2025, 3, 10),
        })
        future = self._published({"loan_id": "L1", "loan_status": "ACTIVE",
                                  "days_past_due": 31, "business_date": "2025-03-10"})
        result = RiskConditionEvaluator.rc03(
            [future], ["L1"], as_of=self.as_of, publication=future_publication,
            mapping_ready=True, **self.fixture_args,
        )
        self.assertEqual(result.state, ConditionState.UNKNOWN)
        self.assertIn("ASSESSMENT_SNAPSHOT_DATE_MISMATCH", result.missing_evidence_reasons)

    def test_empty_and_triggered_populations_retain_publication_mapping_and_source_evidence(self):
        empty = RiskConditionEvaluator.rc02(
            [], as_of=self.as_of, publication=self.publication,
            mapping_ready=True, lineage_references=("DELIVERY-LIN",), **self.fixture_args,
        )
        self.assertEqual(empty.state, ConditionState.NOT_TRIGGERED)
        self.assertIn("selected_publication_version=FIXTURE-PUB-1", empty.evidence)
        self.assertIn("selected_revision=1", empty.evidence)
        self.assertIn("selected_record_count=0", empty.evidence)
        self.assertTrue(any(item.startswith("mapping_version:SRC-03:") for item in empty.evidence))
        self.assertEqual(empty.lineage_references, ("DELIVERY-LIN",))

        triggered = RiskConditionEvaluator.rc03(
            [self._published({"loan_id": "L1", "loan_status": "ACTIVE",
                              "days_past_due": 31, "business_date": "2025-03-09"})],
            ["L1"], as_of=self.as_of, publication=self.publication,
            mapping_ready=True, lineage_references=("POSITION-LIN",), **self.fixture_args,
        )
        self.assertEqual(triggered.state, ConditionState.TRIGGERED)
        self.assertIn("source_loan_id=L1", triggered.evidence)
        self.assertIn("selected_publication_version=FIXTURE-PUB-1", triggered.evidence)
        self.assertEqual(triggered.lineage_references, ("POSITION-LIN", "ROW-LIN"))

    def test_malformed_revision_dpd_and_timestamp_are_unknown(self):
        malformed_current = self._current(occurred_at="not-a-time")
        self.assertEqual(
            RiskConditionEvaluator.rc01(
                malformed_current, [self._tx() for _ in range(5)], customer_id="C1",
                effective_owner_ids=["C1"], initiator_id="C1", window_complete=True,
                mapping_ready=True, publication=self.publication, **self.fixture_args,
            ).state,
            ConditionState.UNKNOWN,
        )
        malformed_revision = {"alert_id": "A1", "case_status": "OPEN", "severity": "HIGH",
                              "effective_start": "2025-03-09T10:00:00+00:00",
                              "publication_version": "FIXTURE-PUB-1", "revision": "bad"}
        self.assertEqual(
            RiskConditionEvaluator.rc02([malformed_revision], as_of=self.as_of,
                                        publication=self.publication, mapping_ready=True,
                                        **self.fixture_args).state,
            ConditionState.UNKNOWN,
        )
        malformed_dpd = self._published({"loan_id": "L1", "loan_status": "ACTIVE",
                                         "days_past_due": "bad", "business_date": "2025-03-09"})
        self.assertEqual(
            RiskConditionEvaluator.rc03([malformed_dpd], ["L1"], as_of=self.as_of,
                                        publication=self.publication, mapping_ready=True,
                                        **self.fixture_args).state,
            ConditionState.UNKNOWN,
        )
        malformed_time = self._published({"account_id": "A1", "restriction_status": "FROZEN",
                                          "effective_start": "not-a-time"})
        self.assertEqual(
            RiskConditionEvaluator.rc05([malformed_time], ["A1"], as_of=self.as_of,
                                        publication=self.publication, mapping_ready=True,
                                        **self.fixture_args).state,
            ConditionState.UNKNOWN,
        )


if __name__ == "__main__":
    unittest.main()
