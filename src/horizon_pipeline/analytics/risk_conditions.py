"""Evidence-driven RC-01 through RC-05 condition evaluation.

This module implements approved logical rules for offline fixtures. It does not
activate pending production physical mappings or contracts.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Any, Iterable, Mapping, Sequence


class ConditionState(str, Enum):
    TRIGGERED = "Triggered"
    NOT_TRIGGERED = "Not triggered"
    UNKNOWN = "Unknown"


@dataclass(frozen=True)
class RiskConditionResult:
    condition_id: str
    state: ConditionState
    evidence: tuple[str, ...]
    lineage_references: tuple[str, ...]
    rule_version: str
    missing_evidence_reasons: tuple[str, ...] = ()
    as_of: datetime | None = None


def _result(condition: str, state: ConditionState, evidence: Iterable[str], lineage: Iterable[str],
            version: str, reasons: Iterable[str] = (), as_of: datetime | None = None) -> RiskConditionResult:
    return RiskConditionResult(condition, state, tuple(evidence), tuple(lineage), version, tuple(reasons), as_of)


def _instant(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    text = str(value).replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        raise ValueError("offset-qualified instant required")
    return parsed


def _decimal(value: Any) -> Decimal:
    if isinstance(value, float):
        raise InvalidOperation("binary float is not exact evidence")
    return Decimal(str(value))


class RiskConditionEvaluator:
    """Evaluate the five approved conditions without aggregating classification."""

    RC01_VERSION = "DD05-DD06-RC01-v1"
    RC02_VERSION = "DD04-DD06-RC02-v1"
    RC03_VERSION = "DD04-DD06-RC03-v1"
    RC04_VERSION = "DD04-DD06-RC04-v1"
    RC05_VERSION = "DD04-DD06-RC05-v1"
    FINALIZED_RC01 = frozenset({"SUCCESSFUL", "POSTED"})
    EXCLUDED_RC01 = frozenset({"PENDING", "FAILED", "DECLINED", "CANCELLED", "VOIDED", "REVERSED"})
    ACTIVE_LOAN = frozenset({"ACTIVE", "DELINQUENT_ACTIVE", "FORBEARANCE_ACTIVE"})
    SIGNIFICANT_SEVERITY = frozenset({"HIGH", "CRITICAL"})
    RESTRICTED = frozenset({"RESTRICTED", "FROZEN", "BLOCKED"})
    SLA_HOURS = {"Critical": 4, "High": 24, "Medium": 72, "Low": 120}

    @classmethod
    def rc01(cls, current: Mapping[str, Any], prior: Sequence[Mapping[str, Any]], *,
             customer_id: str, effective_owner_ids: Sequence[str], initiator_id: str | None,
             window_complete: bool, mapping_ready: bool = True,
             lineage_references: Sequence[str] = ()) -> RiskConditionResult:
        as_of = _instant(current.get("occurred_at", current.get("posted_at")))
        reasons: list[str] = []
        if not mapping_ready:
            reasons.append("MAPPING_UNAVAILABLE")
        if not window_complete:
            reasons.append("INCOMPLETE_90_DAY_WINDOW")
        if initiator_id:
            if initiator_id != customer_id:
                reasons.append("INITIATOR_UNRESOLVED")
        else:
            owners = tuple(dict.fromkeys(effective_owner_ids))
            if len(owners) != 1 or owners[0] != customer_id:
                reasons.append("JOINT_ACCOUNT_INITIATOR_UNRESOLVED" if len(owners) > 1 else "OWNER_UNRESOLVED")
        status = str(current.get("transaction_status", ""))
        currency = str(current.get("currency", ""))
        try:
            amount = abs(_decimal(current.get("amount")))
        except (InvalidOperation, TypeError):
            reasons.append("INVALID_CURRENT_AMOUNT")
            amount = Decimal(0)
        if status in cls.EXCLUDED_RC01 and not reasons:
            return _result("RC-01", ConditionState.NOT_TRIGGERED,
                           (f"recognized_excluded_status={status}",), lineage_references,
                           cls.RC01_VERSION, as_of=as_of)
        if status not in cls.FINALIZED_RC01:
            reasons.append("CURRENT_STATUS_UNMAPPED")
        if not currency or amount == 0:
            reasons.append("INVALID_CURRENT_CURRENCY_OR_ZERO_AMOUNT")
        window_start = as_of - timedelta(days=90)
        eligible: list[Decimal] = []
        for row in prior:
            try:
                occurred = _instant(row.get("occurred_at", row.get("posted_at")))
                prior_amount = abs(_decimal(row.get("amount")))
            except (ValueError, InvalidOperation, TypeError):
                reasons.append("INVALID_PRIOR_EVIDENCE")
                continue
            if (window_start <= occurred < as_of and occurred != as_of
                    and row.get("transaction_status") in cls.FINALIZED_RC01
                    and row.get("currency") == currency and prior_amount != 0):
                eligible.append(prior_amount)
        if len(eligible) < 5:
            reasons.append("FEWER_THAN_FIVE_ELIGIBLE_PRIORS")
        if reasons:
            return _result("RC-01", ConditionState.UNKNOWN, (f"eligible_prior_count={len(eligible)}",),
                           lineage_references, cls.RC01_VERSION, dict.fromkeys(reasons), as_of)
        prior_sum = sum(eligible, Decimal(0))
        if prior_sum == 0:
            return _result("RC-01", ConditionState.UNKNOWN, (), lineage_references, cls.RC01_VERSION,
                           ("ZERO_PRIOR_AVERAGE",), as_of)
        triggered = amount * len(eligible) >= Decimal(3) * prior_sum
        return _result("RC-01", ConditionState.TRIGGERED if triggered else ConditionState.NOT_TRIGGERED,
                       (f"current_absolute={amount}", f"prior_sum={prior_sum}", f"prior_count={len(eligible)}"),
                       lineage_references, cls.RC01_VERSION, as_of=as_of)

    @classmethod
    def rc02(cls, alerts: Sequence[Mapping[str, Any]], *, as_of: datetime,
             population_complete: bool, mapping_ready: bool,
             lineage_references: Sequence[str] = ()) -> RiskConditionResult:
        if not mapping_ready or not population_complete:
            reasons = (("MAPPING_UNAVAILABLE",) if not mapping_ready else ()) + (("POPULATION_INCOMPLETE",) if not population_complete else ())
            return _result("RC-02", ConditionState.UNKNOWN, (), lineage_references, cls.RC02_VERSION, reasons, as_of)
        selected: dict[str, Mapping[str, Any]] = {}
        for alert in alerts:
            if _instant(alert["effective_start"]) <= as_of:
                key = str(alert.get("alert_id"))
                if key not in selected or _instant(alert["effective_start"]) > _instant(selected[key]["effective_start"]):
                    selected[key] = alert
        matches = [a for a in selected.values() if a.get("case_status") == "OPEN" and a.get("severity") in cls.SIGNIFICANT_SEVERITY]
        return _result("RC-02", ConditionState.TRIGGERED if matches else ConditionState.NOT_TRIGGERED,
                       tuple(str(a.get("alert_id")) for a in matches), lineage_references, cls.RC02_VERSION, as_of=as_of)

    @classmethod
    def rc03(cls, positions: Sequence[Mapping[str, Any]], related_loan_ids: Sequence[str], *,
             as_of: datetime, population_complete: bool, mapping_ready: bool,
             lineage_references: Sequence[str] = ()) -> RiskConditionResult:
        if not mapping_ready or not population_complete:
            reasons = (("MAPPING_UNAVAILABLE",) if not mapping_ready else ()) + (("POPULATION_INCOMPLETE",) if not population_complete else ())
            return _result("RC-03", ConditionState.UNKNOWN, (), lineage_references, cls.RC03_VERSION, reasons, as_of)
        related = set(related_loan_ids)
        matches = [p for p in positions if p.get("loan_id") in related and p.get("loan_status") in cls.ACTIVE_LOAN and int(p.get("days_past_due", -1)) > 30]
        return _result("RC-03", ConditionState.TRIGGERED if matches else ConditionState.NOT_TRIGGERED,
                       tuple(str(p.get("loan_id")) for p in matches), lineage_references, cls.RC03_VERSION, as_of=as_of)

    @classmethod
    def rc04(cls, complaints: Sequence[Mapping[str, Any]], *, as_of: datetime,
             population_complete: bool, mapping_ready: bool,
             lineage_references: Sequence[str] = ()) -> RiskConditionResult:
        if not mapping_ready or not population_complete:
            reasons = (("MAPPING_UNAVAILABLE",) if not mapping_ready else ()) + (("POPULATION_INCOMPLETE",) if not population_complete else ())
            return _result("RC-04", ConditionState.UNKNOWN, (), lineage_references, cls.RC04_VERSION, reasons, as_of)
        matches: list[Mapping[str, Any]] = []
        for c in complaints:
            priority = c.get("priority_at_creation", c.get("priority"))
            if priority not in cls.SLA_HOURS:
                return _result("RC-04", ConditionState.UNKNOWN, (), lineage_references, cls.RC04_VERSION, ("PRIORITY_MAPPING_UNAVAILABLE",), as_of)
            if c.get("complaint_status") in {"OPEN", "IN_PROGRESS", "REOPENED"}:
                if as_of - _instant(c["created_at"]) > timedelta(hours=cls.SLA_HOURS[priority]):
                    matches.append(c)
        return _result("RC-04", ConditionState.TRIGGERED if matches else ConditionState.NOT_TRIGGERED,
                       tuple(str(c.get("complaint_id")) for c in matches), lineage_references, cls.RC04_VERSION, as_of=as_of)

    @classmethod
    def rc05(cls, states: Sequence[Mapping[str, Any]], related_account_ids: Sequence[str], *,
             as_of: datetime, population_complete: bool, mapping_ready: bool,
             lineage_references: Sequence[str] = ()) -> RiskConditionResult:
        if not mapping_ready or not population_complete:
            reasons = (("MAPPING_UNAVAILABLE",) if not mapping_ready else ()) + (("POPULATION_INCOMPLETE",) if not population_complete else ())
            return _result("RC-05", ConditionState.UNKNOWN, (), lineage_references, cls.RC05_VERSION, reasons, as_of)
        related = set(related_account_ids)
        selected: dict[str, Mapping[str, Any]] = {}
        for state in states:
            key = str(state.get("account_id"))
            if key in related and _instant(state["effective_start"]) <= as_of:
                if key not in selected or _instant(state["effective_start"]) > _instant(selected[key]["effective_start"]):
                    selected[key] = state
        matches = [s for s in selected.values() if s.get("restriction_status") in cls.RESTRICTED]
        return _result("RC-05", ConditionState.TRIGGERED if matches else ConditionState.NOT_TRIGGERED,
                       tuple(str(s.get("account_id")) for s in matches), lineage_references, cls.RC05_VERSION, as_of=as_of)
