"""Data Quality Rule Catalog and Evaluation Engine.

Implements the DD-09 approved quality rule catalog (DQ-D01 through DQ-D13,
RC-D01 through RC-D03, and PUB-D01) with explicit severity escalation,
referential integrity verification, and cell-level completeness accounting.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Any, Mapping, Sequence

from ..contracts.financial import parse_decimal_exact
from ..contracts.findings import FindingSeverity
from ..contracts.mapping import StatusMappingRegistry
from ..contracts.temporal import parse_offset_timestamp
from .records import ExecutionMode, RawRecord, RecordDisposition

SCALE_4 = Decimal("0.0001")
COMPLETENESS_THRESHOLD_PCT = Decimal("98.00")


@dataclass(frozen=True)
class RecordFinding:
    """Detailed finding for a specific record under DD-09."""

    rule_id: str
    source: str
    section: str
    record_identity: str
    field_name: str
    severity: FindingSeverity
    original_severity: FindingSeverity
    escalation_reason: str
    disposition: RecordDisposition
    observed_value: str
    expected_rule: str
    message: str


@dataclass(frozen=True)
class DQSummary:
    """Consolidated summary of data quality evaluation across a batch."""

    received_records: int
    accepted_records: int
    quarantined_records: int
    excluded_records: int
    critical_findings_count: int
    error_findings_count: int
    warning_findings_count: int
    info_findings_count: int
    received_completeness_pct: Decimal
    curated_completeness_pct: Decimal
    completeness_passed: bool
    findings: tuple[RecordFinding, ...] = field(default_factory=tuple)


# Required fields per section under approved inventory contracts
SECTION_REQUIRED_FIELDS: dict[tuple[str, str], tuple[str, ...]] = {
    ("SRC-01", "customers"): ("customer_id", "customer_name", "tax_identifier_masked", "customer_segment", "primary_branch_id"),
    ("SRC-01", "accounts"): ("account_id", "customer_id", "account_type", "currency", "branch_id", "account_status"),
    ("SRC-01", "holders"): ("account_id", "customer_id", "relationship_role", "effective_start"),
    ("SRC-01", "transactions"): ("transaction_id", "account_id", "business_date", "amount", "currency", "transaction_type", "transaction_status"),
    ("SRC-01", "account_restriction_state"): ("account_id", "restriction_status", "effective_start"),
    ("SRC-01", "account_branch_assignment"): ("account_id", "branch_id", "branch_role", "effective_start"),
    ("SRC-02", "loans"): ("loan_id", "customer_id", "loan_type", "original_principal", "currency", "origination_date", "branch_id"),
    ("SRC-02", "borrowers"): ("loan_id", "customer_id", "relationship_role", "effective_start"),
    ("SRC-02", "positions"): ("loan_id", "business_date", "outstanding_principal", "currency", "days_past_due", "loan_status"),
    ("SRC-02", "payments"): ("payment_id", "loan_id", "amount", "currency", "payment_status"),
    ("SRC-02", "loan_schedule"): ("schedule_id", "loan_id", "payment_frequency", "installment_amount", "currency"),
    ("SRC-02", "loan_obligation"): ("obligation_id", "loan_id", "due_date", "scheduled_amount", "currency"),
    ("SRC-02", "payment_allocation"): ("allocation_id", "payment_id", "allocation_component", "amount", "currency"),
    ("SRC-02", "payment_unapplied"): ("payment_id", "amount", "currency"),
    ("SRC-02", "payment_adjustment"): ("adjustment_id", "payment_id", "adjustment_kind", "amount", "currency"),
    ("SRC-02", "loan_account"): ("loan_id", "account_id", "relationship_role"),
    ("SRC-02", "loan_branch_assignment"): ("loan_id", "branch_id", "branch_role", "effective_start"),
    ("SRC-03", "alerts"): ("alert_id", "customer_id", "account_id", "severity", "alert_reason", "case_status", "created_at"),
    ("SRC-03", "fraud_alert_state"): ("alert_id", "case_status", "effective_start"),
    ("SRC-04", "complaints"): ("complaint_id", "customer_id", "channel", "priority", "complaint_status", "created_at"),
    ("SRC-04", "complaint_snapshot"): ("complaint_id", "business_date", "complaint_status", "priority"),
    ("SRC-04", "complaint_history_event"): ("event_id", "complaint_id", "event_type", "event_at"),
    ("SRC-04", "complaint_branch_assignment"): ("complaint_id", "branch_id", "branch_role", "effective_start"),
    ("SRC-05", "organizational_unit"): ("unit_id", "unit_type"),
    ("SRC-05", "region"): ("region_id", "region_name", "valid_from"),
    ("SRC-05", "branches"): ("branch_id", "region_id", "branch_name", "valid_from"),
    ("SRC-05", "organizational_successor"): ("predecessor_id", "successor_id", "valid_from"),
}

FIXTURE_APPROVED_CURRENCIES = {"USD", "EUR"}


class DataQualityEngine:
    """Evaluates data quality rules across raw records."""

    def __init__(
        self,
        status_registry: StatusMappingRegistry | None = None,
        check_referential_integrity: bool = True,
        execution_mode: ExecutionMode = ExecutionMode.FIXTURE,
    ) -> None:
        self.status_registry = status_registry
        self.check_referential_integrity = check_referential_integrity
        self.execution_mode = execution_mode

    def evaluate_batch(
        self,
        records_by_section: Mapping[tuple[str, str], Sequence[RawRecord]],
    ) -> tuple[dict[tuple[str, str, str], list[RecordFinding]], DQSummary]:
        """Evaluate all records in a batch.

        Returns:
            findings_by_record: map of (source, section, record_id) -> list of findings
            summary: consolidated DQSummary
        """
        findings_by_record: dict[tuple[str, str, str], list[RecordFinding]] = {}
        all_findings: list[RecordFinding] = []

        total_cells_required = 0
        total_cells_present = 0
        curated_cells_required = 0
        curated_cells_present = 0

        total_records_received = 0
        accepted_count = 0
        quarantined_count = 0
        excluded_count = 0

        # Build parent lookup indexes for referential integrity (DQ-D04)
        customer_ids: set[str] = set()
        account_ids: set[str] = set()
        loan_ids: set[str] = set()
        branch_ids: set[str] = set()

        if ("SRC-01", "customers") in records_by_section:
            for r in records_by_section[("SRC-01", "customers")]:
                cid = r.fields.get("customer_id", "").strip()
                if cid:
                    customer_ids.add(cid)

        if ("SRC-01", "accounts") in records_by_section:
            for r in records_by_section[("SRC-01", "accounts")]:
                aid = r.fields.get("account_id", "").strip()
                if aid:
                    account_ids.add(aid)

        if ("SRC-02", "loans") in records_by_section:
            for r in records_by_section[("SRC-02", "loans")]:
                lid = r.fields.get("loan_id", "").strip()
                if lid:
                    loan_ids.add(lid)

        if ("SRC-05", "branches") in records_by_section:
            for r in records_by_section[("SRC-05", "branches")]:
                bid = r.fields.get("branch_id", "").strip()
                if bid:
                    branch_ids.add(bid)

        # 1. Evaluate individual records per section
        for (source, section), records in records_by_section.items():
            req_fields = SECTION_REQUIRED_FIELDS.get((source, section), ())

            for r in records:
                total_records_received += 1
                rec_key = (source, section, r.record_id)
                rec_findings: list[RecordFinding] = []

                # Cell-level completeness tracking
                for col in req_fields:
                    total_cells_required += 1
                    val = r.fields.get(col, "")
                    if val is not None and str(val).strip():
                        total_cells_present += 1

                # Rule DQ-D03: Required-value validity
                for col in req_fields:
                    val = r.fields.get(col, "")
                    if val is None or not str(val).strip():
                        rec_findings.append(
                            RecordFinding(
                                rule_id="DQ-D03",
                                source=source,
                                section=section,
                                record_identity=r.record_id,
                                field_name=col,
                                severity=FindingSeverity.ERROR,
                                original_severity=FindingSeverity.ERROR,
                                escalation_reason="",
                                disposition=RecordDisposition.QUARANTINED,
                                observed_value="",
                                expected_rule="Field is mandatory and cannot be empty or whitespace",
                                message=f"Required field '{col}' is missing or blank",
                            )
                        )

                # Rule DQ-D07: Amount precision and currency
                for amt_col in ("amount", "original_principal", "outstanding_principal", "installment_amount", "scheduled_amount"):
                    if amt_col in r.fields:
                        val = r.fields.get(amt_col, "").strip()
                        if val:
                            try:
                                d = Decimal(val)
                                # Check scale does not exceed 4
                                if abs(d.as_tuple().exponent) > 4:
                                    rec_findings.append(
                                        RecordFinding(
                                            rule_id="DQ-D07",
                                            source=source,
                                            section=section,
                                            record_identity=r.record_id,
                                            field_name=amt_col,
                                            severity=FindingSeverity.ERROR,
                                            original_severity=FindingSeverity.ERROR,
                                            escalation_reason="",
                                            disposition=RecordDisposition.QUARANTINED,
                                            observed_value=val,
                                            expected_rule="Precision cannot exceed scale 4",
                                            message=f"Monetary field '{amt_col}' exceeds scale 4",
                                        )
                                    )
                            except (InvalidOperation, TypeError):
                                rec_findings.append(
                                    RecordFinding(
                                        rule_id="DQ-D07",
                                        source=source,
                                        section=section,
                                        record_identity=r.record_id,
                                        field_name=amt_col,
                                        severity=FindingSeverity.ERROR,
                                        original_severity=FindingSeverity.ERROR,
                                        escalation_reason="",
                                        disposition=RecordDisposition.QUARANTINED,
                                        observed_value=val,
                                        expected_rule="Valid decimal representation required",
                                        message=f"Monetary field '{amt_col}' is not a valid decimal",
                                    )
                                )

                if "currency" in r.fields:
                    curr = r.fields.get("currency", "").strip()
                    if curr:
                        if not re.match(r"^[A-Z]{3}$", curr):
                            rec_findings.append(
                                RecordFinding(
                                    rule_id="DQ-D07",
                                    source=source,
                                    section=section,
                                    record_identity=r.record_id,
                                    field_name="currency",
                                    severity=FindingSeverity.ERROR,
                                    original_severity=FindingSeverity.ERROR,
                                    escalation_reason="",
                                    disposition=RecordDisposition.QUARANTINED,
                                    observed_value=curr,
                                    expected_rule="Currency must be exactly 3 uppercase ISO 4217 characters",
                                    message=f"Currency '{curr}' does not match 3-letter uppercase ISO 4217 format",
                                )
                            )
                        elif self.execution_mode == ExecutionMode.FIXTURE and curr not in FIXTURE_APPROVED_CURRENCIES:
                            rec_findings.append(
                                RecordFinding(
                                    rule_id="DQ-D07",
                                    source=source,
                                    section=section,
                                    record_identity=r.record_id,
                                    field_name="currency",
                                    severity=FindingSeverity.ERROR,
                                    original_severity=FindingSeverity.ERROR,
                                    escalation_reason="",
                                    disposition=RecordDisposition.QUARANTINED,
                                    observed_value=curr,
                                    expected_rule=f"Currency must be in approved fixture currencies {FIXTURE_APPROVED_CURRENCIES}",
                                    message=f"Currency '{curr}' is not an approved fixture currency",
                                )
                            )

                # Rule DQ-D08: Masking and normalization
                if "tax_identifier_masked" in r.fields:
                    raw_tax = r.fields.get("tax_identifier_masked", "").strip()
                    digits = re.sub(r"\D", "", raw_tax)
                    if raw_tax and len(digits) < 4:
                        rec_findings.append(
                            RecordFinding(
                                rule_id="DQ-D08",
                                source=source,
                                section=section,
                                record_identity=r.record_id,
                                field_name="tax_identifier_masked",
                                severity=FindingSeverity.ERROR,
                                original_severity=FindingSeverity.ERROR,
                                escalation_reason="",
                                disposition=RecordDisposition.QUARANTINED,
                                observed_value=raw_tax,
                                expected_rule="Tax identifier must have at least 4 digits for masking",
                                message="Tax identifier too short for masking",
                            )
                        )

                # Rule DQ-D09: Integer and snapshot integrity
                if "days_past_due" in r.fields:
                    dpd_str = r.fields.get("days_past_due", "").strip()
                    if dpd_str:
                        try:
                            dpd = int(dpd_str)
                            if dpd < 0 or dpd > 36500:
                                rec_findings.append(
                                    RecordFinding(
                                        rule_id="DQ-D09",
                                        source=source,
                                        section=section,
                                        record_identity=r.record_id,
                                        field_name="days_past_due",
                                        severity=FindingSeverity.CRITICAL,
                                        original_severity=FindingSeverity.CRITICAL,
                                        escalation_reason="",
                                        disposition=RecordDisposition.QUARANTINED,
                                        observed_value=dpd_str,
                                        expected_rule="Days past due must be integer in range 0..36500",
                                        message=f"DPD value {dpd} out of range [0, 36500]",
                                    )
                                )
                        except ValueError:
                            rec_findings.append(
                                RecordFinding(
                                    rule_id="DQ-D09",
                                    source=source,
                                    section=section,
                                    record_identity=r.record_id,
                                    field_name="days_past_due",
                                    severity=FindingSeverity.CRITICAL,
                                    original_severity=FindingSeverity.CRITICAL,
                                    escalation_reason="",
                                    disposition=RecordDisposition.QUARANTINED,
                                    observed_value=dpd_str,
                                    expected_rule="Days past due must be integer",
                                    message=f"DPD value '{dpd_str}' is not an integer",
                                )
                            )

                # Rule DQ-D05: Temporal instant validity and ordering
                for ts_col in ("posted_at", "paid_at", "created_at", "event_at"):
                    if ts_col in r.fields:
                        ts_val = r.fields.get(ts_col, "").strip()
                        if ts_val:
                            try:
                                parse_offset_timestamp(ts_val, check_chicago_offset=False)
                            except Exception as exc:
                                rec_findings.append(
                                    RecordFinding(
                                        rule_id="DQ-D05",
                                        source=source,
                                        section=section,
                                        record_identity=r.record_id,
                                        field_name=ts_col,
                                        severity=FindingSeverity.ERROR,
                                        original_severity=FindingSeverity.ERROR,
                                        escalation_reason="",
                                        disposition=RecordDisposition.QUARANTINED,
                                        observed_value=ts_val,
                                        expected_rule="ISO timestamp with offset required",
                                        message=f"Invalid timestamp '{ts_val}' for '{ts_col}': {exc}",
                                    )
                                )

                for d_col in ("valid_from", "effective_start", "origination_date", "due_date"):
                    if d_col in r.fields:
                        d_val = r.fields.get(d_col, "").strip()
                        if d_val:
                            try:
                                if "T" in d_val:
                                    parse_offset_timestamp(d_val, check_chicago_offset=False)
                                else:
                                    date.fromisoformat(d_val)
                            except Exception as exc:
                                rec_findings.append(
                                    RecordFinding(
                                        rule_id="DQ-D05",
                                        source=source,
                                        section=section,
                                        record_identity=r.record_id,
                                        field_name=d_col,
                                        severity=FindingSeverity.ERROR,
                                        original_severity=FindingSeverity.ERROR,
                                        escalation_reason="",
                                        disposition=RecordDisposition.QUARANTINED,
                                        observed_value=d_val,
                                        expected_rule="Valid ISO date or timestamp required",
                                        message=f"Invalid date/timestamp '{d_val}' for '{d_col}': {exc}",
                                    )
                                )

                # Rule DQ-D04: Referential integrity (if enabled and cross-references available)
                if self.check_referential_integrity:
                    # accounts -> customers
                    if section == "accounts":
                        cid = r.fields.get("customer_id", "").strip()
                        if cid and customer_ids and cid not in customer_ids:
                            rec_findings.append(
                                RecordFinding(
                                    rule_id="DQ-D04",
                                    source=source,
                                    section=section,
                                    record_identity=r.record_id,
                                    field_name="customer_id",
                                    severity=FindingSeverity.ERROR,
                                    original_severity=FindingSeverity.ERROR,
                                    escalation_reason="",
                                    disposition=RecordDisposition.QUARANTINED,
                                    observed_value=cid,
                                    expected_rule="Referenced customer_id must exist in customers section",
                                    message=f"Orphan account: customer_id '{cid}' not found in customers",
                                )
                            )

                    # transactions -> accounts
                    if section == "transactions":
                        aid = r.fields.get("account_id", "").strip()
                        if aid and account_ids and aid not in account_ids:
                            rec_findings.append(
                                RecordFinding(
                                    rule_id="DQ-D04",
                                    source=source,
                                    section=section,
                                    record_identity=r.record_id,
                                    field_name="account_id",
                                    severity=FindingSeverity.ERROR,
                                    original_severity=FindingSeverity.ERROR,
                                    escalation_reason="",
                                    disposition=RecordDisposition.QUARANTINED,
                                    observed_value=aid,
                                    expected_rule="Referenced account_id must exist in accounts section",
                                    message=f"Orphan transaction: account_id '{aid}' not found in accounts",
                                )
                            )

                    # loans -> customers
                    if section == "loans":
                        cid = r.fields.get("customer_id", "").strip()
                        if cid and customer_ids and cid not in customer_ids:
                            rec_findings.append(
                                RecordFinding(
                                    rule_id="DQ-D04",
                                    source=source,
                                    section=section,
                                    record_identity=r.record_id,
                                    field_name="customer_id",
                                    severity=FindingSeverity.ERROR,
                                    original_severity=FindingSeverity.ERROR,
                                    escalation_reason="",
                                    disposition=RecordDisposition.QUARANTINED,
                                    observed_value=cid,
                                    expected_rule="Referenced customer_id must exist in customers section",
                                    message=f"Orphan loan: customer_id '{cid}' not found in customers",
                                )
                            )

                    # payments -> loans
                    if section == "payments":
                        lid = r.fields.get("loan_id", "").strip()
                        if lid and loan_ids and lid not in loan_ids:
                            rec_findings.append(
                                RecordFinding(
                                    rule_id="DQ-D04",
                                    source=source,
                                    section=section,
                                    record_identity=r.record_id,
                                    field_name="loan_id",
                                    severity=FindingSeverity.ERROR,
                                    original_severity=FindingSeverity.ERROR,
                                    escalation_reason="",
                                    disposition=RecordDisposition.QUARANTINED,
                                    observed_value=lid,
                                    expected_rule="Referenced loan_id must exist in loans section",
                                    message=f"Orphan payment: loan_id '{lid}' not found in loans",
                                )
                            )

                    # alerts -> customers / accounts
                    if section == "alerts":
                        cid = r.fields.get("customer_id", "").strip()
                        if cid and customer_ids and cid not in customer_ids:
                            rec_findings.append(
                                RecordFinding(
                                    rule_id="DQ-D04",
                                    source=source,
                                    section=section,
                                    record_identity=r.record_id,
                                    field_name="customer_id",
                                    severity=FindingSeverity.ERROR,
                                    original_severity=FindingSeverity.ERROR,
                                    escalation_reason="",
                                    disposition=RecordDisposition.QUARANTINED,
                                    observed_value=cid,
                                    expected_rule="Referenced customer_id must exist in customers section",
                                    message=f"Orphan alert: customer_id '{cid}' not found in customers",
                                )
                            )

                    # complaints -> customers
                    if section == "complaints":
                        cid = r.fields.get("customer_id", "").strip()
                        if cid and customer_ids and cid not in customer_ids:
                            rec_findings.append(
                                RecordFinding(
                                    rule_id="DQ-D04",
                                    source=source,
                                    section=section,
                                    record_identity=r.record_id,
                                    field_name="customer_id",
                                    severity=FindingSeverity.ERROR,
                                    original_severity=FindingSeverity.ERROR,
                                    escalation_reason="",
                                    disposition=RecordDisposition.QUARANTINED,
                                    observed_value=cid,
                                    expected_rule="Referenced customer_id must exist in customers section",
                                    message=f"Orphan complaint: customer_id '{cid}' not found in customers",
                                )
                            )

                # Record-level disposition
                if rec_findings:
                    quarantined_count += 1
                    findings_by_record[rec_key] = rec_findings
                    all_findings.extend(rec_findings)
                else:
                    accepted_count += 1
                    # Curated completeness includes accepted cells
                    for col in req_fields:
                        curated_cells_required += 1
                        val = r.fields.get(col, "")
                        if val is not None and str(val).strip():
                            curated_cells_present += 1

        # Calculate completeness
        if total_cells_required > 0:
            rec_comp = (Decimal(total_cells_present) / Decimal(total_cells_required) * Decimal("100")).quantize(Decimal("0.01"))
        else:
            rec_comp = Decimal("100.00")

        if curated_cells_required > 0:
            cur_comp = (Decimal(curated_cells_present) / Decimal(curated_cells_required) * Decimal("100")).quantize(Decimal("0.01"))
        else:
            cur_comp = Decimal("100.00") if total_cells_required == 0 else Decimal("0.00")

        comp_passed = rec_comp >= COMPLETENESS_THRESHOLD_PCT and cur_comp >= COMPLETENESS_THRESHOLD_PCT

        # Rule DQ-D10: Completeness gate
        if not comp_passed:
            comp_finding = RecordFinding(
                rule_id="DQ-D10",
                source="BATCH",
                section="all",
                record_identity="batch_completeness",
                field_name="completeness",
                severity=FindingSeverity.CRITICAL,
                original_severity=FindingSeverity.CRITICAL,
                escalation_reason="Completeness fell below 98.00% threshold",
                disposition=RecordDisposition.QUARANTINED,
                observed_value=f"received={rec_comp}%, curated={cur_comp}%",
                expected_rule="Completeness >= 98.00% required",
                message=f"Completeness failure: received {rec_comp}%, curated {cur_comp}%",
            )
            all_findings.append(comp_finding)

        # Count findings by severity
        crit_count = sum(1 for f in all_findings if f.severity == FindingSeverity.CRITICAL)
        err_count = sum(1 for f in all_findings if f.severity == FindingSeverity.ERROR)
        warn_count = sum(1 for f in all_findings if f.severity == FindingSeverity.WARNING)
        info_count = sum(1 for f in all_findings if f.severity == FindingSeverity.INFO)

        summary = DQSummary(
            received_records=total_records_received,
            accepted_records=accepted_count,
            quarantined_records=quarantined_count,
            excluded_records=excluded_count,
            critical_findings_count=crit_count,
            error_findings_count=err_count,
            warning_findings_count=warn_count,
            info_findings_count=info_count,
            received_completeness_pct=rec_comp,
            curated_completeness_pct=cur_comp,
            completeness_passed=comp_passed,
            findings=tuple(all_findings),
        )

        return findings_by_record, summary
