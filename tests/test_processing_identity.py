"""Unit Tests for Record Identity and Deduplication Engine.

Verifies natural key identification, exact duplicate suppression (INFO),
and conflicting duplicate key detection (CRITICAL) under DD-09 Rule DQ-D02.
"""

from __future__ import annotations

import unittest
from datetime import date

from horizon_pipeline.contracts.findings import FindingSeverity
from horizon_pipeline.processing.identity import RecordIdentityEngine
from horizon_pipeline.processing.records import RawRecord


class ProcessingIdentityTests(unittest.TestCase):
    def setUp(self):
        self.engine = RecordIdentityEngine()
        self.bdate = date(2025, 3, 9)

    def test_distinct_records_accepted(self):
        """Distinct natural keys must all be accepted."""
        rec1 = RawRecord("SRC-01", "customers", "CUST-1", self.bdate, 1, 1, {"customer_id": "CUST-1", "name": "Alice"})
        rec2 = RawRecord("SRC-01", "customers", "CUST-2", self.bdate, 1, 2, {"customer_id": "CUST-2", "name": "Bob"})
        res = self.engine.deduplicate_section([rec1, rec2])
        self.assertEqual(len(res.accepted_records), 2)
        self.assertEqual(len(res.quarantined_records), 0)
        self.assertEqual(len(res.findings), 0)

    def test_exact_duplicate_suppression_emits_info(self):
        """Exact identical rows on same natural key produce INFO finding."""
        rec1 = RawRecord("SRC-01", "customers", "CUST-1", self.bdate, 1, 1, {"customer_id": "CUST-1", "name": "Alice"})
        rec2 = RawRecord("SRC-01", "customers", "CUST-1_dup", self.bdate, 1, 2, {"customer_id": "CUST-1", "name": "Alice"})
        res = self.engine.deduplicate_section([rec1, rec2])
        self.assertEqual(len(res.accepted_records), 1)
        self.assertEqual(len(res.quarantined_records), 1)
        self.assertEqual(len(res.findings), 1)
        self.assertEqual(res.findings[0].rule_id, "DQ-D02")
        self.assertEqual(res.findings[0].severity, FindingSeverity.INFO)

    def test_conflicting_duplicate_emits_critical(self):
        """Conflicting field values on same natural key produce CRITICAL finding."""
        rec1 = RawRecord("SRC-01", "customers", "CUST-1", self.bdate, 1, 1, {"customer_id": "CUST-1", "name": "Alice"})
        rec2 = RawRecord("SRC-01", "customers", "CUST-1_conf", self.bdate, 1, 2, {"customer_id": "CUST-1", "name": "ConflictName"})
        res = self.engine.deduplicate_section([rec1, rec2])
        self.assertEqual(len(res.accepted_records), 1)
        self.assertEqual(len(res.quarantined_records), 1)
        self.assertEqual(len(res.findings), 1)
        self.assertEqual(res.findings[0].rule_id, "DQ-D02")
        self.assertEqual(res.findings[0].severity, FindingSeverity.CRITICAL)

    def test_composite_natural_key_deduplication(self):
        """Holders composite key: account_id + customer_id + relationship_role + effective_start."""
        rec1 = RawRecord(
            "SRC-01",
            "holders",
            "H-1",
            self.bdate,
            1,
            1,
            {
                "account_id": "ACC-1",
                "customer_id": "CUST-1",
                "relationship_role": "PRIMARY",
                "effective_start": "2025-01-01",
                "status": "ACTIVE",
            },
        )
        # Different role: distinct key, must be accepted
        rec2 = RawRecord(
            "SRC-01",
            "holders",
            "H-2",
            self.bdate,
            1,
            2,
            {
                "account_id": "ACC-1",
                "customer_id": "CUST-1",
                "relationship_role": "JOINT",
                "effective_start": "2025-01-01",
                "status": "ACTIVE",
            },
        )
        res = self.engine.deduplicate_section([rec1, rec2])
        self.assertEqual(len(res.accepted_records), 2)
        self.assertEqual(len(res.quarantined_records), 0)

    def test_production_mode_identity_fails_closed(self):
        """In PRODUCTION mode, deduplicate_section fails closed because PD-01 headers are PENDING."""
        from horizon_pipeline.processing.records import ExecutionMode

        prod_engine = RecordIdentityEngine(execution_mode=ExecutionMode.PRODUCTION)
        rec = RawRecord("SRC-01", "customers", "C-1", self.bdate, 1, 1, {"customer_id": "C-1"})
        res = prod_engine.deduplicate_section([rec])
        self.assertEqual(len(res.accepted_records), 0)
        self.assertEqual(len(res.quarantined_records), 1)
        self.assertEqual(res.findings[0].severity, FindingSeverity.CRITICAL)


if __name__ == "__main__":
    unittest.main()
