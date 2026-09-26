"""Quarantine Ledger and Record Management.

Implements isolation, preservation, and audit accounting for quarantined
records under DD-08, DD-09, and DD-10. Quarantined row payloads follow the
24-month analytical schedule (DD-10 line 69), while processing execution/run
metadata and quality logs follow the 7-year audit schedule (DD-10 lines 45, 70).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping, Sequence

from .quality import RecordFinding
from .records import RawRecord, RetentionCategory


@dataclass(frozen=True)
class QuarantinedRecord:
    """Quarantined raw record with associated validation findings."""

    quarantine_id: str
    source: str
    section: str
    record_id: str
    business_date: date
    revision: int
    row_index: int
    raw_fields: Mapping[str, str]
    findings: tuple[RecordFinding, ...]
    quarantined_at: datetime
    retention_category: RetentionCategory = RetentionCategory.ANALYTICAL_24M

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "quarantine_id": self.quarantine_id,
            "source": self.source,
            "section": self.section,
            "record_id": self.record_id,
            "business_date": self.business_date.isoformat(),
            "revision": self.revision,
            "row_index": self.row_index,
            "raw_fields": dict(self.raw_fields),
            "findings": [
                {
                    "rule_id": f.rule_id,
                    "field_name": f.field_name,
                    "severity": f.severity.value,
                    "disposition": f.disposition.value,
                    "observed_value": f.observed_value,
                    "expected_rule": f.expected_rule,
                    "message": f.message,
                }
                for f in self.findings
            ],
            "quarantined_at": self.quarantined_at.isoformat(),
            "retention_category": self.retention_category.value,
        }


class QuarantineLedger:
    """Ledger for recording, querying, and reconciling quarantined records."""

    def __init__(self) -> None:
        self._records: list[QuarantinedRecord] = []

    def record_quarantine(
        self,
        raw_record: RawRecord,
        findings: Sequence[RecordFinding],
        quarantined_at: datetime | None = None,
        retention_category: RetentionCategory = RetentionCategory.ANALYTICAL_24M,
    ) -> QuarantinedRecord:
        """Create and record a QuarantinedRecord from a raw record and findings."""
        now_utc = quarantined_at or datetime.now(timezone.utc)
        qid = f"Q-{raw_record.source}-{raw_record.section}-{raw_record.record_id}-{raw_record.revision}"
        qrec = QuarantinedRecord(
            quarantine_id=qid,
            source=raw_record.source,
            section=raw_record.section,
            record_id=raw_record.record_id,
            business_date=raw_record.business_date,
            revision=raw_record.revision,
            row_index=raw_record.row_index,
            raw_fields=raw_record.fields,
            findings=tuple(findings),
            quarantined_at=now_utc,
            retention_category=retention_category,
        )
        self._records.append(qrec)
        return qrec

    def get_by_section(self, source: str, section: str) -> list[QuarantinedRecord]:
        """Retrieve quarantined records for a specific source and section."""
        return [r for r in self._records if r.source == source and r.section == section]

    def all_records(self) -> list[QuarantinedRecord]:
        """Retrieve all quarantined records."""
        return list(self._records)

    def count(self) -> int:
        """Total number of quarantined records in the ledger."""
        return len(self._records)

    def total_monetary_amount(
        self,
        source: str,
        section: str,
        amount_field: str = "amount",
    ) -> Decimal:
        """Sum monetary amounts for quarantined records of a section.

        Used in PD-05 financial reconciliation.
        """
        total = Decimal("0.0000")
        for r in self.get_by_section(source, section):
            val = r.raw_fields.get(amount_field, "").strip()
            if val:
                try:
                    total += Decimal(val)
                except (InvalidOperation, TypeError):
                    pass
        return total.quantize(Decimal("0.0001"))

    def to_dict(self) -> list[dict[str, Any]]:
        """Export ledger as JSON-serializable list."""
        return [r.to_dict() for r in self._records]
