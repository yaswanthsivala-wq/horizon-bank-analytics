"""Unit Tests for Reconciliation Accounting Engine.

Verifies RC-D01 row reconciliation, RC-D02 financial reconciliation,
exact-zero fixture tolerance, and pending production tolerance handling.
"""

from __future__ import annotations

import unittest
from decimal import Decimal

from horizon_pipeline.contracts.financial import FinancialControlContract
from horizon_pipeline.contracts.findings import FindingSeverity
from horizon_pipeline.contracts.states import ContractState
from horizon_pipeline.processing.reconciliation import OfflineReconciliationEngine


class ProcessingReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.engine = OfflineReconciliationEngine()

    def test_rc_d01_row_reconciliation_balanced(self):
        """RC-D01: Exactly balanced row counts produce balanced=True and zero residual."""
        res = self.engine.reconcile_package(
            section_manifest_counts={("SRC-01", "customers"): 10},
            raw_captured_counts={("SRC-01", "customers"): 10},
            accepted_counts={("SRC-01", "customers"): 8},
            quarantined_counts={("SRC-01", "customers"): 2},
            excluded_counts={("SRC-01", "customers"): 0},
        )
        self.assertTrue(res.all_balanced)
        self.assertEqual(len(res.findings), 0)
        self.assertEqual(res.row_results[0].residual, 0)

    def test_rc_d01_row_reconciliation_mismatch_emits_critical(self):
        """RC-D01: Unreconciled row residual produces CRITICAL finding."""
        res = self.engine.reconcile_package(
            section_manifest_counts={("SRC-01", "customers"): 10},
            raw_captured_counts={("SRC-01", "customers"): 10},
            accepted_counts={("SRC-01", "customers"): 7},  # Sum is 7+2 = 9 != 10
            quarantined_counts={("SRC-01", "customers"): 2},
            excluded_counts={("SRC-01", "customers"): 0},
        )
        self.assertFalse(res.all_balanced)
        self.assertEqual(len(res.findings), 1)
        self.assertEqual(res.findings[0].rule_id, "RC-D01")
        self.assertEqual(res.findings[0].severity, FindingSeverity.CRITICAL)
        self.assertEqual(res.row_results[0].residual, 1)

    def test_rc_d02_financial_reconciliation_exact_zero_fixture(self):
        """RC-D02: Financial reconciliation matches exactly within fixture tolerance."""
        ctrl = FinancialControlContract(
            control_id="FIXTURE-FC-TX",
            source="SRC-01",
            section="transactions",
            schema_version="FIXTURE.SYN.SRC-01.transactions.v001",
            amount_field="amount",
            currency_field="currency",
            currency="USD",
            state=ContractState.ACTIVE,
            tolerance=Decimal("0.0000"),
            tolerance_state=ContractState.ACTIVE,
            is_fixture=True,
        )
        mon_data = {
            ("SRC-01", "transactions"): {
                "source_total": [Decimal("100.0000")],
                "accepted": [Decimal("70.0000"), Decimal("15.0000")],
                "quarantined": [Decimal("15.0000")],
                "excluded": [],
            }
        }
        res = self.engine.reconcile_package(
            section_manifest_counts={("SRC-01", "transactions"): 3},
            raw_captured_counts={("SRC-01", "transactions"): 3},
            accepted_counts={("SRC-01", "transactions"): 2},
            quarantined_counts={("SRC-01", "transactions"): 1},
            financial_controls=[ctrl],
            monetary_data=mon_data,
        )
        self.assertTrue(res.all_balanced)
        fin = res.financial_results[0]
        self.assertTrue(fin.balanced)
        self.assertEqual(fin.residual, Decimal("0.0000"))

    def test_rc_d02_unresolved_production_tolerance_pending(self):
        """RC-D02: Control with tolerance=None reports status=PENDING_TOLERANCE."""
        ctrl = FinancialControlContract(
            control_id="FC-01",
            source="SRC-01",
            section="transactions",
            schema_version="HCB.SYN.SRC-01.transactions.v001",
            amount_field="amount",
            currency_field="currency",
            currency="USD",
            state=ContractState.PENDING,
            tolerance=None,
            tolerance_state=ContractState.PENDING,
            is_fixture=False,
        )
        res = self.engine.reconcile_package(
            section_manifest_counts={("SRC-01", "transactions"): 1},
            raw_captured_counts={("SRC-01", "transactions"): 1},
            accepted_counts={("SRC-01", "transactions"): 1},
            quarantined_counts={("SRC-01", "transactions"): 0},
            financial_controls=[ctrl],
        )
        fin = res.financial_results[0]
        self.assertEqual(fin.status, "PENDING_TOLERANCE")
        self.assertIsNone(fin.tolerance)


if __name__ == "__main__":
    unittest.main()
