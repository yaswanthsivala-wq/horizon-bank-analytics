"""Unit Tests for Raw and Curated Record Structures.

Verifies immutability, type constraints, retention classification, and
execution mode enums under Package 2.
"""

from __future__ import annotations

import dataclasses
import unittest
from datetime import date, datetime, timezone
from decimal import Decimal

from horizon_pipeline.processing.records import (
    CuratedAccount,
    CuratedAccountHolder,
    CuratedBorrower,
    CuratedBranch,
    CuratedComplaint,
    CuratedCustomer,
    CuratedFraudAlert,
    CuratedLoan,
    CuratedPayment,
    CuratedPosition,
    CuratedTransaction,
    ExecutionMode,
    RawRecord,
    RecordDisposition,
    RetentionCategory,
)


class ProcessingRecordsTests(unittest.TestCase):
    def test_execution_mode_values(self):
        """ExecutionMode must strictly define FIXTURE and PRODUCTION."""
        self.assertEqual(ExecutionMode.FIXTURE.value, "FIXTURE")
        self.assertEqual(ExecutionMode.PRODUCTION.value, "PRODUCTION")

    def test_retention_category_values(self):
        """RetentionCategory must reflect DD-10 classifications."""
        self.assertEqual(RetentionCategory.ANALYTICAL_24M.value, "ANALYTICAL_24M")
        self.assertEqual(RetentionCategory.AUDIT_7Y.value, "AUDIT_7Y")

    def test_record_disposition_values(self):
        """RecordDisposition must define ACCEPTED, QUARANTINED, and EXCLUDED."""
        self.assertEqual(RecordDisposition.ACCEPTED.value, "ACCEPTED")
        self.assertEqual(RecordDisposition.QUARANTINED.value, "QUARANTINED")
        self.assertEqual(RecordDisposition.EXCLUDED.value, "EXCLUDED")

    def test_raw_record_immutability(self):
        """RawRecord must be frozen and immutable."""
        rec = RawRecord(
            source="SRC-01",
            section="customers",
            record_id="CUST-001",
            business_date=date(2025, 3, 9),
            revision=1,
            row_index=1,
            fields={"customer_id": "CUST-001"},
        )
        with self.assertRaises(dataclasses.FrozenInstanceError):
            rec.record_id = "CUST-002"  # type: ignore

    def test_curated_customer_immutability_and_retention(self):
        """CuratedCustomer must be immutable and default to 24M analytical retention."""
        cust = CuratedCustomer(
            customer_id="CUST-001",
            customer_name_masked="***oe",
            tax_identifier_masked="***-**-1234",
            customer_segment="RETAIL",
            primary_branch_id="BR-001",
            business_date=date(2025, 3, 9),
        )
        self.assertEqual(cust.retention_category, RetentionCategory.ANALYTICAL_24M)
        self.assertEqual(cust.source_system, "SRC-01")
        with self.assertRaises(dataclasses.FrozenInstanceError):
            cust.customer_segment = "COMMERCIAL"  # type: ignore

    def test_curated_transaction_scale4_immutability(self):
        """CuratedTransaction must hold exact scale-4 Decimal amount."""
        amt = Decimal("150.2500")
        tx = CuratedTransaction(
            transaction_id="TX-001",
            account_id="ACC-001",
            account_id_masked="******0001",
            business_date=date(2025, 3, 9),
            amount=amt,
            currency="USD",
            transaction_type="DEPOSIT",
            transaction_status="POSTED",
            raw_transaction_status="SUCCESSFUL",
            posted_at=datetime(2025, 3, 9, 12, 0, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(tx.amount, amt)
        self.assertEqual(tx.retention_category, RetentionCategory.ANALYTICAL_24M)
        with self.assertRaises(dataclasses.FrozenInstanceError):
            tx.amount = Decimal("200.0000")  # type: ignore


if __name__ == "__main__":
    unittest.main()
