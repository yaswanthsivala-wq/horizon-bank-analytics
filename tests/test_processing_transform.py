"""Unit Tests for Transformation, Parsing, and DD-08 Masking.

Verifies deterministic masking, scale-4 Decimal parsing, UTC temporal parsing,
and domain entity transformations.
"""

from __future__ import annotations

import unittest
from datetime import date, datetime, timezone
from decimal import Decimal

from horizon_pipeline.contracts.mapping import MappingEntry, StatusMappingRegistry
from horizon_pipeline.contracts.states import ContractState
from horizon_pipeline.processing.records import (
    CuratedAccount,
    CuratedCustomer,
    CuratedTransaction,
    RawRecord,
    RetentionCategory,
)
from horizon_pipeline.processing.transform import (
    mask_account_id,
    mask_customer_name,
    mask_tax_identifier,
    parse_instant_utc,
    parse_iso_date,
    parse_scale4_decimal,
    transform_account,
    transform_customer,
    transform_record,
    transform_transaction,
)


class ProcessingTransformTests(unittest.TestCase):
    def test_mask_tax_identifier(self):
        """Tax identifier masking must preserve last four digits (DD-08)."""
        self.assertEqual(mask_tax_identifier("123456789"), "***-**-6789")
        self.assertEqual(mask_tax_identifier("123-45-6789"), "***-**-6789")
        self.assertEqual(mask_tax_identifier("9999"), "***-**-9999")
        self.assertEqual(mask_tax_identifier("123"), "[UNAVAILABLE]")
        self.assertEqual(mask_tax_identifier(""), "[UNAVAILABLE]")
        self.assertEqual(mask_tax_identifier(None), "[UNAVAILABLE]")

    def test_mask_account_id(self):
        """Account masking uses fixed prefix plus final four digits (DD-08)."""
        self.assertEqual(mask_account_id("1000001234"), "******1234")
        self.assertEqual(mask_account_id("0042"), "******0042")
        self.assertEqual(mask_account_id("123"), "[UNAVAILABLE]")
        self.assertEqual(mask_account_id(""), "[UNAVAILABLE]")
        self.assertEqual(mask_account_id(None), "[UNAVAILABLE]")

    def test_mask_customer_name(self):
        """Customer name masking suppresses sensitive personal detail."""
        self.assertEqual(mask_customer_name("John Doe"), "***oe")
        self.assertEqual(mask_customer_name("Al"), "[REDACTED]")
        self.assertEqual(mask_customer_name(""), "[UNAVAILABLE]")
        self.assertEqual(mask_customer_name(None), "[UNAVAILABLE]")

    def test_parse_scale4_decimal(self):
        """Monetary decimal parsing enforces scale 4."""
        self.assertEqual(parse_scale4_decimal("150.25"), Decimal("150.2500"))
        self.assertEqual(parse_scale4_decimal("0"), Decimal("0.0000"))
        self.assertEqual(parse_scale4_decimal("-42.5000"), Decimal("-42.5000"))
        with self.assertRaises(ValueError):
            parse_scale4_decimal("abc")
        with self.assertRaises(ValueError):
            parse_scale4_decimal("")
        with self.assertRaises(ValueError):
            parse_scale4_decimal(None)

    def test_parse_iso_date(self):
        """ISO date parsing strictly validates YYYY-MM-DD."""
        self.assertEqual(parse_iso_date("2025-03-09"), date(2025, 3, 9))
        with self.assertRaises(ValueError):
            parse_iso_date("03/09/2025")

    def test_parse_instant_utc(self):
        """Instant parsing normalizes America/Chicago offset to UTC."""
        dt = parse_instant_utc("2025-03-09T08:00:00-05:00")
        self.assertIsNotNone(dt)
        self.assertEqual(dt.tzinfo, timezone.utc)
        self.assertEqual(dt.hour, 13)

    def test_transform_customer_entity(self):
        """Transform customer raw record to CuratedCustomer."""
        raw = RawRecord(
            source="SRC-01",
            section="customers",
            record_id="CUST-001",
            business_date=date(2025, 3, 9),
            revision=1,
            row_index=1,
            fields={
                "customer_id": "CUST-001",
                "customer_name": "Alice Smith",
                "tax_identifier_masked": "123-45-6789",
                "customer_segment": "RETAIL",
                "primary_branch_id": "BR-001",
                "business_date": "2025-03-09",
            },
        )
        curated = transform_customer(raw, lineage_id="LIN-001")
        self.assertIsInstance(curated, CuratedCustomer)
        self.assertEqual(curated.customer_id, "CUST-001")
        self.assertEqual(curated.tax_identifier_masked, "***-**-6789")
        self.assertEqual(curated.customer_name_masked, "***th")
        self.assertEqual(curated.retention_category, RetentionCategory.ANALYTICAL_24M)

    def test_transform_transaction_with_status_mapping(self):
        """Transform transaction resolves canonical status from StatusMappingRegistry."""
        mappings = StatusMappingRegistry()
        mappings.register_version("SRC-01", "transaction_status", "MAP_V1", ContractState.ACTIVE)
        mappings.register_entry(
            MappingEntry(
                source_system="SRC-01",
                domain_code="transaction_status",
                mapping_version="MAP_V1",
                raw_value="SUCCESSFUL",
                canonical_value="POSTED",
                kpi_eligible=True,
                risk_eligible=True,
                applicability_eligible=True,
                state=ContractState.ACTIVE,
                is_fixture=True,
            )
        )

        raw = RawRecord(
            source="SRC-01",
            section="transactions",
            record_id="TX-100",
            business_date=date(2025, 3, 9),
            revision=1,
            row_index=1,
            fields={
                "transaction_id": "TX-100",
                "account_id": "ACC-0500",
                "business_date": "2025-03-09",
                "amount": "250.75",
                "currency": "USD",
                "transaction_type": "TRANSFER",
                "transaction_status": "SUCCESSFUL",
                "posted_at": "2025-03-09T10:00:00-05:00",
            },
        )
        curated = transform_transaction(
            raw,
            lineage_id="LIN-TX-100",
            status_registry=mappings,
            mapping_version="MAP_V1",
        )
        self.assertIsInstance(curated, CuratedTransaction)
        self.assertEqual(curated.amount, Decimal("250.7500"))
        self.assertEqual(curated.account_id_masked, "******0500")
        self.assertEqual(curated.transaction_status, "POSTED")
        self.assertEqual(curated.raw_transaction_status, "SUCCESSFUL")

    def test_transform_customer_production_mode_raises_pending_contract(self):
        """In PRODUCTION mode, transform_customer fails closed because masking algorithms are PENDING."""
        from horizon_pipeline.contracts.states import PendingContractError
        from horizon_pipeline.processing.records import ExecutionMode

        raw = RawRecord(
            source="SRC-01",
            section="customers",
            record_id="CUST-001",
            business_date=date(2025, 3, 9),
            revision=1,
            row_index=1,
            fields={
                "customer_id": "CUST-001",
                "customer_name": "Alice Smith",
                "tax_identifier_masked": "123-45-6789",
                "customer_segment": "RETAIL",
                "primary_branch_id": "BR-001",
                "business_date": "2025-03-09",
            },
        )
        with self.assertRaises(PendingContractError):
            transform_customer(raw, lineage_id="LIN-001", execution_mode=ExecutionMode.PRODUCTION)


if __name__ == "__main__":
    unittest.main()
