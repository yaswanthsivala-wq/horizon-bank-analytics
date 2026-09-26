"""Production Mode Isolation and Fail-Closed Enforcement Tests.

CRITICAL NOTICE: Verifies strict fail-closed safety boundaries:
1. ConsolidatedPipelineRunner in PRODUCTION mode fails closed immediately.
2. Zero output artifacts created under output_dir in PRODUCTION mode.
3. Zero downstream execution (risk assessments and marts remain unexecuted).
4. Direct invocation of CustomerRiskOrchestrator in PRODUCTION mode strictly raises PendingContractError.
5. Non-ExecutionMode enum arguments raise TypeError.
"""

from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path

from horizon_pipeline.analytics.risk_orchestrator import CustomerRiskOrchestrator
from horizon_pipeline.contracts.states import PendingContractError
from horizon_pipeline.orchestration.runner import ConsolidatedPipelineRunner
from horizon_pipeline.processing.records import ExecutionMode, RecordDisposition
from horizon_pipeline.synthetic import (
    SyntheticBankingDataGenerator,
    build_serialized_fixture_package,
)


class OrchestrationModeIsolationTests(unittest.TestCase):
    def setUp(self):
        self.bdate = date(2025, 3, 9)
        self.gen = SyntheticBankingDataGenerator(seed=777, business_date=self.bdate)
        self.dataset = self.gen.generate(num_customers=3, num_transactions=5, num_loans=2)
        self.pkg = build_serialized_fixture_package(self.dataset, revision=1)

    def test_runner_production_mode_fails_closed_zero_artifacts(self):
        """Runner in PRODUCTION mode returns QUARANTINED, zero artifacts, no downstream execution."""
        runner = ConsolidatedPipelineRunner()

        with tempfile.TemporaryDirectory() as tmp_dir:
            out_path = Path(tmp_dir)

            res = runner.run_package(
                manifest_json=self.pkg.manifest_json,
                payloads=self.pkg.payloads,
                execution_mode=ExecutionMode.PRODUCTION,
                output_dir=out_path,
            )

            # 1. Quarantined Disposition and Failed Status
            self.assertFalse(res.passed)
            self.assertEqual(res.disposition, RecordDisposition.QUARANTINED)
            self.assertEqual(res.execution_mode, ExecutionMode.PRODUCTION)

            # 2. No Downstream Execution
            self.assertIsNone(res.marts_result)
            self.assertEqual(len(res.risk_assessments), 0)
            self.assertEqual(len(res.artifact_checksums), 0)
            self.assertIsNone(res.manifest_checksum)
            self.assertIsNone(res.manifest_path)

            # 3. Findings Contain Pending Physical Contract Indicators
            finding_strs = [str(f) for f in res.findings]
            self.assertTrue(any("HDR" in s or "SCH" in s or "PENDING" in s for s in finding_strs))

            # 4. Zero Output Artifacts Written (output_dir remains completely empty)
            files_in_dir = list(out_path.iterdir())
            self.assertEqual(len(files_in_dir), 0, f"Expected 0 artifacts, found: {files_in_dir}")

    def test_risk_orchestrator_production_mode_raises_pending_contract_error(self):
        """Direct CustomerRiskOrchestrator invocation in PRODUCTION mode raises PendingContractError."""
        orch = CustomerRiskOrchestrator()
        with self.assertRaises(PendingContractError) as ctx:
            orch.assess_customers(
                customers=(),
                business_date=self.bdate,
                execution_mode=ExecutionMode.PRODUCTION,
            )
        self.assertIn("fail-closed", str(ctx.exception).lower())

    def test_risk_orchestrator_invalid_mode_type(self):
        """Passing non-ExecutionMode type to CustomerRiskOrchestrator raises TypeError."""
        orch = CustomerRiskOrchestrator()
        with self.assertRaises(TypeError):
            orch.assess_customers(
                customers=(),
                business_date=self.bdate,
                execution_mode="FIXTURE",  # type: ignore
            )


if __name__ == "__main__":
    unittest.main()
