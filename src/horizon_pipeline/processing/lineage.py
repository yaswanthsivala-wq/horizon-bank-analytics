"""Source-to-Curated and Quarantine Lineage Engine.

Implements end-to-end audit lineage tracking connecting raw delivered records,
manifest checksums, transformation rules, quality findings, and resulting curated
or quarantined entities under DD-07 and DD-08.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Mapping, Sequence

from .records import RecordDisposition, RetentionCategory


@dataclass(frozen=True)
class LineageRecord:
    """Immutable audit record linking source payload to curated or quarantined output."""

    lineage_id: str
    run_id: str
    package_id: str
    business_date: date
    source_system: str
    section: str
    source_record_id: str
    source_checksum: str
    transformation_rules: tuple[str, ...]
    disposition: RecordDisposition
    curated_entity_id: str | None
    finding_codes: tuple[str, ...] = field(default_factory=tuple)
    retention_category: RetentionCategory = RetentionCategory.AUDIT_7Y

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "lineage_id": self.lineage_id,
            "run_id": self.run_id,
            "package_id": self.package_id,
            "business_date": self.business_date.isoformat(),
            "source_system": self.source_system,
            "section": self.section,
            "source_record_id": self.source_record_id,
            "source_checksum": self.source_checksum,
            "transformation_rules": list(self.transformation_rules),
            "disposition": self.disposition.value,
            "curated_entity_id": self.curated_entity_id,
            "finding_codes": list(self.finding_codes),
            "retention_category": self.retention_category.value,
        }


class LineageLedger:
    """Ledger recording and querying lineage across pipeline executions."""

    def __init__(self) -> None:
        self._records: list[LineageRecord] = []
        self._by_id: dict[str, LineageRecord] = {}

    def record_lineage(
        self,
        run_id: str,
        package_id: str,
        business_date: date,
        source_system: str,
        section: str,
        source_record_id: str,
        source_checksum: str,
        transformation_rules: Sequence[str],
        disposition: RecordDisposition,
        curated_entity_id: str | None = None,
        finding_codes: Sequence[str] = (),
        retention_category: RetentionCategory = RetentionCategory.AUDIT_7Y,
    ) -> LineageRecord:
        """Create and append a LineageRecord."""
        lid = f"LIN-{source_system}-{section}-{source_record_id}-{run_id[:8]}"
        rec = LineageRecord(
            lineage_id=lid,
            run_id=run_id,
            package_id=package_id,
            business_date=business_date,
            source_system=source_system,
            section=section,
            source_record_id=source_record_id,
            source_checksum=source_checksum,
            transformation_rules=tuple(transformation_rules),
            disposition=disposition,
            curated_entity_id=curated_entity_id,
            finding_codes=tuple(finding_codes),
            retention_category=retention_category,
        )
        self._records.append(rec)
        self._by_id[lid] = rec
        return rec

    def get_by_id(self, lineage_id: str) -> LineageRecord | None:
        """Retrieve lineage record by ID."""
        return self._by_id.get(lineage_id)

    def all_records(self) -> list[LineageRecord]:
        """Retrieve all lineage records."""
        return list(self._records)

    def count(self) -> int:
        """Total number of lineage records."""
        return len(self._records)

    def to_dict(self) -> list[dict[str, Any]]:
        """Export ledger as JSON-serializable list."""
        return [r.to_dict() for r in self._records]
