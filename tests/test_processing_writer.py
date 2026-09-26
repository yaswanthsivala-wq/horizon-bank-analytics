"""Unit Tests for Output Artifact Writer.

Verifies deterministic file structure generation, JSON formatting,
and SHA-256 checksum tracking across all output artifacts.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

from horizon_pipeline.processing.lineage import LineageLedger
from horizon_pipeline.processing.quality import DQSummary
from horizon_pipeline.processing.quarantine import QuarantineLedger
from horizon_pipeline.processing.reconciliation import ReconciliationSummary
from horizon_pipeline.processing.records import CuratedCustomer, ExecutionMode, RetentionCategory
from horizon_pipeline.processing.writer import OutputArtifactWriter


class ProcessingWriterTests(unittest.TestCase):
    def test_write_run_artifacts_structure_and_checksums(self):
        """Writer creates complete artifact tree and records verified SHA-256 digests."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_path = Path(tmp_dir)
            writer = OutputArtifactWriter(out_path)

            bdate = date(2025, 3, 9)
            cust = CuratedCustomer(
                customer_id="CUST-1",
                customer_name_masked="***oe",
                tax_identifier_masked="***-**-1234",
                customer_segment="RETAIL",
                primary_branch_id="BR-1",
                business_date=bdate,
            )
            q_ledger = QuarantineLedger()
            l_ledger = LineageLedger()
            dq_summary = DQSummary(
                received_records=1,
                accepted_records=1,
                quarantined_records=0,
                excluded_records=0,
                critical_findings_count=0,
                error_findings_count=0,
                warning_findings_count=0,
                info_findings_count=0,
                received_completeness_pct=Decimal("100.00"),
                curated_completeness_pct=Decimal("100.00"),
                completeness_passed=True,
                findings=(),
            )
            rec_summary = ReconciliationSummary(
                row_results=(),
                financial_results=(),
                all_balanced=True,
                findings=(),
            )

            checksums = writer.write_run_artifacts(
                run_id="RUN-TEST-01",
                package_id="PKG-TEST-01",
                business_date=bdate,
                execution_mode=ExecutionMode.FIXTURE,
                curated_entities={"customers": [cust]},
                quarantine_ledger=q_ledger,
                lineage_ledger=l_ledger,
                dq_summary=dq_summary,
                reconciliation_summary=rec_summary,
            )

            # Verify files exist on disk
            for rel_file, expected_digest in checksums.items():
                target_file = out_path / rel_file
                self.assertTrue(target_file.is_file(), f"Missing output file: {rel_file}")
                actual_bytes = target_file.read_bytes()
                actual_digest = hashlib.sha256(actual_bytes).hexdigest()
                self.assertEqual(actual_digest, expected_digest)

            # Verify manifest.json contains valid JSON
            man_content = json.loads((out_path / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(man_content["run_id"], "RUN-TEST-01")
            self.assertEqual(man_content["execution_mode"], "FIXTURE")
            self.assertEqual(man_content["statistics"]["accepted_records"], 1)


if __name__ == "__main__":
    unittest.main()
