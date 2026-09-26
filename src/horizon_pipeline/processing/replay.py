"""Batch Tracking, Replay Detection, and Revision Management.

Implements DD-09 delivery identity: (source, section, business_date, revision).
Distinguishes verified identical replays (INFO), conflicting same-revision deliveries
(CRITICAL), superseding revisions (new revision > current), and stale deliveries (CRITICAL).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Mapping

from ..contracts.findings import FindingSeverity
from .quality import RecordFinding
from .records import RecordDisposition


@dataclass(frozen=True)
class BatchRecord:
    """Historical state of a processed batch."""

    source: str
    section: str
    business_date: date
    revision: int
    checksum: str
    run_id: str


@dataclass(frozen=True)
class BatchRegistrationResult:
    """Result of registering a batch delivery with the tracker."""

    is_new: bool
    is_identical_replay: bool
    is_conflicting_revision: bool
    is_superseding_revision: bool
    is_stale_revision: bool
    findings: tuple[RecordFinding, ...]


class BatchStateTracker:
    """In-memory tracker for delivered batches, revisions, and checksums."""

    def __init__(self) -> None:
        # Key: (source, section, business_date) -> dict of revision -> BatchRecord
        self._history: dict[tuple[str, str, date], dict[int, BatchRecord]] = {}

    def register_batch(
        self,
        source: str,
        section: str,
        business_date: date,
        revision: int,
        checksum: str,
        run_id: str = "",
    ) -> BatchRegistrationResult:
        """Evaluate a delivered batch against historical deliveries."""
        batch_key = (source, section, business_date)
        findings: list[RecordFinding] = []

        if batch_key not in self._history:
            # First time seeing this source/section/date
            rec = BatchRecord(
                source=source,
                section=section,
                business_date=business_date,
                revision=revision,
                checksum=checksum,
                run_id=run_id,
            )
            self._history[batch_key] = {revision: rec}
            return BatchRegistrationResult(
                is_new=True,
                is_identical_replay=False,
                is_conflicting_revision=False,
                is_superseding_revision=False,
                is_stale_revision=False,
                findings=(),
            )

        rev_map = self._history[batch_key]
        highest_rev = max(rev_map.keys())

        # 1. Stale lower revision received after higher revision was already recorded: CRITICAL
        if revision < highest_rev:
            findings.append(
                RecordFinding(
                    rule_id="DQ-D02",
                    source=source,
                    section=section,
                    record_identity=f"rev_{revision}",
                    field_name="revision",
                    severity=FindingSeverity.CRITICAL,
                    original_severity=FindingSeverity.CRITICAL,
                    escalation_reason="Stale out-of-order revision received",
                    disposition=RecordDisposition.QUARANTINED,
                    observed_value=str(revision),
                    expected_rule=f"Revision must be greater than current active revision {highest_rev}",
                    message=f"Stale revision {revision} received; current highest is {highest_rev}",
                )
            )
            return BatchRegistrationResult(
                is_new=False,
                is_identical_replay=False,
                is_conflicting_revision=False,
                is_superseding_revision=False,
                is_stale_revision=True,
                findings=tuple(findings),
            )

        # 2. Check if this exact revision was previously processed
        if revision in rev_map:
            prior = rev_map[revision]
            if prior.checksum == checksum:
                # Verified identical replay under DD-09: INFO
                findings.append(
                    RecordFinding(
                        rule_id="DQ-D02",
                        source=source,
                        section=section,
                        record_identity=f"rev_{revision}",
                        field_name="checksum",
                        severity=FindingSeverity.INFO,
                        original_severity=FindingSeverity.INFO,
                        escalation_reason="",
                        disposition=RecordDisposition.ACCEPTED,
                        observed_value=checksum,
                        expected_rule="Verified identical replay; existing facts preserved",
                        message=f"Verified identical replay of {source}.{section} rev {revision} (run {prior.run_id})",
                    )
                )
                return BatchRegistrationResult(
                    is_new=False,
                    is_identical_replay=True,
                    is_conflicting_revision=False,
                    is_superseding_revision=False,
                    is_stale_revision=False,
                    findings=tuple(findings),
                )
            else:
                # Conflicting same-revision delivery under DD-09: CRITICAL
                findings.append(
                    RecordFinding(
                        rule_id="DQ-D02",
                        source=source,
                        section=section,
                        record_identity=f"rev_{revision}",
                        field_name="checksum",
                        severity=FindingSeverity.CRITICAL,
                        original_severity=FindingSeverity.CRITICAL,
                        escalation_reason="Conflicting content for identical source/section/date/revision",
                        disposition=RecordDisposition.QUARANTINED,
                        observed_value=checksum,
                        expected_rule=f"Checksum must match prior delivery '{prior.checksum}' for rev {revision}",
                        message=f"Conflicting same-revision delivery: new checksum {checksum} != prior {prior.checksum}",
                    )
                )
                return BatchRegistrationResult(
                    is_new=False,
                    is_identical_replay=False,
                    is_conflicting_revision=True,
                    is_superseding_revision=False,
                    is_stale_revision=False,
                    findings=tuple(findings),
                )

        # 3. New superseding revision (revision > highest_rev)
        rec = BatchRecord(
            source=source,
            section=section,
            business_date=business_date,
            revision=revision,
            checksum=checksum,
            run_id=run_id,
        )
        rev_map[revision] = rec
        return BatchRegistrationResult(
            is_new=True,
            is_identical_replay=False,
            is_conflicting_revision=False,
            is_superseding_revision=True,
            is_stale_revision=False,
            findings=(),
        )

    def get_latest_revision(self, source: str, section: str, business_date: date) -> int | None:
        """Get highest processed revision number for source/section/date."""
        batch_key = (source, section, business_date)
        if batch_key in self._history:
            return max(self._history[batch_key].keys())
        return None
