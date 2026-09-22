"""End-to-End Offline Contract Engine Integration Tests.

CRITICAL NOTICE: TEST FIXTURE ONLY.
All contracts and packages evaluated in this test are explicitly isolated
test fixtures with is_fixture=True. They are NOT approved Horizon Community Bank
production contracts and must never enter production registries.
"""

import hashlib
import json
import unittest
from datetime import date
from decimal import Decimal

from horizon_pipeline.contracts.findings import Disposition, FindingSeverity
from horizon_pipeline.contracts.registry import MasterProductionRegistry
from horizon_pipeline.pipeline import OfflinePipelineEngine
from horizon_pipeline.synthetic import (
    SyntheticBankingDataGenerator,
    build_serialized_fixture_package,
    build_test_fixture_registries,
)


class EndToEndOfflineFixtureTests(unittest.TestCase):
    def setUp(self):
        self.bdate = date(2025, 3, 9)
        # Build isolated test fixture registries
        headers, schemas, applicability, mappings, financial = build_test_fixture_registries()
        self.engine = OfflinePipelineEngine(
            headers=headers,
            schemas=schemas,
            applicability=applicability,
            mappings=mappings,
            financial=financial,
        )

        # Generate deterministic synthetic data
        gen = SyntheticBankingDataGenerator(seed=777, business_date=self.bdate)
        self.dataset = gen.generate(num_customers=5, num_transactions=10, num_loans=3)
        self.pkg = build_serialized_fixture_package(self.dataset, revision=1)

    def test_e2e_passing_flow_accepted(self):
        """Passing Flow: All 27 sections pass manifest, header, schema, applicability, mapping, temporal, and financial controls."""
        result = self.engine.execute_package(
            manifest_json=self.pkg.manifest_json,
            payloads=self.pkg.payloads,
            expected_business_date=self.bdate,
            require_all_27_sections=True,
        )

        self.assertEqual(result.disposition, Disposition.ACCEPTED)
        self.assertTrue(result.passed)
        self.assertEqual(len(result.processed_sections), 27)

        # Verify no fatal or error findings
        fatal_or_error = [f for f in result.findings if f.severity in (FindingSeverity.FATAL, FindingSeverity.ERROR)]
        self.assertEqual(fatal_or_error, [])

    def test_e2e_failing_flow_corrupted_payload_checksum(self):
        """Failing Flow: Tampered payload bytes cause checksum mismatch and package REJECTION."""
        corrupted_payloads = dict(self.pkg.payloads)
        # Corrupt one section
        target_path = "sections/SRC-01/transactions.csv"
        corrupted_payloads[target_path] = corrupted_payloads[target_path] + b"tampered,data,row\n"

        result = self.engine.execute_package(
            manifest_json=self.pkg.manifest_json,
            payloads=corrupted_payloads,
            expected_business_date=self.bdate,
            require_all_27_sections=True,
        )

        self.assertEqual(result.disposition, Disposition.REJECTED)
        self.assertFalse(result.passed)
        self.assertTrue(any(f.code == "PAY-CHECKSUM-MISMATCH" for f in result.findings))

    def test_e2e_failing_flow_missing_mandatory_section(self):
        """Failing Flow: Package omitting a mandatory section is REJECTED."""
        missing_payloads = dict(self.pkg.payloads)
        del missing_payloads["sections/SRC-03/alerts.csv"]

        result = self.engine.execute_package(
            manifest_json=self.pkg.manifest_json,
            payloads=missing_payloads,
            expected_business_date=self.bdate,
            require_all_27_sections=True,
        )

        self.assertEqual(result.disposition, Disposition.REJECTED)
        self.assertFalse(result.passed)
        self.assertTrue(any(f.code == "PAY-MISSING-PAYLOAD" for f in result.findings))

    def test_e2e_failing_flow_path_traversal(self):
        """Failing Flow: manifest.json with path traversal attempt is REJECTED."""
        manifest_data = json.loads(self.pkg.manifest_json)
        manifest_data["sections"][0]["payload_path"] = "../sections/SRC-01/customers.csv"
        traversal_manifest = json.dumps(manifest_data)

        result = self.engine.execute_package(
            manifest_json=traversal_manifest,
            payloads=self.pkg.payloads,
            expected_business_date=self.bdate,
            require_all_27_sections=True,
        )

        self.assertEqual(result.disposition, Disposition.REJECTED)
        self.assertFalse(result.passed)
        self.assertTrue(any(f.code == "MAN-UNSAFE-PATH" for f in result.findings))

    def test_e2e_failing_flow_production_contracts_fail_closed(self):
        """Failing Flow: Running a delivery through the MasterProductionRegistry fails closed."""
        # Using MasterProductionRegistry where all 27 sections are PENDING
        prod_master = MasterProductionRegistry()
        prod_engine = OfflinePipelineEngine(
            headers=prod_master.headers,
            schemas=prod_master.schemas,
            applicability=prod_master.applicability,
            mappings=prod_master.mappings,
            financial=prod_master.financial,
        )

        result = prod_engine.execute_package(
            manifest_json=self.pkg.manifest_json,
            payloads=self.pkg.payloads,
            expected_business_date=self.bdate,
            require_all_27_sections=True,
        )

        # Fails closed because production contracts are pending/unsupported
        self.assertEqual(result.disposition, Disposition.REJECTED)
        self.assertFalse(result.passed)
        self.assertTrue(any("HDR" in f.code or "SCH" in f.code for f in result.findings))


if __name__ == "__main__":
    unittest.main()
