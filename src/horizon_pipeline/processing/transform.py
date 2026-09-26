"""Deterministic Field Transformation and Masking Engine.

Implements deterministic transformation, normalization, scale-4 Decimal parsing,
temporal parsing, and DD-08 data masking for offline processing.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping

from ..contracts.financial import parse_decimal_exact
from ..contracts.mapping import StatusMappingRegistry
from ..contracts.states import PendingContractError
from ..contracts.temporal import parse_offset_timestamp
from .records import (
    CuratedAccount,
    CuratedAccountHolder,
    CuratedBorrower,
    CuratedBranch,
    CuratedComplaint,
    CuratedCustomer,
    CuratedFraudAlert,
    CuratedLoan,
    CuratedPayment,
    CuratedPosition,
    CuratedSupportingRecord,
    CuratedTransaction,
    ExecutionMode,
    RawRecord,
    RetentionCategory,
)

SCALE_4 = Decimal("0.0001")


def mask_tax_identifier(
    val: str | None,
    execution_mode: ExecutionMode = ExecutionMode.FIXTURE,
) -> str:
    """Mask tax identifier / SSN according to DD-08.

    In ExecutionMode.PRODUCTION, raises PendingContractError because physical masking
    algorithms remain PENDING confirmation under DD-08 lines 37, 41-42.
    In ExecutionMode.FIXTURE, preserves final 4 characters (e.g. '***-**-1234').
    """
    if execution_mode == ExecutionMode.PRODUCTION:
        raise PendingContractError(
            "Production masking algorithm is PENDING confirmation under DD-08 lines 37, 41-42",
            contract_type="MASKING",
            identifier="DD-08",
        )
    if val is None:
        return "[UNAVAILABLE]"
    clean = val.strip()
    if not clean:
        return "[UNAVAILABLE]"

    # If standard 9 digits or SSN format
    digits_only = re.sub(r"\D", "", clean)
    if len(digits_only) >= 4:
        last4 = digits_only[-4:]
        return f"***-**-{last4}"

    if len(clean) >= 4:
        return f"***{clean[-4:]}"

    return "[UNAVAILABLE]"


def mask_account_id(
    val: str | None,
    execution_mode: ExecutionMode = ExecutionMode.FIXTURE,
) -> str:
    """Mask deposit/loan account number according to DD-08.

    In ExecutionMode.PRODUCTION, raises PendingContractError because physical masking
    algorithms remain PENDING confirmation under DD-08 lines 37, 41-42.
    In ExecutionMode.FIXTURE, uses fixed mask plus final 4 characters.
    """
    if execution_mode == ExecutionMode.PRODUCTION:
        raise PendingContractError(
            "Production masking algorithm is PENDING confirmation under DD-08 lines 37, 41-42",
            contract_type="MASKING",
            identifier="DD-08",
        )
    if val is None:
        return "[UNAVAILABLE]"
    clean = val.strip()
    if len(clean) < 4:
        return "[UNAVAILABLE]"
    return f"******{clean[-4:]}"


def mask_customer_name(
    val: str | None,
    execution_mode: ExecutionMode = ExecutionMode.FIXTURE,
) -> str:
    """Mask customer name for ordinary reporting/curated deidentification.

    In ExecutionMode.PRODUCTION, raises PendingContractError because deidentification
    transformation contract remains PENDING confirmation under DD-08 lines 37, 41-42.
    In ExecutionMode.FIXTURE, returns fixed mask preserving last 2 characters or [REDACTED].
    """
    if execution_mode == ExecutionMode.PRODUCTION:
        raise PendingContractError(
            "Production deidentification contract is PENDING confirmation under DD-08 lines 37, 41-42",
            contract_type="MASKING",
            identifier="DD-08",
        )
    if val is None:
        return "[UNAVAILABLE]"
    clean = val.strip()
    if not clean:
        return "[UNAVAILABLE]"
    if len(clean) <= 2:
        return "[REDACTED]"
    return f"***{clean[-2:]}"


def parse_scale4_decimal(val: str | None, field_name: str = "amount") -> Decimal:
    """Parse string to exact Decimal with scale 4.

    Raises ValueError on empty or invalid decimal strings.
    """
    if val is None or not val.strip():
        raise ValueError(f"Field '{field_name}' requires non-empty Decimal value")
    try:
        parsed = Decimal(val.strip())
    except (InvalidOperation, TypeError) as exc:
        raise ValueError(f"Invalid decimal '{val}' for field '{field_name}': {exc}") from exc
    return parsed.quantize(SCALE_4)


def parse_iso_date(val: str | None, field_name: str = "date") -> date:
    """Parse ISO date YYYY-MM-DD."""
    if val is None or not val.strip():
        raise ValueError(f"Field '{field_name}' requires non-empty date value")
    try:
        return date.fromisoformat(val.strip())
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Invalid date '{val}' for field '{field_name}': {exc}") from exc


def parse_instant_utc(val: str | None, field_name: str = "timestamp") -> datetime | None:
    """Parse ISO timestamp with offset and normalize to UTC."""
    if val is None or not val.strip():
        return None
    try:
        norm = parse_offset_timestamp(val.strip(), check_chicago_offset=False)
        return norm.utc_instant
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Invalid timestamp '{val}' for field '{field_name}': {exc}") from exc


def parse_date_or_instant(val: str | None, field_name: str = "date_or_instant") -> datetime | date:
    """Parse date string (YYYY-MM-DD) or offset ISO timestamp."""
    if val is None or not val.strip():
        raise ValueError(f"Field '{field_name}' requires non-empty date or timestamp")
    clean = val.strip()
    if "T" in clean:
        dt = parse_instant_utc(clean, field_name)
        if dt is None:
            raise ValueError(f"Field '{field_name}' failed to parse as instant")
        return dt
    return parse_iso_date(clean, field_name)


# =====================================================================
# Domain Entity Transformers
# =====================================================================

def transform_customer(
    raw: RawRecord,
    lineage_id: str,
    execution_mode: ExecutionMode = ExecutionMode.FIXTURE,
) -> CuratedCustomer:
    """Transform SRC-01 customers raw record to CuratedCustomer."""
    f = raw.fields
    cid = f.get("customer_id", "").strip()
    tax_id = f.get("tax_identifier_masked", "").strip()
    name = f.get("customer_name", "").strip()
    segment = f.get("customer_segment", "").strip()
    branch_id = f.get("primary_branch_id", "").strip()
    bdate_str = f.get("business_date", "").strip()
    bdate = parse_iso_date(bdate_str, "business_date") if bdate_str else raw.business_date

    return CuratedCustomer(
        customer_id=cid,
        customer_name_masked=mask_customer_name(name, execution_mode=execution_mode),
        tax_identifier_masked=mask_tax_identifier(tax_id, execution_mode=execution_mode),
        customer_segment=segment,
        primary_branch_id=branch_id,
        business_date=bdate,
        source_system=raw.source,
        entity_name=raw.section,
        revision=raw.revision,
        lineage_id=lineage_id,
        retention_category=RetentionCategory.ANALYTICAL_24M,
    )


def transform_account(
    raw: RawRecord,
    lineage_id: str,
    execution_mode: ExecutionMode = ExecutionMode.FIXTURE,
) -> CuratedAccount:
    """Transform SRC-01 accounts raw record to CuratedAccount."""
    f = raw.fields
    aid = f.get("account_id", "").strip()
    cid = f.get("customer_id", "").strip()
    atype = f.get("account_type", "").strip()
    currency = f.get("currency", "USD").strip()
    branch_id = f.get("branch_id", "").strip()
    status = f.get("account_status", "").strip()
    bdate_str = f.get("business_date", "").strip()
    bdate = parse_iso_date(bdate_str, "business_date") if bdate_str else raw.business_date

    return CuratedAccount(
        account_id=aid,
        account_id_masked=mask_account_id(aid, execution_mode=execution_mode),
        customer_id=cid,
        account_type=atype,
        currency=currency,
        branch_id=branch_id,
        account_status=status,
        business_date=bdate,
        source_system=raw.source,
        entity_name=raw.section,
        revision=raw.revision,
        lineage_id=lineage_id,
        retention_category=RetentionCategory.ANALYTICAL_24M,
    )


def transform_account_holder(raw: RawRecord, lineage_id: str) -> CuratedAccountHolder:
    """Transform SRC-01 holders raw record to CuratedAccountHolder."""
    f = raw.fields
    aid = f.get("account_id", "").strip()
    cid = f.get("customer_id", "").strip()
    role = f.get("relationship_role", "").strip()
    start_str = f.get("effective_start", "").strip()
    eff_start = parse_date_or_instant(start_str, "effective_start")

    return CuratedAccountHolder(
        account_id=aid,
        customer_id=cid,
        relationship_role=role,
        effective_start=eff_start,
        source_system=raw.source,
        entity_name=raw.section,
        revision=raw.revision,
        lineage_id=lineage_id,
        retention_category=RetentionCategory.ANALYTICAL_24M,
    )


def transform_transaction(
    raw: RawRecord,
    lineage_id: str,
    status_registry: StatusMappingRegistry | None = None,
    mapping_version: str = "FIXTURE_MAP_V1",
) -> CuratedTransaction:
    """Transform SRC-01 transactions raw record to CuratedTransaction."""
    f = raw.fields
    tid = f.get("transaction_id", "").strip()
    aid = f.get("account_id", "").strip()
    bdate_str = f.get("business_date", "").strip()
    bdate = parse_iso_date(bdate_str, "business_date") if bdate_str else raw.business_date
    amount = parse_scale4_decimal(f.get("amount"), "amount")
    currency = f.get("currency", "USD").strip()
    ttype = f.get("transaction_type", "").strip()
    raw_status = f.get("transaction_status", "").strip()

    # Resolve canonical status if mapping registry provided
    canonical_status = raw_status
    if status_registry is not None:
        resolution, _ = status_registry.resolve(
            source_system=raw.source,
            domain_code="transaction_status",
            mapping_version=mapping_version,
            raw_value=raw_status,
        )
        if resolution and resolution.canonical_value:
            canonical_status = resolution.canonical_value

    posted_at_str = f.get("posted_at", "").strip()
    posted_at = parse_instant_utc(posted_at_str, "posted_at") if posted_at_str else None

    return CuratedTransaction(
        transaction_id=tid,
        account_id=aid,
        account_id_masked=mask_account_id(aid),
        business_date=bdate,
        amount=amount,
        currency=currency,
        transaction_type=ttype,
        transaction_status=canonical_status,
        raw_transaction_status=raw_status,
        posted_at=posted_at,
        source_system=raw.source,
        entity_name=raw.section,
        revision=raw.revision,
        lineage_id=lineage_id,
        retention_category=RetentionCategory.ANALYTICAL_24M,
    )


def transform_loan(raw: RawRecord, lineage_id: str) -> CuratedLoan:
    """Transform SRC-02 loans raw record to CuratedLoan."""
    f = raw.fields
    lid = f.get("loan_id", "").strip()
    cid = f.get("customer_id", "").strip()
    ltype = f.get("loan_type", "").strip()
    principal = parse_scale4_decimal(f.get("original_principal"), "original_principal")
    currency = f.get("currency", "USD").strip()
    orig_date_str = f.get("origination_date", "").strip()
    orig_date = parse_iso_date(orig_date_str, "origination_date")
    branch_id = f.get("branch_id", "").strip()

    return CuratedLoan(
        loan_id=lid,
        customer_id=cid,
        loan_type=ltype,
        original_principal=principal,
        currency=currency,
        origination_date=orig_date,
        branch_id=branch_id,
        source_system=raw.source,
        entity_name=raw.section,
        revision=raw.revision,
        lineage_id=lineage_id,
        retention_category=RetentionCategory.ANALYTICAL_24M,
    )


def transform_borrower(raw: RawRecord, lineage_id: str) -> CuratedBorrower:
    """Transform SRC-02 borrowers raw record to CuratedBorrower."""
    f = raw.fields
    lid = f.get("loan_id", "").strip()
    cid = f.get("customer_id", "").strip()
    role = f.get("relationship_role", "").strip()
    start_str = f.get("effective_start", "").strip()
    eff_start = parse_date_or_instant(start_str, "effective_start")

    return CuratedBorrower(
        loan_id=lid,
        customer_id=cid,
        relationship_role=role,
        effective_start=eff_start,
        source_system=raw.source,
        entity_name=raw.section,
        revision=raw.revision,
        lineage_id=lineage_id,
        retention_category=RetentionCategory.ANALYTICAL_24M,
    )


def transform_position(raw: RawRecord, lineage_id: str) -> CuratedPosition:
    """Transform SRC-02 positions raw record to CuratedPosition."""
    f = raw.fields
    lid = f.get("loan_id", "").strip()
    bdate_str = f.get("business_date", "").strip()
    bdate = parse_iso_date(bdate_str, "business_date") if bdate_str else raw.business_date
    principal = parse_scale4_decimal(f.get("outstanding_principal"), "outstanding_principal")
    currency = f.get("currency", "USD").strip()
    dpd_str = f.get("days_past_due", "0").strip()
    try:
        dpd = int(dpd_str)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Invalid days_past_due '{dpd_str}': {exc}") from exc
    status = f.get("loan_status", "").strip()

    return CuratedPosition(
        loan_id=lid,
        business_date=bdate,
        outstanding_principal=principal,
        currency=currency,
        days_past_due=dpd,
        loan_status=status,
        source_system=raw.source,
        entity_name=raw.section,
        revision=raw.revision,
        lineage_id=lineage_id,
        retention_category=RetentionCategory.ANALYTICAL_24M,
    )


def transform_payment(
    raw: RawRecord,
    lineage_id: str,
    status_registry: StatusMappingRegistry | None = None,
    mapping_version: str = "FIXTURE_MAP_V1",
) -> CuratedPayment:
    """Transform SRC-02 payments raw record to CuratedPayment."""
    f = raw.fields
    pid = f.get("payment_id", "").strip()
    lid = f.get("loan_id", "").strip()
    amount = parse_scale4_decimal(f.get("amount"), "amount")
    currency = f.get("currency", "USD").strip()
    raw_status = f.get("payment_status", "").strip()

    canonical_status = raw_status
    if status_registry is not None:
        resolution, _ = status_registry.resolve(
            source_system=raw.source,
            domain_code="payment_status",
            mapping_version=mapping_version,
            raw_value=raw_status,
        )
        if resolution and resolution.canonical_value:
            canonical_status = resolution.canonical_value

    paid_at_str = f.get("paid_at", "").strip()
    paid_at = parse_instant_utc(paid_at_str, "paid_at") if paid_at_str else None
    posted_at_str = f.get("posted_at", "").strip()
    posted_at = parse_instant_utc(posted_at_str, "posted_at") if posted_at_str else None

    return CuratedPayment(
        payment_id=pid,
        loan_id=lid,
        amount=amount,
        currency=currency,
        payment_status=canonical_status,
        raw_payment_status=raw_status,
        paid_at=paid_at,
        posted_at=posted_at,
        source_system=raw.source,
        entity_name=raw.section,
        revision=raw.revision,
        lineage_id=lineage_id,
        retention_category=RetentionCategory.ANALYTICAL_24M,
    )


def transform_fraud_alert(raw: RawRecord, lineage_id: str) -> CuratedFraudAlert:
    """Transform SRC-03 alerts raw record to CuratedFraudAlert."""
    f = raw.fields
    aid = f.get("alert_id", "").strip()
    cid = f.get("customer_id", "").strip()
    acc_id = f.get("account_id", "").strip()
    severity = f.get("severity", "").strip()
    reason = f.get("alert_reason", "").strip()
    status = f.get("case_status", "").strip()
    created_at_str = f.get("created_at", "").strip()
    created_at = parse_instant_utc(created_at_str, "created_at")
    if created_at is None:
        raise ValueError(f"created_at is required for alert {aid}")

    return CuratedFraudAlert(
        alert_id=aid,
        customer_id=cid,
        account_id=acc_id,
        severity=severity,
        alert_reason=reason,
        case_status=status,
        created_at=created_at,
        source_system=raw.source,
        entity_name=raw.section,
        revision=raw.revision,
        lineage_id=lineage_id,
        retention_category=RetentionCategory.ANALYTICAL_24M,
    )


def transform_complaint(raw: RawRecord, lineage_id: str) -> CuratedComplaint:
    """Transform SRC-04 complaints raw record to CuratedComplaint."""
    f = raw.fields
    cid = f.get("complaint_id", "").strip()
    cust_id = f.get("customer_id", "").strip()
    channel = f.get("channel", "").strip()
    priority = f.get("priority", "").strip()
    status = f.get("complaint_status", "").strip()
    branch_id = f.get("branch_id", "").strip()
    created_at_str = f.get("created_at", "").strip()
    created_at = parse_instant_utc(created_at_str, "created_at")
    if created_at is None:
        raise ValueError(f"created_at is required for complaint {cid}")

    return CuratedComplaint(
        complaint_id=cid,
        customer_id=cust_id,
        channel=channel,
        priority=priority,
        complaint_status=status,
        branch_id=branch_id,
        created_at=created_at,
        source_system=raw.source,
        entity_name=raw.section,
        revision=raw.revision,
        lineage_id=lineage_id,
        retention_category=RetentionCategory.ANALYTICAL_24M,
    )


def transform_branch(raw: RawRecord, lineage_id: str) -> CuratedBranch:
    """Transform SRC-05 branches raw record to CuratedBranch."""
    f = raw.fields
    bid = f.get("branch_id", "").strip()
    rid = f.get("region_id", "").strip()
    bname = f.get("branch_name", "").strip()
    vfrom_str = f.get("valid_from", "").strip()
    valid_from = parse_date_or_instant(vfrom_str, "valid_from")

    return CuratedBranch(
        branch_id=bid,
        region_id=rid,
        branch_name=bname,
        valid_from=valid_from,
        source_system=raw.source,
        entity_name=raw.section,
        revision=raw.revision,
        lineage_id=lineage_id,
        retention_category=RetentionCategory.ANALYTICAL_24M,
    )


# Section-to-transformer registry
TRANSFORMERS: dict[tuple[str, str], Any] = {
    ("SRC-01", "customers"): transform_customer,
    ("SRC-01", "accounts"): transform_account,
    ("SRC-01", "holders"): transform_account_holder,
    ("SRC-01", "transactions"): transform_transaction,
    ("SRC-02", "loans"): transform_loan,
    ("SRC-02", "borrowers"): transform_borrower,
    ("SRC-02", "positions"): transform_position,
    ("SRC-02", "payments"): transform_payment,
    ("SRC-03", "alerts"): transform_fraud_alert,
    ("SRC-04", "complaints"): transform_complaint,
    ("SRC-05", "branches"): transform_branch,
}


def transform_record(
    raw: RawRecord,
    lineage_id: str,
    status_registry: StatusMappingRegistry | None = None,
    mapping_version: str = "FIXTURE_MAP_V1",
    execution_mode: ExecutionMode = ExecutionMode.FIXTURE,
) -> Any:
    """Dispatch and transform a RawRecord into its curated domain entity.

    Returns the curated entity or raises ValueError if no transformer or transformation error.
    """
    key = (raw.source, raw.section)
    transformer = TRANSFORMERS.get(key)
    if transformer is None:
        return CuratedSupportingRecord(
            record_id=raw.record_id,
            source_system=raw.source,
            entity_name=raw.section,
            revision=raw.revision,
            fields=raw.fields,
            lineage_id=lineage_id,
            retention_category=RetentionCategory.ANALYTICAL_24M,
        )

    if key in (("SRC-01", "customers"), ("SRC-01", "accounts")):
        return transformer(raw, lineage_id, execution_mode=execution_mode)
    if key in (("SRC-01", "transactions"), ("SRC-02", "payments")):
        return transformer(raw, lineage_id, status_registry=status_registry, mapping_version=mapping_version)
    return transformer(raw, lineage_id)
