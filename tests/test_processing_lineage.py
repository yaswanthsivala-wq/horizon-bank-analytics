"""Unit Tests for Lineage Ledger and Causal Traceability.

Verifies end-to-end lineage links: raw record -> transform rules -> curated entity ID,
and audit retention tagging under DD-07 and DD-08.
"""

from __future__ import annotations

import unittest
from datetime import date

from horizon_pipeline.processing.lineage import LineageLedger
from horizon_pipeline.processing.records import RecordDisposition, RetentionCategory


class ProcessingLineageTests(unittest.TestCase):
    def setUp(self):
        self.ledger = LineageLedger()
        self.bdate = date(2025, 3, 9)

    def test_record_lineage_and_causal_lookup(self):
        """Record lineage and trace curated entity back to source record and checksum."""
        rec = self.ledger.record_lineage(
            run_id="RUN-100",
            package_id="PKG-20250309-1",
            business_date=self.bdate,
            source_system="SRC-01",
            section="customers",
            source_record_id="CUST-001",
            source_checksum="sha256_cust_payload",
            transformation_rules=("TRANSFORM_CUSTOMER", "MASKING_DD08"),
            disposition=RecordDisposition.ACCEPTED,
            curated_entity_id="CUST-001",
            finding_codes=(),
            retention_category=RetentionCategory.ANALYTICAL_24M,
        )

        self.assertIsNotNone(rec.lineage_id)
        looked_up = self.ledger.get_by_id(rec.lineage_id)
        self.assertEqual(looked_up, rec)
        self.assertEqual(looked_up.source_record_id, "CUST-001")
        self.assertEqual(looked_up.source_checksum, "sha256_cust_payload")
        self.assertEqual(looked_up.retention_category, RetentionCategory.ANALYTICAL_24M)
        self.assertEqual(self.ledger.count(), 1)


if __name__ == "__main__":
    unittest.main()
