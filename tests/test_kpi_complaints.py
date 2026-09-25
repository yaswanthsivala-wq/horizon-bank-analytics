"""Acceptance and unit tests for Complaint KPIs (K08-K10).

Governed by:
- DD-06 Approved KPI and canonical mapping policy
- Sprint 3 Package 3 Increment 3 implementation plan
"""

from datetime import datetime, timedelta
from decimal import Decimal
import pytest

from horizon_pipeline.analytics.kpi import ComplaintKPIResult, KPIEngine
from horizon_pipeline.processing.records import ExecutionMode


class TestComplaintKPIs:
    """Test suite for K08 (Avg Resolution Time), K09 (Open Complaints), and K10 (SLA Breach Rate)."""

    def test_ac_k08_01_complaint_resolution_time_continuous_calendar_clock(self):
        """AC-K08-01: Average resolution time in elapsed continuous 24/7 calendar hours."""
        period_start = datetime(2026, 9, 22, 0, 0, 0)
        period_end = datetime(2026, 9, 23, 0, 0, 0)
        as_of = datetime(2026, 9, 23, 0, 0, 0)

        # C1: created 2026-09-20 10:00, closed 2026-09-22 10:00 (48.0 hours)
        # C2: created 2026-09-22 00:00, closed 2026-09-22 12:00 (12.0 hours)
        # Average = (48 + 12) / 2 = 30.0000 hours
        complaints = [
            {
                "complaint_id": "C1",
                "created_at": datetime(2026, 9, 20, 10, 0, 0),
                "final_closed_at": datetime(2026, 9, 22, 10, 0, 0),
                "complaint_status": "CLOSED",
                "priority": "MEDIUM",
            },
            {
                "complaint_id": "C2",
                "created_at": datetime(2026, 9, 22, 0, 0, 0),
                "final_closed_at": datetime(2026, 9, 22, 12, 0, 0),
                "complaint_status": "CLOSED",
                "priority": "HIGH",
            },
        ]

        result = KPIEngine.calculate_complaint_kpis(
            complaints=complaints,
            period_start=period_start,
            period_end=period_end,
            as_of_time=as_of,
            execution_mode=ExecutionMode.FIXTURE,
        )

        assert result.closed_complaint_count == 2
        assert result.total_resolution_hours == Decimal("60.0000")
        assert result.avg_resolution_hours == Decimal("30.0000")

    def test_ac_k09_01_open_complaints_count_including_reopened(self):
        """AC-K09-01: Count complaints without current closure at as-of time, including REOPENED."""
        as_of = datetime(2026, 9, 22, 12, 0, 0)
        period_start = datetime(2026, 9, 22, 0, 0, 0)
        period_end = datetime(2026, 9, 23, 0, 0, 0)

        complaints = [
            # Open complaint:
            {"complaint_id": "C1", "created_at": datetime(2026, 9, 22, 8, 0), "complaint_status": "OPEN", "priority": "MEDIUM"},
            # Reopened complaint:
            {"complaint_id": "C2", "created_at": datetime(2026, 9, 20, 8, 0), "complaint_status": "REOPENED", "priority": "HIGH"},
            # Closed complaint:
            {"complaint_id": "C3", "created_at": datetime(2026, 9, 21, 8, 0), "final_closed_at": datetime(2026, 9, 22, 10, 0), "complaint_status": "CLOSED", "priority": "LOW"},
            # Future complaint (after as_of):
            {"complaint_id": "C4", "created_at": datetime(2026, 9, 22, 14, 0), "complaint_status": "OPEN", "priority": "LOW"},
        ]

        result = KPIEngine.calculate_complaint_kpis(
            complaints=complaints,
            period_start=period_start,
            period_end=period_end,
            as_of_time=as_of,
            execution_mode=ExecutionMode.FIXTURE,
        )

        # Open count at as_of: C1 (OPEN) and C2 (REOPENED) = 2. C3 is CLOSED, C4 is after as_of.
        assert result.open_complaint_count == 2
        assert result.reopened_complaint_count == 1

    def test_ac_k10_01_continuous_clock_and_strict_greater_than_breach(self):
        """AC-K10-01: SLA breach requires elapsed_hours > threshold (24.0000h is NOT breached; 24.0001h is breached)."""
        as_of = datetime(2026, 9, 22, 12, 0, 0)
        period_start = datetime(2026, 9, 22, 0, 0, 0)
        period_end = datetime(2026, 9, 23, 0, 0, 0)

        # HIGH priority SLA = 24.0 hours
        # C_exact: created exactly 24 hours prior (elapsed = 24.0000h) => Not breached
        # C_breached: created 24 hours and 1 second prior (elapsed = 24.000277...h) => Breached
        c_exact = {
            "complaint_id": "C_EXACT",
            "created_at": as_of - timedelta(hours=24),
            "complaint_status": "OPEN",
            "priority": "HIGH",
        }
        c_breached = {
            "complaint_id": "C_BREACHED",
            "created_at": as_of - timedelta(hours=24, seconds=1),
            "complaint_status": "OPEN",
            "priority": "HIGH",
        }

        result = KPIEngine.calculate_complaint_kpis(
            complaints=[c_exact, c_breached],
            period_start=period_start,
            period_end=period_end,
            as_of_time=as_of,
            execution_mode=ExecutionMode.FIXTURE,
        )

        assert result.sla_eligible_complaint_count == 2
        assert result.sla_breached_complaint_count == 1  # Only C_BREACHED
        assert result.sla_breach_rate_pct == Decimal("50.00000000")

    def test_ac_k10_02_reopened_complaint_continuity(self):
        """AC-K10-02: Reopened complaints measure elapsed time continuously from original created_at without reset."""
        as_of = datetime(2026, 9, 22, 12, 0, 0)
        period_start = datetime(2026, 9, 22, 0, 0, 0)
        period_end = datetime(2026, 9, 23, 0, 0, 0)

        # Reopened complaint with priority HIGH (24h SLA).
        # Original created_at was 30 hours ago.
        # It was closed after 10 hours and recently reopened.
        # Continuous elapsed hours = 30 hours > 24 hours SLA => Breached!
        c_reopened = {
            "complaint_id": "C_REOPENED",
            "created_at": as_of - timedelta(hours=30),
            "final_closed_at": as_of - timedelta(hours=20),
            "complaint_status": "REOPENED",
            "priority": "HIGH",
        }

        result = KPIEngine.calculate_complaint_kpis(
            complaints=[c_reopened],
            period_start=period_start,
            period_end=period_end,
            as_of_time=as_of,
            execution_mode=ExecutionMode.FIXTURE,
        )

        assert result.sla_eligible_complaint_count == 1
        assert result.sla_breached_complaint_count == 1
        assert result.sla_breach_rate_pct == Decimal("100.00000000")

    def test_quarantine_contradictory_timestamps(self):
        """Complaints with final_closed_at < created_at are quarantined and excluded."""
        as_of = datetime(2026, 9, 22, 12, 0, 0)
        period_start = datetime(2026, 9, 22, 0, 0, 0)
        period_end = datetime(2026, 9, 23, 0, 0, 0)

        c_bad = {
            "complaint_id": "C_BAD",
            "created_at": datetime(2026, 9, 22, 10, 0),
            "final_closed_at": datetime(2026, 9, 22, 8, 0),  # Prior to created_at!
            "complaint_status": "CLOSED",
            "priority": "MEDIUM",
        }

        result = KPIEngine.calculate_complaint_kpis(
            complaints=[c_bad],
            period_start=period_start,
            period_end=period_end,
            as_of_time=as_of,
            execution_mode=ExecutionMode.FIXTURE,
        )

        assert result.closed_complaint_count == 0
        assert result.sla_eligible_complaint_count == 0

    def test_priority_sla_thresholds_boundaries(self):
        """Test strict > breach for CRITICAL (4h), MEDIUM (72h), and LOW (120h)."""
        as_of = datetime(2026, 9, 22, 12, 0, 0)
        period_start = datetime(2026, 9, 22, 0, 0, 0)
        period_end = datetime(2026, 9, 23, 0, 0, 0)

        # Critical: 4h SLA
        c_crit_exact = {"complaint_id": "C_CRIT_1", "created_at": as_of - timedelta(hours=4), "complaint_status": "OPEN", "priority": "CRITICAL"}
        c_crit_breach = {"complaint_id": "C_CRIT_2", "created_at": as_of - timedelta(hours=4, seconds=1), "complaint_status": "OPEN", "priority": "CRITICAL"}

        # Medium: 72h SLA
        c_med_exact = {"complaint_id": "C_MED_1", "created_at": as_of - timedelta(hours=72), "complaint_status": "OPEN", "priority": "MEDIUM"}
        c_med_breach = {"complaint_id": "C_MED_2", "created_at": as_of - timedelta(hours=72, seconds=1), "complaint_status": "OPEN", "priority": "MEDIUM"}

        # Low: 120h SLA
        c_low_exact = {"complaint_id": "C_LOW_1", "created_at": as_of - timedelta(hours=120), "complaint_status": "OPEN", "priority": "LOW"}
        c_low_breach = {"complaint_id": "C_LOW_2", "created_at": as_of - timedelta(hours=120, seconds=1), "complaint_status": "OPEN", "priority": "LOW"}

        result = KPIEngine.calculate_complaint_kpis(
            complaints=[c_crit_exact, c_crit_breach, c_med_exact, c_med_breach, c_low_exact, c_low_breach],
            period_start=period_start,
            period_end=period_end,
            as_of_time=as_of,
            execution_mode=ExecutionMode.FIXTURE,
        )

        assert result.sla_eligible_complaint_count == 6
        assert result.sla_breached_complaint_count == 3  # The 3 breached ones
        assert result.sla_breach_rate_pct == Decimal("50.00000000")

    def test_zero_closed_complaints_returns_none(self):
        """When closed complaint count is 0, avg_resolution_hours is None."""
        as_of = datetime(2026, 9, 22, 12, 0, 0)
        period_start = datetime(2026, 9, 22, 0, 0, 0)
        period_end = datetime(2026, 9, 23, 0, 0, 0)

        result = KPIEngine.calculate_complaint_kpis(
            complaints=[],
            period_start=period_start,
            period_end=period_end,
            as_of_time=as_of,
            execution_mode=ExecutionMode.FIXTURE,
        )
        assert result.closed_complaint_count == 0
        assert result.avg_resolution_hours is None
        assert result.total_resolution_hours == Decimal("0.0000")

    def test_curated_complaint_dataclass_input(self):
        """CuratedComplaint dataclass instances are processed correctly."""
        from horizon_pipeline.processing.records import CuratedComplaint

        as_of = datetime(2026, 9, 22, 12, 0, 0)
        period_start = datetime(2026, 9, 22, 0, 0, 0)
        period_end = datetime(2026, 9, 23, 0, 0, 0)

        c = CuratedComplaint(
            complaint_id="C100",
            customer_id="CUST1",
            channel="ONLINE",
            priority="CRITICAL",
            complaint_status="OPEN",
            branch_id="BR01",
            created_at=as_of - timedelta(hours=5),
        )

        result = KPIEngine.calculate_complaint_kpis(
            complaints=[c],
            period_start=period_start,
            period_end=period_end,
            as_of_time=as_of,
            execution_mode=ExecutionMode.FIXTURE,
        )

        assert result.open_complaint_count == 1
        assert result.sla_eligible_complaint_count == 1
        assert result.sla_breached_complaint_count == 1
        assert result.sla_breach_rate_pct == Decimal("100.00000000")
