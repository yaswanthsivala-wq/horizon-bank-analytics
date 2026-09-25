"""Acceptance and unit tests for Dimensional Analytical Marts.

Governed by:
- DD-06 Approved KPI and canonical mapping policy
- DD-04 Customer risk catalog and classification hierarchy
- DD-09 Data quality and reconciliation policy (gating rules)
- DD-02 Relationship exposure non-additive attribution
- Sprint 3 Package 3 Increment 3 implementation plan
"""

import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
import pytest

from horizon_pipeline.analytics.kpi import KPIPublicationStatus
from horizon_pipeline.analytics.marts import (
    AnalyticalMartsBuilder,
    ComplaintMartRecord,
    CustomerRiskMartRecord,
    LoanDelinquencyMartRecord,
    MartBuilder,
    TransactionMartRecord,
    write_analytical_marts,
)
from horizon_pipeline.analytics.risk_classification import RiskClassification
from horizon_pipeline.processing.records import ExecutionMode


class TestAnalyticalMarts:
    """Test suite for dimensional analytical marts building and serialization."""

    def test_build_transaction_mart(self):
        """Test mart_transaction_kpis dimensional aggregation and account branch lookup."""
        start = datetime(2026, 9, 22, 0, 0)
        end = datetime(2026, 9, 23, 0, 0)

        accounts = [
            {"account_id": "ACC1", "branch_id": "BR01"},
            {"account_id": "ACC2", "branch_id": "BR02"},
        ]

        txs = [
            # BR01, ONLINE, USD
            {"transaction_id": "T1", "account_id": "ACC1", "channel": "ONLINE", "occurred_at": datetime(2026, 9, 22, 10), "transaction_status": "SUCCESSFUL", "amount": "100.0000", "currency": "USD"},
            {"transaction_id": "T2", "account_id": "ACC1", "channel": "ONLINE", "occurred_at": datetime(2026, 9, 22, 11), "transaction_status": "FAILED", "amount": "50.0000", "currency": "USD"},
            # BR02, BRANCH, USD
            {"transaction_id": "T3", "account_id": "ACC2", "channel": "BRANCH", "occurred_at": datetime(2026, 9, 22, 12), "transaction_status": "POSTED", "amount": "200.0000", "currency": "USD"},
        ]
        alerts = [
            {"alert_id": "A1", "transaction_id": "T1"},
        ]

        records = MartBuilder.build_transaction_mart(
            transactions=txs,
            fraud_alerts=alerts,
            accounts=accounts,
            period_start=start,
            period_end=end,
            execution_mode=ExecutionMode.FIXTURE,
        )

        assert len(records) == 2
        # Deterministic ordering by branch_id: BR01 first, then BR02
        r1, r2 = records

        assert r1.branch_id == "BR01"
        assert r1.channel == "ONLINE"
        assert r1.currency == "USD"
        assert r1.total_transaction_count == 2
        assert r1.successful_transaction_count == 1
        assert r1.failed_transaction_count == 1
        assert r1.rate_eligible_transaction_count == 2
        assert r1.success_rate_pct == Decimal("50.00000000")
        assert r1.failure_rate_pct == Decimal("50.00000000")
        assert r1.eligible_transactions_with_fraud_alert_count == 1
        assert r1.fraud_alert_rate_pct == Decimal("50.00000000")
        assert r1.total_transaction_amount == Decimal("150.0000")

        assert r2.branch_id == "BR02"
        assert r2.channel == "BRANCH"
        assert r2.total_transaction_count == 1
        assert r2.posted_transaction_count == 1
        assert r2.success_rate_pct == Decimal("100.00000000")
        assert r2.eligible_transactions_with_fraud_alert_count == 0
        assert r2.fraud_alert_rate_pct == Decimal("0.00000000")

    def test_build_loan_delinquency_mart(self):
        """Test mart_loan_delinquency_kpis dimensional aggregation and loan lookup."""
        b_date = date(2026, 9, 22)

        loans = [
            {"loan_id": "L1", "branch_id": "BR01", "loan_type": "MORTGAGE"},
            {"loan_id": "L2", "branch_id": "BR01", "loan_type": "MORTGAGE"},
            {"loan_id": "L3", "branch_id": "BR02", "loan_type": "AUTO"},
        ]

        positions = [
            {"loan_id": "L1", "business_date": b_date, "loan_status": "ACTIVE", "days_past_due": 10, "outstanding_principal": "100000.0000", "currency": "USD"},
            {"loan_id": "L2", "business_date": b_date, "loan_status": "ACTIVE", "days_past_due": 45, "outstanding_principal": "50000.0000", "currency": "USD"},
            {"loan_id": "L3", "business_date": b_date, "loan_status": "ACTIVE", "days_past_due": 60, "outstanding_principal": None, "currency": "USD"},  # Missing principal!
        ]

        records = MartBuilder.build_loan_delinquency_mart(
            loan_positions=positions,
            loans=loans,
            business_date=b_date,
            execution_mode=ExecutionMode.FIXTURE,
        )

        assert len(records) == 2
        # BR01 MORTGAGE published; BR02 AUTO blocked candidate
        r_mortgage, r_auto = records

        assert r_mortgage.branch_id == "BR01"
        assert r_mortgage.loan_type == "MORTGAGE"
        assert r_mortgage.active_loan_count == 2
        assert r_mortgage.delinquent_active_loan_count == 1
        assert r_mortgage.loan_delinquency_rate_pct == Decimal("50.00000000")
        assert r_mortgage.delinquent_outstanding_principal == Decimal("50000.0000")
        assert r_mortgage.k06_publication_status == KPIPublicationStatus.PUBLISHED

        assert r_auto.branch_id == "BR02"
        assert r_auto.loan_type == "AUTO"
        assert r_auto.k06_publication_status == KPIPublicationStatus.BLOCKED_CANDIDATE
        assert r_auto.delinquent_outstanding_principal is None
        assert "PRINCIPAL_MISSING" in r_auto.blocked_reasons

    def test_build_customer_risk_mart(self):
        """Test mart_customer_risk_kpis with customer branch attribution and population segregation."""
        as_of = date(2026, 9, 22)

        customers = [
            {"customer_id": "C1", "primary_branch_id": "BR01"},
            {"customer_id": "C2", "primary_branch_id": "BR01"},
            {"customer_id": "C3", "primary_branch_id": "BR01"},
            {"customer_id": "C4", "primary_branch_id": "BR02"},
        ]

        assessments = [
            {"customer_id": "C1", "business_date": as_of, "classification": RiskClassification.PROVISIONAL_HIGH_RISK},
            {"customer_id": "C2", "business_date": as_of, "classification": RiskClassification.INCOMPLETE_EVIDENCE},
            {"customer_id": "C3", "business_date": as_of, "classification": RiskClassification.NOT_HIGH_RISK},
            {"customer_id": "C4", "business_date": as_of, "classification": RiskClassification.PROVISIONAL_HIGH_RISK},
        ]

        records = MartBuilder.build_customer_risk_mart(
            assessments=assessments,
            customers=customers,
            as_of_date=as_of,
            execution_mode=ExecutionMode.FIXTURE,
        )

        assert len(records) == 2
        r_br01, r_br02 = records

        assert r_br01.home_branch_id == "BR01"
        assert r_br01.total_assessed_customer_count == 3
        assert r_br01.provisional_high_risk_customer_count == 1
        assert r_br01.incomplete_evidence_customer_count == 1
        assert r_br01.not_high_risk_customer_count == 1
        assert r_br01.relationship_exposure_non_additive is True

        assert r_br02.home_branch_id == "BR02"
        assert r_br02.total_assessed_customer_count == 1
        assert r_br02.provisional_high_risk_customer_count == 1
        assert r_br02.relationship_exposure_non_additive is True

    def test_build_complaint_mart(self):
        """Test mart_complaint_kpis dimensional aggregation."""
        start = datetime(2026, 9, 22, 0, 0)
        end = datetime(2026, 9, 23, 0, 0)

        complaints = [
            {
                "complaint_id": "C1",
                "branch_id": "BR01",
                "channel": "PHONE",
                "priority": "HIGH",
                "created_at": datetime(2026, 9, 22, 2),
                "final_closed_at": datetime(2026, 9, 22, 14),
                "complaint_status": "CLOSED",
            },
        ]

        records = MartBuilder.build_complaint_mart(
            complaints=complaints,
            period_start=start,
            period_end=end,
            execution_mode=ExecutionMode.FIXTURE,
        )

        assert len(records) == 1
        r = records[0]
        assert r.branch_id == "BR01"
        assert r.channel == "PHONE"
        assert r.priority == "HIGH"
        assert r.closed_complaint_count == 1
        assert r.avg_resolution_hours == Decimal("12.0000")
        assert r.sla_eligible_complaint_count == 1
        assert r.sla_breached_complaint_count == 0  # 12h <= 24h SLA

    def test_analytical_marts_builder_and_writer(self, tmp_path: Path):
        """Test end-to-end analytical marts coordinator and deterministic JSON artifact writer."""
        start = datetime(2026, 9, 22, 0, 0)
        end = datetime(2026, 9, 23, 0, 0)
        b_date = date(2026, 9, 22)

        result = AnalyticalMartsBuilder.build_all(
            transactions=[
                {"transaction_id": "T1", "branch_id": "BR01", "channel": "ONLINE", "currency": "USD", "occurred_at": datetime(2026, 9, 22, 10), "transaction_status": "SUCCESSFUL", "amount": "100.0000"},
            ],
            loan_positions=[
                {"loan_id": "L1", "branch_id": "BR01", "loan_type": "MORTGAGE", "currency": "USD", "business_date": b_date, "loan_status": "ACTIVE", "days_past_due": 0, "outstanding_principal": "50000.0000"},
            ],
            assessments=[
                {"customer_id": "C1", "home_branch_id": "BR01", "business_date": b_date, "classification": RiskClassification.NOT_HIGH_RISK},
            ],
            complaints=[
                {"complaint_id": "C1", "branch_id": "BR01", "channel": "ONLINE", "priority": "MEDIUM", "created_at": datetime(2026, 9, 22, 8), "complaint_status": "OPEN"},
            ],
            period_start=start,
            period_end=end,
            business_date=b_date,
            execution_mode=ExecutionMode.FIXTURE,
        )

        assert len(result.transaction_mart) == 1
        assert len(result.loan_mart) == 1
        assert len(result.customer_risk_mart) == 1
        assert len(result.complaint_mart) == 1

        checksums = write_analytical_marts(tmp_path, result)

        assert "marts/mart_transaction_kpis.json" in checksums
        assert "marts/mart_loan_delinquency_kpis.json" in checksums
        assert "marts/mart_customer_risk_kpis.json" in checksums
        assert "marts/mart_complaint_kpis.json" in checksums

        # Verify JSON file structure
        tx_file = tmp_path / "marts/mart_transaction_kpis.json"
        data = json.loads(tx_file.read_text(encoding="utf-8"))
        assert len(data) == 1
        assert data[0]["branch_id"] == "BR01"
        assert data[0]["success_rate_pct"] == "100.00000000"

    def test_unmapped_fallback_dimensions(self):
        """Records with missing branch, channel, or loan type receive deterministic fallback values."""
        start = datetime(2026, 9, 22, 0, 0)
        end = datetime(2026, 9, 23, 0, 0)
        b_date = date(2026, 9, 22)

        # Transaction with no branch, channel, currency
        txs = [{"transaction_id": "T1", "occurred_at": datetime(2026, 9, 22, 10), "transaction_status": "SUCCESSFUL", "amount": "10"}]
        tx_records = MartBuilder.build_transaction_mart(
            transactions=txs,
            period_start=start,
            period_end=end,
            execution_mode=ExecutionMode.FIXTURE,
        )
        assert len(tx_records) == 1
        assert tx_records[0].branch_id == "UNKNOWN_BRANCH"
        assert tx_records[0].channel == "UNKNOWN_CHANNEL"
        assert tx_records[0].currency == "USD"

        # Loan with no branch, type, currency
        positions = [{"loan_id": "L1", "business_date": b_date, "loan_status": "ACTIVE", "days_past_due": 0, "outstanding_principal": "100"}]
        loan_records = MartBuilder.build_loan_delinquency_mart(
            loan_positions=positions,
            business_date=b_date,
            execution_mode=ExecutionMode.FIXTURE,
        )
        assert len(loan_records) == 1
        assert loan_records[0].branch_id == "UNKNOWN_BRANCH"
        assert loan_records[0].loan_type == "UNKNOWN_TYPE"
        assert loan_records[0].currency == "USD"

        # Customer assessment with no branch
        assessments = [{"customer_id": "C1", "business_date": b_date, "classification": RiskClassification.NOT_HIGH_RISK}]
        risk_records = MartBuilder.build_customer_risk_mart(
            assessments=assessments,
            as_of_date=b_date,
            execution_mode=ExecutionMode.FIXTURE,
        )
        assert len(risk_records) == 1
        assert risk_records[0].home_branch_id == "UNKNOWN_BRANCH"

        # Complaint with no branch, channel, priority
        complaints = [{"complaint_id": "C1", "created_at": datetime(2026, 9, 22, 10), "complaint_status": "OPEN"}]
        c_records = MartBuilder.build_complaint_mart(
            complaints=complaints,
            period_start=start,
            period_end=end,
            execution_mode=ExecutionMode.FIXTURE,
        )
        assert len(c_records) == 1
        assert c_records[0].branch_id == "UNKNOWN_BRANCH"
        assert c_records[0].channel == "UNKNOWN_CHANNEL"
        assert c_records[0].priority == "MEDIUM"
