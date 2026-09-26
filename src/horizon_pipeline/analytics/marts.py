"""Dimensional Analytical Marts for Horizon Bank Analytics.

Governed by:
- DD-06 Approved KPI and canonical mapping policy
- DD-04 Customer risk catalog and classification hierarchy
- DD-09 Data quality and reconciliation policy (gating rules)
- DD-02 Relationship exposure non-additive attribution

Implements four dimensional analytical marts:
1. `mart_transaction_kpis`
2. `mart_loan_delinquency_kpis`
3. `mart_customer_risk_kpis`
4. `mart_complaint_kpis`

This module executes in pure offline mode. In ExecutionMode.PRODUCTION, it fails
closed with PendingContractError because production contracts remain pending confirmation.
In ExecutionMode.FIXTURE, it executes with exact scale-4 Decimal currency arithmetic
and scale-8 ratio precision.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Sequence

from ..contracts.states import PendingContractError
from ..processing.records import ExecutionMode
from .kpi import (
    ComplaintKPIResult,
    CustomerRiskKPIResult,
    KPIEngine,
    KPIPublicationStatus,
    LoanKPIResult,
    ONE_HUNDRED,
    SCALE_4,
    SCALE_8,
    TransactionKPIResult,
)
from .risk_classification import (
    EvidenceState,
    RiskAssessment,
    RiskClassification,
)


# =====================================================================
# Mart Record Structures (Frozen, Conformed Grains)
# =====================================================================

@dataclass(frozen=True)
class TransactionMartRecord:
    """Dimensional mart record for transaction KPIs (K01-K04).

    Grain: [period_start, period_end, branch_id, channel, currency]
    """

    period_start: datetime
    period_end: datetime
    branch_id: str
    channel: str
    currency: str
    total_transaction_count: int  # K01
    successful_transaction_count: int
    posted_transaction_count: int
    failed_transaction_count: int
    declined_transaction_count: int
    cancelled_count: int
    voided_count: int
    reversed_count: int
    rate_eligible_transaction_count: int  # Denominator for K02, K03, K04
    success_rate_pct: Decimal | None  # K02
    failure_rate_pct: Decimal | None  # K03
    eligible_transactions_with_fraud_alert_count: int  # K04 Numerator
    fraud_alert_rate_pct: Decimal | None  # K04
    total_transaction_amount: Decimal


@dataclass(frozen=True)
class LoanDelinquencyMartRecord:
    """Dimensional mart record for loan delinquency KPIs (K05-K06).

    Grain: [business_date, branch_id, currency, loan_type]
    """

    business_date: date
    branch_id: str
    currency: str
    loan_type: str
    active_loan_count: int  # K05 Denominator
    delinquent_active_loan_count: int  # K05 Numerator (DPD > 30 and Active)
    loan_delinquency_rate_pct: Decimal | None  # K05
    total_loans_evaluated: int
    delinquent_loan_count_all_statuses: int  # DPD > 30 all statuses
    delinquent_outstanding_principal: Decimal | None  # K06 (None if blocked)
    k06_publication_status: KPIPublicationStatus
    quarantined_negative_principal_count: int
    missing_principal_count: int
    blocked_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class CustomerRiskMartRecord:
    """Dimensional mart record for customer risk KPIs (K07).

    Grain: [as_of_date, home_branch_id]
    """

    as_of_date: date
    home_branch_id: str
    total_assessed_customer_count: int
    provisional_high_risk_customer_count: int  # K07: t >= 2
    incomplete_evidence_customer_count: int  # t < 2, t + u >= 2 (separate unknown population)
    unavailable_assessment_customer_count: int  # Priority 1 invalid evidence
    not_high_risk_customer_count: int  # t < 2, t + u < 2 (confirmed not-high-risk)
    rc01_triggered_count: int
    rc02_triggered_count: int
    rc03_triggered_count: int
    rc04_triggered_count: int
    rc05_triggered_count: int
    relationship_exposure_non_additive: bool = True  # DD-02 mandatory rule


@dataclass(frozen=True)
class ComplaintMartRecord:
    """Dimensional mart record for complaint KPIs (K08-K10).

    Grain: [period_start, period_end, branch_id, channel, priority]
    """

    period_start: datetime
    period_end: datetime
    branch_id: str
    channel: str
    priority: str
    closed_complaint_count: int
    total_resolution_hours: Decimal
    avg_resolution_hours: Decimal | None  # K08
    open_complaint_count: int  # K09
    reopened_complaint_count: int
    sla_eligible_complaint_count: int  # K10 Denominator
    sla_breached_complaint_count: int  # K10 Numerator
    sla_breach_rate_pct: Decimal | None  # K10


@dataclass(frozen=True)
class AnalyticalMartsResult:
    """Consolidated analytical marts output container."""

    transaction_mart: tuple[TransactionMartRecord, ...]
    loan_mart: tuple[LoanDelinquencyMartRecord, ...]
    customer_risk_mart: tuple[CustomerRiskMartRecord, ...]
    complaint_mart: tuple[ComplaintMartRecord, ...]
    execution_mode: ExecutionMode = ExecutionMode.FIXTURE


# =====================================================================
# Serialization Support
# =====================================================================

class MartJSONEncoder(json.JSONEncoder):
    """Deterministic JSON encoder for mart records."""

    def default(self, o: Any) -> Any:
        if isinstance(o, Decimal):
            return str(o)
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if isinstance(o, Enum):
            return o.value
        if dataclasses.is_dataclass(o) and not isinstance(o, type):
            return dataclasses.asdict(o)
        return super().default(o)


# =====================================================================
# Mart Builders
# =====================================================================

class MartBuilder:
    """Builder for conformed dimensional analytical marts."""

    @staticmethod
    def _require_execution_mode(execution_mode: object) -> ExecutionMode:
        if type(execution_mode) is not ExecutionMode:
            raise TypeError("execution_mode must be an ExecutionMode enum member")
        if execution_mode is ExecutionMode.PRODUCTION:
            raise PendingContractError(
                "MasterProductionRegistry contracts remain pending confirmation; "
                "production mart generation is fail-closed."
            )
        return execution_mode

    @classmethod
    def build_transaction_mart(
        cls,
        *,
        transactions: Sequence[Any],
        fraud_alerts: Sequence[Any] = (),
        period_start: datetime,
        period_end: datetime,
        accounts: Sequence[Any] | Mapping[str, Any] | None = None,
        execution_mode: ExecutionMode = ExecutionMode.FIXTURE,
    ) -> tuple[TransactionMartRecord, ...]:
        """Build mart_transaction_kpis aggregated by [period_start, period_end, branch_id, channel, currency]."""
        cls._require_execution_mode(execution_mode)

        # Build account-to-branch lookup if available
        account_branch_map: dict[str, str] = {}
        if accounts is not None:
            if isinstance(accounts, Mapping):
                for acc_id, acc_obj in accounts.items():
                    br = getattr(acc_obj, "branch_id", None) or (
                        acc_obj.get("branch_id") if isinstance(acc_obj, dict) else None
                    )
                    if br:
                        account_branch_map[str(acc_id)] = str(br)
            else:
                for acc in accounts:
                    acc_id = getattr(acc, "account_id", None) or (
                        acc.get("account_id") if isinstance(acc, dict) else None
                    )
                    br = getattr(acc, "branch_id", None) or (
                        acc.get("branch_id") if isinstance(acc, dict) else None
                    )
                    if acc_id and br:
                        account_branch_map[str(acc_id)] = str(br)

        # Group transactions by (branch_id, channel, currency)
        grouped_txs: dict[tuple[str, str, str], list[Any]] = defaultdict(list)

        for tx in transactions:
            branch_id = getattr(tx, "branch_id", None) or (
                tx.get("branch_id") if isinstance(tx, dict) else None
            )
            if not branch_id:
                acc_id = getattr(tx, "account_id", None) or (
                    tx.get("account_id") if isinstance(tx, dict) else None
                )
                if acc_id and str(acc_id) in account_branch_map:
                    branch_id = account_branch_map[str(acc_id)]
                else:
                    branch_id = "UNKNOWN_BRANCH"

            channel = getattr(tx, "channel", None) or (
                tx.get("channel") if isinstance(tx, dict) else None
            ) or "UNKNOWN_CHANNEL"

            curr = getattr(tx, "currency", None) or (
                tx.get("currency") if isinstance(tx, dict) else None
            ) or "USD"

            grouped_txs[(str(branch_id), str(channel).upper(), str(curr).upper())].append(tx)

        records: list[TransactionMartRecord] = []

        for (branch_id, channel, curr), group_txs in grouped_txs.items():
            kpi_res: TransactionKPIResult = KPIEngine.calculate_transaction_kpis(
                transactions=group_txs,
                fraud_alerts=fraud_alerts,
                period_start=period_start,
                period_end=period_end,
                currency=curr,
                execution_mode=execution_mode,
            )

            records.append(
                TransactionMartRecord(
                    period_start=period_start,
                    period_end=period_end,
                    branch_id=branch_id,
                    channel=channel,
                    currency=curr,
                    total_transaction_count=kpi_res.total_volume,
                    successful_transaction_count=kpi_res.successful_count,
                    posted_transaction_count=kpi_res.posted_count,
                    failed_transaction_count=kpi_res.failed_count,
                    declined_transaction_count=kpi_res.declined_count,
                    cancelled_count=kpi_res.cancelled_count,
                    voided_count=kpi_res.voided_count,
                    reversed_count=kpi_res.reversed_count,
                    rate_eligible_transaction_count=kpi_res.rate_eligible_count,
                    success_rate_pct=kpi_res.success_rate_pct,
                    failure_rate_pct=kpi_res.failure_rate_pct,
                    eligible_transactions_with_fraud_alert_count=kpi_res.eligible_fraud_alert_tx_count,
                    fraud_alert_rate_pct=kpi_res.fraud_alert_rate_pct,
                    total_transaction_amount=kpi_res.total_amount,
                )
            )

        # Deterministic sorting
        records.sort(
            key=lambda r: (r.period_start, r.period_end, r.branch_id, r.channel, r.currency)
        )
        return tuple(records)

    @classmethod
    def build_loan_delinquency_mart(
        cls,
        *,
        loan_positions: Sequence[Any],
        loans: Sequence[Any] | Mapping[str, Any] | None = None,
        business_date: date,
        execution_mode: ExecutionMode = ExecutionMode.FIXTURE,
    ) -> tuple[LoanDelinquencyMartRecord, ...]:
        """Build mart_loan_delinquency_kpis aggregated by [business_date, branch_id, currency, loan_type]."""
        cls._require_execution_mode(execution_mode)

        # Build loan attribute lookup (branch_id, loan_type)
        loan_meta_map: dict[str, tuple[str, str]] = {}
        if loans is not None:
            if isinstance(loans, Mapping):
                for lid, lobj in loans.items():
                    br = getattr(lobj, "branch_id", None) or (
                        lobj.get("branch_id") if isinstance(lobj, dict) else None
                    ) or "UNKNOWN_BRANCH"
                    ltype = getattr(lobj, "loan_type", None) or (
                        lobj.get("loan_type") if isinstance(lobj, dict) else None
                    ) or "UNKNOWN_TYPE"
                    loan_meta_map[str(lid)] = (str(br), str(ltype).upper())
            else:
                for lobj in loans:
                    lid = getattr(lobj, "loan_id", None) or (
                        lobj.get("loan_id") if isinstance(lobj, dict) else None
                    )
                    br = getattr(lobj, "branch_id", None) or (
                        lobj.get("branch_id") if isinstance(lobj, dict) else None
                    ) or "UNKNOWN_BRANCH"
                    ltype = getattr(lobj, "loan_type", None) or (
                        lobj.get("loan_type") if isinstance(lobj, dict) else None
                    ) or "UNKNOWN_TYPE"
                    if lid:
                        loan_meta_map[str(lid)] = (str(br), str(ltype).upper())

        # Group positions by (branch_id, currency, loan_type)
        grouped_positions: dict[tuple[str, str, str], list[Any]] = defaultdict(list)

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

            lid = getattr(pos, "loan_id", None) or (
                pos.get("loan_id") if isinstance(pos, dict) else None
            )
            meta = loan_meta_map.get(str(lid), ("UNKNOWN_BRANCH", "UNKNOWN_TYPE")) if lid else ("UNKNOWN_BRANCH", "UNKNOWN_TYPE")

            br = getattr(pos, "branch_id", None) or (
                pos.get("branch_id") if isinstance(pos, dict) else None
            ) or meta[0]

            ltype = getattr(pos, "loan_type", None) or (
                pos.get("loan_type") if isinstance(pos, dict) else None
            ) or meta[1]

            curr = getattr(pos, "currency", None) or (
                pos.get("currency") if isinstance(pos, dict) else None
            ) or "USD"

            grouped_positions[(str(br), str(curr).upper(), str(ltype).upper())].append(pos)

        records: list[LoanDelinquencyMartRecord] = []

        for (branch_id, curr, loan_type), group_positions in grouped_positions.items():
            active_count = 0
            delinquent_active_count = 0
            total_evaluated = 0
            delinquent_all_statuses = 0
            delinquent_principal = Decimal("0.0000")
            quarantined_negative = 0
            missing_principal_count = 0
            blocked_reasons: list[str] = []

            for pos in group_positions:
                total_evaluated += 1
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

                status_str = str(status).upper() if status else ""
                dpd = int(dpd_val) if dpd_val is not None else 0

                is_active = status_str in KPIEngine.ACTIVE_LOAN_STATUSES
                if is_active:
                    active_count += 1
                    if dpd > 30:
                        delinquent_active_count += 1

                if dpd > 30:
                    delinquent_all_statuses += 1
                    if p_val is None or p_val == "":
                        missing_principal_count += 1
                        if "PRINCIPAL_MISSING" not in blocked_reasons:
                            blocked_reasons.append("PRINCIPAL_MISSING")
                    else:
                        try:
                            p_dec = KPIEngine._to_decimal(p_val)
                            if p_dec < Decimal("0"):
                                quarantined_negative += 1
                                if "PRINCIPAL_NEGATIVE" not in blocked_reasons:
                                    blocked_reasons.append("PRINCIPAL_NEGATIVE")
                            else:
                                delinquent_principal += p_dec
                        except (InvalidOperation, TypeError):
                            missing_principal_count += 1
                            if "PRINCIPAL_MISSING" not in blocked_reasons:
                                blocked_reasons.append("PRINCIPAL_MISSING")

            if active_count > 0:
                delinquency_rate = (
                    (Decimal(delinquent_active_count) / Decimal(active_count)) * ONE_HUNDRED
                ).quantize(SCALE_8, rounding=ROUND_HALF_UP)
            else:
                delinquency_rate = None

            if blocked_reasons:
                pub_status = KPIPublicationStatus.BLOCKED_CANDIDATE
                pub_principal = None
            else:
                pub_status = KPIPublicationStatus.PUBLISHED
                pub_principal = delinquent_principal.quantize(SCALE_4)

            records.append(
                LoanDelinquencyMartRecord(
                    business_date=business_date,
                    branch_id=branch_id,
                    currency=curr,
                    loan_type=loan_type,
                    active_loan_count=active_count,
                    delinquent_active_loan_count=delinquent_active_count,
                    loan_delinquency_rate_pct=delinquency_rate,
                    total_loans_evaluated=total_evaluated,
                    delinquent_loan_count_all_statuses=delinquent_all_statuses,
                    delinquent_outstanding_principal=pub_principal,
                    k06_publication_status=pub_status,
                    quarantined_negative_principal_count=quarantined_negative,
                    missing_principal_count=missing_principal_count,
                    blocked_reasons=tuple(blocked_reasons),
                )
            )

        records.sort(
            key=lambda r: (r.business_date, r.branch_id, r.currency, r.loan_type)
        )
        return tuple(records)

    @classmethod
    def build_customer_risk_mart(
        cls,
        *,
        assessments: Sequence[RiskAssessment | Mapping[str, Any]],
        customers: Sequence[Any] | Mapping[str, Any] | None = None,
        as_of_date: date,
        execution_mode: ExecutionMode = ExecutionMode.FIXTURE,
    ) -> tuple[CustomerRiskMartRecord, ...]:
        """Build mart_customer_risk_kpis aggregated by [as_of_date, home_branch_id]."""
        cls._require_execution_mode(execution_mode)

        # Build customer home branch lookup
        cust_branch_map: dict[str, str] = {}
        if customers is not None:
            if isinstance(customers, Mapping):
                for cid, cobj in customers.items():
                    br = getattr(cobj, "primary_branch_id", None) or getattr(cobj, "branch_id", None) or (
                        (cobj.get("primary_branch_id") or cobj.get("branch_id")) if isinstance(cobj, dict) else None
                    )
                    if br:
                        cust_branch_map[str(cid)] = str(br)
            else:
                for cobj in customers:
                    cid = getattr(cobj, "customer_id", None) or (
                        cobj.get("customer_id") if isinstance(cobj, dict) else None
                    )
                    br = getattr(cobj, "primary_branch_id", None) or getattr(cobj, "branch_id", None) or (
                        (cobj.get("primary_branch_id") or cobj.get("branch_id")) if isinstance(cobj, dict) else None
                    )
                    if cid and br:
                        cust_branch_map[str(cid)] = str(br)

        grouped_assessments: dict[str, list[Any]] = defaultdict(list)

        for item in assessments:
            if isinstance(item, RiskAssessment):
                cid = item.customer_id
                c_date = item.business_date
            else:
                cid = item.get("customer_id")
                c_date = item.get("business_date")

            if c_date and c_date != as_of_date:
                if isinstance(c_date, str) and isinstance(as_of_date, date):
                    try:
                        if date.fromisoformat(c_date) != as_of_date:
                            continue
                    except ValueError:
                        continue
                else:
                    continue

            br = getattr(item, "home_branch_id", None) or getattr(item, "branch_id", None)
            if not br and isinstance(item, dict):
                br = item.get("home_branch_id") or item.get("branch_id")

            if not br and cid and str(cid) in cust_branch_map:
                br = cust_branch_map[str(cid)]
            elif not br:
                br = "UNKNOWN_BRANCH"

            grouped_assessments[str(br)].append(item)

        records: list[CustomerRiskMartRecord] = []

        for home_branch_id, group_items in grouped_assessments.items():
            kpi_res = KPIEngine.calculate_customer_risk_kpis(
                assessments=group_items,
                as_of_date=as_of_date,
                execution_mode=execution_mode,
            )

            records.append(
                CustomerRiskMartRecord(
                    as_of_date=as_of_date,
                    home_branch_id=home_branch_id,
                    total_assessed_customer_count=kpi_res.total_assessed_customers,
                    provisional_high_risk_customer_count=kpi_res.provisional_high_risk_customer_count,
                    incomplete_evidence_customer_count=kpi_res.incomplete_evidence_customer_count,
                    unavailable_assessment_customer_count=kpi_res.unavailable_assessment_customer_count,
                    not_high_risk_customer_count=kpi_res.not_high_risk_customer_count,
                    rc01_triggered_count=kpi_res.rc01_triggered_count,
                    rc02_triggered_count=kpi_res.rc02_triggered_count,
                    rc03_triggered_count=kpi_res.rc03_triggered_count,
                    rc04_triggered_count=kpi_res.rc04_triggered_count,
                    rc05_triggered_count=kpi_res.rc05_triggered_count,
                    relationship_exposure_non_additive=True,
                )
            )

        records.sort(key=lambda r: (r.as_of_date, r.home_branch_id))
        return tuple(records)

    @classmethod
    def build_complaint_mart(
        cls,
        *,
        complaints: Sequence[Any],
        period_start: datetime,
        period_end: datetime,
        as_of_time: datetime | None = None,
        execution_mode: ExecutionMode = ExecutionMode.FIXTURE,
    ) -> tuple[ComplaintMartRecord, ...]:
        """Build mart_complaint_kpis aggregated by [period_start, period_end, branch_id, channel, priority]."""
        cls._require_execution_mode(execution_mode)

        if as_of_time is None:
            as_of_time = period_end

        grouped_complaints: dict[tuple[str, str, str], list[Any]] = defaultdict(list)

        for c in complaints:
            br = getattr(c, "branch_id", None) or (
                c.get("branch_id") if isinstance(c, dict) else None
            ) or "UNKNOWN_BRANCH"

            channel = getattr(c, "channel", None) or (
                c.get("channel") if isinstance(c, dict) else None
            ) or "UNKNOWN_CHANNEL"

            priority = getattr(c, "priority_at_creation", None) or getattr(c, "priority", None) or (
                c.get("priority_at_creation") or c.get("priority") if isinstance(c, dict) else None
            ) or "MEDIUM"

            grouped_complaints[(str(br), str(channel).upper(), str(priority).upper())].append(c)

        records: list[ComplaintMartRecord] = []

        for (branch_id, channel, priority), group_c in grouped_complaints.items():
            kpi_res = KPIEngine.calculate_complaint_kpis(
                complaints=group_c,
                period_start=period_start,
                period_end=period_end,
                as_of_time=as_of_time,
                execution_mode=execution_mode,
            )

            records.append(
                ComplaintMartRecord(
                    period_start=period_start,
                    period_end=period_end,
                    branch_id=branch_id,
                    channel=channel,
                    priority=priority,
                    closed_complaint_count=kpi_res.closed_complaint_count,
                    total_resolution_hours=kpi_res.total_resolution_hours,
                    avg_resolution_hours=kpi_res.avg_resolution_hours,
                    open_complaint_count=kpi_res.open_complaint_count,
                    reopened_complaint_count=kpi_res.reopened_complaint_count,
                    sla_eligible_complaint_count=kpi_res.sla_eligible_complaint_count,
                    sla_breached_complaint_count=kpi_res.sla_breached_complaint_count,
                    sla_breach_rate_pct=kpi_res.sla_breach_rate_pct,
                )
            )

        records.sort(
            key=lambda r: (r.period_start, r.period_end, r.branch_id, r.channel, r.priority)
        )
        return tuple(records)


class AnalyticalMartsBuilder:
    """Coordinator for generating all analytical marts."""

    @classmethod
    def build_all(
        cls,
        *,
        transactions: Sequence[Any] = (),
        fraud_alerts: Sequence[Any] = (),
        accounts: Sequence[Any] | Mapping[str, Any] | None = None,
        period_start: datetime,
        period_end: datetime,
        loan_positions: Sequence[Any] = (),
        loans: Sequence[Any] | Mapping[str, Any] | None = None,
        business_date: date,
        assessments: Sequence[RiskAssessment | Mapping[str, Any]] = (),
        customers: Sequence[Any] | Mapping[str, Any] | None = None,
        complaints: Sequence[Any] = (),
        as_of_time: datetime | None = None,
        execution_mode: ExecutionMode = ExecutionMode.FIXTURE,
    ) -> AnalyticalMartsResult:
        """Build all four dimensional analytical marts."""
        tx_mart = MartBuilder.build_transaction_mart(
            transactions=transactions,
            fraud_alerts=fraud_alerts,
            period_start=period_start,
            period_end=period_end,
            accounts=accounts,
            execution_mode=execution_mode,
        )
        loan_mart = MartBuilder.build_loan_delinquency_mart(
            loan_positions=loan_positions,
            loans=loans,
            business_date=business_date,
            execution_mode=execution_mode,
        )
        risk_mart = MartBuilder.build_customer_risk_mart(
            assessments=assessments,
            customers=customers,
            as_of_date=business_date,
            execution_mode=execution_mode,
        )
        complaint_mart = MartBuilder.build_complaint_mart(
            complaints=complaints,
            period_start=period_start,
            period_end=period_end,
            as_of_time=as_of_time,
            execution_mode=execution_mode,
        )
        return AnalyticalMartsResult(
            transaction_mart=tx_mart,
            loan_mart=loan_mart,
            customer_risk_mart=risk_mart,
            complaint_mart=complaint_mart,
            execution_mode=execution_mode,
        )


def write_analytical_marts(
    output_dir: Path | str,
    marts_result: AnalyticalMartsResult,
) -> dict[str, str]:
    """Write all dimensional analytical marts deterministically as JSON artifacts.

    Returns mapping of relative artifact paths to their SHA-256 checksums.
    """
    out_path = Path(output_dir)
    marts_dir = out_path / "marts"
    marts_dir.mkdir(parents=True, exist_ok=True)

    file_checksums: dict[str, str] = {}

    def _write_mart_file(rel_path: str, data: Sequence[Any]) -> None:
        full_path = out_path / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        dict_records = [dataclasses.asdict(r) for r in data]
        content = json.dumps(dict_records, indent=2, sort_keys=True, cls=MartJSONEncoder) + "\n"
        content_bytes = content.encode("utf-8")
        full_path.write_bytes(content_bytes)
        digest = hashlib.sha256(content_bytes).hexdigest()
        file_checksums[rel_path] = digest

    _write_mart_file("marts/mart_transaction_kpis.json", marts_result.transaction_mart)
    _write_mart_file("marts/mart_loan_delinquency_kpis.json", marts_result.loan_mart)
    _write_mart_file("marts/mart_customer_risk_kpis.json", marts_result.customer_risk_mart)
    _write_mart_file("marts/mart_complaint_kpis.json", marts_result.complaint_mart)

    return file_checksums
