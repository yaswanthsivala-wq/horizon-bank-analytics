"""Logical data models for deterministic synthetic banking data foundation.

NOTICE: SYNTHETIC / NON-PRODUCTION ONLY.
No real customer or bank data is present or accepted.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass(frozen=True)
class SyntheticBranch:
    """SRC-05 Branch reference entity."""

    branch_id: str
    region_id: str
    branch_name: str
    valid_from: date
    valid_to: date | None = None
    is_active: bool = True


@dataclass(frozen=True)
class SyntheticCustomer:
    """SRC-01 Customer entity."""

    customer_id: str
    tax_identifier_masked: str  # Masked fake SSN, e.g. XXX-XX-1234
    customer_name: str
    customer_segment: str       # RETAIL, SMALL_BUSINESS
    primary_branch_id: str
    created_date: date


@dataclass(frozen=True)
class SyntheticAccount:
    """SRC-01 Account entity."""

    account_id: str
    customer_id: str
    account_type: str           # CHECKING, SAVINGS
    currency: str               # USD
    branch_id: str
    opened_date: date
    status: str                 # ACTIVE, CLOSED


@dataclass(frozen=True)
class SyntheticHolder:
    """SRC-01 Account-Customer Holder relationship."""

    account_id: str
    customer_id: str
    relationship_role: str      # PRIMARY, JOINT
    effective_start: date


@dataclass(frozen=True)
class SyntheticTransaction:
    """SRC-01 Transaction entity."""

    transaction_id: str
    account_id: str
    business_date: date
    amount: Decimal
    currency: str
    transaction_type: str       # TRANSFER, PAYMENT, WITHDRAWAL, DEPOSIT
    transaction_status: str     # SUCCESSFUL, POSTED, FAILED
    posted_at_utc: str          # ISO instant with Z


@dataclass(frozen=True)
class SyntheticLoan:
    """SRC-02 Loan entity."""

    loan_id: str
    customer_id: str
    loan_type: str              # PERSONAL, AUTO, MORTGAGE
    original_principal: Decimal
    currency: str
    origination_date: date
    maturity_date: date
    branch_id: str


@dataclass(frozen=True)
class SyntheticLoanPosition:
    """SRC-02 Daily loan position snapshot."""

    loan_id: str
    business_date: date
    outstanding_principal: Decimal
    currency: str
    days_past_due: int
    loan_status: str            # ACTIVE, DELINQUENT_ACTIVE


@dataclass(frozen=True)
class SyntheticLoanPayment:
    """SRC-02 Loan payment event."""

    payment_id: str
    loan_id: str
    payment_amount: Decimal
    currency: str
    payment_status: str         # POSTED, PENDING
    paid_at_utc: str
    posted_at_utc: str | None = None


@dataclass(frozen=True)
class SyntheticFraudAlert:
    """SRC-03 Fraud monitoring alert."""

    alert_id: str
    customer_id: str
    account_id: str
    severity: str               # LOW, MEDIUM, HIGH, CRITICAL
    alert_reason: str           # VELOCITY, AMOUNT, RESTRICTION
    case_status: str            # OPEN, CLOSED
    created_at_utc: str


@dataclass(frozen=True)
class SyntheticComplaint:
    """SRC-04 CRM customer complaint."""

    complaint_id: str
    customer_id: str
    channel: str                # PHONE, WEB, BRANCH
    priority: str               # Critical, High, Medium, Low
    status: str                 # OPEN, IN_PROGRESS, CLOSED
    branch_id: str
    created_at_utc: str
