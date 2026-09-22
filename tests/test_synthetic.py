"""Unit tests for Deterministic Synthetic Banking Data Foundation."""

import unittest
from datetime import date

from horizon_pipeline.intake import REQUIRED_SECTIONS
from horizon_pipeline.synthetic import (
    SyntheticBankingDataGenerator,
    build_serialized_fixture_package,
    build_test_fixture_registries,
)


class SyntheticDataTests(unittest.TestCase):
    def test_determinism_same_seed_produces_identical_dataset_and_payloads(self):
        """Verify that identical seed produces identical records, bytes, and checksums."""
        bdate = date(2025, 3, 9)
        gen1 = SyntheticBankingDataGenerator(seed=12345, business_date=bdate)
        dataset1 = gen1.generate(num_customers=10, num_transactions=20, num_loans=5)

        gen2 = SyntheticBankingDataGenerator(seed=12345, business_date=bdate)
        dataset2 = gen2.generate(num_customers=10, num_transactions=20, num_loans=5)

        self.assertEqual(dataset1.sections, dataset2.sections)

        # Serialized packages must have exact identical bytes and manifest
        pkg1 = build_serialized_fixture_package(dataset1, revision=1)
        pkg2 = build_serialized_fixture_package(dataset2, revision=1)

        self.assertEqual(pkg1.manifest_json, pkg2.manifest_json)
        self.assertEqual(pkg1.payloads, pkg2.payloads)

    def test_all_27_sections_represented(self):
        """Verify that the generator populates logical sections for all 27 mandatory sections."""
        gen = SyntheticBankingDataGenerator(seed=42, business_date=date(2025, 3, 9))
        dataset = gen.generate(num_customers=5, num_transactions=10, num_loans=2)

        for src, sec_names in REQUIRED_SECTIONS.items():
            for sec in sec_names:
                self.assertIn((src, sec), dataset.sections)

        self.assertEqual(len(dataset.sections), 27)

    def test_referential_integrity_across_entities(self):
        """Verify key relationships: customer -> account -> transaction, loans, alerts, complaints."""
        gen = SyntheticBankingDataGenerator(seed=999, business_date=date(2025, 3, 9))
        dataset = gen.generate(num_customers=15, num_transactions=30, num_loans=8)

        # Customer IDs
        cust_ids = {c["customer_id"] for c in dataset.sections[("SRC-01", "customers")]}
        self.assertGreater(len(cust_ids), 0)

        # Accounts reference valid customer
        acc_map = {}
        for acc in dataset.sections[("SRC-01", "accounts")]:
            self.assertIn(acc["customer_id"], cust_ids)
            acc_map[acc["account_id"]] = acc

        # Transactions reference valid account
        for tx in dataset.sections[("SRC-01", "transactions")]:
            self.assertIn(tx["account_id"], acc_map)

        # Loans reference valid customer
        for loan in dataset.sections[("SRC-02", "loans")]:
            self.assertIn(loan["customer_id"], cust_ids)

        # Fraud alerts reference valid account
        for alert in dataset.sections[("SRC-03", "alerts")]:
            self.assertIn(alert["account_id"], acc_map)

        # Branch references
        branch_ids = {b["branch_id"] for b in dataset.sections[("SRC-05", "branches")]}
        for cust in dataset.sections[("SRC-01", "customers")]:
            self.assertIn(cust["primary_branch_id"], branch_ids)

    def test_risk_scenarios_are_additive_and_default_output_is_unchanged(self):
        args = dict(num_customers=5, num_transactions=10, num_loans=2)
        default = SyntheticBankingDataGenerator(seed=77).generate(**args)
        explicit_default = SyntheticBankingDataGenerator(seed=77).generate(**args, include_risk_scenarios=False)
        enriched = SyntheticBankingDataGenerator(seed=77).generate(**args, include_risk_scenarios=True)
        self.assertEqual(default.sections, explicit_default.sections)
        self.assertEqual(len(enriched.sections[("SRC-01", "account_restriction_state")]), len(default.sections[("SRC-01", "account_restriction_state")]) + 1)
        self.assertEqual(len(enriched.sections[("SRC-03", "fraud_alert_state")]), len(default.sections[("SRC-03", "fraud_alert_state")]) + 1)
        self.assertEqual(len(enriched.sections[("SRC-04", "complaint_snapshot")]), len(default.sections[("SRC-04", "complaint_snapshot")]) + 1)
        self.assertEqual(len(enriched.sections[("SRC-04", "complaint_history_event")]), len(default.sections[("SRC-04", "complaint_history_event")]) + 2)

    def test_risk_scenario_generation_is_deterministic(self):
        first = SyntheticBankingDataGenerator(seed=88).generate(include_risk_scenarios=True)
        second = SyntheticBankingDataGenerator(seed=88).generate(include_risk_scenarios=True)
        self.assertEqual(first.sections, second.sections)

    def test_risk_fixture_mappings_are_isolated_and_resolvable(self):
        _, _, _, mappings, _ = build_test_fixture_registries()
        resolved, findings = mappings.resolve("SRC-03", "fraud_severity", "FIXTURE_MAP_V1", "HIGH")
        self.assertTrue(resolved.is_resolved)
        self.assertEqual(resolved.canonical_value, "HIGH")
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
