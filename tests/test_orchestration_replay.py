"""Orchestration Batch Replay and Conflict Protection Tests.

CRITICAL NOTICE: TEST FIXTURES ONLY.
Verifies BatchStateTracker integration in ConsolidatedPipelineRunner (AC-ORCH-08):
1. Identical retry is permitted and idempotent.
2. Conflicting same-revision payload is blocked and quarantined.
3. Stale lower revision is blocked and quarantined.
"""

from __future__ import annotations

import copy
import unittest
from datetime import date

from horizon_pipeline.orchestration.runner import ConsolidatedPipelineRunner
from horizon_pipeline.processing.records import ExecutionMode, RecordDisposition
from horizon_pipeline.processing.replay import BatchStateTracker
from horizon_pipeline.synthetic import (
    SyntheticBankingDataGenerator,
    build_serialized_fixture_package,
)


class OrchestrationReplayTests(unittest.TestCase):
    def setUp(self):
        self.bdate = date(2025, 3, 9)
        self.gen = SyntheticBankingDataGenerator(seed=555, business_date=self.bdate)
        self.dataset = self.gen.generate(num_customers=3, num_transactions=5, num_loans=2)
        self.pkg_rev1 = build_serialized_fixture_package(self.dataset, revision=1)
        self.pkg_rev2 = build_serialized_fixture_package(self.dataset, revision=2)

    def test_replay_identical_retry_permitted_idempotent(self):
        """Identical retry with matching checksum succeeds idempotently."""
        tracker = BatchStateTracker()
        runner = ConsolidatedPipelineRunner(batch_tracker=tracker)

        # Run 1: Initial delivery
        res1 = runner.run_package(
            manifest_json=self.pkg_rev1.manifest_json,
            payloads=self.pkg_rev1.payloads,
            execution_mode=ExecutionMode.FIXTURE,
        )
        self.assertTrue(res1.passed)
        self.assertEqual(res1.disposition, RecordDisposition.ACCEPTED)

        # Run 2: Exact identical retry
        res2 = runner.run_package(
            manifest_json=self.pkg_rev1.manifest_json,
            payloads=self.pkg_rev1.payloads,
            execution_mode=ExecutionMode.FIXTURE,
        )
        self.assertTrue(res2.passed)
        self.assertEqual(res2.disposition, RecordDisposition.ACCEPTED)
        self.assertEqual(len(res1.risk_assessments), len(res2.risk_assessments))

    def test_replay_payload_conflict_quarantines_batch(self):
        """Conflicting payload with same revision is blocked and quarantined."""
        tracker = BatchStateTracker()
        runner = ConsolidatedPipelineRunner(batch_tracker=tracker)

        # Run 1: Initial delivery
        res1 = runner.run_package(
            manifest_json=self.pkg_rev1.manifest_json,
            payloads=self.pkg_rev1.payloads,
            execution_mode=ExecutionMode.FIXTURE,
        )
        self.assertTrue(res1.passed)

        # Mutate dataset payload with same revision 1
        mutated_dataset = copy.deepcopy(self.dataset)
        mutated_dataset.sections[("SRC-01", "transactions")][0]["amount"] = "999.0000"
        conflicting_pkg = build_serialized_fixture_package(mutated_dataset, revision=1)

        # Run 2: Conflicting payload bytes
        res2 = runner.run_package(
            manifest_json=conflicting_pkg.manifest_json,
            payloads=conflicting_pkg.payloads,
            execution_mode=ExecutionMode.FIXTURE,
        )
        self.assertFalse(res2.passed)
        self.assertEqual(res2.disposition, RecordDisposition.QUARANTINED)
        self.assertIsNone(res2.marts_result)

        finding_rules = [getattr(f, "rule_id", None) or getattr(f, "code", "") for f in res2.findings]
        self.assertTrue(any("DQ-D02" in str(r) for r in finding_rules))

    def test_replay_stale_revision_blocked(self):
        """Delivering a stale lower revision is blocked and quarantined."""
        tracker = BatchStateTracker()
        runner = ConsolidatedPipelineRunner(batch_tracker=tracker)

        # Run 1: Delivery with revision 2
        res_rev2 = runner.run_package(
            manifest_json=self.pkg_rev2.manifest_json,
            payloads=self.pkg_rev2.payloads,
            execution_mode=ExecutionMode.FIXTURE,
        )
        self.assertTrue(res_rev2.passed)

        # Run 2: Attempting stale revision 1 for same business date
        res_rev1 = runner.run_package(
            manifest_json=self.pkg_rev1.manifest_json,
            payloads=self.pkg_rev1.payloads,
            execution_mode=ExecutionMode.FIXTURE,
        )
        self.assertFalse(res_rev1.passed)
        self.assertEqual(res_rev1.disposition, RecordDisposition.QUARANTINED)
        self.assertIsNone(res_rev1.marts_result)


if __name__ == "__main__":
    unittest.main()
