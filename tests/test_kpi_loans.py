"""Acceptance and unit tests for Loan Delinquency KPIs (K05-K06).

Governed by:
- DD-06 Approved KPI and canonical mapping policy
- DD-09 Data quality and reconciliation policy (gating rules)
- Sprint 3 Package 3 Increment 3 implementation plan
"""

from datetime import date
from decimal import Decimal
import pytest

from horizon_pipeline.analytics.kpi import KPIEngine, KPIPublicationStatus, LoanKPIResult
from horizon_pipeline.processing.records import ExecutionMode


class TestLoanKPIs:
    """Test suite for K05 (Delinquency Rate) and K06 (Delinquent Balance)."""

    def test_ac_k05_01_active_loans_and_dpd_boundary(self):
        """AC-K05-01: Only active loans in K05, DPD > 30 strictly delinquent (DPD=30 not delinquent)."""
        b_date = date(2026, 9, 22)

        loans = [
            # Active loans:
            {"loan_id": "L1", "business_date": b_date, "loan_status": "ACTIVE", "days_past_due": 0, "outstanding_principal": "1000.0000", "currency": "USD"},
            {"loan_id": "L2", "business_date": b_date, "loan_status": "DELINQUENT_ACTIVE", "days_past_due": 30, "outstanding_principal": "2000.0000", "currency": "USD"},  # DPD 30: NOT delinquent
            {"loan_id": "L3", "business_date": b_date, "loan_status": "FORBEARANCE_ACTIVE", "days_past_due": 31, "outstanding_principal": "3000.0000", "currency": "USD"},  # DPD 31: DELINQUENT
            {"loan_id": "L4", "business_date": b_date, "loan_status": "ACTIVE", "days_past_due": 45, "outstanding_principal": "4000.0000", "currency": "USD"},  # DPD 45: DELINQUENT
            # Inactive loans (excluded from K05):
            {"loan_id": "L5", "business_date": b_date, "loan_status": "PAID_OFF", "days_past_due": 0, "outstanding_principal": "0.0000", "currency": "USD"},
            {"loan_id": "L6", "business_date": b_date, "loan_status": "CLOSED", "days_past_due": 0, "outstanding_principal": "0.0000", "currency": "USD"},
            {"loan_id": "L7", "business_date": b_date, "loan_status": "CHARGED_OFF", "days_past_due": 120, "outstanding_principal": "5000.0000", "currency": "USD"},  # DPD 120, but charged off
        ]

        result = KPIEngine.calculate_loan_kpis(
            loan_positions=loans,
            business_date=b_date,
            execution_mode=ExecutionMode.FIXTURE,
        )

        # Active loans: L1, L2, L3, L4 = 4
        # Delinquent active: L3 (DPD 31), L4 (DPD 45) = 2. L2 (DPD 30) is NOT delinquent.
        assert result.active_loan_count == 4
        assert result.delinquent_active_loan_count == 2
        assert result.delinquency_rate_pct == Decimal("50.00000000")

        # K06 evaluates ALL statuses with DPD > 30: L3, L4, and L7 = 3 loans
        assert result.delinquent_loan_count_all_statuses == 3
        # L3 (3000) + L4 (4000) + L7 (5000) = 12000.0000 USD
        assert result.k06_publication_status["USD"] == KPIPublicationStatus.PUBLISHED
        assert result.delinquent_outstanding_principal_by_currency["USD"] == Decimal("12000.0000")

    def test_ac_k06_01_missing_principal_gating(self):
        """AC-K06-01: Any DPD > 30 loan with missing principal blocks K06 candidate publication."""
        b_date = date(2026, 9, 22)

        loans = [
            {"loan_id": "L1", "business_date": b_date, "loan_status": "ACTIVE", "days_past_due": 45, "outstanding_principal": "1000.0000", "currency": "USD"},
            {"loan_id": "L2", "business_date": b_date, "loan_status": "ACTIVE", "days_past_due": 60, "outstanding_principal": None, "currency": "USD"},  # Missing principal!
        ]

        result = KPIEngine.calculate_loan_kpis(
            loan_positions=loans,
            business_date=b_date,
            execution_mode=ExecutionMode.FIXTURE,
        )

        assert result.missing_principal_count == 1
        assert result.k06_publication_status["USD"] == KPIPublicationStatus.BLOCKED_CANDIDATE
        assert result.delinquent_outstanding_principal_by_currency["USD"] is None
        assert "PRINCIPAL_MISSING" in result.k06_blocked_reasons["USD"]

    def test_ac_k06_02_negative_principal_quarantine_and_gating(self):
        """AC-K06-02: Any DPD > 30 loan with negative principal is quarantined and blocks K06 publication."""
        b_date = date(2026, 9, 22)

        loans = [
            {"loan_id": "L1", "business_date": b_date, "loan_status": "ACTIVE", "days_past_due": 45, "outstanding_principal": "1000.0000", "currency": "USD"},
            {"loan_id": "L2", "business_date": b_date, "loan_status": "ACTIVE", "days_past_due": 60, "outstanding_principal": "-500.0000", "currency": "USD"},  # Negative!
        ]

        result = KPIEngine.calculate_loan_kpis(
            loan_positions=loans,
            business_date=b_date,
            execution_mode=ExecutionMode.FIXTURE,
        )

        assert result.quarantined_negative_principal_count == 1
        assert result.k06_publication_status["USD"] == KPIPublicationStatus.BLOCKED_CANDIDATE
        assert result.delinquent_outstanding_principal_by_currency["USD"] is None
        assert "PRINCIPAL_NEGATIVE" in result.k06_blocked_reasons["USD"]

    def test_k06_currency_isolation(self):
        """USD is blocked by missing principal, but EUR without defects publishes successfully."""
        b_date = date(2026, 9, 22)

        loans = [
            {"loan_id": "L1_USD", "business_date": b_date, "loan_status": "ACTIVE", "days_past_due": 45, "outstanding_principal": None, "currency": "USD"},
            {"loan_id": "L2_EUR", "business_date": b_date, "loan_status": "ACTIVE", "days_past_due": 45, "outstanding_principal": "2500.0000", "currency": "EUR"},
        ]

        result = KPIEngine.calculate_loan_kpis(
            loan_positions=loans,
            business_date=b_date,
            execution_mode=ExecutionMode.FIXTURE,
        )

        assert result.k06_publication_status["USD"] == KPIPublicationStatus.BLOCKED_CANDIDATE
        assert result.delinquent_outstanding_principal_by_currency["USD"] is None
        assert result.k06_publication_status["EUR"] == KPIPublicationStatus.PUBLISHED
        assert result.delinquent_outstanding_principal_by_currency["EUR"] == Decimal("2500.0000")

    def test_zero_active_loans_returns_none(self):
        """When active loans count is 0, delinquency rate is None."""
        b_date = date(2026, 9, 22)
        loans = [
            {"loan_id": "L1", "business_date": b_date, "loan_status": "PAID_OFF", "days_past_due": 0, "outstanding_principal": "0.0000", "currency": "USD"},
        ]
        result = KPIEngine.calculate_loan_kpis(
            loan_positions=loans,
            business_date=b_date,
            execution_mode=ExecutionMode.FIXTURE,
        )
        assert result.active_loan_count == 0
        assert result.delinquency_rate_pct is None

    def test_business_date_filtering(self):
        """Positions for other business dates are excluded."""
        b_date = date(2026, 9, 22)
        loans = [
            {"loan_id": "L1", "business_date": date(2026, 9, 21), "loan_status": "ACTIVE", "days_past_due": 45, "outstanding_principal": "1000.0000", "currency": "USD"},
            {"loan_id": "L2", "business_date": b_date, "loan_status": "ACTIVE", "days_past_due": 0, "outstanding_principal": "1000.0000", "currency": "USD"},
        ]
        result = KPIEngine.calculate_loan_kpis(
            loan_positions=loans,
            business_date=b_date,
            execution_mode=ExecutionMode.FIXTURE,
        )
        assert result.total_loans_evaluated == 1
        assert result.active_loan_count == 1
        assert result.delinquent_active_loan_count == 0

    def test_curated_position_dataclass_input(self):
        """CuratedPosition dataclass instances are processed correctly."""
        from horizon_pipeline.processing.records import CuratedPosition

        b_date = date(2026, 9, 22)
        pos = CuratedPosition(
            loan_id="L100",
            business_date=b_date,
            outstanding_principal=Decimal("45000.0000"),
            currency="USD",
            days_past_due=60,
            loan_status="ACTIVE",
        )

        result = KPIEngine.calculate_loan_kpis(
            loan_positions=[pos],
            business_date=b_date,
            execution_mode=ExecutionMode.FIXTURE,
        )

        assert result.active_loan_count == 1
        assert result.delinquent_active_loan_count == 1
        assert result.delinquency_rate_pct == Decimal("100.00000000")
        assert result.k06_publication_status["USD"] == KPIPublicationStatus.PUBLISHED
        assert result.delinquent_outstanding_principal_by_currency["USD"] == Decimal("45000.0000")
