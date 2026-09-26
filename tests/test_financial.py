"""Unit tests for PD-05 Financial Control Engine and Exact-Decimal Arithmetic."""

import unittest
from decimal import Decimal

from horizon_pipeline.contracts.financial import (
    ControlAvailability,
    FinancialControlContract,
    FinancialControlEngine,
    parse_decimal_exact,
)
from horizon_pipeline.contracts.registry import (
    CANDIDATE_SCHEMA_TEMPLATE,
    PD05_CANDIDATE_CONTROLS,
    MasterProductionRegistry,
)
from horizon_pipeline.contracts.states import ContractState


class FinancialControlTests(unittest.TestCase):
    def setUp(self):
        self.engine = FinancialControlEngine()

        # Register active fixture financial control for USD
        self.engine.register(
            FinancialControlContract(
                control_id="TEST-FC-USD",
                source="SRC-01",
                section="transactions",
                schema_version="TEST.SRC-01.transactions.v1",
                amount_field="amount",
                currency_field="currency",
                currency="USD",
                state=ContractState.ACTIVE,
                tolerance=Decimal("0.0000"),
                tolerance_state=ContractState.ACTIVE,
                is_fixture=True,
            )
        )

        # Register active fixture financial control for EUR (segregated)
        self.engine.register(
            FinancialControlContract(
                control_id="TEST-FC-EUR",
                source="SRC-01",
                section="transactions",
                schema_version="TEST.SRC-01.transactions.v1",
                amount_field="amount",
                currency_field="currency",
                currency="EUR",
                state=ContractState.ACTIVE,
                tolerance=Decimal("0.0000"),
                tolerance_state=ContractState.ACTIVE,
                is_fixture=True,
            )
        )

        # Register pending financial control
        self.engine.register(
            FinancialControlContract(
                control_id="TEST-FC-PENDING",
                source="SRC-02",
                section="positions",
                schema_version="TEST.SRC-02.positions.v1",
                amount_field="outstanding_principal",
                currency_field="currency",
                currency="USD",
                state=ContractState.PENDING,
                tolerance=None,
                tolerance_state=ContractState.PENDING,
                is_fixture=True,
            )
        )

    def test_exact_decimal_parsing_and_float_rejection(self):
        # String parsing to exact Decimal
        d = parse_decimal_exact("123.4500")
        self.assertEqual(d, Decimal("123.4500"))

        # Binary float is strictly forbidden
        with self.assertRaises(TypeError):
            parse_decimal_exact(123.45)

        # Excess scale (>4 decimal places) rejected
        with self.assertRaises(ValueError):
            parse_decimal_exact("123.45678")

    def test_balanced_reconciliation_zero_residual(self):
        # Example from PD-05: source 125.0000 = accepted 100.0000 + quarantined 20.0000 + excluded 5.0000
        result, findings = self.engine.reconcile_population(
            source="SRC-01",
            section="transactions",
            schema_version="TEST.SRC-01.transactions.v1",
            currency="USD",
            source_control_total="125.0000",
            accepted_amounts=["70.0000", "30.0000"],
            quarantined_amounts=["20.0000"],
            approved_excluded_amounts=["5.0000"],
        )
        self.assertTrue(result.is_balanced)
        self.assertEqual(result.residual, Decimal("0.0000"))
        self.assertEqual(result.accepted_total, Decimal("100.0000"))
        self.assertEqual(result.quarantined_total, Decimal("20.0000"))
        self.assertEqual(result.approved_excluded_total, Decimal("5.0000"))
        self.assertEqual(result.reconciled_component_total, Decimal("125.0000"))
        self.assertEqual(findings, [])

    def test_reconciliation_imbalance_detected(self):
        result, findings = self.engine.reconcile_population(
            source="SRC-01",
            section="transactions",
            schema_version="TEST.SRC-01.transactions.v1",
            currency="USD",
            source_control_total="125.0000",
            accepted_amounts=["100.0000"],
            quarantined_amounts=["20.0000"],
            approved_excluded_amounts=["0.0000"],  # Missing 5.0000
        )
        self.assertFalse(result.is_balanced)
        self.assertEqual(result.residual, Decimal("5.0000"))
        self.assertTrue(any(f.code == "FIN-RECONCILIATION-IMBALANCE" for f in findings))

    def test_missing_source_control_is_not_zero(self):
        # Invariant: Missing control is NOT zero
        result, findings = self.engine.reconcile_population(
            source="SRC-01",
            section="transactions",
            schema_version="TEST.SRC-01.transactions.v1",
            currency="USD",
            source_control_total=None,
            accepted_amounts=["100.0000"],
        )
        self.assertFalse(result.is_balanced)
        self.assertIsNone(result.source_control_total)
        self.assertTrue(any(f.code == "FIN-MISSING-SOURCE-TOTAL" for f in findings))

    def test_unavailable_control_fails_closed_with_reason(self):
        # Unavailable is NOT zero
        result, findings = self.engine.reconcile_population(
            source="SRC-01",
            section="transactions",
            schema_version="TEST.SRC-01.transactions.v1",
            currency="USD",
            source_control_total="100.0000",
            accepted_amounts=["100.0000"],
            availability=ControlAvailability.UNAVAILABLE,
            unavailable_reason="Source system feed outage",
        )
        self.assertFalse(result.is_balanced)
        self.assertEqual(result.availability, ControlAvailability.UNAVAILABLE)
        self.assertTrue(any(f.code == "FIN-CONTROL-UNAVAILABLE" for f in findings))

    def test_currency_segregation_no_cross_currency(self):
        # Look up EUR control specifically; cannot reconcile GBP or cross-currencies
        result, findings = self.engine.reconcile_population(
            source="SRC-01",
            section="transactions",
            schema_version="TEST.SRC-01.transactions.v1",
            currency="GBP",
            source_control_total="100.0000",
            accepted_amounts=["100.0000"],
        )
        self.assertFalse(result.is_balanced)
        self.assertTrue(any(f.code == "FIN-UNSUPPORTED-CONTROL" for f in findings))

    def test_pending_control_fails_closed(self):
        result, findings = self.engine.reconcile_population(
            source="SRC-02",
            section="positions",
            schema_version="TEST.SRC-02.positions.v1",
            currency="USD",
            source_control_total="500000.0000",
            accepted_amounts=["500000.0000"],
        )
        self.assertFalse(result.is_balanced)
        self.assertTrue(any(f.code == "FIN-CONTROL-PENDING" for f in findings))

    def test_production_pd05_controls_remain_pending(self):
        """Regression 1: All production PD-05 candidate controls remain PENDING."""
        master = MasterProductionRegistry()
        for ctrl_id, source, section, _, _, currency in PD05_CANDIDATE_CONTROLS:
            schema_id = CANDIDATE_SCHEMA_TEMPLATE.format(source=source, section=section)
            ctrl = master.financial.get(source, section, schema_id, currency)
            self.assertIsNotNone(ctrl, f"Missing candidate control {ctrl_id}")
            self.assertEqual(ctrl.state, ContractState.PENDING)
            self.assertFalse(ctrl.is_fixture)

    def test_unresolved_production_tolerance_not_defaulted_to_zero(self):
        """Regression 2: Unresolved production tolerance is not defaulted to 0.0000 or numeric zero."""
        master = MasterProductionRegistry()
        for ctrl_id, source, section, _, _, currency in PD05_CANDIDATE_CONTROLS:
            schema_id = CANDIDATE_SCHEMA_TEMPLATE.format(source=source, section=section)
            ctrl = master.financial.get(source, section, schema_id, currency)
            self.assertIsNotNone(ctrl)
            self.assertIsNone(ctrl.tolerance, f"Production tolerance for {ctrl_id} must be None, not defaulted")
            self.assertEqual(ctrl.tolerance_state, ContractState.PENDING, f"Tolerance state for {ctrl_id} must be PENDING")

    def test_reconciliation_requiring_unresolved_tolerance_fails_closed(self):
        """Regression 3: Reconciliation requiring unresolved tolerance fails closed."""
        # Case A: Active control with unresolved tolerance fails closed
        engine = FinancialControlEngine()
        engine.register(
            FinancialControlContract(
                control_id="ACTIVE-UNRESOLVED-TOL",
                source="SRC-01",
                section="transactions",
                schema_version="TEST.v1",
                amount_field="amount",
                currency_field="currency",
                currency="USD",
                state=ContractState.ACTIVE,
                tolerance=None,
                tolerance_state=ContractState.PENDING,
                is_fixture=False,
            )
        )
        result, findings = engine.reconcile_population(
            source="SRC-01",
            section="transactions",
            schema_version="TEST.v1",
            currency="USD",
            source_control_total="1000.0000",
            accepted_amounts=["1000.0000"],
        )
        self.assertFalse(result.is_balanced)
        self.assertEqual(result.availability, ControlAvailability.UNAVAILABLE)
        self.assertTrue(any(f.code == "FIN-TOLERANCE-UNRESOLVED" for f in findings))

        # Case B: Master registry candidate controls fail closed
        master = MasterProductionRegistry()
        for ctrl_id, source, section, _, _, currency in PD05_CANDIDATE_CONTROLS:
            schema_id = CANDIDATE_SCHEMA_TEMPLATE.format(source=source, section=section)
            res, findings = master.financial.reconcile_population(
                source=source,
                section=section,
                schema_version=schema_id,
                currency=currency,
                source_control_total="100.0000",
                accepted_amounts=["100.0000"],
            )
            self.assertFalse(res.is_balanced)
            self.assertTrue(any(f.code in {"FIN-CONTROL-PENDING", "FIN-TOLERANCE-UNRESOLVED"} for f in findings))

    def test_fixture_only_control_may_use_explicit_zero_tolerance(self):
        """Regression 4: Fixture-only control may use explicit Decimal('0.0000') tolerance."""
        # Using TEST-FC-USD registered in setUp with is_fixture=True and tolerance=Decimal("0.0000")
        ctrl = self.engine.get("SRC-01", "transactions", "TEST.SRC-01.transactions.v1", "USD")
        self.assertIsNotNone(ctrl)
        self.assertTrue(ctrl.is_fixture)
        self.assertEqual(ctrl.tolerance, Decimal("0.0000"))
        self.assertEqual(ctrl.tolerance_state, ContractState.ACTIVE)

        # Balanced fixture reconciliation succeeds
        result, findings = self.engine.reconcile_population(
            source="SRC-01",
            section="transactions",
            schema_version="TEST.SRC-01.transactions.v1",
            currency="USD",
            source_control_total="250.5000",
            accepted_amounts=["200.0000", "50.5000"],
        )
        self.assertTrue(result.is_balanced)
        self.assertEqual(result.residual, Decimal("0.0000"))
        self.assertEqual(findings, [])

        # Non-zero residual fails balancing against exact zero tolerance
        res_imbalanced, imbal_findings = self.engine.reconcile_population(
            source="SRC-01",
            section="transactions",
            schema_version="TEST.SRC-01.transactions.v1",
            currency="USD",
            source_control_total="250.5000",
            accepted_amounts=["200.0000", "50.4999"],  # off by 0.0001
        )
        self.assertFalse(res_imbalanced.is_balanced)
        self.assertEqual(res_imbalanced.residual, Decimal("0.0001"))
        self.assertTrue(any(f.code == "FIN-RECONCILIATION-IMBALANCE" for f in imbal_findings))

    def test_exact_residual_calculation_deterministic_scale4(self):
        """Regression 5: Exact mathematical residual calculation remains deterministic and scale-4."""
        # residual = source_control_total - (accepted + quarantined + excluded)
        # Using scale-4 fractions that would drift in IEEE 754 binary floating point:
        # e.g., 0.1 + 0.2 != 0.3 in float, but in Decimal("0.1000") + Decimal("0.2000") == Decimal("0.3000")
        result, findings = self.engine.reconcile_population(
            source="SRC-01",
            section="transactions",
            schema_version="TEST.SRC-01.transactions.v1",
            currency="USD",
            source_control_total="3000.3000",
            accepted_amounts=["1000.1000", "1000.2000"],
            quarantined_amounts=["500.0000"],
            approved_excluded_amounts=["500.0000"],
        )
        self.assertTrue(result.is_balanced)
        self.assertEqual(result.residual, Decimal("0.0000"))
        self.assertIsInstance(result.residual, Decimal)
        self.assertEqual(result.residual.as_tuple().exponent, -4)
        self.assertEqual(result.reconciled_component_total, Decimal("3000.3000"))

        # Fractional scale-4 residual test:
        # 1000.0003 control, components 1000.0001 -> residual 0.0002
        res2, _ = self.engine.reconcile_population(
            source="SRC-01",
            section="transactions",
            schema_version="TEST.SRC-01.transactions.v1",
            currency="USD",
            source_control_total="1000.0003",
            accepted_amounts=["1000.0001"],
        )
        self.assertEqual(res2.residual, Decimal("0.0002"))
        self.assertEqual(res2.residual.as_tuple().exponent, -4)


if __name__ == "__main__":
    unittest.main()
