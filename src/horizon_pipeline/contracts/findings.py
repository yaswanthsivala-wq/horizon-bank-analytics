"""Controlled findings and disposition model for Horizon Community Bank.

Distinguishes between accepted delivery, record-level quarantine, and
fatal package failure (rejection).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FindingSeverity(str, Enum):
    """Controlled severity levels for contract and data findings."""

    FATAL = "FATAL"      # Package-level failure: delivery must be rejected
    ERROR = "ERROR"      # Record/field-level failure: causes quarantine or rejection
    WARNING = "WARNING"  # Advisory observation
    INFO = "INFO"        # Informational trace


class Disposition(str, Enum):
    """Controlled disposition of a validated payload or package."""

    ACCEPTED = "ACCEPTED"        # Passed all applicable gates
    QUARANTINED = "QUARANTINED"  # Record-level data quality or integrity issue
    REJECTED = "REJECTED"        # Package-level failure (framing, checksum, missing)


@dataclass(frozen=True)
class ValidationFinding:
    """A structured finding emitted during contract or pipeline validation."""

    code: str
    severity: FindingSeverity
    source: str
    section: str
    message: str
    record_identity: str | None = None
    field_name: str | None = None
    contract_type: str | None = None
    evidence: str | None = None
    disposition: Disposition = Disposition.REJECTED

    def to_summary(self) -> str:
        """Produce a human-readable trace line."""
        prefix = f"{self.source}/{self.section}" if self.source and self.section else (self.source or "PACKAGE")
        loc = f" (record={self.record_identity})" if self.record_identity else ""
        fld = f" [field={self.field_name}]" if self.field_name else ""
        return f"[{self.severity.value}] {prefix}{loc}{fld}: {self.code} - {self.message}"
