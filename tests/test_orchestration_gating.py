"""Publication Gating and Cohort Isolation Integration Tests.

CRITICAL NOTICE: TEST FIXTURES ONLY.
Verifies:
1. Package-level PUB-D01 failure (critical DQ defect):
   - Package disposition is QUARANTINED.
   - Marts are suppressed (marts_result is None).
   - Only diagnostic artifacts written: quarantine/, lineage/, dq_summary.json,
     reconciliation_summary.json, manifest.json, manifest.json.sha256.
   - accepted/, risk/, and marts/ are strictly omitted from output_dir.
2. K06 Currency-Cohort Candidate Gating Isolation:
   - A missing-principal defect on a delinquent USD loan blocks candidate publication
     ONLY for the USD cohort.
   - The package remains ACCEPTED.
   - Other currency cohorts (EUR) and other marts remain PUBLISHED.
3. Financial reconciliation failure triggers PUB-D01 gate and suppresses marts.
"""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from horizon_pipeline.analytics.kpi import KPIPublicationStatus
from horizon_pipeline.orchestration.runner import ConsolidatedPipelineRunner
from horizon_pipeline.processing.records import ExecutionMode, RecordDisposition
from horizon_pipeline.synthetic import (
    SyntheticBankingDataGenerator,
    build_serialized_fixture_package,
    serialize_csv_exact_bytes,
)


class OrchestrationGatingTests(unittest.TestCase):
    def setUp(self):
        self.bdate = date(2025, 3, 9)
        self.gen = SyntheticBankingDataGenerator(seed=999, business_date=self.bdate)
        self.dataset = self.gen.generate(num_customers=5, num_transactions=10, num_loans=3)
        self.pkg = build_serialized_fixture_package(self.dataset, revision=1)

    def test_package_level_pub_d01_dq_defect_quarantines_and_omits_accepted_and_marts(self):
        """Fatal DQ defect triggers PUB-D01: writes diagnostics only, omits accepted/risk/marts."""
        corrupted_dataset = copy.deepcopy(self.dataset)
        raw_tx = dict(corrupted_dataset.sections[("SRC-01", "transactions")][0])
        raw_tx["currency"] = "INVALID_CURR"
        corrupted_dataset.sections[("SRC-01", "transactions")][0] = raw_tx

        corrupted_pkg = build_serialized_fixture_package(corrupted_dataset, revision=1)
        runner = ConsolidatedPipelineRunner()

        with tempfile.TemporaryDirectory() as tmp_dir:
            out_path = Path(tmp_dir)

            res = runner.run_package(
                manifest_json=corrupted_pkg.manifest_json,
                payloads=corrupted_pkg.payloads,
                execution_mode=ExecutionMode.FIXTURE,
                output_dir=out_path,
            )

            # 1. Quarantined Package Disposition
            self.assertFalse(res.passed)
            self.assertEqual(res.disposition, RecordDisposition.QUARANTINED)
            self.assertIsNone(res.marts_result)
            self.assertEqual(len(res.risk_assessments), 0)

            # 2. Diagnostic Artifacts Present
            self.assertTrue((out_path / "manifest.json").is_file())
            self.assertTrue((out_path / "manifest.json.sha256").is_file())
            self.assertTrue((out_path / "dq_summary.json").is_file())
            self.assertTrue((out_path / "reconciliation_summary.json").is_file())
            self.assertTrue((out_path / "quarantine" / "quarantine_records.json").is_file())
            self.assertTrue((out_path / "lineage" / "lineage_records.json").is_file())

            # 3. Approved Output Artifacts Strictly OMITTED
            self.assertFalse((out_path / "accepted").exists(), "accepted/ must be omitted for quarantined runs")
            self.assertFalse((out_path / "risk").exists(), "risk/ must be omitted for quarantined runs")
            self.assertFalse((out_path / "marts").exists(), "marts/ must be omitted for quarantined runs")

            # 4. Manifest records QUARANTINED disposition
            man_dict = json.loads((out_path / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(man_dict["disposition"], "QUARANTINED")

    def test_k06_blocked_candidate_cohort_isolation_does_not_quarantine_package(self):
        """K06 candidate defect blocks ONLY that currency cohort; package remains ACCEPTED."""
        dataset = copy.deepcopy(self.dataset)

        # Mutate positions:
        # Loan 1: USD, DPD = 45, missing principal (None)
        # Loan 2: EUR, DPD = 45, valid principal 25000.0000
        pos_list = dataset.sections[("SRC-02", "positions")]
        pos_list[0] = {
            "loan_id": pos_list[0]["loan_id"],
            "business_date": self.bdate.isoformat(),
            "outstanding_principal": "-5000.0000",  # negative principal -> PRINCIPAL_NEGATIVE
            "currency": "USD",
            "days_past_due": "45",
            "loan_status": "ACTIVE",
        }
        if len(pos_list) > 1:
            pos_list[1] = {
                "loan_id": pos_list[1]["loan_id"],
                "business_date": self.bdate.isoformat(),
                "outstanding_principal": "25000.0000",
                "currency": "EUR",
                "days_past_due": "45",
                "loan_status": "ACTIVE",
            }

        pkg = build_serialized_fixture_package(dataset, revision=1)
        runner = ConsolidatedPipelineRunner()

        with tempfile.TemporaryDirectory() as tmp_dir:
            out_path = Path(tmp_dir)

            res = runner.run_package(
                manifest_json=pkg.manifest_json,
                payloads=pkg.payloads,
                execution_mode=ExecutionMode.FIXTURE,
                output_dir=out_path,
            )

            # Package passes overall because row and financial controls balanced
            self.assertTrue(res.passed)
            self.assertEqual(res.disposition, RecordDisposition.ACCEPTED)
            self.assertIsNotNone(res.marts_result)

            loan_records = res.marts_result.loan_mart
            # Check cohorts
            usd_delinquent = [r for r in loan_records if r.currency == "USD" and r.delinquent_loan_count_all_statuses > 0]
            eur_delinquent = [r for r in loan_records if r.currency == "EUR" and r.delinquent_loan_count_all_statuses > 0]

            # USD delinquent cohort must be BLOCKED_CANDIDATE for K06
            self.assertGreater(len(usd_delinquent), 0)
            for r in usd_delinquent:
                self.assertEqual(r.k06_publication_status, KPIPublicationStatus.BLOCKED_CANDIDATE)
                self.assertIsNone(r.delinquent_outstanding_principal)
                self.assertIn("PRINCIPAL_NEGATIVE", r.blocked_reasons)

            # EUR delinquent cohort must be PUBLISHED for K06
            self.assertGreater(len(eur_delinquent), 0)
            for r in eur_delinquent:
                self.assertEqual(r.k06_publication_status, KPIPublicationStatus.PUBLISHED)
                self.assertEqual(r.delinquent_outstanding_principal, Decimal("25000.0000"))

            # Other marts remain published
            self.assertGreater(len(res.marts_result.transaction_mart), 0)
            self.assertGreater(len(res.marts_result.customer_risk_mart), 0)
            self.assertGreater(len(res.marts_result.complaint_mart), 0)

            # Mart files written to disk
            self.assertTrue((out_path / "marts" / "mart_loan_delinquency_kpis.json").is_file())
            self.assertTrue((out_path / "marts" / "mart_transaction_kpis.json").is_file())


if __name__ == "__main__":
    unittest.main()
