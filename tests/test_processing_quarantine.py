"""Unit Tests for Quarantine Ledger and Isolation Management.

Verifies quarantine preservation, audit retention classification, and monetary
accounting for financial reconciliation.
"""

from __future__ import annotations

import unittest
from datetime import date, datetime, timezone
from decimal import Decimal

from horizon_pipeline.contracts.findings import FindingSeverity
from horizon_pipeline.processing.quality import RecordFinding
from horizon_pipeline.processing.quarantine import QuarantineLedger
from horizon_pipeline.processing.records import RawRecord, RecordDisposition, RetentionCategory


class ProcessingQuarantineTests(unittest.TestCase):
    def setUp(self):
        self.ledger = QuarantineLedger()
        self.bdate = date(2025, 3, 9)

    def test_record_quarantine_analytical_retention(self):
        """Quarantined records follow 24-month analytical schedule per DD-10 line 69."""
        raw = RawRecord(
            source="SRC-01",
            section="transactions",
            record_id="TX-FAIL-1",
            business_date=self.bdate,
            revision=1,
            row_index=1,
            fields={"transaction_id": "TX-FAIL-1", "amount": "invalid"},
        )
        finding = RecordFinding(
            rule_id="DQ-D07",
            source="SRC-01",
            section="transactions",
            record_identity="TX-FAIL-1",
            field_name="amount",
            severity=FindingSeverity.ERROR,
            original_severity=FindingSeverity.ERROR,
            escalation_reason="",
            disposition=RecordDisposition.QUARANTINED,
            observed_value="invalid",
            expected_rule="Decimal required",
            message="Invalid amount",
        )
        qrec = self.ledger.record_quarantine(raw, [finding])
        self.assertEqual(qrec.retention_category, RetentionCategory.ANALYTICAL_24M)
        self.assertEqual(qrec.source, "SRC-01")
        self.assertEqual(qrec.section, "transactions")
        self.assertEqual(len(qrec.findings), 1)
        self.assertEqual(self.ledger.count(), 1)

    def test_quarantine_monetary_total_calculation(self):
        """Quarantine ledger sums monetary amounts with scale-4 precision."""
        for i, amt in enumerate(["10.5000", "25.2500", "invalid", "14.2500"]):
            raw = RawRecord(
                source="SRC-01",
                section="transactions",
                record_id=f"TX-{i}",
                business_date=self.bdate,
                revision=1,
                row_index=i + 1,
                fields={"transaction_id": f"TX-{i}", "amount": amt},
            )
            self.ledger.record_quarantine(raw, [])

        total = self.ledger.total_monetary_amount("SRC-01", "transactions", "amount")
        # 10.5000 + 25.2500 + 14.2500 = 50.0000
        self.assertEqual(total, Decimal("50.0000"))


if __name__ == "__main__":
    unittest.main()
