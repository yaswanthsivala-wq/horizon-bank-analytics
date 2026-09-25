"""Deterministic computation of approved core banking KPIs (K01 through K10).

Governed by:
- DD-06 Approved KPI and canonical mapping policy
- Sprint 2 KPI-to-data mappings
- DD-04 Customer risk catalog and classification hierarchy
- DD-09 Data quality and reconciliation policy (gating rules)
- DD-02 Relationship exposure non-additive attribution

This module executes in pure offline mode. In ExecutionMode.PRODUCTION, it fails
closed with PendingContractError because production contracts remain pending confirmation.
In ExecutionMode.FIXTURE, it executes with exact scale-4 Decimal currency arithmetic
and scale-8 ratio precision.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from enum import Enum
from typing import Any, Mapping, Sequence

from ..contracts.states import PendingContractError
from ..processing.records import ExecutionMode
from .risk_classification import (
    EvidenceState,
    RiskAssessment,
    RiskClassification,
)

SCALE_4 = Decimal("0.0001")
SCALE_8 = Decimal("0.00000001")
ONE_HUNDRED = Decimal("100")


class KPIPublicationStatus(str, Enum):
    """Publication disposition for a calculated KPI metric."""

    PUBLISHED = "PUBLISHED"
    BLOCKED_CANDIDATE = "BLOCKED_CANDIDATE"
    UNAVAILABLE = "UNAVAILABLE"


# =====================================================================
# Result Data Structures
# =====================================================================

@dataclass(frozen=True)
class TransactionKPIResult:
    """Calculated transaction KPIs (K01-K04) for an aggregation period."""

    period_start: datetime
    period_end: datetime
    total_volume: int  # K01: Terminal processed count
    successful_count: int
    posted_count: int
    failed_count: int
    declined_count: int
    cancelled_count: int
    voided_count: int
    reversed_count: int
    pending_count: int  # Excluded from terminal volume
    rate_eligible_count: int  # Denominator for K02, K03, K04
    success_rate_pct: Decimal | None  # K02: (SUCCESSFUL + POSTED) / Denom * 100
    failure_rate_pct: Decimal | None  # K03: (FAILED + DECLINED) / Denom * 100
    eligible_fraud_alert_tx_count: int  # K04 Numerator: Distinct eligible tx with >=1 alert
    fraud_alert_rate_pct: Decimal | None  # K04: Fraud Tx / Denom * 100
    total_amount: Decimal
    currency: str


@dataclass(frozen=True)
class LoanKPIResult:
    """Calculated loan delinquency KPIs (K05-K06) for a business date."""

    business_date: date
    active_loan_count: int  # K05 Denominator
    delinquent_active_loan_count: int  # K05 Numerator: DPD > 30 and Active
    delinquency_rate_pct: Decimal | None  # K05: Delinquent Active / Active * 100
    total_loans_evaluated: int
    delinquent_loan_count_all_statuses: int  # DPD > 30 all statuses
    delinquent_outstanding_principal_by_currency: Mapping[str, Decimal | None]  # K06
    k06_publication_status: Mapping[str, KPIPublicationStatus]
    k06_blocked_reasons: Mapping[str, tuple[str, ...]]
    quarantined_negative_principal_count: int
    missing_principal_count: int


@dataclass(frozen=True)
class CustomerRiskKPIResult:
    """Calculated customer risk KPIs (K07) for an as-of date."""

    as_of_date: date
    total_assessed_customers: int
    provisional_high_risk_customer_count: int  # K07: t >= 2
    incomplete_evidence_customer_count: int  # t < 2, t + u >= 2 (separate unknown population)
    unavailable_assessment_customer_count: int  # Priority 1 missing version/evidence
    not_high_risk_customer_count: int  # t < 2, t + u < 2 (confirmed not-high-risk)
    rc01_triggered_count: int
    rc02_triggered_count: int
    rc03_triggered_count: int
    rc04_triggered_count: int
    rc05_triggered_count: int
    relationship_exposure_non_additive: bool = True  # DD-02 mandatory rule


@dataclass(frozen=True)
class ComplaintKPIResult:
    """Calculated complaint KPIs (K08-K10) for a reporting cohort."""

    period_start: datetime
    period_end: datetime
    as_of_time: datetime
    closed_complaint_count: int
    total_resolution_hours: Decimal
    avg_resolution_hours: Decimal | None  # K08: Mean resolution hours for finally closed
    open_complaint_count: int  # K09: Open/non-closed at as-of time
    reopened_complaint_count: int
    sla_eligible_complaint_count: int  # K10 Denominator
    sla_breached_complaint_count: int  # K10 Numerator: elapsed > SLA
    sla_breach_rate_pct: Decimal | None  # K10: Breached / Eligible * 100


# =====================================================================
# Engine Implementation
# =====================================================================

class KPIEngine:
    """Deterministic calculation engine for core banking KPIs (K01-K10)."""

    # DD-06 canonical transaction sets
    TERMINAL_STATUSES = frozenset({
        "SUCCESSFUL", "POSTED", "FAILED", "DECLINED",
        "CANCELLED", "VOIDED", "REVERSED",
    })
    RATE_ELIGIBLE_STATUSES = frozenset({"SUCCESSFUL", "POSTED", "FAILED", "DECLINED"})
    SUCCESS_STATUSES = frozenset({"SUCCESSFUL", "POSTED"})
    FAILURE_STATUSES = frozenset({"FAILED", "DECLINED"})

    # DD-06 canonical loan sets
    ACTIVE_LOAN_STATUSES = frozenset({"ACTIVE", "DELINQUENT_ACTIVE", "FORBEARANCE_ACTIVE"})

    # DD-06 complaint priority SLAs in elapsed calendar hours
    SLA_HOURS_BY_PRIORITY: Mapping[str, Decimal] = {
        "CRITICAL": Decimal("4"),
        "HIGH": Decimal("24"),
        "MEDIUM": Decimal("72"),
        "LOW": Decimal("120"),
    }

    @staticmethod
    def _require_execution_mode(execution_mode: object) -> ExecutionMode:
        if type(execution_mode) is not ExecutionMode:
            raise TypeError("execution_mode must be an ExecutionMode enum member")
        if execution_mode is ExecutionMode.PRODUCTION:
            raise PendingContractError(
                "MasterProductionRegistry contracts remain pending confirmation; "
                "production KPI computation is fail-closed."
            )
        return execution_mode

    @staticmethod
    def _to_decimal(val: Any) -> Decimal:
        if isinstance(val, Decimal):
            return val
        if val is None or val == "":
            raise InvalidOperation("Value is None or empty")
        return Decimal(str(val))

    @classmethod
    def calculate_transaction_kpis(
        cls,
        *,
        transactions: Sequence[Any],
        fraud_alerts: Sequence[Any] = (),
        period_start: datetime,
        period_end: datetime,
        currency: str = "USD",
        execution_mode: ExecutionMode = ExecutionMode.FIXTURE,
    ) -> TransactionKPIResult:
        """Calculate K01 through K04 for transactions occurring within [period_start, period_end).

        Eligible denominator for K02, K03, and K04:
        SUCCESSFUL, POSTED, FAILED, DECLINED.

        K04 counts distinct transactions with >= 1 linked fraud alert IF AND ONLY IF
        the transaction belongs to the same eligible 4-status population.
        """
        cls._require_execution_mode(execution_mode)

        # Build lookup of transaction IDs with linked fraud alerts
        alert_tx_ids: set[str] = set()
        for alert in fraud_alerts:
            tx_id = (
                getattr(alert, "transaction_id", None)
                or getattr(alert, "linked_transaction_id", None)
                or (alert.get("transaction_id") or alert.get("linked_transaction_id") if isinstance(alert, dict) else None)
            )
            if tx_id:
                alert_tx_ids.add(str(tx_id))

        counts = {
            "SUCCESSFUL": 0, "POSTED": 0, "FAILED": 0, "DECLINED": 0,
            "CANCELLED": 0, "VOIDED": 0, "REVERSED": 0, "PENDING": 0,
        }
        total_volume = 0
        total_amount = Decimal("0.0000")
        eligible_fraud_tx: set[str] = set()

        for tx in transactions:
            tx_id = getattr(tx, "transaction_id", None) or (
                tx.get("transaction_id") if isinstance(tx, dict) else None
            )
            raw_dt = getattr(tx, "occurred_at", None) or getattr(tx, "posted_at", None) or (
                tx.get("occurred_at") or tx.get("posted_at") if isinstance(tx, dict) else None
            )
            tx_curr = getattr(tx, "currency", None) or (
                tx.get("currency") if isinstance(tx, dict) else None
            )
            status = getattr(tx, "transaction_status", None) or (
                tx.get("transaction_status") if isinstance(tx, dict) else None
            )
            amt_val = getattr(tx, "amount", None) or (
                tx.get("amount") if isinstance(tx, dict) else None
            )

            # Currency matching
            if tx_curr != currency:
                continue

            # Temporal filtering: half-open [period_start, period_end)
            if raw_dt is None:
                continue
            if isinstance(raw_dt, str):
                try:
                    dt = datetime.fromisoformat(raw_dt)
                except ValueError:
                    continue
            elif isinstance(raw_dt, date) and not isinstance(raw_dt, datetime):
                dt = datetime.combine(raw_dt, datetime.min.time())
            else:
                dt = raw_dt
            # Normalize naive/aware comparisons if needed
            if dt.tzinfo is not None and period_start.tzinfo is None:
                dt = dt.replace(tzinfo=None)
            elif dt.tzinfo is None and period_start.tzinfo is not None:
                dt = dt.replace(tzinfo=period_start.tzinfo)

            if not (period_start <= dt < period_end):
                continue

            status_str = str(status).upper() if status else ""

            if status_str == "PENDING":
                counts["PENDING"] += 1
                continue

            if status_str in cls.TERMINAL_STATUSES:
                total_volume += 1
                counts[status_str] = counts.get(status_str, 0) + 1
                try:
                    total_amount += cls._to_decimal(amt_val)
                except (InvalidOperation, TypeError):
                    pass

                # Check K04 alert link: ONLY if status is in the 4-status eligible set!
                if status_str in cls.RATE_ELIGIBLE_STATUSES:
                    if tx_id and str(tx_id) in alert_tx_ids:
                        eligible_fraud_tx.add(str(tx_id))

        rate_eligible_count = (
            counts["SUCCESSFUL"] + counts["POSTED"] + counts["FAILED"] + counts["DECLINED"]
        )

        if rate_eligible_count > 0:
            denom_dec = Decimal(rate_eligible_count)
            success_num = Decimal(counts["SUCCESSFUL"] + counts["POSTED"])
            failure_num = Decimal(counts["FAILED"] + counts["DECLINED"])
            fraud_num = Decimal(len(eligible_fraud_tx))

            success_rate = ((success_num / denom_dec) * ONE_HUNDRED).quantize(
                SCALE_8, rounding=ROUND_HALF_UP
            )
            failure_rate = ((failure_num / denom_dec) * ONE_HUNDRED).quantize(
                SCALE_8, rounding=ROUND_HALF_UP
            )
            fraud_rate = ((fraud_num / denom_dec) * ONE_HUNDRED).quantize(
                SCALE_8, rounding=ROUND_HALF_UP
            )
        else:
            success_rate = None
            failure_rate = None
            fraud_rate = None

        return TransactionKPIResult(
            period_start=period_start,
            period_end=period_end,
            total_volume=total_volume,
            successful_count=counts["SUCCESSFUL"],
            posted_count=counts["POSTED"],
            failed_count=counts["FAILED"],
            declined_count=counts["DECLINED"],
            cancelled_count=counts["CANCELLED"],
            voided_count=counts["VOIDED"],
            reversed_count=counts["REVERSED"],
            pending_count=counts["PENDING"],
            rate_eligible_count=rate_eligible_count,
            success_rate_pct=success_rate,
            failure_rate_pct=failure_rate,
            eligible_fraud_alert_tx_count=len(eligible_fraud_tx),
            fraud_alert_rate_pct=fraud_rate,
            total_amount=total_amount.quantize(SCALE_4),
            currency=currency,
        )

    @classmethod
    def calculate_loan_kpis(
        cls,
        *,
        loan_positions: Sequence[Any],
        business_date: date,
        execution_mode: ExecutionMode = ExecutionMode.FIXTURE,
    ) -> LoanKPIResult:
        """Calculate K05 (Delinquency Rate) and K06 (Delinquent Balance).

        K05 is active loans with DPD > 30 / active loans * 100.
        K06 is sum of principal for all loans with DPD > 30, across all statuses.
        Under DD-09: any negative principal (PRINCIPAL_NEGATIVE) or missing principal
        (PRINCIPAL_MISSING) on a DPD > 30 loan blocks K06 publication for that currency.
        """
        cls._require_execution_mode(execution_mode)

        active_count = 0
        delinquent_active_count = 0
        total_loans_evaluated = 0
        delinquent_all_statuses = 0

        # Currency-level buckets for K06
        principals_by_currency: dict[str, Decimal] = {}
        blocked_by_currency: dict[str, list[str]] = {}
        quarantined_negative = 0
        missing_principal_count = 0

        for pos in loan_positions:
            b_date = getattr(pos, "business_date", None) or (
                pos.get("business_date") if isinstance(pos, dict) else None
            )
            if b_date and b_date != business_date:
                if isinstance(b_date, str) and isinstance(business_date, date):
                    try:
                        if date.fromisoformat(b_date) != business_date:
                            continue
                    except ValueError:
                        continue
                else:
                    continue

            status = getattr(pos, "loan_status", None) or (
                pos.get("loan_status") if isinstance(pos, dict) else None
            )
            dpd_val = getattr(pos, "days_past_due", None)
            if dpd_val is None and isinstance(pos, dict):
                dpd_val = pos.get("days_past_due", 0)
            if dpd_val is None:
                dpd_val = 0

            p_val = getattr(pos, "outstanding_principal", None)
            if p_val is None and isinstance(pos, dict):
                p_val = pos.get("outstanding_principal")

            currency = getattr(pos, "currency", None)
            if currency is None and isinstance(pos, dict):
                currency = pos.get("currency", "USD")
            if currency is None:
                currency = "USD"
            currency = str(currency).upper()

            if currency not in principals_by_currency:
                principals_by_currency[currency] = Decimal("0.0000")
                blocked_by_currency[currency] = []

            total_loans_evaluated += 1
            status_str = str(status).upper() if status else ""
            dpd = int(dpd_val) if dpd_val is not None else 0

            # K05 Active evaluation
            is_active = status_str in cls.ACTIVE_LOAN_STATUSES
            if is_active:
                active_count += 1
                if dpd > 30:
                    delinquent_active_count += 1

            # K06 All-status evaluation
            if dpd > 30:
                delinquent_all_statuses += 1
                if p_val is None or p_val == "":
                    # DD-09: Missing principal on DPD > 30 loan blocks candidate
                    missing_principal_count += 1
                    if "PRINCIPAL_MISSING" not in blocked_by_currency[currency]:
                        blocked_by_currency[currency].append("PRINCIPAL_MISSING")
                else:
                    try:
                        p_dec = cls._to_decimal(p_val)
                        if p_dec < Decimal("0"):
                            # DD-09: Negative principal on DPD > 30 loan is quarantined and blocks candidate
                            quarantined_negative += 1
                            if "PRINCIPAL_NEGATIVE" not in blocked_by_currency[currency]:
                                blocked_by_currency[currency].append("PRINCIPAL_NEGATIVE")
                        else:
                            principals_by_currency[currency] += p_dec
                    except (InvalidOperation, TypeError):
                        missing_principal_count += 1
                        if "PRINCIPAL_MISSING" not in blocked_by_currency[currency]:
                            blocked_by_currency[currency].append("PRINCIPAL_MISSING")

        # Compute K05
        if active_count > 0:
            k05_rate = (
                (Decimal(delinquent_active_count) / Decimal(active_count)) * ONE_HUNDRED
            ).quantize(SCALE_8, rounding=ROUND_HALF_UP)
        else:
            k05_rate = None

        # Build K06 final results by currency
        k06_principals: dict[str, Decimal | None] = {}
        k06_statuses: dict[str, KPIPublicationStatus] = {}
        k06_reasons: dict[str, tuple[str, ...]] = {}

        for curr, reasons in blocked_by_currency.items():
            k06_reasons[curr] = tuple(reasons)
            if reasons:
                k06_statuses[curr] = KPIPublicationStatus.BLOCKED_CANDIDATE
                k06_principals[curr] = None
            else:
                k06_statuses[curr] = KPIPublicationStatus.PUBLISHED
                k06_principals[curr] = principals_by_currency[curr].quantize(SCALE_4)

        return LoanKPIResult(
            business_date=business_date,
            active_loan_count=active_count,
            delinquent_active_loan_count=delinquent_active_count,
            delinquency_rate_pct=k05_rate,
            total_loans_evaluated=total_loans_evaluated,
            delinquent_loan_count_all_statuses=delinquent_all_statuses,
            delinquent_outstanding_principal_by_currency=k06_principals,
            k06_publication_status=k06_statuses,
            k06_blocked_reasons=k06_reasons,
            quarantined_negative_principal_count=quarantined_negative,
            missing_principal_count=missing_principal_count,
        )

    @classmethod
    def calculate_customer_risk_kpis(
        cls,
        *,
        assessments: Sequence[RiskAssessment | Mapping[str, Any]],
        as_of_date: date,
        execution_mode: ExecutionMode = ExecutionMode.FIXTURE,
    ) -> CustomerRiskKPIResult:
        """Calculate K07 (High-Risk Customers) and population breakdowns.

        K07 strictly counts RiskClassification.PROVISIONAL_HIGH_RISK (t >= 2).
        INCOMPLETE_EVIDENCE and UNAVAILABLE are segregated as separate unknown/unavailable
        populations and NEVER counted as confirmed not-high-risk.
        """
        cls._require_execution_mode(execution_mode)

        total_assessed = 0
        provisional_high_risk = 0
        incomplete_evidence = 0
        unavailable_count = 0
        not_high_risk = 0

        rc_counts = {"RC-01": 0, "RC-02": 0, "RC-03": 0, "RC-04": 0, "RC-05": 0}

        for item in assessments:
            if isinstance(item, RiskAssessment):
                c_date = item.business_date
                classification = item.classification
                cond_results = item.condition_results
            else:
                c_date = item.get("business_date")
                classification = item.get("classification")
                cond_results = item.get("condition_results", ())

            if c_date and c_date != as_of_date:
                if isinstance(c_date, str) and isinstance(as_of_date, date):
                    try:
                        if date.fromisoformat(c_date) != as_of_date:
                            continue
                    except ValueError:
                        continue
                else:
                    continue

            total_assessed += 1

            class_val = getattr(classification, "value", classification)
            if (
                classification == RiskClassification.PROVISIONAL_HIGH_RISK
                or class_val == RiskClassification.PROVISIONAL_HIGH_RISK.value
                or str(classification).upper() == "PROVISIONAL_HIGH_RISK"
            ):
                provisional_high_risk += 1
            elif (
                classification == RiskClassification.INCOMPLETE_EVIDENCE
                or class_val == RiskClassification.INCOMPLETE_EVIDENCE.value
                or str(classification).upper() == "INCOMPLETE_EVIDENCE"
            ):
                incomplete_evidence += 1
            elif (
                classification == RiskClassification.UNAVAILABLE
                or class_val == RiskClassification.UNAVAILABLE.value
                or str(classification).upper() == "UNAVAILABLE"
            ):
                unavailable_count += 1
            elif (
                classification == RiskClassification.NOT_HIGH_RISK
                or class_val == RiskClassification.NOT_HIGH_RISK.value
                or str(classification).upper() == "NOT_HIGH_RISK"
            ):
                not_high_risk += 1

            for cond in cond_results:
                cid = getattr(cond, "condition_id", None) or (
                    cond.get("condition_id") if isinstance(cond, dict) else None
                )
                state = getattr(cond, "state", None) or (
                    cond.get("state") if isinstance(cond, dict) else None
                )
                state_str = str(state.value if hasattr(state, "value") else state).upper()
                if state_str in ("TRIGGERED", "CONDITIONSTATE.TRIGGERED"):
                    if cid in rc_counts:
                        rc_counts[cid] += 1

        return CustomerRiskKPIResult(
            as_of_date=as_of_date,
            total_assessed_customers=total_assessed,
            provisional_high_risk_customer_count=provisional_high_risk,
            incomplete_evidence_customer_count=incomplete_evidence,
            unavailable_assessment_customer_count=unavailable_count,
            not_high_risk_customer_count=not_high_risk,
            rc01_triggered_count=rc_counts["RC-01"],
            rc02_triggered_count=rc_counts["RC-02"],
            rc03_triggered_count=rc_counts["RC-03"],
            rc04_triggered_count=rc_counts["RC-04"],
            rc05_triggered_count=rc_counts["RC-05"],
            relationship_exposure_non_additive=True,
        )

    @classmethod
    def calculate_complaint_kpis(
        cls,
        *,
        complaints: Sequence[Any],
        period_start: datetime,
        period_end: datetime,
        as_of_time: datetime,
        execution_mode: ExecutionMode = ExecutionMode.FIXTURE,
    ) -> ComplaintKPIResult:
        """Calculate K08 (Avg Resolution Time), K09 (Open Complaints), and K10 (SLA Breach Rate).

        Clocks run continuously in 24/7 calendar hours.
        Reopened complaints retain original created_at clock without reset.
        Breach requires elapsed hours strictly greater than priority threshold.
        """
        cls._require_execution_mode(execution_mode)

        # Normalize timezones
        ref_tz = as_of_time.tzinfo

        closed_count = 0
        total_resolution_seconds = Decimal("0")
        open_count = 0
        reopened_count = 0

        sla_eligible_count = 0
        sla_breached_count = 0

        for c in complaints:
            c_id = getattr(c, "complaint_id", None) or (
                c.get("complaint_id") if isinstance(c, dict) else None
            )
            created_at = getattr(c, "created_at", None) or (
                c.get("created_at") if isinstance(c, dict) else None
            )
            closed_at = (
                getattr(c, "final_closed_at", None)
                or getattr(c, "closed_at", None)
                or ((c.get("final_closed_at") or c.get("closed_at")) if isinstance(c, dict) else None)
            )
            status = getattr(c, "complaint_status", None) or (
                c.get("complaint_status") if isinstance(c, dict) else None
            )
            priority = getattr(c, "priority_at_creation", None) or getattr(c, "priority", None) or (
                c.get("priority_at_creation") or c.get("priority") if isinstance(c, dict) else None
            )

            if created_at is None:
                continue

            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at)
                except ValueError:
                    continue

            if isinstance(closed_at, str):
                try:
                    closed_at = datetime.fromisoformat(closed_at)
                except ValueError:
                    closed_at = None

            # Ensure timezone compatibility
            if created_at.tzinfo is not None and ref_tz is None:
                created_at = created_at.replace(tzinfo=None)
            elif created_at.tzinfo is None and ref_tz is not None:
                created_at = created_at.replace(tzinfo=ref_tz)

            if closed_at is not None:
                if closed_at.tzinfo is not None and ref_tz is None:
                    closed_at = closed_at.replace(tzinfo=None)
                elif closed_at.tzinfo is None and ref_tz is not None:
                    closed_at = closed_at.replace(tzinfo=ref_tz)

            # Contradictory timestamp check
            if closed_at is not None and closed_at < created_at:
                continue

            status_str = str(status).upper() if status else ""
            priority_str = str(priority).upper() if priority else "MEDIUM"
            sla_thresh = cls.SLA_HOURS_BY_PRIORITY.get(priority_str, Decimal("72"))

            is_closed = status_str == "CLOSED" or (closed_at is not None and status_str != "REOPENED")
            is_reopened = status_str == "REOPENED"

            # K08: complaints finally closed within [period_start, period_end)
            if is_closed and closed_at is not None:
                if period_start <= closed_at < period_end:
                    closed_count += 1
                    dur_sec = Decimal(str((closed_at - created_at).total_seconds()))
                    total_resolution_seconds += dur_sec

            # K09: Open complaints at as_of_time
            if not is_closed or is_reopened:
                if created_at <= as_of_time:
                    open_count += 1
                    if is_reopened:
                        reopened_count += 1

            # K10: SLA breach evaluation across eligible complaints as-of
            if created_at <= as_of_time:
                sla_eligible_count += 1
                if is_closed and closed_at is not None and closed_at <= as_of_time:
                    elapsed_hours = Decimal(str((closed_at - created_at).total_seconds())) / Decimal("3600")
                else:
                    # Open or reopened complaint measured from original created_at to as_of_time
                    elapsed_hours = Decimal(str((as_of_time - created_at).total_seconds())) / Decimal("3600")

                # Strict breach: elapsed_hours > sla_thresh
                if elapsed_hours > sla_thresh:
                    sla_breached_count += 1

        # K08 calculation
        if closed_count > 0:
            avg_hours = (
                (total_resolution_seconds / Decimal(closed_count)) / Decimal("3600")
            ).quantize(SCALE_4, rounding=ROUND_HALF_UP)
            total_hours = (total_resolution_seconds / Decimal("3600")).quantize(SCALE_4)
        else:
            avg_hours = None
            total_hours = Decimal("0.0000")

        # K10 calculation
        if sla_eligible_count > 0:
            sla_breach_rate = (
                (Decimal(sla_breached_count) / Decimal(sla_eligible_count)) * ONE_HUNDRED
            ).quantize(SCALE_8, rounding=ROUND_HALF_UP)
        else:
            sla_breach_rate = None

        return ComplaintKPIResult(
            period_start=period_start,
            period_end=period_end,
            as_of_time=as_of_time,
            closed_complaint_count=closed_count,
            total_resolution_hours=total_hours,
            avg_resolution_hours=avg_hours,
            open_complaint_count=open_count,
            reopened_complaint_count=reopened_count,
            sla_eligible_complaint_count=sla_eligible_count,
            sla_breached_complaint_count=sla_breached_count,
            sla_breach_rate_pct=sla_breach_rate,
        )
