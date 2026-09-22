"""Contract Safety Tests.

CRITICAL REGRESSION GUARDS:
Verifies that production registries strictly maintain unresolved contracts as PENDING,
with 0 active production predicates, 0 active production mapping rows, 0 active production
financial controls, and runtime tzdb 2026a not falsely marked verified.
"""

import unittest

from horizon_pipeline.contracts.registry import (
    CANDIDATE_SCHEMA_TEMPLATE,
    PD04_CANDIDATE_PREDICATES,
    PD05_CANDIDATE_CONTROLS,
    PD06_CANDIDATE_DOMAINS,
    MasterProductionRegistry,
)
from horizon_pipeline.contracts.states import ContractState, PendingContractError
from horizon_pipeline.contracts.temporal import get_tzdb_runtime_proof
from horizon_pipeline.intake import REQUIRED_SECTIONS


class ContractSafetyTests(unittest.TestCase):
    def setUp(self):
        self.master = MasterProductionRegistry()

    def test_all_27_production_headers_remain_pending(self):
        """Verify that all 27 mandatory sections have PENDING header contracts."""
        total_sections = sum(len(secs) for secs in REQUIRED_SECTIONS.values())
        self.assertEqual(total_sections, 27)

        for source, sections in REQUIRED_SECTIONS.items():
            for section in sections:
                schema_id = CANDIDATE_SCHEMA_TEMPLATE.format(source=source, section=section)
                contract = self.master.headers.get(source, section, schema_id)
                self.assertIsNotNone(contract, f"Missing header contract entry for {source}/{section}")
                self.assertEqual(
                    contract.state,
                    ContractState.PENDING,
                    f"Production header for {source}/{section} must be PENDING",
                )
                self.assertFalse(contract.is_fixture)
                # Ensure execution fails closed
                with self.assertRaises(PendingContractError):
                    self.master.headers.require_active(source, section, schema_id)

    def test_all_27_production_schemas_remain_pending(self):
        """Verify that all 27 candidate v001 schemas remain PENDING and inactive."""
        for source, sections in REQUIRED_SECTIONS.items():
            for section in sections:
                schema_id = CANDIDATE_SCHEMA_TEMPLATE.format(source=source, section=section)
                contract = self.master.schemas.get(source, section, schema_id)
                self.assertIsNotNone(contract, f"Missing schema entry for {source}/{section}")
                self.assertEqual(
                    contract.state,
                    ContractState.PENDING,
                    f"Production schema for {source}/{section} must be PENDING",
                )
                self.assertFalse(contract.is_fixture)
                # Ensure lookup fails closed
                with self.assertRaises(PendingContractError):
                    self.master.schemas.require_active(source, section, schema_id)

    def test_production_active_predicates_remain_zero(self):
        """Verify that active production predicates count is exactly zero."""
        active_count = 0
        for p in self.master.applicability._predicates.values():
            if not p.is_fixture and p.state == ContractState.ACTIVE:
                active_count += 1

        self.assertEqual(active_count, 0, "No production applicability predicate may be ACTIVE")
        self.assertEqual(len(PD04_CANDIDATE_PREDICATES), 51, "Must track all 51 PD-04 candidate predicates")

        for idx, (source, section, target_field, _, _) in enumerate(PD04_CANDIDATE_PREDICATES, start=1):
            schema_id = CANDIDATE_SCHEMA_TEMPLATE.format(source=source, section=section)
            field_alias = target_field.split(".")[-1]
            p = self.master.applicability.get(source, section, schema_id, field_alias)
            self.assertIsNotNone(p, f"Missing candidate predicate for {target_field}")
            self.assertEqual(p.state, ContractState.PENDING)

    def test_production_financial_controls_remain_pending(self):
        """Verify that all 7 candidate financial controls remain PENDING (0 active) with unresolved tolerance."""
        active_controls = [
            c for c in self.master.financial._controls.values()
            if not c.is_fixture and c.state == ContractState.ACTIVE
        ]
        self.assertEqual(len(active_controls), 0, "No production financial control may be ACTIVE")
        self.assertEqual(len(PD05_CANDIDATE_CONTROLS), 7, "Must track all 7 PD-05 candidate controls")

        for ctrl_id, source, section, _, _, currency in PD05_CANDIDATE_CONTROLS:
            schema_id = CANDIDATE_SCHEMA_TEMPLATE.format(source=source, section=section)
            ctrl = self.master.financial.get(source, section, schema_id, currency)
            self.assertIsNotNone(ctrl, f"Missing control {ctrl_id}")
            self.assertEqual(ctrl.state, ContractState.PENDING, f"Control {ctrl_id} must be PENDING")
            self.assertIsNone(ctrl.tolerance, f"Tolerance for {ctrl_id} must not be defaulted; must be None")
            self.assertEqual(ctrl.tolerance_state, ContractState.PENDING, f"Tolerance state for {ctrl_id} must be PENDING")
            self.assertFalse(ctrl.is_fixture, f"Control {ctrl_id} must not be a test fixture")

            # Execution against candidate control must fail closed
            result, findings = self.master.financial.reconcile_population(
                source=source,
                section=section,
                schema_version=schema_id,
                currency=currency,
                source_control_total="100.0000",
                accepted_amounts=["100.0000"],
            )
            self.assertFalse(result.is_balanced)
            self.assertTrue(any(f.code == "FIN-CONTROL-PENDING" for f in findings))
            self.assertTrue(any(f.code == "FIN-TOLERANCE-UNRESOLVED" for f in findings))

    def test_production_mapping_rows_remain_pending(self):
        """Verify that all 23 candidate domain mapping groups remain PENDING (0 active)."""
        self.assertEqual(len(PD06_CANDIDATE_DOMAINS), 23, "Must track all 23 PD-06 candidate domain groups")

        active_entries = [
            e for e in self.master.mappings._entries.values()
            if not e.is_fixture and e.state == ContractState.ACTIVE
        ]
        self.assertEqual(len(active_entries), 0, "No production mapping entry may be ACTIVE")

        for source, _, domain in PD06_CANDIDATE_DOMAINS:
            state = self.master.mappings._versions.get((source, domain, "IDENTITY_SYN_V1"))
            self.assertEqual(
                state,
                ContractState.PENDING,
                f"Domain mapping group for {source}/{domain} must be PENDING",
            )

    def test_runtime_tzdb_2026a_is_not_falsely_verified(self):
        """Verify that PD-07 runtime tzdb 2026a is NOT falsely marked as verified."""
        proof = get_tzdb_runtime_proof(target_version="2026a")
        self.assertFalse(proof.is_verified, "Cannot claim tzdb 2026a is verified on this runtime")
        self.assertEqual(proof.state, ContractState.PENDING)
        self.assertIn("2026a", proof.evidence)


if __name__ == "__main__":
    unittest.main()
