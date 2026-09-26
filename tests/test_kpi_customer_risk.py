"""Acceptance and unit tests for Customer Risk KPIs (K07).

Governed by:
- DD-04 Customer risk catalog and classification hierarchy
- DD-06 Approved KPI and canonical mapping policy
- DD-02 Relationship exposure non-additive attribution
- Sprint 3 Package 3 Increment 3 implementation plan
"""

from datetime import date, datetime
import pytest

from horizon_pipeline.analytics.kpi import CustomerRiskKPIResult, KPIEngine
from horizon_pipeline.analytics.risk_classification import (
    EvidenceState,
    RiskAssessment,
    RiskClassification,
)
from horizon_pipeline.analytics.risk_conditions import ConditionState, RiskConditionResult
from horizon_pipeline.processing.records import ExecutionMode


class TestCustomerRiskKPIs:
    """Test suite for K07 and population segregation."""

    def test_ac_k07_01_provisional_high_risk_aggregation(self):
        """AC-K07-01: Count only PROVISIONAL_HIGH_RISK (t >= 2) in K07."""
        as_of = date(2026, 9, 22)

        assessments = [
            {"customer_id": "C1", "business_date": as_of, "classification": RiskClassification.PROVISIONAL_HIGH_RISK},
            {"customer_id": "C2", "business_date": as_of, "classification": RiskClassification.PROVISIONAL_HIGH_RISK},
            {"customer_id": "C3", "business_date": as_of, "classification": RiskClassification.NOT_HIGH_RISK},
        ]

        result = KPIEngine.calculate_customer_risk_kpis(
            assessments=assessments,
            as_of_date=as_of,
            execution_mode=ExecutionMode.FIXTURE,
        )

        assert result.total_assessed_customers == 3
        assert result.provisional_high_risk_customer_count == 2
        assert result.not_high_risk_customer_count == 1
        assert result.relationship_exposure_non_additive is True

    def test_ac_k07_02_segregation_of_incomplete_evidence_and_unavailable(self):
        """AC-K07-02: INCOMPLETE_EVIDENCE and UNAVAILABLE are segregated as separate unknown populations, NEVER not-high-risk."""
        as_of = date(2026, 9, 22)

        # C1: Incomplete evidence (t=1, u=1)
        # C2: Unavailable assessment (Priority 1)
        # C3: Confirmed Not high risk (t=0, u=0)
        # C4: Provisional high risk (t=2, u=0)
        assessments = [
            {"customer_id": "C1", "business_date": as_of, "classification": RiskClassification.INCOMPLETE_EVIDENCE},
            {"customer_id": "C2", "business_date": as_of, "classification": RiskClassification.UNAVAILABLE},
            {"customer_id": "C3", "business_date": as_of, "classification": RiskClassification.NOT_HIGH_RISK},
            {"customer_id": "C4", "business_date": as_of, "classification": RiskClassification.PROVISIONAL_HIGH_RISK},
        ]

        result = KPIEngine.calculate_customer_risk_kpis(
            assessments=assessments,
            as_of_date=as_of,
            execution_mode=ExecutionMode.FIXTURE,
        )

        assert result.total_assessed_customers == 4
        assert result.provisional_high_risk_customer_count == 1  # C4
        assert result.incomplete_evidence_customer_count == 1     # C1
        assert result.unavailable_assessment_customer_count == 1  # C2
        assert result.not_high_risk_customer_count == 1          # C3 only!
        # C1 and C2 must not be conflated with C3
        assert (
            result.provisional_high_risk_customer_count
            + result.incomplete_evidence_customer_count
            + result.unavailable_assessment_customer_count
            + result.not_high_risk_customer_count
        ) == 4

    def test_rc_condition_counts(self):
        """Test tracking of individual condition triggers (RC-01 through RC-05)."""
        as_of = date(2026, 9, 22)

        c1_conds = (
            RiskConditionResult(condition_id="RC-01", state=ConditionState.TRIGGERED, evidence=("SAR filed",), lineage_references=(), rule_version="1.0.0"),
            RiskConditionResult(condition_id="RC-02", state=ConditionState.TRIGGERED, evidence=("High DPD",), lineage_references=(), rule_version="1.0.0"),
            RiskConditionResult(condition_id="RC-03", state=ConditionState.NOT_TRIGGERED, evidence=(), lineage_references=(), rule_version="1.0.0"),
        )
        c2_conds = (
            RiskConditionResult(condition_id="RC-01", state=ConditionState.TRIGGERED, evidence=("SAR filed",), lineage_references=(), rule_version="1.0.0"),
            RiskConditionResult(condition_id="RC-04", state=ConditionState.TRIGGERED, evidence=("Fraud burst",), lineage_references=(), rule_version="1.0.0"),
        )

        assessments = [
            RiskAssessment(
                assessment_id="A1",
                customer_id="C1",
                business_date=as_of,
                assessment_at=datetime(2026, 9, 22, 10, 0),
                classification=RiskClassification.PROVISIONAL_HIGH_RISK,
                evidence_state=EvidenceState.COMPLETE,
                triggered_count=2,
                unknown_count=0,
                classification_rule_version="1.0.0",
                catalog_version="1.0.0",
                condition_results=c1_conds,
                lineage_references=(),
            ),
            RiskAssessment(
                assessment_id="A2",
                customer_id="C2",
                business_date=as_of,
                assessment_at=datetime(2026, 9, 22, 11, 0),
                classification=RiskClassification.PROVISIONAL_HIGH_RISK,
                evidence_state=EvidenceState.COMPLETE,
                triggered_count=2,
                unknown_count=0,
                classification_rule_version="1.0.0",
                catalog_version="1.0.0",
                condition_results=c2_conds,
                lineage_references=(),
            ),
        ]

        result = KPIEngine.calculate_customer_risk_kpis(
            assessments=assessments,
            as_of_date=as_of,
            execution_mode=ExecutionMode.FIXTURE,
        )

        assert result.provisional_high_risk_customer_count == 2
        assert result.rc01_triggered_count == 2
        assert result.rc02_triggered_count == 1
        assert result.rc03_triggered_count == 0
        assert result.rc04_triggered_count == 1
        assert result.rc05_triggered_count == 0

    def test_as_of_date_filtering(self):
        """Assessments for other dates are excluded."""
        as_of = date(2026, 9, 22)
        assessments = [
            {"customer_id": "C1", "business_date": date(2026, 9, 21), "classification": RiskClassification.PROVISIONAL_HIGH_RISK},
            {"customer_id": "C2", "business_date": as_of, "classification": RiskClassification.PROVISIONAL_HIGH_RISK},
        ]
        result = KPIEngine.calculate_customer_risk_kpis(
            assessments=assessments,
            as_of_date=as_of,
            execution_mode=ExecutionMode.FIXTURE,
        )
        assert result.total_assessed_customers == 1
        assert result.provisional_high_risk_customer_count == 1

    def test_empty_assessments(self):
        """Empty assessment sequence returns zero counts and preserves non-additive flag."""
        as_of = date(2026, 9, 22)
        result = KPIEngine.calculate_customer_risk_kpis(
            assessments=(),
            as_of_date=as_of,
            execution_mode=ExecutionMode.FIXTURE,
        )
        assert result.total_assessed_customers == 0
        assert result.provisional_high_risk_customer_count == 0
        assert result.incomplete_evidence_customer_count == 0
        assert result.unavailable_assessment_customer_count == 0
        assert result.not_high_risk_customer_count == 0
        assert result.relationship_exposure_non_additive is True
