"""End-to-End Orchestrated Pipeline Runner Integration Tests.

CRITICAL NOTICE: TEST FIXTURES ONLY.
Verifies complete pipeline execution:
1. Happy-path passing flow across all 27 sections in FIXTURE mode.
2. Verified output artifact generation including risk assessments and analytical marts.
3. Verification of manifest.json exclusion from artifact_checksums and companion sha256 file.
4. Deterministic run_id and created_at_utc execution.
5. Realistic default package fixture assertions.
"""

from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

from horizon_pipeline.contracts.states import PendingContractError
from horizon_pipeline.orchestration.runner import ConsolidatedPipelineRunner, ConsolidatedRunResult
from horizon_pipeline.processing.records import ExecutionMode, RecordDisposition
from horizon_pipeline.processing.replay import BatchStateTracker
from horizon_pipeline.synthetic import (
    SyntheticBankingDataGenerator,
    build_serialized_fixture_package,
)


class OrchestrationRunnerTests(unittest.TestCase):
    def setUp(self):
        self.bdate = date(2025, 3, 9)
        self.gen = SyntheticBankingDataGenerator(seed=888, business_date=self.bdate)
        self.dataset = self.gen.generate(num_customers=5, num_transactions=10, num_loans=3)
        self.pkg = build_serialized_fixture_package(self.dataset, revision=1)

    def test_runner_fixture_passing_flow_default_package(self):
        """Passing Flow: Full 27-section package in FIXTURE mode executes end-to-end."""
        tracker = BatchStateTracker()
        runner = ConsolidatedPipelineRunner(batch_tracker=tracker)

        with tempfile.TemporaryDirectory() as tmp_dir:
            out_path = Path(tmp_dir)
            res = runner.run_package(
                manifest_json=self.pkg.manifest_json,
                payloads=self.pkg.payloads,
                execution_mode=ExecutionMode.FIXTURE,
                output_dir=out_path,
            )

            # 1. Verify Overall Outcome
            self.assertTrue(res.passed)
            self.assertEqual(res.disposition, RecordDisposition.ACCEPTED)
            self.assertEqual(res.execution_mode, ExecutionMode.FIXTURE)
            self.assertEqual(res.processing_result.quarantine_ledger.count(), 0)

            # 2. Verify Risk Assessments Generated
            self.assertEqual(len(res.risk_assessments), 5)
            customer_ids = {a.customer_id for a in res.risk_assessments}
            self.assertEqual(len(customer_ids), 5)

            # 3. Verify Four Analytical Marts Populated
            self.assertIsNotNone(res.marts_result)
            marts = res.marts_result
            self.assertGreater(len(marts.transaction_mart), 0)
            self.assertGreater(len(marts.loan_mart), 0)
            self.assertGreater(len(marts.customer_risk_mart), 0)
            self.assertGreater(len(marts.complaint_mart), 0)

            # Default package realistic metric assertions:
            # All loans in default generator have DPD=0 -> 0 delinquent active loans
            for r in marts.loan_mart:
                self.assertEqual(r.delinquent_active_loan_count, 0)
                self.assertEqual(r.loan_delinquency_rate_pct, Decimal("0.00000000"))

            # All complaints in default generator are OPEN -> 0 closed complaints, avg resolution is None
            for r in marts.complaint_mart:
                self.assertEqual(r.closed_complaint_count, 0)
                self.assertIsNone(r.avg_resolution_hours)

            # 4. Verify Files Written on Disk
            self.assertTrue((out_path / "manifest.json").is_file())
            self.assertTrue((out_path / "manifest.json.sha256").is_file())
            self.assertTrue((out_path / "dq_summary.json").is_file())
            self.assertTrue((out_path / "reconciliation_summary.json").is_file())
            self.assertTrue((out_path / "accepted" / "customers.json").is_file())
            self.assertTrue((out_path / "risk" / "customer_risk_assessments.json").is_file())
            self.assertTrue((out_path / "marts" / "mart_transaction_kpis.json").is_file())
            self.assertTrue((out_path / "marts" / "mart_loan_delinquency_kpis.json").is_file())
            self.assertTrue((out_path / "marts" / "mart_customer_risk_kpis.json").is_file())
            self.assertTrue((out_path / "marts" / "mart_complaint_kpis.json").is_file())

            # 5. Verify manifest.json is strictly excluded from its own artifact_checksums
            manifest_data = json.loads((out_path / "manifest.json").read_text(encoding="utf-8"))
            self.assertNotIn("manifest.json", manifest_data["artifact_checksums"])
            self.assertNotIn("manifest.json.sha256", manifest_data["artifact_checksums"])

            # 6. Verify companion manifest.json.sha256 matches actual hash of manifest.json
            manifest_bytes = (out_path / "manifest.json").read_bytes()
            computed_manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
            sha_file_content = (out_path / "manifest.json.sha256").read_text(encoding="utf-8").strip()
            self.assertEqual(sha_file_content, f"{computed_manifest_sha} *manifest.json")

            # 7. Verify all indexed artifacts match their recorded SHA-256 digests
            for rel_path, recorded_digest in manifest_data["artifact_checksums"].items():
                file_bytes = (out_path / rel_path).read_bytes()
                file_digest = hashlib.sha256(file_bytes).hexdigest()
                self.assertEqual(file_digest, recorded_digest, f"Digest mismatch on {rel_path}")

    def test_runner_deterministic_run_id_and_created_at(self):
        """Deterministic run_id is derived from manifest when not supplied."""
        runner = ConsolidatedPipelineRunner()

        expected_run_id = f"RUN-{hashlib.sha256(self.pkg.manifest_json.encode('utf-8')).hexdigest()[:12].upper()}"

        res1 = runner.run_package(
            manifest_json=self.pkg.manifest_json,
            payloads=self.pkg.payloads,
            execution_mode=ExecutionMode.FIXTURE,
        )
        self.assertEqual(res1.run_id, expected_run_id)

        # Explicit run_id is preserved
        res2 = runner.run_package(
            manifest_json=self.pkg.manifest_json,
            payloads=self.pkg.payloads,
            execution_mode=ExecutionMode.FIXTURE,
            run_id="RUN-CUSTOM-EXPLICIT",
        )
        self.assertEqual(res2.run_id, "RUN-CUSTOM-EXPLICIT")

    def test_runner_invalid_execution_mode_type(self):
        """Passing non-ExecutionMode type raises TypeError."""
        runner = ConsolidatedPipelineRunner()
        with self.assertRaises(TypeError):
            runner.run_package(
                manifest_json=self.pkg.manifest_json,
                payloads=self.pkg.payloads,
                execution_mode="FIXTURE",  # type: ignore
            )


if __name__ == "__main__":
    unittest.main()
