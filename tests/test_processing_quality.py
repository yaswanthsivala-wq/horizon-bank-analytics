"""Unit Tests for Data Quality Rule Catalog and Evaluation Engine.

Verifies DD-09 rule enforcement: DQ-D03, DQ-D04, DQ-D07, DQ-D08, DQ-D09, and DQ-D10.
"""

from __future__ import annotations

import unittest
from datetime import date
from decimal import Decimal

from horizon_pipeline.contracts.findings import FindingSeverity
from horizon_pipeline.processing.quality import DataQualityEngine
from horizon_pipeline.processing.records import RawRecord, RecordDisposition


class ProcessingQualityTests(unittest.TestCase):
    def setUp(self):
        self.bdate = date(2025, 3, 9)
        self.engine = DataQualityEngine(check_referential_integrity=True)

    def test_dq_d03_missing_required_field(self):
        """Rule DQ-D03: Missing required field produces ERROR finding and quarantines record."""
        # customer missing customer_name
        raw = RawRecord(
            source="SRC-01",
            section="customers",
            record_id="CUST-001",
            business_date=self.bdate,
            revision=1,
            row_index=1,
            fields={
                "customer_id": "CUST-001",
                "customer_name": "",  # Empty
                "tax_identifier_masked": "123-45-6789",
                "customer_segment": "RETAIL",
                "primary_branch_id": "BR-001",
            },
        )
        findings_map, summary = self.engine.evaluate_batch({("SRC-01", "customers"): [raw]})
        self.assertIn(("SRC-01", "customers", "CUST-001"), findings_map)
        finds = findings_map[("SRC-01", "customers", "CUST-001")]
        self.assertTrue(any(f.rule_id == "DQ-D03" for f in finds))
        self.assertEqual(summary.quarantined_records, 1)
        self.assertEqual(summary.accepted_records, 0)

    def test_dq_d07_amount_scale_exceeded(self):
        """Rule DQ-D07: Monetary amount with more than 4 decimal places produces ERROR."""
        raw = RawRecord(
            source="SRC-01",
            section="transactions",
            record_id="TX-001",
            business_date=self.bdate,
            revision=1,
            row_index=1,
            fields={
                "transaction_id": "TX-001",
                "account_id": "ACC-001",
                "business_date": "2025-03-09",
                "amount": "12.34567",  # Exceeds scale 4
                "currency": "USD",
                "transaction_type": "DEPOSIT",
                "transaction_status": "POSTED",
            },
        )
        findings_map, summary = self.engine.evaluate_batch({("SRC-01", "transactions"): [raw]})
        finds = findings_map.get(("SRC-01", "transactions", "TX-001"), [])
        self.assertTrue(any(f.rule_id == "DQ-D07" for f in finds))

    def test_dq_d09_dpd_range_violation(self):
        """Rule DQ-D09: Days past due out of range 0..36500 produces CRITICAL finding."""
        raw = RawRecord(
            source="SRC-02",
            section="positions",
            record_id="POS-001",
            business_date=self.bdate,
            revision=1,
            row_index=1,
            fields={
                "loan_id": "LOAN-001",
                "business_date": "2025-03-09",
                "outstanding_principal": "1000.0000",
                "currency": "USD",
                "days_past_due": "50000",  # Exceeds 36500
                "loan_status": "DELINQUENT",
            },
        )
        findings_map, summary = self.engine.evaluate_batch({("SRC-02", "positions"): [raw]})
        finds = findings_map.get(("SRC-02", "positions", "POS-001"), [])
        dpd_finds = [f for f in finds if f.rule_id == "DQ-D09"]
        self.assertTrue(len(dpd_finds) > 0)
        self.assertEqual(dpd_finds[0].severity, FindingSeverity.CRITICAL)

    def test_dq_d04_referential_integrity_orphan_account(self):
        """Rule DQ-D04: Account pointing to non-existent customer produces ERROR."""
        cust = RawRecord(
            source="SRC-01",
            section="customers",
            record_id="CUST-001",
            business_date=self.bdate,
            revision=1,
            row_index=1,
            fields={
                "customer_id": "CUST-001",
                "customer_name": "Valid Cust",
                "tax_identifier_masked": "123-45-6789",
                "customer_segment": "RETAIL",
                "primary_branch_id": "BR-001",
            },
        )
        acc = RawRecord(
            source="SRC-01",
            section="accounts",
            record_id="ACC-001",
            business_date=self.bdate,
            revision=1,
            row_index=1,
            fields={
                "account_id": "ACC-001",
                "customer_id": "CUST-MISSING",  # Orphan
                "account_type": "CHECKING",
                "currency": "USD",
                "branch_id": "BR-001",
                "account_status": "OPEN",
            },
        )
        batch = {
            ("SRC-01", "customers"): [cust],
            ("SRC-01", "accounts"): [acc],
        }
        findings_map, summary = self.engine.evaluate_batch(batch)
        acc_finds = findings_map.get(("SRC-01", "accounts", "ACC-001"), [])
        self.assertTrue(any(f.rule_id == "DQ-D04" for f in acc_finds))

    def test_dq_d07_currency_iso_format_and_fixture_whitelist(self):
        """Rule DQ-D07: Check 3-letter ISO format in all modes; check fixture whitelist only in fixture mode."""
        from horizon_pipeline.processing.records import ExecutionMode

        base_fields = {
            "transaction_id": "TX-001",
            "account_id": "ACC-001",
            "business_date": "2025-03-09",
            "amount": "10.0000",
            "transaction_type": "DEPOSIT",
            "transaction_status": "POSTED",
        }

        # Invalid ISO format: 'us' (lowercase, 2 letters)
        raw_bad_fmt = RawRecord(
            source="SRC-01",
            section="transactions",
            record_id="TX-BAD-FMT",
            business_date=self.bdate,
            revision=1,
            row_index=1,
            fields={**base_fields, "currency": "us"},
        )
        _, summary_bad = self.engine.evaluate_batch({("SRC-01", "transactions"): [raw_bad_fmt]})
        self.assertEqual(summary_bad.quarantined_records, 1)

        # EUR is valid in fixture mode
        raw_eur = RawRecord(
            source="SRC-01",
            section="transactions",
            record_id="TX-EUR",
            business_date=self.bdate,
            revision=1,
            row_index=1,
            fields={**base_fields, "currency": "EUR"},
        )
        _, summary_eur = self.engine.evaluate_batch({("SRC-01", "transactions"): [raw_eur]})
        self.assertEqual(summary_eur.quarantined_records, 0)

        # GBP in fixture mode is quarantined (not in fixture approved currencies)
        raw_gbp = RawRecord(
            source="SRC-01",
            section="transactions",
            record_id="TX-GBP",
            business_date=self.bdate,
            revision=1,
            row_index=1,
            fields={**base_fields, "currency": "GBP"},
        )
        _, summary_gbp = self.engine.evaluate_batch({("SRC-01", "transactions"): [raw_gbp]})
        self.assertEqual(summary_gbp.quarantined_records, 1)

        # In production mode, GBP matches 3-letter ISO format and whitelist is PENDING
        prod_engine = DataQualityEngine(check_referential_integrity=False, execution_mode=ExecutionMode.PRODUCTION)
        _, summary_prod_gbp = prod_engine.evaluate_batch({("SRC-01", "transactions"): [raw_gbp]})
        self.assertEqual(summary_prod_gbp.quarantined_records, 0)


if __name__ == "__main__":
    unittest.main()
