"""Approved RC-01 through RC-05 logical condition tests."""

import unittest
from datetime import datetime, timezone

from horizon_pipeline.analytics import ConditionState, RiskConditionEvaluator


class RiskConditionTests(unittest.TestCase):
    def setUp(self):
        self.as_of = datetime(2025, 3, 9, 12, tzinfo=timezone.utc)

    def _tx(self, amount="10.0000", days=1, status="POSTED", currency="USD"):
        return {"amount": amount, "occurred_at": (self.as_of.replace(day=8)).isoformat(),
                "transaction_status": status, "currency": currency}

    def test_rc01_exact_threshold_triggers(self):
        prior = [self._tx() for _ in range(5)]
        current = {"amount": "30.0000", "occurred_at": self.as_of.isoformat(),
                   "transaction_status": "POSTED", "currency": "USD"}
        result = RiskConditionEvaluator.rc01(current, prior, customer_id="C1",
            effective_owner_ids=["C1"], initiator_id="C1", window_complete=True,
            lineage_references=["LIN-1"])
        self.assertEqual(result.state, ConditionState.TRIGGERED)
        self.assertEqual(result.lineage_references, ("LIN-1",))

    def test_rc01_below_threshold_not_triggered(self):
        current = {"amount": "29.9999", "occurred_at": self.as_of.isoformat(),
                   "transaction_status": "SUCCESSFUL", "currency": "USD"}
        result = RiskConditionEvaluator.rc01(current, [self._tx() for _ in range(5)],
            customer_id="C1", effective_owner_ids=["C1"], initiator_id=None, window_complete=True)
        self.assertEqual(result.state, ConditionState.NOT_TRIGGERED)

    def test_rc01_joint_owner_without_initiator_unknown(self):
        current = {"amount": "30.0000", "occurred_at": self.as_of.isoformat(),
                   "transaction_status": "POSTED", "currency": "USD"}
        result = RiskConditionEvaluator.rc01(current, [self._tx() for _ in range(5)],
            customer_id="C1", effective_owner_ids=["C1", "C2"], initiator_id=None, window_complete=True)
        self.assertEqual(result.state, ConditionState.UNKNOWN)
        self.assertIn("JOINT_ACCOUNT_INITIATOR_UNRESOLVED", result.missing_evidence_reasons)

    def test_rc01_incomplete_or_fewer_than_five_unknown(self):
        current = {"amount": "30.0000", "occurred_at": self.as_of.isoformat(),
                   "transaction_status": "POSTED", "currency": "USD"}
        result = RiskConditionEvaluator.rc01(current, [self._tx() for _ in range(4)],
            customer_id="C1", effective_owner_ids=["C1"], initiator_id="C1", window_complete=False)
        self.assertEqual(result.state, ConditionState.UNKNOWN)
        self.assertIn("INCOMPLETE_90_DAY_WINDOW", result.missing_evidence_reasons)

    def test_rc01_known_failed_status_is_excluded_not_compared(self):
        current = {"amount": "100.0000", "occurred_at": self.as_of.isoformat(),
                   "transaction_status": "FAILED", "currency": "USD"}
        result = RiskConditionEvaluator.rc01(current, [self._tx() for _ in range(5)],
            customer_id="C1", effective_owner_ids=["C1"], initiator_id="C1", window_complete=True)
        self.assertEqual(result.state, ConditionState.NOT_TRIGGERED)
        self.assertIn("recognized_excluded_status=FAILED", result.evidence)

    def test_rc02_positive_negative_and_mapping_unknown(self):
        alert = {"alert_id": "A1", "case_status": "OPEN", "severity": "HIGH",
                 "effective_start": "2025-03-09T10:00:00+00:00"}
        self.assertEqual(RiskConditionEvaluator.rc02([alert], as_of=self.as_of, population_complete=True, mapping_ready=True).state, ConditionState.TRIGGERED)
        self.assertEqual(RiskConditionEvaluator.rc02([], as_of=self.as_of, population_complete=True, mapping_ready=True).state, ConditionState.NOT_TRIGGERED)
        self.assertEqual(RiskConditionEvaluator.rc02([alert], as_of=self.as_of, population_complete=True, mapping_ready=False).state, ConditionState.UNKNOWN)

    def test_rc02_selects_latest_state_as_of(self):
        history = [
            {"alert_id": "A1", "case_status": "OPEN", "severity": "HIGH", "effective_start": "2025-03-09T08:00:00+00:00"},
            {"alert_id": "A1", "case_status": "CLOSED", "severity": "HIGH", "effective_start": "2025-03-09T10:00:00+00:00"},
        ]
        self.assertEqual(RiskConditionEvaluator.rc02(history, as_of=self.as_of, population_complete=True, mapping_ready=True).state, ConditionState.NOT_TRIGGERED)

    def test_rc03_strictly_greater_than_30_and_historical_as_of(self):
        base = {"loan_id": "L1", "loan_status": "ACTIVE"}
        at_30 = dict(base, days_past_due=30)
        at_31 = dict(base, days_past_due=31)
        self.assertEqual(RiskConditionEvaluator.rc03([at_30], ["L1"], as_of=self.as_of, population_complete=True, mapping_ready=True).state, ConditionState.NOT_TRIGGERED)
        result = RiskConditionEvaluator.rc03([at_31], ["L1"], as_of=self.as_of, population_complete=True, mapping_ready=True)
        self.assertEqual(result.state, ConditionState.TRIGGERED)
        self.assertEqual(result.as_of, self.as_of)

    def test_rc04_strict_sla_boundary_and_reopened_clock(self):
        exact = {"complaint_id": "C1", "priority_at_creation": "Critical", "complaint_status": "REOPENED", "created_at": "2025-03-09T08:00:00+00:00"}
        self.assertEqual(RiskConditionEvaluator.rc04([exact], as_of=self.as_of, population_complete=True, mapping_ready=True).state, ConditionState.NOT_TRIGGERED)
        later = self.as_of.replace(minute=1)
        self.assertEqual(RiskConditionEvaluator.rc04([exact], as_of=later, population_complete=True, mapping_ready=True).state, ConditionState.TRIGGERED)

    def test_rc04_missing_priority_mapping_unknown(self):
        complaint = {"complaint_id": "C1", "priority": "URGENT", "complaint_status": "OPEN", "created_at": "2025-03-01T00:00:00+00:00"}
        self.assertEqual(RiskConditionEvaluator.rc04([complaint], as_of=self.as_of, population_complete=True, mapping_ready=True).state, ConditionState.UNKNOWN)

    def test_rc05_as_of_restriction_and_incomplete_population(self):
        state = {"account_id": "A1", "restriction_status": "FROZEN", "effective_start": "2025-03-09T08:00:00+00:00"}
        self.assertEqual(RiskConditionEvaluator.rc05([state], ["A1"], as_of=self.as_of, population_complete=True, mapping_ready=True).state, ConditionState.TRIGGERED)
        self.assertEqual(RiskConditionEvaluator.rc05([state], ["A1"], as_of=self.as_of, population_complete=False, mapping_ready=True).state, ConditionState.UNKNOWN)

    def test_rc05_selects_latest_restriction_state_as_of(self):
        history = [
            {"account_id": "A1", "restriction_status": "FROZEN", "effective_start": "2025-03-09T08:00:00+00:00"},
            {"account_id": "A1", "restriction_status": "NONE", "effective_start": "2025-03-09T10:00:00+00:00"},
        ]
        self.assertEqual(RiskConditionEvaluator.rc05(history, ["A1"], as_of=self.as_of, population_complete=True, mapping_ready=True).state, ConditionState.NOT_TRIGGERED)


if __name__ == "__main__":
    unittest.main()
