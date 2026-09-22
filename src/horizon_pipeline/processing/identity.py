"""Natural Key Deduplication and Record Identity Engine.

Enforces natural key constraints per section, distinguishes exact identical
duplicates from conflicting key collisions under DD-09 (Rule DQ-D02), and
prevents duplicate facts from entering curated storage.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from ..contracts.findings import FindingSeverity
from .quality import RecordFinding
from .records import ExecutionMode, RawRecord, RecordDisposition

# Natural business key field(s) per section
SECTION_NATURAL_KEYS: dict[tuple[str, str], tuple[str, ...]] = {
    ("SRC-01", "customers"): ("customer_id",),
    ("SRC-01", "accounts"): ("account_id",),
    ("SRC-01", "holders"): ("account_id", "customer_id", "relationship_role", "effective_start"),
    ("SRC-01", "transactions"): ("transaction_id",),
    ("SRC-01", "account_restriction_state"): ("account_id", "effective_start"),
    ("SRC-01", "account_branch_assignment"): ("account_id", "branch_id", "effective_start"),
    ("SRC-02", "loans"): ("loan_id",),
    ("SRC-02", "borrowers"): ("loan_id", "customer_id", "relationship_role", "effective_start"),
    ("SRC-02", "positions"): ("loan_id", "business_date"),
    ("SRC-02", "payments"): ("payment_id",),
    ("SRC-02", "loan_schedule"): ("schedule_id",),
    ("SRC-02", "loan_obligation"): ("obligation_id",),
    ("SRC-02", "payment_allocation"): ("allocation_id",),
    ("SRC-02", "payment_unapplied"): ("payment_id",),
    ("SRC-02", "payment_adjustment"): ("adjustment_id",),
    ("SRC-02", "loan_account"): ("loan_id", "account_id"),
    ("SRC-02", "loan_branch_assignment"): ("loan_id", "branch_id", "effective_start"),
    ("SRC-03", "alerts"): ("alert_id",),
    ("SRC-03", "fraud_alert_state"): ("alert_id", "effective_start"),
    ("SRC-04", "complaints"): ("complaint_id",),
    ("SRC-04", "complaint_snapshot"): ("complaint_id", "business_date"),
    ("SRC-04", "complaint_history_event"): ("event_id",),
    ("SRC-04", "complaint_branch_assignment"): ("complaint_id", "branch_id", "effective_start"),
    ("SRC-05", "organizational_unit"): ("unit_id", "unit_type"),
    ("SRC-05", "region"): ("region_id", "valid_from"),
    ("SRC-05", "branches"): ("branch_id", "valid_from"),
    ("SRC-05", "organizational_successor"): ("predecessor_id", "successor_id", "valid_from"),
}


@dataclass(frozen=True)
class DeduplicationResult:
    """Result of deduplicating records within a section."""

    accepted_records: tuple[RawRecord, ...]
    quarantined_records: tuple[RawRecord, ...]
    findings: tuple[RecordFinding, ...]


def extract_natural_key(raw_record: RawRecord) -> tuple[str, ...]:
    """Extract natural key tuple for a RawRecord based on registered keys."""
    key_fields = SECTION_NATURAL_KEYS.get((raw_record.source, raw_record.section), ("record_id",))
    return tuple(raw_record.fields.get(f, "").strip() for f in key_fields)


class RecordIdentityEngine:
    """Detects exact duplicates and conflicting key collisions in record batches."""

    def __init__(self, execution_mode: ExecutionMode = ExecutionMode.FIXTURE) -> None:
        self.execution_mode = execution_mode

    def deduplicate_section(
        self,
        records: Sequence[RawRecord],
        execution_mode: ExecutionMode | None = None,
    ) -> DeduplicationResult:
        """Deduplicate records in a single section.

        - In PRODUCTION mode: fails closed because physical natural key headers are PENDING under PD-01.
        - If natural key has not been seen: accept record.
        - If natural key seen and ALL fields match: exact duplicate -> suppress duplicate fact (quarantine/exclude or skip), emit INFO finding.
        - If natural key seen and ANY field differs: conflicting duplicate -> emit DQ-D02 CRITICAL finding, quarantine conflicting row.
        """
        mode = execution_mode if execution_mode is not None else self.execution_mode
        if mode == ExecutionMode.PRODUCTION:
            findings = [
                RecordFinding(
                    rule_id="DQ-D02",
                    source=records[0].source if records else "UNKNOWN",
                    section=records[0].section if records else "UNKNOWN",
                    record_identity="BATCH",
                    field_name="natural_key",
                    severity=FindingSeverity.CRITICAL,
                    original_severity=FindingSeverity.CRITICAL,
                    escalation_reason="Production physical natural key headers are PENDING under PD-01",
                    disposition=RecordDisposition.QUARANTINED,
                    observed_value="UNCONFIRMED_PHYSICAL_HEADERS",
                    expected_rule="Production physical key extraction requires approved PD-01 headers",
                    message="Production natural key extraction failed closed: physical headers are PENDING",
                )
            ]
            return DeduplicationResult(
                accepted_records=(),
                quarantined_records=tuple(records),
                findings=tuple(findings),
            )

        seen_keys: dict[tuple[str, ...], RawRecord] = {}
        accepted: list[RawRecord] = []
        quarantined: list[RawRecord] = []
        findings: list[RecordFinding] = []

        for r in records:
            key = extract_natural_key(r)
            # If key is empty (all empty components), cannot identify
            if not any(key):
                accepted.append(r)
                continue

            if key not in seen_keys:
                seen_keys[key] = r
                accepted.append(r)
            else:
                prior = seen_keys[key]
                # Compare fields
                if dict(prior.fields) == dict(r.fields):
                    # Exact duplicate row
                    findings.append(
                        RecordFinding(
                            rule_id="DQ-D02",
                            source=r.source,
                            section=r.section,
                            record_identity=r.record_id,
                            field_name="natural_key",
                            severity=FindingSeverity.INFO,
                            original_severity=FindingSeverity.INFO,
                            escalation_reason="",
                            disposition=RecordDisposition.QUARANTINED,
                            observed_value=str(key),
                            expected_rule="Exact duplicate row detected; duplicate fact suppressed",
                            message=f"Exact duplicate of record '{prior.record_id}' on key {key}",
                        )
                    )
                    quarantined.append(r)
                else:
                    # Conflicting duplicate: CRITICAL failure
                    findings.append(
                        RecordFinding(
                            rule_id="DQ-D02",
                            source=r.source,
                            section=r.section,
                            record_identity=r.record_id,
                            field_name="natural_key",
                            severity=FindingSeverity.CRITICAL,
                            original_severity=FindingSeverity.CRITICAL,
                            escalation_reason="Conflicting duplicate key within same delivery",
                            disposition=RecordDisposition.QUARANTINED,
                            observed_value=str(key),
                            expected_rule="Natural key must uniquely identify distinct records",
                            message=f"Conflicting duplicate for key {key}: conflicts with prior row '{prior.record_id}'",
                        )
                    )
                    quarantined.append(r)

        return DeduplicationResult(
            accepted_records=tuple(accepted),
            quarantined_records=tuple(quarantined),
            findings=tuple(findings),
        )
