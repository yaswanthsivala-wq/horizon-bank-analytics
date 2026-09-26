"""Unit tests for PD-01 Physical Header and PD-02 Schema Registries."""

import unittest

from horizon_pipeline.contracts.findings import FindingSeverity
from horizon_pipeline.contracts.headers import HeaderRegistry, PhysicalHeaderContract
from horizon_pipeline.contracts.schemas import FieldContract, SchemaContract, SchemaRegistry
from horizon_pipeline.contracts.states import ContractState, PendingContractError, UnsupportedContractError


class HeadersAndSchemasTests(unittest.TestCase):
    def setUp(self):
        self.headers = HeaderRegistry()
        self.schemas = SchemaRegistry()

        # Register an active test-fixture header
        self.headers.register(
            PhysicalHeaderContract(
                source="SRC-01",
                section="accounts",
                schema_version="TEST.SRC-01.accounts.v1",
                columns=("account_id", "customer_id", "account_type", "currency"),
                state=ContractState.ACTIVE,
                is_fixture=True,
            )
        )

        # Register a pending test header
        self.headers.register(
            PhysicalHeaderContract(
                source="SRC-01",
                section="customers",
                schema_version="TEST.SRC-01.customers.v1",
                columns=(),
                state=ContractState.PENDING,
                is_fixture=True,
            )
        )

        # Register an active test schema
        self.schemas.register(
            SchemaContract(
                source="SRC-01",
                section="accounts",
                schema_version="TEST.SRC-01.accounts.v1",
                fields=(
                    FieldContract("account_id", "text", required=True),
                    FieldContract("customer_id", "text", required=True),
                    FieldContract("account_type", "text", required=True),
                    FieldContract("currency", "currency", required=True),
                ),
                state=ContractState.ACTIVE,
                is_fixture=True,
            )
        )

        # Register a pending test schema
        self.schemas.register(
            SchemaContract(
                source="SRC-01",
                section="customers",
                schema_version="TEST.SRC-01.customers.v1",
                fields=(),
                state=ContractState.PENDING,
                is_fixture=True,
            )
        )

    def test_valid_exact_header(self):
        findings = self.headers.validate_header(
            "SRC-01", "accounts", "TEST.SRC-01.accounts.v1",
            ["account_id", "customer_id", "account_type", "currency"],
        )
        self.assertEqual(findings, [])

    def test_duplicate_header_column_rejected(self):
        findings = self.headers.validate_header(
            "SRC-01", "accounts", "TEST.SRC-01.accounts.v1",
            ["account_id", "customer_id", "account_id", "currency"],
        )
        self.assertTrue(any(f.code == "HDR-DUPLICATE" for f in findings))

    def test_missing_header_column_rejected(self):
        findings = self.headers.validate_header(
            "SRC-01", "accounts", "TEST.SRC-01.accounts.v1",
            ["account_id", "customer_id", "account_type"],
        )
        self.assertTrue(any(f.code == "HDR-MISSING-COLUMN" for f in findings))

    def test_unexpected_header_column_rejected(self):
        findings = self.headers.validate_header(
            "SRC-01", "accounts", "TEST.SRC-01.accounts.v1",
            ["account_id", "customer_id", "account_type", "currency", "extra_col"],
        )
        self.assertTrue(any(f.code == "HDR-UNEXPECTED-COLUMN" for f in findings))

    def test_wrong_header_order_rejected(self):
        findings = self.headers.validate_header(
            "SRC-01", "accounts", "TEST.SRC-01.accounts.v1",
            ["customer_id", "account_id", "account_type", "currency"],
        )
        self.assertTrue(any(f.code == "HDR-ORDER-MISMATCH" for f in findings))

    def test_whitespace_column_rejected(self):
        findings = self.headers.validate_header(
            "SRC-01", "accounts", "TEST.SRC-01.accounts.v1",
            ["account_id", "   ", "account_type", "currency"],
        )
        self.assertTrue(any(f.code == "HDR-EMPTY-COLUMN" for f in findings))

    def test_pending_header_fails_closed(self):
        findings = self.headers.validate_header(
            "SRC-01", "customers", "TEST.SRC-01.customers.v1",
            ["customer_id", "customer_name"],
        )
        self.assertTrue(any(f.code == "HDR-PENDING" for f in findings))
        with self.assertRaises(PendingContractError):
            self.headers.require_active("SRC-01", "customers", "TEST.SRC-01.customers.v1")

    def test_unknown_header_fails_closed(self):
        findings = self.headers.validate_header(
            "SRC-01", "unknown", "TEST.unknown.v1",
            ["col1"],
        )
        self.assertTrue(any(f.code == "HDR-UNSUPPORTED" for f in findings))
        with self.assertRaises(UnsupportedContractError):
            self.headers.require_active("SRC-01", "unknown", "TEST.unknown.v1")

    def test_pending_schema_fails_closed(self):
        findings = self.schemas.validate_schema_reference("SRC-01", "customers", "TEST.SRC-01.customers.v1")
        self.assertTrue(any(f.code == "SCH-PENDING" for f in findings))
        with self.assertRaises(PendingContractError):
            self.schemas.require_active("SRC-01", "customers", "TEST.SRC-01.customers.v1")

    def test_unknown_schema_fails_closed(self):
        findings = self.schemas.validate_schema_reference("SRC-01", "unknown", "TEST.unknown.v1")
        self.assertTrue(any(f.code == "SCH-UNKNOWN" for f in findings))
        with self.assertRaises(UnsupportedContractError):
            self.schemas.require_active("SRC-01", "unknown", "TEST.unknown.v1")


if __name__ == "__main__":
    unittest.main()
