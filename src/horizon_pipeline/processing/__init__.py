"""Offline Processing Package for Horizon Community Bank.

Exports record definitions, transformation, data quality, quarantine,
lineage, reconciliation, and offline processing orchestration engines.
"""

from __future__ import annotations

from .engine import OfflineProcessingEngine, ProcessingResult
from .identity import DeduplicationResult, RecordIdentityEngine, extract_natural_key
from .lineage import LineageLedger, LineageRecord
from .quality import DataQualityEngine, DQSummary, RecordFinding
from .quarantine import QuarantineLedger, QuarantinedRecord
from .reconciliation import (
    FinancialReconciliationResult,
    OfflineReconciliationEngine,
    ReconciliationSummary,
    RowReconciliationResult,
)
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
    RecordDisposition,
    RetentionCategory,
)
from .replay import BatchRecord, BatchRegistrationResult, BatchStateTracker
from .transform import (
    mask_account_id,
    mask_customer_name,
    mask_tax_identifier,
    parse_instant_utc,
    parse_iso_date,
    parse_scale4_decimal,
    transform_record,
)
from .writer import OfflineOutputEncoder, OutputArtifactWriter

__all__ = [
    # Engine
    "OfflineProcessingEngine",
    "ProcessingResult",
    # Identity
    "RecordIdentityEngine",
    "DeduplicationResult",
    "extract_natural_key",
    # Lineage
    "LineageLedger",
    "LineageRecord",
    # Quality
    "DataQualityEngine",
    "DQSummary",
    "RecordFinding",
    # Quarantine
    "QuarantineLedger",
    "QuarantinedRecord",
    # Reconciliation
    "OfflineReconciliationEngine",
    "ReconciliationSummary",
    "RowReconciliationResult",
    "FinancialReconciliationResult",
    # Records
    "ExecutionMode",
    "RetentionCategory",
    "RecordDisposition",
    "RawRecord",
    "CuratedCustomer",
    "CuratedAccount",
    "CuratedAccountHolder",
    "CuratedTransaction",
    "CuratedLoan",
    "CuratedBorrower",
    "CuratedPosition",
    "CuratedPayment",
    "CuratedFraudAlert",
    "CuratedComplaint",
    "CuratedBranch",
    "CuratedSupportingRecord",
    # Replay
    "BatchStateTracker",
    "BatchRegistrationResult",
    "BatchRecord",
    # Transform
    "mask_account_id",
    "mask_tax_identifier",
    "mask_customer_name",
    "parse_scale4_decimal",
    "parse_iso_date",
    "parse_instant_utc",
    "transform_record",
    # Writer
    "OutputArtifactWriter",
    "OfflineOutputEncoder",
]
