"""Unit tests for PD-04 Conditional Applicability Engine."""

import unittest

from horizon_pipeline.contracts.applicability import (
    ApplicabilityPredicateContract,
    ApplicabilityRegistry,
    ApplicabilityState,
    CellState,
    CompletenessMetrics,
    FieldDisposition,
)
from horizon_pipeline.contracts.states import ContractState


class ApplicabilityTests(unittest.TestCase):
    def setUp(self):
        self.registry = ApplicabilityRegistry()

        # Register active fixture predicate: posted_at applicable only if payment_status == 'POSTED'
        self.registry.register(
            ApplicabilityPredicateContract(
                predicate_id="TEST-PRED-POSTED",
                source="SRC-02",
                section="payments",
                schema_version="TEST.SRC-02.payments.v1",
                field_name="posted_at",
                disposition=FieldDisposition.RECEIVED,
                state=ContractState.ACTIVE,
                evaluator=lambda row: row.get("payment_status") == "POSTED",
                is_fixture=True,
            )
        )

        # Register pending predicate
        self.registry.register(
            ApplicabilityPredicateContract(
                predicate_id="TEST-PRED-PENDING",
                source="SRC-01",
                section="customers",
                schema_version="TEST.SRC-01.customers.v1",
                field_name="approval_reference",
                disposition=FieldDisposition.RECEIVED,
                state=ContractState.PENDING,
                is_fixture=True,
            )
        )

    def test_cell_absent(self):
        state, findings = self.registry.evaluate_cell_state(
            "SRC-01", "accounts", "v1", "account_id",
            None, {}, ApplicabilityState.ALWAYS, True, True,
        )
        self.assertEqual(state, CellState.ABSENT)
        self.assertTrue(any(f.code == "APP-CELL-ABSENT" for f in findings))

    def test_blank_cell_is_not_inapplicable(self):
        # Invariant: blank != inapplicable
        state, findings = self.registry.evaluate_cell_state(
            "SRC-01", "accounts", "v1", "account_id",
            "   ", {"account_id": "   "}, ApplicabilityState.ALWAYS, True, True,
        )
        self.assertEqual(state, CellState.BLANK)
        self.assertNotEqual(state, CellState.INAPPLICABLE)
        self.assertTrue(any(f.code == "APP-BLANK-CELL" for f in findings))

    def test_null_recognized_empty_cell(self):
        # Empty string represents null per G3
        state, findings = self.registry.evaluate_cell_state(
            "SRC-01", "accounts", "v1", "account_id",
            "", {"account_id": ""}, ApplicabilityState.ALWAYS, True, True,
        )
        self.assertEqual(state, CellState.NULL)
        self.assertTrue(any(f.code == "APP-MISSING-REQUIRED" for f in findings))

    def test_invalid_cell_is_not_inapplicable(self):
        # Invariant: invalid != inapplicable
        state, findings = self.registry.evaluate_cell_state(
            "SRC-01", "accounts", "v1", "account_id",
            "invalid_id", {"account_id": "invalid_id"}, ApplicabilityState.ALWAYS, True, is_valid_type=False,
        )
        self.assertEqual(state, CellState.INVALID)
        self.assertNotEqual(state, CellState.INAPPLICABLE)
        self.assertTrue(any(f.code == "APP-INVALID-CELL" for f in findings))

    def test_conditional_applicable_true(self):
        row = {"payment_status": "POSTED"}
        state, findings = self.registry.evaluate_cell_state(
            "SRC-02", "payments", "TEST.SRC-02.payments.v1", "posted_at",
            "2025-03-09T12:00:00.000000Z", row, ApplicabilityState.CONDITIONAL, True, True,
        )
        self.assertEqual(state, CellState.VALID)
        self.assertEqual(findings, [])

    def test_conditional_applicable_false_validly_inapplicable(self):
        row = {"payment_status": "PENDING"}
        state, findings = self.registry.evaluate_cell_state(
            "SRC-02", "payments", "TEST.SRC-02.payments.v1", "posted_at",
            "", row, ApplicabilityState.CONDITIONAL, True, True,
        )
        self.assertEqual(state, CellState.INAPPLICABLE)
        self.assertEqual(findings, [])

    def test_inapplicable_cell_with_unexpected_value_fails(self):
        row = {"payment_status": "PENDING"}
        state, findings = self.registry.evaluate_cell_state(
            "SRC-02", "payments", "TEST.SRC-02.payments.v1", "posted_at",
            "2025-03-09T12:00:00.000000Z", row, ApplicabilityState.CONDITIONAL, True, True,
        )
        self.assertEqual(state, CellState.INAPPLICABLE)
        self.assertTrue(any(f.code == "APP-INAPPLICABLE-HAS-VALUE" for f in findings))

    def test_pending_predicate_fails_closed_as_unresolved(self):
        state, findings = self.registry.evaluate_cell_state(
            "SRC-01", "customers", "TEST.SRC-01.customers.v1", "approval_reference",
            "", {}, ApplicabilityState.CONDITIONAL, True, True,
        )
        self.assertEqual(state, CellState.UNRESOLVED)
        self.assertTrue(any(f.code == "APP-PREDICATE-PENDING" for f in findings))

    def test_unsupported_predicate_fails_closed_as_unresolved(self):
        state, findings = self.registry.evaluate_cell_state(
            "SRC-01", "customers", "unknown_schema", "unknown_field",
            "", {}, ApplicabilityState.CONDITIONAL, True, True,
        )
        self.assertEqual(state, CellState.UNRESOLVED)
        self.assertTrue(any(f.code == "APP-PREDICATE-UNSUPPORTED" for f in findings))

    def test_completeness_metrics_ratio_unavailable_when_unresolved(self):
        # When unresolved cells exist, completeness ratio must NOT be fabricated
        metrics_unresolved = CompletenessMetrics(
            applicable_required_denominator=100,
            present_required_numerator=95,
            inapplicable_cells=5,
            optional_cells=10,
            invalid_cells=2,
            unresolved_cells=1,
        )
        self.assertFalse(metrics_unresolved.is_computable)
        self.assertIsNone(metrics_unresolved.ratio)

        # When zero unresolved cells, ratio is computed
        metrics_clean = CompletenessMetrics(
            applicable_required_denominator=100,
            present_required_numerator=99,
            inapplicable_cells=5,
            optional_cells=10,
            invalid_cells=1,
            unresolved_cells=0,
        )
        self.assertTrue(metrics_clean.is_computable)
        self.assertEqual(metrics_clean.ratio, 0.99)


if __name__ == "__main__":
    unittest.main()
