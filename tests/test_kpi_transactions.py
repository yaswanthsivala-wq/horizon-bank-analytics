"""Acceptance and unit tests for Transaction KPIs (K01-K04).

Governed by:
- DD-06 Approved KPI and canonical mapping policy
- Sprint 3 Package 3 Increment 3 implementation plan
"""

from datetime import datetime, timezone
from decimal import Decimal
import pytest

from horizon_pipeline.analytics.kpi import KPIEngine, TransactionKPIResult
from horizon_pipeline.processing.records import ExecutionMode


class TestTransactionKPIs:
    """Test suite for K01 through K04."""

    def test_ac_k01_01_terminal_volume_and_pending_exclusion(self):
        """AC-K01-01: Count terminal statuses, strictly exclude PENDING, respect half-open [start, end)."""
        period_start = datetime(2026, 9, 22, 0, 0, 0)
        period_end = datetime(2026, 9, 23, 0, 0, 0)

        txs = [
            {"transaction_id": "T1", "occurred_at": datetime(2026, 9, 22, 10, 0), "transaction_status": "SUCCESSFUL", "amount": "100.0000", "currency": "USD"},
            {"transaction_id": "T2", "occurred_at": datetime(2026, 9, 22, 11, 0), "transaction_status": "POSTED", "amount": "50.0000", "currency": "USD"},
            {"transaction_id": "T3", "occurred_at": datetime(2026, 9, 22, 12, 0), "transaction_status": "FAILED", "amount": "25.0000", "currency": "USD"},
            {"transaction_id": "T4", "occurred_at": datetime(2026, 9, 22, 13, 0), "transaction_status": "DECLINED", "amount": "10.0000", "currency": "USD"},
            {"transaction_id": "T5", "occurred_at": datetime(2026, 9, 22, 14, 0), "transaction_status": "CANCELLED", "amount": "5.0000", "currency": "USD"},
            {"transaction_id": "T6", "occurred_at": datetime(2026, 9, 22, 15, 0), "transaction_status": "VOIDED", "amount": "15.0000", "currency": "USD"},
            {"transaction_id": "T7", "occurred_at": datetime(2026, 9, 22, 16, 0), "transaction_status": "REVERSED", "amount": "20.0000", "currency": "USD"},
            {"transaction_id": "T8", "occurred_at": datetime(2026, 9, 22, 17, 0), "transaction_status": "PENDING", "amount": "30.0000", "currency": "USD"},
            # Boundary tests: exactly start is included, exactly end is excluded
            {"transaction_id": "T9", "occurred_at": datetime(2026, 9, 22, 0, 0, 0), "transaction_status": "SUCCESSFUL", "amount": "1.0000", "currency": "USD"},
            {"transaction_id": "T10", "occurred_at": datetime(2026, 9, 23, 0, 0, 0), "transaction_status": "SUCCESSFUL", "amount": "1.0000", "currency": "USD"},
        ]

        result = KPIEngine.calculate_transaction_kpis(
            transactions=txs,
            period_start=period_start,
            period_end=period_end,
            currency="USD",
            execution_mode=ExecutionMode.FIXTURE,
        )

        # Terminal count excludes PENDING (T8) and T10 (at period_end)
        # Included: T1, T2, T3, T4, T5, T6, T7, T9 = 8 transactions
        assert result.total_volume == 8
        assert result.pending_count == 1
        assert result.successful_count == 2
        assert result.posted_count == 1
        assert result.failed_count == 1
        assert result.declined_count == 1
        assert result.cancelled_count == 1
        assert result.voided_count == 1
        assert result.reversed_count == 1

        # Denominator for K02/K03/K04 = SUCCESSFUL(2) + POSTED(1) + FAILED(1) + DECLINED(1) = 5
        assert result.rate_eligible_count == 5

    def test_ac_k02_01_and_k03_01_success_and_failure_rates(self):
        """AC-K02-01 & AC-K03-01: Success & failure rates sum to 100%, zero-denominator returns None."""
        period_start = datetime(2026, 9, 22, 0, 0, 0)
        period_end = datetime(2026, 9, 23, 0, 0, 0)

        # 3 successful, 1 posted, 1 failed, 1 declined => eligible = 6
        # Success = 4 / 6 = 66.66666667%, Failure = 2 / 6 = 33.33333333%
        txs = [
            {"transaction_id": "T1", "occurred_at": datetime(2026, 9, 22, 1), "transaction_status": "SUCCESSFUL", "amount": "10", "currency": "USD"},
            {"transaction_id": "T2", "occurred_at": datetime(2026, 9, 22, 2), "transaction_status": "SUCCESSFUL", "amount": "10", "currency": "USD"},
            {"transaction_id": "T3", "occurred_at": datetime(2026, 9, 22, 3), "transaction_status": "SUCCESSFUL", "amount": "10", "currency": "USD"},
            {"transaction_id": "T4", "occurred_at": datetime(2026, 9, 22, 4), "transaction_status": "POSTED", "amount": "10", "currency": "USD"},
            {"transaction_id": "T5", "occurred_at": datetime(2026, 9, 22, 5), "transaction_status": "FAILED", "amount": "10", "currency": "USD"},
            {"transaction_id": "T6", "occurred_at": datetime(2026, 9, 22, 6), "transaction_status": "DECLINED", "amount": "10", "currency": "USD"},
            {"transaction_id": "T7", "occurred_at": datetime(2026, 9, 22, 7), "transaction_status": "CANCELLED", "amount": "10", "currency": "USD"},
        ]

        result = KPIEngine.calculate_transaction_kpis(
            transactions=txs,
            period_start=period_start,
            period_end=period_end,
            currency="USD",
            execution_mode=ExecutionMode.FIXTURE,
        )

        assert result.rate_eligible_count == 6
        assert result.success_rate_pct == Decimal("66.66666667")
        assert result.failure_rate_pct == Decimal("33.33333333")
        assert (result.success_rate_pct + result.failure_rate_pct) == Decimal("100.00000000")

        # Zero denominator case: only CANCELLED and VOIDED
        non_rate_txs = [
            {"transaction_id": "T8", "occurred_at": datetime(2026, 9, 22, 8), "transaction_status": "CANCELLED", "amount": "10", "currency": "USD"},
            {"transaction_id": "T9", "occurred_at": datetime(2026, 9, 22, 9), "transaction_status": "VOIDED", "amount": "10", "currency": "USD"},
        ]
        result_empty = KPIEngine.calculate_transaction_kpis(
            transactions=non_rate_txs,
            period_start=period_start,
            period_end=period_end,
            currency="USD",
            execution_mode=ExecutionMode.FIXTURE,
        )
        assert result_empty.total_volume == 2
        assert result_empty.rate_eligible_count == 0
        assert result_empty.success_rate_pct is None
        assert result_empty.failure_rate_pct is None
        assert result_empty.fraud_alert_rate_pct is None

    def test_ac_k04_01_fraud_alert_deduplication(self):
        """AC-K04-01: Multiple alerts on one eligible transaction count as 1 in numerator."""
        period_start = datetime(2026, 9, 22, 0, 0, 0)
        period_end = datetime(2026, 9, 23, 0, 0, 0)

        txs = [
            {"transaction_id": "TX1", "occurred_at": datetime(2026, 9, 22, 10), "transaction_status": "SUCCESSFUL", "amount": "100", "currency": "USD"},
            {"transaction_id": "TX2", "occurred_at": datetime(2026, 9, 22, 11), "transaction_status": "POSTED", "amount": "100", "currency": "USD"},
        ]
        alerts = [
            {"alert_id": "A1", "transaction_id": "TX1"},
            {"alert_id": "A2", "transaction_id": "TX1"},
            {"alert_id": "A3", "transaction_id": "TX1"},
        ]

        result = KPIEngine.calculate_transaction_kpis(
            transactions=txs,
            fraud_alerts=alerts,
            period_start=period_start,
            period_end=period_end,
            currency="USD",
            execution_mode=ExecutionMode.FIXTURE,
        )

        assert result.rate_eligible_count == 2
        assert result.eligible_fraud_alert_tx_count == 1
        assert result.fraud_alert_rate_pct == Decimal("50.00000000")

    def test_ac_k04_02_k04_eligible_status_filter_and_denominator_consistency(self):
        """AC-K04-02: Non-eligible statuses (CANCELLED, VOIDED, REVERSED, PENDING) with alerts excluded from numerator and denominator."""
        period_start = datetime(2026, 9, 22, 0, 0, 0)
        period_end = datetime(2026, 9, 23, 0, 0, 0)

        txs = [
            {"transaction_id": "TX1", "occurred_at": datetime(2026, 9, 22, 10), "transaction_status": "SUCCESSFUL", "amount": "100", "currency": "USD"},
            {"transaction_id": "TX2", "occurred_at": datetime(2026, 9, 22, 11), "transaction_status": "CANCELLED", "amount": "100", "currency": "USD"},
            {"transaction_id": "TX3", "occurred_at": datetime(2026, 9, 22, 12), "transaction_status": "POSTED", "amount": "100", "currency": "USD"},
        ]
        alerts = [
            {"alert_id": "A1", "transaction_id": "TX1"},
            {"alert_id": "A2", "transaction_id": "TX2"},  # Linked to CANCELLED tx!
        ]

        result = KPIEngine.calculate_transaction_kpis(
            transactions=txs,
            fraud_alerts=alerts,
            period_start=period_start,
            period_end=period_end,
            currency="USD",
            execution_mode=ExecutionMode.FIXTURE,
        )

        # Denominator: TX1 (SUCCESSFUL) and TX3 (POSTED) = 2
        # TX2 (CANCELLED) is excluded from denominator AND from numerator
        assert result.rate_eligible_count == 2
        assert result.eligible_fraud_alert_tx_count == 1
        assert result.fraud_alert_rate_pct == Decimal("50.00000000")

    def test_currency_filtering(self):
        """Transactions in EUR are ignored when computing USD KPIs."""
        period_start = datetime(2026, 9, 22, 0, 0, 0)
        period_end = datetime(2026, 9, 23, 0, 0, 0)

        txs = [
            {"transaction_id": "T1", "occurred_at": datetime(2026, 9, 22, 10), "transaction_status": "SUCCESSFUL", "amount": "100", "currency": "USD"},
            {"transaction_id": "T2", "occurred_at": datetime(2026, 9, 22, 11), "transaction_status": "SUCCESSFUL", "amount": "200", "currency": "EUR"},
        ]

        result = KPIEngine.calculate_transaction_kpis(
            transactions=txs,
            period_start=period_start,
            period_end=period_end,
            currency="USD",
            execution_mode=ExecutionMode.FIXTURE,
        )

        assert result.total_volume == 1
        assert result.total_amount == Decimal("100.0000")
        assert result.currency == "USD"

    def test_unlinked_fraud_alerts(self):
        """Unlinked fraud alerts (unknown transaction ID) cannot enter the numerator."""
        period_start = datetime(2026, 9, 22, 0, 0, 0)
        period_end = datetime(2026, 9, 23, 0, 0, 0)

        txs = [
            {"transaction_id": "T1", "occurred_at": datetime(2026, 9, 22, 10), "transaction_status": "SUCCESSFUL", "amount": "100", "currency": "USD"},
        ]
        alerts = [
            {"alert_id": "A_UNLINKED", "transaction_id": "T_NONEXISTENT"},
        ]

        result = KPIEngine.calculate_transaction_kpis(
            transactions=txs,
            fraud_alerts=alerts,
            period_start=period_start,
            period_end=period_end,
            currency="USD",
            execution_mode=ExecutionMode.FIXTURE,
        )

        assert result.rate_eligible_count == 1
        assert result.eligible_fraud_alert_tx_count == 0
        assert result.fraud_alert_rate_pct == Decimal("0.00000000")

    def test_curated_transaction_dataclass_input(self):
        """CuratedTransaction dataclass instances are processed correctly."""
        from horizon_pipeline.processing.records import CuratedTransaction
        from datetime import date

        period_start = datetime(2026, 9, 22, 0, 0, 0)
        period_end = datetime(2026, 9, 23, 0, 0, 0)

        tx = CuratedTransaction(
            transaction_id="TX_OBJ",
            account_id="ACC1",
            account_id_masked="***1",
            business_date=date(2026, 9, 22),
            amount=Decimal("150.5000"),
            currency="USD",
            transaction_type="DEPOSIT",
            transaction_status="SUCCESSFUL",
            raw_transaction_status="SUCCESSFUL",
            posted_at=datetime(2026, 9, 22, 14, 30),
        )

        result = KPIEngine.calculate_transaction_kpis(
            transactions=[tx],
            period_start=period_start,
            period_end=period_end,
            currency="USD",
            execution_mode=ExecutionMode.FIXTURE,
        )

        assert result.total_volume == 1
        assert result.successful_count == 1
        assert result.total_amount == Decimal("150.5000")
        assert result.success_rate_pct == Decimal("100.00000000")
