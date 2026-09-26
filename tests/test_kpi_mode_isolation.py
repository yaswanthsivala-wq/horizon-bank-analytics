"""Acceptance and unit tests for ExecutionMode Isolation & Fail-Closed Enforcement.

Governed by:
- Sprint 3 Package 3 Increment 3 implementation plan
- MasterProductionRegistry isolation rules
"""

from datetime import date, datetime
import pytest

from horizon_pipeline.analytics.kpi import KPIEngine
from horizon_pipeline.analytics.marts import AnalyticalMartsBuilder, MartBuilder
from horizon_pipeline.contracts.states import PendingContractError
from horizon_pipeline.processing.records import ExecutionMode


class TestModeIsolation:
    """Test suite for AC-MODE-01: Fail-closed production boundaries."""

    def test_ac_mode_01_kpi_engine_production_fails_closed(self):
        """AC-MODE-01: All KPIEngine methods raise PendingContractError under ExecutionMode.PRODUCTION."""
        start = datetime(2026, 9, 22, 0, 0)
        end = datetime(2026, 9, 23, 0, 0)
        b_date = date(2026, 9, 22)

        with pytest.raises(PendingContractError, match="MasterProductionRegistry"):
            KPIEngine.calculate_transaction_kpis(
                transactions=(),
                period_start=start,
                period_end=end,
                execution_mode=ExecutionMode.PRODUCTION,
            )

        with pytest.raises(PendingContractError, match="MasterProductionRegistry"):
            KPIEngine.calculate_loan_kpis(
                loan_positions=(),
                business_date=b_date,
                execution_mode=ExecutionMode.PRODUCTION,
            )

        with pytest.raises(PendingContractError, match="MasterProductionRegistry"):
            KPIEngine.calculate_customer_risk_kpis(
                assessments=(),
                as_of_date=b_date,
                execution_mode=ExecutionMode.PRODUCTION,
            )

        with pytest.raises(PendingContractError, match="MasterProductionRegistry"):
            KPIEngine.calculate_complaint_kpis(
                complaints=(),
                period_start=start,
                period_end=end,
                as_of_time=end,
                execution_mode=ExecutionMode.PRODUCTION,
            )

    def test_ac_mode_01_mart_builders_production_fail_closed(self):
        """AC-MODE-01: All MartBuilder methods raise PendingContractError under ExecutionMode.PRODUCTION."""
        start = datetime(2026, 9, 22, 0, 0)
        end = datetime(2026, 9, 23, 0, 0)
        b_date = date(2026, 9, 22)

        with pytest.raises(PendingContractError, match="MasterProductionRegistry"):
            MartBuilder.build_transaction_mart(
                transactions=(),
                period_start=start,
                period_end=end,
                execution_mode=ExecutionMode.PRODUCTION,
            )

        with pytest.raises(PendingContractError, match="MasterProductionRegistry"):
            MartBuilder.build_loan_delinquency_mart(
                loan_positions=(),
                business_date=b_date,
                execution_mode=ExecutionMode.PRODUCTION,
            )

        with pytest.raises(PendingContractError, match="MasterProductionRegistry"):
            MartBuilder.build_customer_risk_mart(
                assessments=(),
                as_of_date=b_date,
                execution_mode=ExecutionMode.PRODUCTION,
            )

        with pytest.raises(PendingContractError, match="MasterProductionRegistry"):
            MartBuilder.build_complaint_mart(
                complaints=(),
                period_start=start,
                period_end=end,
                execution_mode=ExecutionMode.PRODUCTION,
            )

        with pytest.raises(PendingContractError, match="MasterProductionRegistry"):
            AnalyticalMartsBuilder.build_all(
                period_start=start,
                period_end=end,
                business_date=b_date,
                execution_mode=ExecutionMode.PRODUCTION,
            )

    def test_invalid_execution_mode_type_raises_type_error(self):
        """Passing a string or invalid type for execution_mode raises TypeError."""
        start = datetime(2026, 9, 22, 0, 0)
        end = datetime(2026, 9, 23, 0, 0)

        with pytest.raises(TypeError, match="ExecutionMode enum member"):
            KPIEngine.calculate_transaction_kpis(
                transactions=(),
                period_start=start,
                period_end=end,
                execution_mode="FIXTURE",  # String instead of Enum member!
            )
