"""End-to-End Offline Processing Engine Integration Tests.

CRITICAL NOTICE: TEST FIXTURES ONLY.
Verifies complete pipeline execution:
1. Passing flow across all 27 sections in FIXTURE mode.
2. Strict fail-closed execution in PRODUCTION mode against MasterProductionRegistry.
3. Mixed record quarantine and reconciliation balance.
4. Replay and conflict detection across multiple deliveries.
5. Absolute registry isolation between test fixtures and production contracts.
"""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from horizon_pipeline.contracts.financial import parse_decimal_exact
from horizon_pipeline.contracts.findings import FindingSeverity
from horizon_pipeline.contracts.registry import MasterProductionRegistry
from horizon_pipeline.contracts.states import ContractState
from horizon_pipeline.processing.engine import OfflineProcessingEngine
from horizon_pipeline.processing.records import ExecutionMode, RecordDisposition, RetentionCategory
from horizon_pipeline.processing.replay import BatchStateTracker
from horizon_pipeline.synthetic import (
    SyntheticBankingDataGenerator,
    build_serialized_fixture_package,
    build_test_fixture_registries,
    serialize_csv_exact_bytes,
)


class ProcessingE2ETests(unittest.TestCase):
    def setUp(self):
        self.bdate = date(2025, 3, 9)
        self.gen = SyntheticBankingDataGenerator(seed=888, business_date=self.bdate)
        self.dataset = self.gen.generate(num_customers=5, num_transactions=10, num_loans=3)
        self.pkg = build_serialized_fixture_package(self.dataset, revision=1)

    def test_e2e_fixture_passing_flow(self):
        """Passing Flow: Full 27-section package in FIXTURE mode transforms, traces, and reconciles."""
        tracker = BatchStateTracker()
        engine = OfflineProcessingEngine(batch_tracker=tracker)

        with tempfile.TemporaryDirectory() as tmp_dir:
            res = engine.process_package(
                manifest_json=self.pkg.manifest_json,
                payloads=self.pkg.payloads,
                execution_mode=ExecutionMode.FIXTURE,
                output_dir=Path(tmp_dir),
            )

            self.assertTrue(res.passed)
            self.assertEqual(res.disposition, RecordDisposition.ACCEPTED)
            self.assertEqual(res.execution_mode, ExecutionMode.FIXTURE)
            self.assertEqual(res.quarantine_ledger.count(), 0)

            # Curated entities populated
            self.assertIn("customers", res.curated_entities)
            self.assertIn("accounts", res.curated_entities)
            self.assertIn("transactions", res.curated_entities)
            self.assertIn("loans", res.curated_entities)
            self.assertIn("positions", res.curated_entities)
            self.assertIn("payments", res.curated_entities)

            # Completeness and reconciliation passed
            self.assertTrue(res.dq_summary.completeness_passed)
            self.assertTrue(res.reconciliation_summary.all_balanced)

            # Artifacts written to disk
            self.assertTrue((Path(tmp_dir) / "manifest.json").is_file())
            self.assertTrue((Path(tmp_dir) / "accepted" / "customers.json").is_file())
            self.assertTrue((Path(tmp_dir) / "dq_summary.json").is_file())
            self.assertTrue((Path(tmp_dir) / "reconciliation_summary.json").is_file())

    def test_e2e_production_mode_fails_closed(self):
        """Production Mode: Engine must bind strictly to MasterProductionRegistry and fail closed."""
        engine = OfflineProcessingEngine()

        res = engine.process_package(
            manifest_json=self.pkg.manifest_json,
            payloads=self.pkg.payloads,
            execution_mode=ExecutionMode.PRODUCTION,
        )

        self.assertFalse(res.passed)
        self.assertEqual(res.disposition, RecordDisposition.QUARANTINED)
        self.assertEqual(res.execution_mode, ExecutionMode.PRODUCTION)
        self.assertEqual(len(res.curated_entities), 0)
        self.assertTrue(any("HDR" in str(f) or "SCH" in str(f) for f in res.findings))

    def test_e2e_quarantine_with_mixed_records(self):
        """Mixed Flow: Invalid record is quarantined while valid records are accepted and reconciled."""
        # Modify dataset: add an invalid transaction row with unapproved currency
        corrupted_dataset = copy.deepcopy(self.dataset)
        raw_tx = dict(corrupted_dataset.sections[("SRC-01", "transactions")][0])
        raw_tx["transaction_id"] = "TX-INVALID-CURR"
        raw_tx["currency"] = "INVALID"  # Unapproved currency under DQ-D07
        corrupted_dataset.sections[("SRC-01", "transactions")].append(raw_tx)

        corrupted_pkg = build_serialized_fixture_package(corrupted_dataset, revision=1)

        tracker = BatchStateTracker()
        engine = OfflineProcessingEngine(batch_tracker=tracker)

        res = engine.process_package(
            manifest_json=corrupted_pkg.manifest_json,
            payloads=corrupted_pkg.payloads,
            execution_mode=ExecutionMode.FIXTURE,
        )

        # Quarantined due to error finding
        self.assertFalse(res.passed)
        self.assertEqual(res.disposition, RecordDisposition.QUARANTINED)
        self.assertEqual(res.quarantine_ledger.count(), 1)

        quar_rec = res.quarantine_ledger.all_records()[0]
        self.assertEqual(quar_rec.record_id, "TX-INVALID-CURR")
        self.assertEqual(quar_rec.retention_category, RetentionCategory.ANALYTICAL_24M)

        # Valid transactions accepted
        accepted_txs = res.curated_entities.get("transactions", [])
        self.assertEqual(len(accepted_txs), len(self.dataset.sections[("SRC-01", "transactions")]))

        # Row reconciliation balances (received = accepted + quarantined)
        self.assertTrue(res.reconciliation_summary.all_balanced)

    def test_e2e_eur_currency_accepted_in_fixture_mode(self):
        """EUR is an approved fixture currency alongside USD (no USD-only assumption)."""
        eur_dataset = copy.deepcopy(self.dataset)
        raw_tx = dict(eur_dataset.sections[("SRC-01", "transactions")][0])
        raw_tx["transaction_id"] = "TX-EUR-001"
        raw_tx["currency"] = "EUR"
        eur_dataset.sections[("SRC-01", "transactions")].append(raw_tx)

        eur_pkg = build_serialized_fixture_package(eur_dataset, revision=1)

        tracker = BatchStateTracker()
        engine = OfflineProcessingEngine(batch_tracker=tracker)

        res = engine.process_package(
            manifest_json=eur_pkg.manifest_json,
            payloads=eur_pkg.payloads,
            execution_mode=ExecutionMode.FIXTURE,
        )

        self.assertTrue(res.passed)
        self.assertEqual(res.quarantine_ledger.count(), 0)
        self.assertTrue(res.reconciliation_summary.all_balanced)

    def test_production_masking_fails_closed(self):
        """Production masking algorithms remain PENDING and must fail closed under DD-08."""
        from horizon_pipeline.contracts.states import PendingContractError
        from horizon_pipeline.processing.transform import (
            mask_account_id,
            mask_customer_name,
            mask_tax_identifier,
        )

        with self.assertRaises(PendingContractError):
            mask_tax_identifier("123-45-6789", execution_mode=ExecutionMode.PRODUCTION)

        with self.assertRaises(PendingContractError):
            mask_account_id("1234567890", execution_mode=ExecutionMode.PRODUCTION)

        with self.assertRaises(PendingContractError):
            mask_customer_name("John Doe", execution_mode=ExecutionMode.PRODUCTION)

    def test_production_natural_key_fails_closed(self):
        """Production natural key extraction fails closed with CRITICAL finding under PD-01."""
        from horizon_pipeline.processing.identity import RecordIdentityEngine
        from horizon_pipeline.processing.records import RawRecord

        engine = RecordIdentityEngine(execution_mode=ExecutionMode.PRODUCTION)
        rec = RawRecord("SRC-01", "customers", "CUST-1", self.dataset.business_date, 1, 1, {"customer_id": "CUST-1"})
        res = engine.deduplicate_section([rec])

        self.assertEqual(len(res.accepted_records), 0)
        self.assertEqual(len(res.quarantined_records), 1)
        self.assertEqual(len(res.findings), 1)
        self.assertEqual(res.findings[0].severity, FindingSeverity.CRITICAL)

    def test_e2e_replay_and_conflict_detection(self):
        """Replay Flow: Identical delivery emits INFO; conflicting checksum is rejected (CRITICAL)."""
        tracker = BatchStateTracker()
        engine = OfflineProcessingEngine(batch_tracker=tracker)

        # First run: passing
        res1 = engine.process_package(
            manifest_json=self.pkg.manifest_json,
            payloads=self.pkg.payloads,
            execution_mode=ExecutionMode.FIXTURE,
        )
        self.assertTrue(res1.passed)

        # Re-run identical delivery: passes as identical replay
        res2 = engine.process_package(
            manifest_json=self.pkg.manifest_json,
            payloads=self.pkg.payloads,
            execution_mode=ExecutionMode.FIXTURE,
        )
        self.assertTrue(res2.passed)
        self.assertTrue(any(getattr(f, "rule_id", getattr(f, "code", None)) == "DQ-D02" and f.severity == FindingSeverity.INFO for f in res2.findings))

        # Build conflicting delivery under the same revision (different payload checksum)
        conflicting_dataset = copy.deepcopy(self.dataset)
        conflicting_dataset.sections[("SRC-01", "customers")][0]["customer_name"] = "Conflicting Name"
        conflicting_pkg = build_serialized_fixture_package(conflicting_dataset, revision=1)

        res3 = engine.process_package(
            manifest_json=conflicting_pkg.manifest_json,
            payloads=conflicting_pkg.payloads,
            execution_mode=ExecutionMode.FIXTURE,
        )
        self.assertFalse(res3.passed)
        self.assertTrue(any(getattr(f, "rule_id", getattr(f, "code", None)) == "DQ-D02" and f.severity == FindingSeverity.CRITICAL for f in res3.findings))

    def test_fixture_production_isolation(self):
        """Registry Isolation: Executing fixture pipeline must never mutate MasterProductionRegistry."""
        prod_master = MasterProductionRegistry()
        pending_headers = sum(1 for c in prod_master.headers._registry.values() if c.state == ContractState.PENDING)
        pending_schemas = sum(1 for c in prod_master.schemas._registry.values() if c.state == ContractState.PENDING)
        pending_controls = sum(1 for c in prod_master.financial.all_controls() if c.state == ContractState.PENDING)

        self.assertEqual(pending_headers, 27)
        self.assertEqual(pending_schemas, 27)
        self.assertEqual(pending_controls, 7)

        # Run fixture pipeline
        engine = OfflineProcessingEngine()
        engine.process_package(
            manifest_json=self.pkg.manifest_json,
            payloads=self.pkg.payloads,
            execution_mode=ExecutionMode.FIXTURE,
        )

        # Verify MasterProductionRegistry remains strictly unchanged
        prod_master_after = MasterProductionRegistry()
        after_headers = sum(1 for c in prod_master_after.headers._registry.values() if c.state == ContractState.PENDING)
        active_headers = sum(1 for c in prod_master_after.headers._registry.values() if c.state == ContractState.ACTIVE)
        after_schemas = sum(1 for c in prod_master_after.schemas._registry.values() if c.state == ContractState.PENDING)
        active_schemas = sum(1 for c in prod_master_after.schemas._registry.values() if c.state == ContractState.ACTIVE)
        after_controls = sum(1 for c in prod_master_after.financial.all_controls() if c.state == ContractState.PENDING)
        active_controls = sum(1 for c in prod_master_after.financial.all_controls() if c.state == ContractState.ACTIVE)

        self.assertEqual(after_headers, 27)
        self.assertEqual(active_headers, 0)
        self.assertEqual(after_schemas, 27)
        self.assertEqual(active_schemas, 0)
        self.assertEqual(after_controls, 7)
        self.assertEqual(active_controls, 0)


if __name__ == "__main__":
    unittest.main()
