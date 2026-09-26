"""Raw and Curated Record Structures for Offline Processing.

Defines immutable, typed data structures for raw logical records,
curated domain entities, execution modes, retention classifications,
and record-level dispositions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Mapping


class ExecutionMode(str, Enum):
    """Pipeline execution mode."""

    FIXTURE = "FIXTURE"
    PRODUCTION = "PRODUCTION"


class RetentionCategory(str, Enum):
    """Data retention category under DD-10."""

    ANALYTICAL_24M = "ANALYTICAL_24M"  # 24-month rolling analytical window
    AUDIT_7Y = "AUDIT_7Y"              # 7-year minimized audit evidence


class RecordDisposition(str, Enum):
    """Record-level quality and pipeline disposition."""

    ACCEPTED = "ACCEPTED"
    QUARANTINED = "QUARANTINED"
    EXCLUDED = "EXCLUDED"


@dataclass(frozen=True)
class RawRecord:
    """Raw logical record extracted from a validated section payload."""

    source: str
    section: str
    record_id: str
    business_date: date
    revision: int
    row_index: int
    fields: Mapping[str, str] = field(default_factory=dict)
    payload_path: str = ""


# =====================================================================
# Curated Domain Entities (Immutable, Lineage-Traceable)
# =====================================================================

@dataclass(frozen=True)
class CuratedCustomer:
    """Curated customer entity (SRC-01)."""

    customer_id: str
    customer_name_masked: str
    tax_identifier_masked: str
    customer_segment: str
    primary_branch_id: str
    business_date: date
    source_system: str = "SRC-01"
    entity_name: str = "customers"
    revision: int = 1
    lineage_id: str = ""
    retention_category: RetentionCategory = RetentionCategory.ANALYTICAL_24M


@dataclass(frozen=True)
class CuratedAccount:
    """Curated deposit account entity (SRC-01)."""

    account_id: str
    account_id_masked: str
    customer_id: str
    account_type: str
    currency: str
    branch_id: str
    account_status: str
    business_date: date
    source_system: str = "SRC-01"
    entity_name: str = "accounts"
    revision: int = 1
    lineage_id: str = ""
    retention_category: RetentionCategory = RetentionCategory.ANALYTICAL_24M


@dataclass(frozen=True)
class CuratedAccountHolder:
    """Curated account-holder ownership/relationship (SRC-01). Non-additive."""

    account_id: str
    customer_id: str
    relationship_role: str
    effective_start: datetime | date
    source_system: str = "SRC-01"
    entity_name: str = "holders"
    revision: int = 1
    lineage_id: str = ""
    retention_category: RetentionCategory = RetentionCategory.ANALYTICAL_24M


@dataclass(frozen=True)
class CuratedTransaction:
    """Curated monetary transaction (SRC-01). Exact Decimal, scale 4."""

    transaction_id: str
    account_id: str
    account_id_masked: str
    business_date: date
    amount: Decimal
    currency: str
    transaction_type: str
    transaction_status: str  # Canonical status
    raw_transaction_status: str
    posted_at: datetime | None
    source_system: str = "SRC-01"
    entity_name: str = "transactions"
    revision: int = 1
    lineage_id: str = ""
    retention_category: RetentionCategory = RetentionCategory.ANALYTICAL_24M


@dataclass(frozen=True)
class CuratedLoan:
    """Curated credit loan agreement (SRC-02)."""

    loan_id: str
    customer_id: str
    loan_type: str
    original_principal: Decimal
    currency: str
    origination_date: date
    branch_id: str
    source_system: str = "SRC-02"
    entity_name: str = "loans"
    revision: int = 1
    lineage_id: str = ""
    retention_category: RetentionCategory = RetentionCategory.ANALYTICAL_24M


@dataclass(frozen=True)
class CuratedBorrower:
    """Curated borrower role/relationship (SRC-02). Non-additive."""

    loan_id: str
    customer_id: str
    relationship_role: str
    effective_start: datetime | date
    source_system: str = "SRC-02"
    entity_name: str = "borrowers"
    revision: int = 1
    lineage_id: str = ""
    retention_category: RetentionCategory = RetentionCategory.ANALYTICAL_24M


@dataclass(frozen=True)
class CuratedPosition:
    """Curated daily credit position snapshot (SRC-02). Authoritative for DPD/principal."""

    loan_id: str
    business_date: date
    outstanding_principal: Decimal
    currency: str
    days_past_due: int
    loan_status: str
    source_system: str = "SRC-02"
    entity_name: str = "positions"
    revision: int = 1
    lineage_id: str = ""
    retention_category: RetentionCategory = RetentionCategory.ANALYTICAL_24M


@dataclass(frozen=True)
class CuratedPayment:
    """Curated actual loan payment event (SRC-02). Exact Decimal, scale 4."""

    payment_id: str
    loan_id: str
    amount: Decimal
    currency: str
    payment_status: str
    raw_payment_status: str
    paid_at: datetime | None
    posted_at: datetime | None
    source_system: str = "SRC-02"
    entity_name: str = "payments"
    revision: int = 1
    lineage_id: str = ""
    retention_category: RetentionCategory = RetentionCategory.ANALYTICAL_24M


@dataclass(frozen=True)
class CuratedFraudAlert:
    """Curated fraud monitoring alert (SRC-03)."""

    alert_id: str
    customer_id: str
    account_id: str
    severity: str
    alert_reason: str
    case_status: str
    created_at: datetime
    source_system: str = "SRC-03"
    entity_name: str = "alerts"
    revision: int = 1
    lineage_id: str = ""
    retention_category: RetentionCategory = RetentionCategory.ANALYTICAL_24M


@dataclass(frozen=True)
class CuratedComplaint:
    """Curated customer service complaint (SRC-04)."""

    complaint_id: str
    customer_id: str
    channel: str
    priority: str
    complaint_status: str
    branch_id: str
    created_at: datetime
    source_system: str = "SRC-04"
    entity_name: str = "complaints"
    revision: int = 1
    lineage_id: str = ""
    retention_category: RetentionCategory = RetentionCategory.ANALYTICAL_24M


@dataclass(frozen=True)
class CuratedBranch:
    """Curated branch reference entity (SRC-05)."""

    branch_id: str
    region_id: str
    branch_name: str
    valid_from: datetime | date
    source_system: str = "SRC-05"
    entity_name: str = "branches"
    revision: int = 1
    lineage_id: str = ""
    retention_category: RetentionCategory = RetentionCategory.ANALYTICAL_24M


@dataclass(frozen=True)
class CuratedSupportingRecord:
    """Curated supporting, state, assignment, or schedule record.

    Used for sections without a dedicated curated domain model.
    """

    record_id: str
    source_system: str
    entity_name: str
    revision: int
    fields: Mapping[str, Any]
    lineage_id: str = ""
    retention_category: RetentionCategory = RetentionCategory.ANALYTICAL_24M
