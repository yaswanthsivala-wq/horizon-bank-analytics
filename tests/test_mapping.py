"""Unit tests for PD-06 Status and Domain Reference Mapping Engine."""

import unittest

from horizon_pipeline.contracts.mapping import MappingEntry, StatusMappingRegistry
from horizon_pipeline.contracts.states import ContractState


class StatusMappingTests(unittest.TestCase):
    def setUp(self):
        self.registry = StatusMappingRegistry()

        # Register active fixture mapping version
        self.registry.register_version("SRC-01", "transaction_status", "TEST_V1", ContractState.ACTIVE)
        self.registry.register_entry(
            MappingEntry(
                source_system="SRC-01",
                domain_code="transaction_status",
                mapping_version="TEST_V1",
                raw_value="SUCCESSFUL",
                canonical_value="POSTED",
                kpi_eligible=True,
                risk_eligible=True,
                state=ContractState.ACTIVE,
                is_fixture=True,
            )
        )
        self.registry.register_entry(
            MappingEntry(
                source_system="SRC-01",
                domain_code="transaction_status",
                mapping_version="TEST_V1",
                raw_value="FAILED",
                canonical_value="FAILED",
                kpi_eligible=False,
                risk_eligible=True,
                state=ContractState.ACTIVE,
                is_fixture=True,
            )
        )

        # Register pending mapping version
        self.registry.register_version("SRC-02", "loan_status", "PENDING_V1", ContractState.PENDING)

        # Register unsupported/retired mapping version
        self.registry.register_version("SRC-01", "transaction_status", "RETIRED_V0", ContractState.UNSUPPORTED)

    def test_active_mapping_lookup_preserves_raw_value(self):
        res, findings = self.registry.resolve("SRC-01", "transaction_status", "TEST_V1", "SUCCESSFUL")
        self.assertTrue(res.is_resolved)
        self.assertEqual(res.raw_value, "SUCCESSFUL")
        self.assertEqual(res.canonical_value, "POSTED")
        self.assertEqual(res.applied_version, "TEST_V1")
        self.assertTrue(res.kpi_eligible)
        self.assertEqual(findings, [])

    def test_unknown_raw_code_fails_closed_no_default(self):
        # Invariant: Unknown mapping must NOT silently become OTHER, UNKNOWN, or null
        res, findings = self.registry.resolve("SRC-01", "transaction_status", "TEST_V1", "UNKNOWN_STATUS")
        self.assertFalse(res.is_resolved)
        self.assertEqual(res.raw_value, "UNKNOWN_STATUS")
        self.assertIsNone(res.canonical_value)
        self.assertTrue(any(f.code == "MAP-UNKNOWN-RAW-CODE" for f in findings))

    def test_unknown_mapping_version_fails_closed(self):
        res, findings = self.registry.resolve("SRC-01", "transaction_status", "NONEXISTENT_VER", "SUCCESSFUL")
        self.assertFalse(res.is_resolved)
        self.assertTrue(any(f.code == "MAP-UNKNOWN-VERSION" for f in findings))

    def test_pending_mapping_version_fails_closed(self):
        res, findings = self.registry.resolve("SRC-02", "loan_status", "PENDING_V1", "ACTIVE")
        self.assertFalse(res.is_resolved)
        self.assertTrue(any(f.code == "MAP-PENDING-VERSION" for f in findings))

    def test_retired_mapping_version_fails_closed(self):
        res, findings = self.registry.resolve("SRC-01", "transaction_status", "RETIRED_V0", "SUCCESSFUL")
        self.assertFalse(res.is_resolved)
        self.assertTrue(any(f.code == "MAP-UNSUPPORTED-VERSION" for f in findings))


if __name__ == "__main__":
    unittest.main()
