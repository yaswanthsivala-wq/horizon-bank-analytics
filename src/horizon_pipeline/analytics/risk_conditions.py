"""Evidence-driven RC-01 through RC-05 condition evaluation.

This module implements approved logical rules for offline fixtures. It does not
activate pending production physical mappings or contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from enum import Enum
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Sequence

from ..contracts.registry import MasterProductionRegistry
from ..contracts.states import ContractState
from ..contracts.temporal import CHICAGO_TZ
from ..processing.records import ExecutionMode


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


@dataclass(frozen=True)
class PublicationEvidence:
    """Selected successful publication and delivery evidence for one population."""

    business_date: date
    publication_version: str
    revision: int
    selected_publication_version: str
    selected_revision: int
    manifest_present: bool
    population_complete: bool
    zero_row_confirmed: bool = False
    supersedes_revision: int | None = None
    mapping_versions: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "mapping_versions", MappingProxyType(dict(self.mapping_versions)))


def _require_execution_mode(execution_mode: object) -> ExecutionMode:
    if type(execution_mode) is not ExecutionMode:
        raise TypeError("execution_mode must be an ExecutionMode enum member")
    return execution_mode


def _publication_reasons(publication: PublicationEvidence | None) -> tuple[str, ...]:
    if publication is None:
        return ("PUBLICATION_EVIDENCE_MISSING",)
    reasons: list[str] = []
    if not publication.publication_version or not publication.manifest_present:
        reasons.append("PUBLICATION_OR_MANIFEST_MISSING")
    if (publication.publication_version != publication.selected_publication_version
            or publication.revision != publication.selected_revision):
        reasons.append("PUBLICATION_REVISION_NOT_SELECTED")
    if publication.revision < 1:
        reasons.append("INVALID_REVISION")
    if publication.supersedes_revision is not None:
        if publication.revision <= publication.supersedes_revision:
            reasons.append("INVALID_CORRECTION_REVISION")
        else:
            # Physical predecessor lookup and correction approval binding are
            # not approved contracts yet. Never accept a caller assertion.
            reasons.append("CORRECTION_AUTHORITY_PENDING")
    if not publication.population_complete:
        reasons.append("POPULATION_INCOMPLETE")
    return tuple(reasons)


def _selected_rows(
    rows: Sequence[Mapping[str, Any]], publication: PublicationEvidence
) -> list[Mapping[str, Any]]:
    selected: list[Mapping[str, Any]] = []
    for row in rows:
        try:
            revision = int(row.get("revision", -1))
        except (TypeError, ValueError):
            continue
        if (row.get("publication_version") == publication.selected_publication_version
                and revision == publication.selected_revision):
            selected.append(row)
    return selected


def _publication_evidence(publication: PublicationEvidence) -> tuple[str, ...]:
    items = [
        f"selected_publication_version={publication.selected_publication_version}",
        f"selected_revision={publication.selected_revision}",
        f"publication_business_date={publication.business_date.isoformat()}",
        f"manifest_present={str(publication.manifest_present).lower()}",
        f"population_complete={str(publication.population_complete).lower()}",
    ]
    items.extend(
        f"mapping_version:{domain}={version}"
        for domain, version in sorted(publication.mapping_versions.items())
    )
    if publication.supersedes_revision is not None:
        items.append(f"supersedes_revision={publication.supersedes_revision}")
    return tuple(items)


def _required_mapping_reasons(
    publication: PublicationEvidence | None,
    required_domains: Sequence[tuple[str, str]],
) -> tuple[str, ...]:
    if publication is None:
        return ()
    missing = [
        f"{source}:{domain}" for source, domain in required_domains
        if not publication.mapping_versions.get(f"{source}:{domain}")
    ]
    return tuple(f"MAPPING_VERSION_MISSING:{domain}" for domain in missing)


def _row_identity(row: Mapping[str, Any], key: str) -> str | None:
    value = row.get(key)
    return str(value) if value not in (None, "") else None


def _row_contract_reasons(rows: Sequence[Mapping[str, Any]]) -> tuple[str, ...]:
    for row in rows:
        try:
            int(row.get("revision", -1))
        except (TypeError, ValueError):
            return ("MALFORMED_ROW_REVISION",)
    return ()


def _combined_lineage(
    supplied: Sequence[str], rows: Sequence[Mapping[str, Any]]
) -> tuple[str, ...]:
    values = list(supplied)
    for row in rows:
        refs = row.get("lineage_references", ())
        if isinstance(refs, str):
            refs = (refs,)
        values.extend(str(ref) for ref in refs if ref)
    return tuple(dict.fromkeys(values))


def _date_value(value: Any) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    return date.fromisoformat(str(value))


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

    @staticmethod
    def _production_mapping_ready(
        execution_mode: ExecutionMode,
        publication: PublicationEvidence | None,
        required_domains: Sequence[tuple[str, str]],
    ) -> bool:
        if execution_mode == ExecutionMode.FIXTURE:
            return True
        if publication is None:
            return False
        registry = MasterProductionRegistry().mappings
        for source, domain in required_domains:
            version = publication.mapping_versions.get(f"{source}:{domain}")
            if not version or registry.version_state(source, domain, version) != ContractState.ACTIVE:
                return False
            if (registry.version_has_only_fixture_entries(source, domain, version)
                    or not registry.version_has_active_production_entries(source, domain, version)):
                return False
        return True

    @classmethod
    def rc01(cls, current: Mapping[str, Any], prior: Sequence[Mapping[str, Any]], *,
             customer_id: str, effective_owner_ids: Sequence[str], initiator_id: str | None,
             window_complete: bool, mapping_ready: bool,
             execution_mode: ExecutionMode, publication: PublicationEvidence | None,
             lineage_references: Sequence[str] = ()) -> RiskConditionResult:
        _require_execution_mode(execution_mode)
        result_lineage = _combined_lineage(lineage_references, (current, *prior))
        try:
            as_of = _instant(current.get("occurred_at", current.get("posted_at")))
        except (TypeError, ValueError):
            evidence = _publication_evidence(publication) if publication else ()
            return _result("RC-01", ConditionState.UNKNOWN, evidence, result_lineage,
                           cls.RC01_VERSION, ("MALFORMED_CURRENT_EVENT_TIMESTAMP",))
        reasons: list[str] = list(_publication_reasons(publication))
        reasons.extend(_required_mapping_reasons(publication, (("SRC-01", "transaction_status"),)))
        reasons.extend(_row_contract_reasons((current,)))
        if publication is not None and current not in _selected_rows((current,), publication):
            reasons.append("CURRENT_EVENT_NOT_IN_SELECTED_PUBLICATION")
        if not _row_identity(current, "transaction_id"):
            reasons.append("SOURCE_RECORD_ID_MISSING")
        if execution_mode == ExecutionMode.PRODUCTION:
            mapping_ready = False
            reasons.append("PRODUCTION_PUBLICATION_AUTHORITY_PENDING")
        if not mapping_ready:
            reasons.append("MAPPING_UNAVAILABLE")
        if not window_complete:
            reasons.append("INCOMPLETE_90_DAY_WINDOW")
        if initiator_id:
            if initiator_id != customer_id:
                reasons.append("INITIATOR_UNRESOLVED")
            attribution_method = "SOURCE_INITIATOR"
        else:
            owners = tuple(dict.fromkeys(effective_owner_ids))
            attribution_method = "SOLE_EFFECTIVE_OWNER"
            if len(owners) != 1 or owners[0] != customer_id:
                reasons.append("JOINT_ACCOUNT_INITIATOR_UNRESOLVED" if len(owners) > 1 else "OWNER_UNRESOLVED")
        status = str(current.get("transaction_status", ""))
        currency = str(current.get("currency", ""))
        try:
            signed_amount = _decimal(current.get("amount"))
            amount = abs(signed_amount)
        except (InvalidOperation, TypeError):
            reasons.append("INVALID_CURRENT_AMOUNT")
            signed_amount = Decimal(0)
            amount = Decimal(0)
        if status in cls.EXCLUDED_RC01 and not reasons:
            excluded_evidence = list(_publication_evidence(publication)) if publication else []
            excluded_evidence.extend((f"source_transaction_id={current.get('transaction_id')}",
                                      f"recognized_excluded_status={status}"))
            if not result_lineage:
                return _result("RC-01", ConditionState.UNKNOWN, excluded_evidence,
                               result_lineage, cls.RC01_VERSION,
                               ("DELIVERY_LINEAGE_MISSING",), as_of)
            return _result("RC-01", ConditionState.NOT_TRIGGERED, excluded_evidence,
                           result_lineage, cls.RC01_VERSION, as_of=as_of)
        if status not in cls.FINALIZED_RC01:
            reasons.append("CURRENT_STATUS_UNMAPPED")
        if not currency or amount == 0:
            reasons.append("INVALID_CURRENT_CURRENCY_OR_ZERO_AMOUNT")
        # DD-05 uses preceding Chicago calendar days. Local wall-time subtraction
        # preserves the boundary across 23/25-hour DST transitions.
        window_start = (as_of.astimezone(CHICAGO_TZ) - timedelta(days=90)).astimezone(timezone.utc)
        eligible: list[Decimal] = []
        for row in prior:
            try:
                occurred = _instant(row.get("occurred_at", row.get("posted_at")))
                prior_amount = abs(_decimal(row.get("amount")))
            except (ValueError, InvalidOperation, TypeError):
                reasons.append("INVALID_PRIOR_EVIDENCE")
                continue
            if row.get("attributed_customer_id") != customer_id:
                reasons.append("PRIOR_ATTRIBUTION_UNRESOLVED")
                continue
            if not row.get("publication_version") or row.get("revision") in (None, ""):
                reasons.append("PRIOR_PUBLICATION_LINEAGE_MISSING")
                continue
            if (window_start <= occurred < as_of and occurred != as_of
                    and row.get("transaction_status") in cls.FINALIZED_RC01
                    and row.get("currency") == currency and prior_amount != 0):
                eligible.append(prior_amount)
        if len(eligible) < 5:
            reasons.append("FEWER_THAN_FIVE_ELIGIBLE_PRIORS")
        base_evidence = list(_publication_evidence(publication)) if publication else []
        base_evidence.extend((
            f"source_transaction_id={current.get('transaction_id')}",
            f"window_start={window_start.isoformat()}",
            f"window_end={as_of.astimezone(timezone.utc).isoformat()}",
            f"currency={currency}",
            f"signed_amount={current.get('amount')}",
            f"absolute_amount={amount}",
            f"direction={'CREDIT' if signed_amount > 0 else 'DEBIT' if signed_amount < 0 else 'ZERO'}",
            f"attribution_method={attribution_method}",
        ))
        if reasons:
            return _result("RC-01", ConditionState.UNKNOWN, (*base_evidence, f"eligible_prior_count={len(eligible)}"),
                           result_lineage, cls.RC01_VERSION, dict.fromkeys(reasons), as_of)
        prior_sum = sum(eligible, Decimal(0))
        if prior_sum == 0:
            return _result("RC-01", ConditionState.UNKNOWN, base_evidence, result_lineage, cls.RC01_VERSION,
                           ("ZERO_PRIOR_AVERAGE",), as_of)
        triggered = amount * len(eligible) >= Decimal(3) * prior_sum
        if not triggered and not result_lineage:
            return _result("RC-01", ConditionState.UNKNOWN,
                           (*base_evidence, f"prior_sum={prior_sum}", f"prior_count={len(eligible)}"),
                           result_lineage, cls.RC01_VERSION,
                           ("DELIVERY_LINEAGE_MISSING",), as_of)
        return _result("RC-01", ConditionState.TRIGGERED if triggered else ConditionState.NOT_TRIGGERED,
                       (*base_evidence, f"prior_sum={prior_sum}", f"prior_count={len(eligible)}"),
                       result_lineage, cls.RC01_VERSION, as_of=as_of)

    @classmethod
    def rc01_customer_day(
        cls,
        current_transactions: Sequence[Mapping[str, Any]],
        prior_transactions: Sequence[Mapping[str, Any]],
        *,
        customer_id: str,
        as_of: datetime,
        publication: PublicationEvidence | None,
        window_complete: bool,
        mapping_ready: bool,
        execution_mode: ExecutionMode,
        lineage_references: Sequence[str] = (),
    ) -> RiskConditionResult:
        """Aggregate eligible current events once per customer/day and revision."""
        _require_execution_mode(execution_mode)
        reasons = list(_publication_reasons(publication))
        reasons.extend(_row_contract_reasons(current_transactions))
        reasons.extend(_required_mapping_reasons(publication, (("SRC-01", "transaction_status"),)))
        if execution_mode == ExecutionMode.PRODUCTION:
            mapping_ready = False
            reasons.append("PRODUCTION_PUBLICATION_AUTHORITY_PENDING")
        if not mapping_ready:
            reasons.append("MAPPING_UNAVAILABLE")
        if reasons:
            evidence = _publication_evidence(publication) if publication else ()
            return _result("RC-01", ConditionState.UNKNOWN, evidence, lineage_references,
                           cls.RC01_VERSION, dict.fromkeys(reasons), as_of)
        assert publication is not None
        try:
            current_rows = [
                row for row in _selected_rows(current_transactions, publication)
                if _instant(row.get("occurred_at", row.get("posted_at"))).astimezone(CHICAGO_TZ).date()
                == publication.business_date
            ]
        except (TypeError, ValueError):
            return _result("RC-01", ConditionState.UNKNOWN, _publication_evidence(publication),
                           lineage_references, cls.RC01_VERSION,
                           ("MALFORMED_CURRENT_EVENT_TIMESTAMP",), as_of)
        if not current_rows:
            empty_evidence = (*_publication_evidence(publication), "selected_record_count=0")
            if publication.zero_row_confirmed:
                evidence = (*empty_evidence, "manifest_confirmed_zero_events=true")
                if not lineage_references:
                    return _result("RC-01", ConditionState.UNKNOWN, evidence,
                                   lineage_references, cls.RC01_VERSION,
                                   ("DELIVERY_LINEAGE_MISSING",), as_of)
                return _result("RC-01", ConditionState.NOT_TRIGGERED, evidence,
                               lineage_references, cls.RC01_VERSION, as_of=as_of)
            return _result("RC-01", ConditionState.UNKNOWN, empty_evidence, lineage_references,
                           cls.RC01_VERSION, ("ZERO_EVENTS_NOT_MANIFEST_CONFIRMED",), as_of)

        outcomes: list[RiskConditionResult] = []
        evaluated_rows: list[Mapping[str, Any]] = []
        for current in current_rows:
            event_customer = current.get("customer_id")
            if event_customer not in (None, customer_id):
                continue
            evaluated_rows.append(current)
            outcomes.append(cls.rc01(
                current,
                prior_transactions,
                customer_id=customer_id,
                effective_owner_ids=tuple(current.get("effective_owner_ids", ())),
                initiator_id=current.get("initiator_id"),
                window_complete=window_complete,
                mapping_ready=mapping_ready,
                execution_mode=execution_mode,
                publication=publication,
                lineage_references=tuple(current.get("lineage_references", ())),
            ))
        if not outcomes:
            evidence = (*_publication_evidence(publication),
                        f"selected_record_count={len(current_rows)}")
            return _result("RC-01", ConditionState.UNKNOWN, evidence, lineage_references,
                           cls.RC01_VERSION, ("CUSTOMER_CURRENT_POPULATION_UNRESOLVED",), as_of)
        triggered = [item for item in outcomes if item.state == ConditionState.TRIGGERED]
        unknown = [item for item in outcomes if item.state == ConditionState.UNKNOWN]
        state = (ConditionState.TRIGGERED if triggered else
                 ConditionState.UNKNOWN if unknown else ConditionState.NOT_TRIGGERED)
        evidence = [*_publication_evidence(publication), f"evaluated_event_count={len(outcomes)}"]
        evidence.extend(f"source_transaction_id={row.get('transaction_id')}" for row in evaluated_rows)
        for row, outcome in zip(evaluated_rows, outcomes):
            tx_id = row.get("transaction_id")
            evidence.extend(f"comparison:{tx_id}:{item}" for item in outcome.evidence)
        evidence.extend(
            f"triggering_transaction={row.get('transaction_id')}"
            for row, outcome in zip(evaluated_rows, outcomes)
            if outcome.state == ConditionState.TRIGGERED
        )
        if publication.supersedes_revision is not None:
            evidence.append(f"supersedes_revision={publication.supersedes_revision}")
        missing = tuple(dict.fromkeys(
            reason for outcome in unknown for reason in outcome.missing_evidence_reasons
        ))
        combined_lineage = list(lineage_references)
        for outcome in outcomes:
            combined_lineage.extend(outcome.lineage_references)
        deduplicated_lineage = tuple(dict.fromkeys(combined_lineage))
        if state == ConditionState.NOT_TRIGGERED and not deduplicated_lineage:
            return _result("RC-01", ConditionState.UNKNOWN, evidence, deduplicated_lineage,
                           cls.RC01_VERSION, ("DELIVERY_LINEAGE_MISSING",), as_of)
        return _result("RC-01", state, evidence, deduplicated_lineage,
                       cls.RC01_VERSION, missing, as_of)

    @classmethod
    def rc02(cls, alerts: Sequence[Mapping[str, Any]], *, as_of: datetime,
             mapping_ready: bool, execution_mode: ExecutionMode,
             publication: PublicationEvidence | None,
             lineage_references: Sequence[str] = ()) -> RiskConditionResult:
        _require_execution_mode(execution_mode)
        domains = (("SRC-03", "fraud_case_status"), ("SRC-03", "fraud_severity"))
        reasons = list(_publication_reasons(publication))
        reasons.extend(_row_contract_reasons(alerts))
        reasons.extend(_required_mapping_reasons(publication, domains))
        if execution_mode == ExecutionMode.PRODUCTION:
            reasons.append("PRODUCTION_PUBLICATION_AUTHORITY_PENDING")
        if not mapping_ready or not cls._production_mapping_ready(
            execution_mode, publication, domains,
        ):
            reasons.append("MAPPING_UNAVAILABLE")
        if reasons:
            evidence = _publication_evidence(publication) if publication else ()
            return _result("RC-02", ConditionState.UNKNOWN, evidence, lineage_references, cls.RC02_VERSION, reasons, as_of)
        assert publication is not None
        selected: dict[str, Mapping[str, Any]] = {}
        try:
            selected_rows = _selected_rows(alerts, publication)
            for alert in selected_rows:
                if _instant(alert["effective_start"]) > as_of:
                    continue
                key = str(alert.get("alert_id"))
                if key not in selected or _instant(alert["effective_start"]) > _instant(selected[key]["effective_start"]):
                    selected[key] = alert
        except (KeyError, TypeError, ValueError):
            return _result("RC-02", ConditionState.UNKNOWN, _publication_evidence(publication),
                           lineage_references, cls.RC02_VERSION, ("MALFORMED_ALERT_STATE",), as_of)
        matches = [a for a in selected.values() if a.get("case_status") == "OPEN" and a.get("severity") in cls.SIGNIFICANT_SEVERITY]
        evidence = [*_publication_evidence(publication), f"selected_record_count={len(selected)}"]
        evidence.extend(f"source_alert_id={a.get('alert_id')}" for a in selected.values())
        result_lineage = _combined_lineage(lineage_references, tuple(selected.values()))
        if not matches and not result_lineage:
            return _result("RC-02", ConditionState.UNKNOWN, evidence, result_lineage,
                           cls.RC02_VERSION, ("DELIVERY_LINEAGE_MISSING",), as_of)
        return _result("RC-02", ConditionState.TRIGGERED if matches else ConditionState.NOT_TRIGGERED,
                       evidence, result_lineage, cls.RC02_VERSION, as_of=as_of)

    @classmethod
    def rc03(cls, positions: Sequence[Mapping[str, Any]], related_loan_ids: Sequence[str], *,
             as_of: datetime, mapping_ready: bool, execution_mode: ExecutionMode,
             publication: PublicationEvidence | None,
             lineage_references: Sequence[str] = ()) -> RiskConditionResult:
        _require_execution_mode(execution_mode)
        domains = (("SRC-02", "loan_status"),)
        reasons = list(_publication_reasons(publication))
        reasons.extend(_row_contract_reasons(positions))
        reasons.extend(_required_mapping_reasons(publication, domains))
        if execution_mode == ExecutionMode.PRODUCTION:
            reasons.append("PRODUCTION_PUBLICATION_AUTHORITY_PENDING")
        if not mapping_ready or not cls._production_mapping_ready(
            execution_mode, publication, domains,
        ):
            reasons.append("MAPPING_UNAVAILABLE")
        if reasons:
            evidence = _publication_evidence(publication) if publication else ()
            return _result("RC-03", ConditionState.UNKNOWN, evidence, lineage_references, cls.RC03_VERSION, reasons, as_of)
        assert publication is not None
        if publication.business_date != as_of.astimezone(CHICAGO_TZ).date():
            return _result("RC-03", ConditionState.UNKNOWN, _publication_evidence(publication),
                           lineage_references, cls.RC03_VERSION,
                           ("ASSESSMENT_SNAPSHOT_DATE_MISMATCH",), as_of)
        related = set(related_loan_ids)
        rows = _selected_rows(positions, publication)
        valid_rows: list[Mapping[str, Any]] = []
        try:
            for position in rows:
                if _date_value(position.get("business_date")) != publication.business_date:
                    return _result("RC-03", ConditionState.UNKNOWN, _publication_evidence(publication),
                                   lineage_references, cls.RC03_VERSION,
                                   ("SNAPSHOT_BUSINESS_DATE_MISMATCH",), as_of)
                int(position.get("days_past_due"))
                valid_rows.append(position)
        except (TypeError, ValueError):
            return _result("RC-03", ConditionState.UNKNOWN, _publication_evidence(publication),
                           lineage_references, cls.RC03_VERSION,
                           ("MALFORMED_SNAPSHOT_IDENTITY_OR_DPD",), as_of)
        matches = [p for p in valid_rows if p.get("loan_id") in related and p.get("loan_status") in cls.ACTIVE_LOAN and int(p["days_past_due"]) > 30]
        evidence = [*_publication_evidence(publication), f"selected_record_count={len(valid_rows)}"]
        evidence.extend(f"source_loan_id={p.get('loan_id')}" for p in valid_rows)
        result_lineage = _combined_lineage(lineage_references, valid_rows)
        if not matches and not result_lineage:
            return _result("RC-03", ConditionState.UNKNOWN, evidence, result_lineage,
                           cls.RC03_VERSION, ("DELIVERY_LINEAGE_MISSING",), as_of)
        return _result("RC-03", ConditionState.TRIGGERED if matches else ConditionState.NOT_TRIGGERED,
                       evidence, result_lineage, cls.RC03_VERSION, as_of=as_of)

    @classmethod
    def rc04(cls, complaints: Sequence[Mapping[str, Any]], *, as_of: datetime,
             mapping_ready: bool, execution_mode: ExecutionMode,
             publication: PublicationEvidence | None,
             lineage_references: Sequence[str] = ()) -> RiskConditionResult:
        _require_execution_mode(execution_mode)
        domains = (("SRC-04", "complaint_status"), ("SRC-04", "complaint_priority"))
        reasons = list(_publication_reasons(publication))
        reasons.extend(_row_contract_reasons(complaints))
        reasons.extend(_required_mapping_reasons(publication, domains))
        if execution_mode == ExecutionMode.PRODUCTION:
            reasons.append("PRODUCTION_PUBLICATION_AUTHORITY_PENDING")
        if not mapping_ready or not cls._production_mapping_ready(
            execution_mode, publication, domains,
        ):
            reasons.append("MAPPING_UNAVAILABLE")
        if reasons:
            evidence = _publication_evidence(publication) if publication else ()
            return _result("RC-04", ConditionState.UNKNOWN, evidence, lineage_references, cls.RC04_VERSION, reasons, as_of)
        assert publication is not None
        matches: list[Mapping[str, Any]] = []
        selected_rows = _selected_rows(complaints, publication)
        try:
            for c in selected_rows:
                priority = c.get("priority_at_creation", c.get("priority"))
                if priority not in cls.SLA_HOURS:
                    return _result("RC-04", ConditionState.UNKNOWN, _publication_evidence(publication), lineage_references, cls.RC04_VERSION, ("PRIORITY_MAPPING_UNAVAILABLE",), as_of)
                if c.get("complaint_status") in {"OPEN", "IN_PROGRESS", "REOPENED"}:
                    if as_of - _instant(c["created_at"]) > timedelta(hours=cls.SLA_HOURS[priority]):
                        matches.append(c)
        except (KeyError, TypeError, ValueError):
            return _result("RC-04", ConditionState.UNKNOWN, _publication_evidence(publication),
                           lineage_references, cls.RC04_VERSION, ("MALFORMED_COMPLAINT_STATE",), as_of)
        evidence = [*_publication_evidence(publication), f"selected_record_count={len(selected_rows)}"]
        evidence.extend(f"source_complaint_id={c.get('complaint_id')}" for c in selected_rows)
        result_lineage = _combined_lineage(lineage_references, selected_rows)
        if not matches and not result_lineage:
            return _result("RC-04", ConditionState.UNKNOWN, evidence, result_lineage,
                           cls.RC04_VERSION, ("DELIVERY_LINEAGE_MISSING",), as_of)
        return _result("RC-04", ConditionState.TRIGGERED if matches else ConditionState.NOT_TRIGGERED,
                       evidence, result_lineage, cls.RC04_VERSION, as_of=as_of)

    @classmethod
    def rc05(cls, states: Sequence[Mapping[str, Any]], related_account_ids: Sequence[str], *,
             as_of: datetime, mapping_ready: bool, execution_mode: ExecutionMode,
             publication: PublicationEvidence | None,
             lineage_references: Sequence[str] = ()) -> RiskConditionResult:
        _require_execution_mode(execution_mode)
        domains = (("SRC-01", "restriction_status"),)
        reasons = list(_publication_reasons(publication))
        reasons.extend(_row_contract_reasons(states))
        reasons.extend(_required_mapping_reasons(publication, domains))
        if execution_mode == ExecutionMode.PRODUCTION:
            reasons.append("PRODUCTION_PUBLICATION_AUTHORITY_PENDING")
        if not mapping_ready or not cls._production_mapping_ready(
            execution_mode, publication, domains,
        ):
            reasons.append("MAPPING_UNAVAILABLE")
        if reasons:
            evidence = _publication_evidence(publication) if publication else ()
            return _result("RC-05", ConditionState.UNKNOWN, evidence, lineage_references, cls.RC05_VERSION, reasons, as_of)
        assert publication is not None
        related = set(related_account_ids)
        selected: dict[str, Mapping[str, Any]] = {}
        selected_rows = _selected_rows(states, publication)
        try:
            for state in selected_rows:
                key = str(state.get("account_id"))
                if key in related and _instant(state["effective_start"]) <= as_of:
                    if key not in selected or _instant(state["effective_start"]) > _instant(selected[key]["effective_start"]):
                        selected[key] = state
        except (KeyError, TypeError, ValueError):
            return _result("RC-05", ConditionState.UNKNOWN, _publication_evidence(publication),
                           lineage_references, cls.RC05_VERSION, ("MALFORMED_RESTRICTION_STATE",), as_of)
        matches = [s for s in selected.values() if s.get("restriction_status") in cls.RESTRICTED]
        evidence = [*_publication_evidence(publication), f"selected_record_count={len(selected)}"]
        evidence.extend(f"source_account_id={s.get('account_id')}" for s in selected.values())
        result_lineage = _combined_lineage(lineage_references, tuple(selected.values()))
        if not matches and not result_lineage:
            return _result("RC-05", ConditionState.UNKNOWN, evidence, result_lineage,
                           cls.RC05_VERSION, ("DELIVERY_LINEAGE_MISSING",), as_of)
        return _result("RC-05", ConditionState.TRIGGERED if matches else ConditionState.NOT_TRIGGERED,
                       evidence, result_lineage, cls.RC05_VERSION, as_of=as_of)
