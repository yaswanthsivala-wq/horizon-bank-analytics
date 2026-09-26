"""Offline Processing Engine Orchestrator.

Orchestrates the complete offline transformation, data quality, quarantine,
lineage, reconciliation, and output generation pipeline under DD-08, DD-09,
DD-10, DD-11, and DD-12.

Strictly enforces ExecutionMode:
- ExecutionMode.PRODUCTION: Binds exclusively to MasterProductionRegistry and
  fails closed on pending/unsupported production contracts.
- ExecutionMode.FIXTURE: Executes against isolated test fixture registries.
"""

from __future__ import annotations

import csv
import io
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping, Sequence

from ..contracts.financial import FinancialControlEngine
from ..contracts.findings import Disposition, FindingSeverity, ValidationFinding
from ..contracts.headers import HeaderRegistry
from ..contracts.manifests import PackageManifest, parse_and_validate_manifest_json, validate_payload_bytes
from ..contracts.mapping import StatusMappingRegistry
from ..contracts.registry import MasterProductionRegistry
from ..contracts.schemas import SchemaRegistry
from ..pipeline import OfflinePipelineEngine
from ..synthetic.fixtures import build_test_fixture_registries
from .identity import RecordIdentityEngine
from .lineage import LineageLedger, LineageRecord
from .quality import DataQualityEngine, DQSummary, RecordFinding
from .quarantine import QuarantineLedger, QuarantinedRecord
from .reconciliation import OfflineReconciliationEngine, ReconciliationSummary
from .records import (
    ExecutionMode,
    RawRecord,
    RecordDisposition,
    RetentionCategory,
)
from .replay import BatchStateTracker
from .transform import transform_record
from .writer import OutputArtifactWriter

SCALE_4 = Decimal("0.0001")


@dataclass(frozen=True)
class ProcessingResult:
    """Consolidated outcome of package processing."""

    run_id: str
    package_id: str
    business_date: date
    execution_mode: ExecutionMode
    disposition: RecordDisposition
    passed: bool
    curated_entities: Mapping[str, Sequence[Any]]
    quarantine_ledger: QuarantineLedger
    lineage_ledger: LineageLedger
    dq_summary: DQSummary
    reconciliation_summary: ReconciliationSummary
    artifact_checksums: Mapping[str, str] = field(default_factory=dict)
    findings: tuple[Any, ...] = field(default_factory=tuple)


class OfflineProcessingEngine:
    """Coordinates end-to-end offline processing for Horizon Community Bank."""

    def __init__(
        self,
        batch_tracker: BatchStateTracker | None = None,
    ) -> None:
        self.batch_tracker = batch_tracker or BatchStateTracker()
        self.identity_engine = RecordIdentityEngine()
        self.reconciliation_engine = OfflineReconciliationEngine()

    def process_package(
        self,
        manifest_json: str,
        payloads: Mapping[str, bytes],
        execution_mode: ExecutionMode = ExecutionMode.FIXTURE,
        run_id: str | None = None,
        output_dir: Path | str | None = None,
        fixture_registries: tuple[
            HeaderRegistry,
            SchemaRegistry,
            Any,
            StatusMappingRegistry,
            FinancialControlEngine,
        ] | None = None,
    ) -> ProcessingResult:
        """Process a delivered package end-to-end.

        In PRODUCTION mode, binds strictly to MasterProductionRegistry and fails closed.
        In FIXTURE mode, uses isolated test fixture registries.
        """
        active_run_id = run_id or f"RUN-{uuid.uuid4().hex[:12].upper()}"

        # 1. Mode and Contract Engine Binding
        if execution_mode == ExecutionMode.PRODUCTION:
            prod_master = MasterProductionRegistry()
            contract_engine = OfflinePipelineEngine(
                headers=prod_master.headers,
                schemas=prod_master.schemas,
                applicability=prod_master.applicability,
                mappings=prod_master.mappings,
                financial=prod_master.financial,
            )
            # Execute validation against production contracts
            pipeline_result = contract_engine.execute_package(
                manifest_json=manifest_json,
                payloads=payloads,
                require_all_27_sections=True,
            )
            # MasterProductionRegistry contracts are all PENDING, so it must fail closed
            empty_dq = DQSummary(
                received_records=0,
                accepted_records=0,
                quarantined_records=0,
                excluded_records=0,
                critical_findings_count=len([f for f in pipeline_result.findings if f.severity == FindingSeverity.FATAL]),
                error_findings_count=len([f for f in pipeline_result.findings if f.severity == FindingSeverity.ERROR]),
                warning_findings_count=0,
                info_findings_count=0,
                received_completeness_pct=Decimal("0.00"),
                curated_completeness_pct=Decimal("0.00"),
                completeness_passed=False,
                findings=(),
            )
            empty_rec = ReconciliationSummary(
                row_results=(),
                financial_results=(),
                all_balanced=False,
                findings=(),
            )
            bdate = pipeline_result.manifest.business_date if pipeline_result.manifest else date.today()
            pkg_id = f"PKG-{bdate.isoformat()}" if pipeline_result.manifest else "UNKNOWN_PACKAGE"

            return ProcessingResult(
                run_id=active_run_id,
                package_id=pkg_id,
                business_date=bdate,
                execution_mode=ExecutionMode.PRODUCTION,
                disposition=RecordDisposition.QUARANTINED,
                passed=False,
                curated_entities={},
                quarantine_ledger=QuarantineLedger(),
                lineage_ledger=LineageLedger(),
                dq_summary=empty_dq,
                reconciliation_summary=empty_rec,
                artifact_checksums={},
                findings=pipeline_result.findings,
            )

        # 2. FIXTURE Mode: Initialize fixture registries and engines
        if fixture_registries is None:
            headers, schemas, applicability, mappings, financial = build_test_fixture_registries()
        else:
            headers, schemas, applicability, mappings, financial = fixture_registries

        contract_engine = OfflinePipelineEngine(
            headers=headers,
            schemas=schemas,
            applicability=applicability,
            mappings=mappings,
            financial=financial,
        )

        pipeline_result = contract_engine.execute_package(
            manifest_json=manifest_json,
            payloads=payloads,
            require_all_27_sections=True,
        )

        manifest = pipeline_result.manifest
        if manifest is None or pipeline_result.disposition == Disposition.REJECTED:
            # Fatal manifest or byte-level contract failure
            bdate = manifest.business_date if manifest else date.today()
            pkg_id = f"PKG-{bdate.isoformat()}" if manifest else "UNKNOWN_PACKAGE"
            empty_dq = DQSummary(
                received_records=0,
                accepted_records=0,
                quarantined_records=0,
                excluded_records=0,
                critical_findings_count=len([f for f in pipeline_result.findings if f.severity == FindingSeverity.FATAL]),
                error_findings_count=len([f for f in pipeline_result.findings if f.severity == FindingSeverity.ERROR]),
                warning_findings_count=0,
                info_findings_count=0,
                received_completeness_pct=Decimal("0.00"),
                curated_completeness_pct=Decimal("0.00"),
                completeness_passed=False,
                findings=(),
            )
            empty_rec = ReconciliationSummary(
                row_results=(),
                financial_results=(),
                all_balanced=False,
                findings=(),
            )
            return ProcessingResult(
                run_id=active_run_id,
                package_id=pkg_id,
                business_date=bdate,
                execution_mode=ExecutionMode.FIXTURE,
                disposition=RecordDisposition.QUARANTINED,
                passed=False,
                curated_entities={},
                quarantine_ledger=QuarantineLedger(),
                lineage_ledger=LineageLedger(),
                dq_summary=empty_dq,
                reconciliation_summary=empty_rec,
                artifact_checksums={},
                findings=pipeline_result.findings,
            )

        active_package_id = f"PKG-{manifest.business_date.isoformat()}"

        # 3. Parse Raw Records from validated payloads
        raw_records_by_section: dict[tuple[str, str], list[RawRecord]] = {}
        manifest_counts_by_section: dict[tuple[str, str], int] = {}
        raw_captured_counts: dict[tuple[str, str], int] = {}
        checksums_by_section: dict[tuple[str, str], str] = {}

        for entry in manifest.sections:
            key = (entry.source_system, entry.entity_name)
            manifest_counts_by_section[key] = entry.row_count
            checksums_by_section[key] = entry.checksum
            raw_payload_bytes = payloads[entry.payload_path]

            # Parse CSV rows
            text = raw_payload_bytes.decode("utf-8")
            reader = csv.DictReader(io.StringIO(text))
            sec_raw_records: list[RawRecord] = []
            for idx, row in enumerate(reader, start=1):
                # Identify business ID or fallback to row index
                rec_id = row.get("id") or row.get(f"{entry.entity_name.rstrip('s')}_id") or row.get(list(row.keys())[0] if row else "") or f"ROW_{idx}"
                rec = RawRecord(
                    source=entry.source_system,
                    section=entry.entity_name,
                    record_id=str(rec_id).strip(),
                    business_date=manifest.business_date,
                    revision=entry.revision,
                    row_index=idx,
                    fields={k: str(v).strip() for k, v in row.items()},
                    payload_path=entry.payload_path,
                )
                sec_raw_records.append(rec)

            raw_records_by_section[key] = sec_raw_records
            raw_captured_counts[key] = len(sec_raw_records)

        # 4. Batch Replay and Revision Registration (DD-09)
        replay_findings: list[RecordFinding] = []
        is_replay_blocked = False

        for entry in manifest.sections:
            reg_res = self.batch_tracker.register_batch(
                source=entry.source_system,
                section=entry.entity_name,
                business_date=manifest.business_date,
                revision=entry.revision,
                checksum=entry.checksum,
                run_id=active_run_id,
            )
            replay_findings.extend(reg_res.findings)
            if reg_res.is_conflicting_revision or reg_res.is_stale_revision:
                is_replay_blocked = True

        if is_replay_blocked:
            empty_dq = DQSummary(
                received_records=sum(raw_captured_counts.values()),
                accepted_records=0,
                quarantined_records=sum(raw_captured_counts.values()),
                excluded_records=0,
                critical_findings_count=len(replay_findings),
                error_findings_count=0,
                warning_findings_count=0,
                info_findings_count=0,
                received_completeness_pct=Decimal("0.00"),
                curated_completeness_pct=Decimal("0.00"),
                completeness_passed=False,
                findings=tuple(replay_findings),
            )
            empty_rec = ReconciliationSummary(
                row_results=(),
                financial_results=(),
                all_balanced=False,
                findings=tuple(replay_findings),
            )
            return ProcessingResult(
                run_id=active_run_id,
                package_id=f"PKG-{manifest.business_date.isoformat()}",
                business_date=manifest.business_date,
                execution_mode=ExecutionMode.FIXTURE,
                disposition=RecordDisposition.QUARANTINED,
                passed=False,
                curated_entities={},
                quarantine_ledger=QuarantineLedger(),
                lineage_ledger=LineageLedger(),
                dq_summary=empty_dq,
                reconciliation_summary=empty_rec,
                artifact_checksums={},
                findings=tuple(replay_findings),
            )

        # 5. Natural Key Deduplication per section
        deduped_records_by_section: dict[tuple[str, str], list[RawRecord]] = {}
        quarantined_by_identity: dict[tuple[str, str], list[RawRecord]] = {}
        identity_findings_by_record: dict[tuple[str, str, str], list[RecordFinding]] = {}

        for key, records in raw_records_by_section.items():
            dedup_res = self.identity_engine.deduplicate_section(records, execution_mode=execution_mode)
            deduped_records_by_section[key] = list(dedup_res.accepted_records)
            quarantined_by_identity[key] = list(dedup_res.quarantined_records)
            for f in dedup_res.findings:
                rec_k = (f.source, f.section, f.record_identity)
                identity_findings_by_record.setdefault(rec_k, []).append(f)

        # 6. Data Quality Evaluation (DQ-D01 .. DQ-D13)
        dq_engine = DataQualityEngine(
            status_registry=mappings,
            check_referential_integrity=True,
            execution_mode=execution_mode,
        )
        dq_findings_by_record, dq_summary = dq_engine.evaluate_batch(deduped_records_by_section)

        # Combine findings
        quarantine_ledger = QuarantineLedger()
        lineage_ledger = LineageLedger()
        curated_entities: dict[str, list[Any]] = {}

        accepted_counts: dict[tuple[str, str], int] = {}
        quarantined_counts: dict[tuple[str, str], int] = {}

        # Tracking monetary values for financial reconciliation
        monetary_accounting: dict[tuple[str, str], dict[str, list[Decimal]]] = {}

        # 7. Process Records: Quarantine vs Transformation
        for key, records in raw_records_by_section.items():
            source, section = key
            sec_accepted = 0
            sec_quarantined = 0
            sec_checksum = checksums_by_section.get(key, "")

            monetary_accounting[key] = {
                "accepted": [],
                "quarantined": [],
                "excluded": [],
                "source_total": [],
            }

            # First handle records quarantined during deduplication
            for q_rec in quarantined_by_identity.get(key, []):
                sec_quarantined += 1
                rec_k = (source, section, q_rec.record_id)
                q_finds = identity_findings_by_record.get(rec_k, [])
                quarantine_ledger.record_quarantine(q_rec, q_finds)

                lineage_ledger.record_lineage(
                    run_id=active_run_id,
                    package_id=active_package_id,
                    business_date=manifest.business_date,
                    source_system=source,
                    section=section,
                    source_record_id=q_rec.record_id,
                    source_checksum=sec_checksum,
                    transformation_rules=("DEDUPLICATION",),
                    disposition=RecordDisposition.QUARANTINED,
                    finding_codes=[f.rule_id for f in q_finds],
                    retention_category=RetentionCategory.AUDIT_7Y,
                )
                amt_str = q_rec.fields.get("amount", "").strip()
                if amt_str:
                    try:
                        monetary_accounting[key]["quarantined"].append(Decimal(amt_str))
                    except Exception:
                        pass

            # Next handle deduped records evaluated by DQ
            for rec in deduped_records_by_section.get(key, []):
                rec_k = (source, section, rec.record_id)
                rec_finds = dq_findings_by_record.get(rec_k, [])

                amt_str = rec.fields.get("amount", "").strip()
                parsed_amt = None
                if amt_str:
                    try:
                        parsed_amt = Decimal(amt_str)
                    except Exception:
                        pass

                if rec_finds:
                    # Quarantined due to DQ findings
                    sec_quarantined += 1
                    quarantine_ledger.record_quarantine(rec, rec_finds)
                    lineage_ledger.record_lineage(
                        run_id=active_run_id,
                        package_id=active_package_id,
                        business_date=manifest.business_date,
                        source_system=source,
                        section=section,
                        source_record_id=rec.record_id,
                        source_checksum=sec_checksum,
                        transformation_rules=("DQ_VALIDATION",),
                        disposition=RecordDisposition.QUARANTINED,
                        finding_codes=[f.rule_id for f in rec_finds],
                        retention_category=RetentionCategory.AUDIT_7Y,
                    )
                    if parsed_amt is not None:
                        monetary_accounting[key]["quarantined"].append(parsed_amt)
                else:
                    # Accepted: Transform to Curated Entity
                    lineage_id = f"LIN-{source}-{section}-{rec.record_id}-{active_run_id[:8]}"
                    try:
                        curated_rec = transform_record(
                            raw=rec,
                            lineage_id=lineage_id,
                            status_registry=mappings,
                            execution_mode=execution_mode,
                        )
                        entity_name = getattr(curated_rec, "entity_name", section)
                        curated_entities.setdefault(entity_name, []).append(curated_rec)
                        sec_accepted += 1

                        lineage_ledger.record_lineage(
                            run_id=active_run_id,
                            package_id=active_package_id,
                            business_date=manifest.business_date,
                            source_system=source,
                            section=section,
                            source_record_id=rec.record_id,
                            source_checksum=sec_checksum,
                            transformation_rules=("TRANSFORMATION", "MASKING_DD08"),
                            disposition=RecordDisposition.ACCEPTED,
                            curated_entity_id=getattr(curated_rec, f"{entity_name.rstrip('s')}_id", rec.record_id),
                            retention_category=RetentionCategory.ANALYTICAL_24M,
                        )
                        if parsed_amt is not None:
                            monetary_accounting[key]["accepted"].append(parsed_amt)

                    except Exception as exc:
                        # Transformation failure cascades to quarantine
                        sec_quarantined += 1
                        tr_find = RecordFinding(
                            rule_id="DQ-D03",
                            source=source,
                            section=section,
                            record_identity=rec.record_id,
                            field_name="transformation",
                            severity=FindingSeverity.ERROR,
                            original_severity=FindingSeverity.ERROR,
                            escalation_reason="",
                            disposition=RecordDisposition.QUARANTINED,
                            observed_value=str(exc),
                            expected_rule="Deterministic transformation must succeed",
                            message=f"Transformation error: {exc}",
                        )
                        quarantine_ledger.record_quarantine(rec, [tr_find])
                        lineage_ledger.record_lineage(
                            run_id=active_run_id,
                            package_id=active_package_id,
                            business_date=manifest.business_date,
                            source_system=source,
                            section=section,
                            source_record_id=rec.record_id,
                            source_checksum=sec_checksum,
                            transformation_rules=("TRANSFORMATION_ERROR",),
                            disposition=RecordDisposition.QUARANTINED,
                            finding_codes=["DQ-D03"],
                            retention_category=RetentionCategory.AUDIT_7Y,
                        )
                        if parsed_amt is not None:
                            monetary_accounting[key]["quarantined"].append(parsed_amt)

            accepted_counts[key] = sec_accepted
            quarantined_counts[key] = sec_quarantined

            # Compute source total as sum of accepted and quarantined for this run
            acc_list = monetary_accounting[key]["accepted"]
            quar_list = monetary_accounting[key]["quarantined"]
            monetary_accounting[key]["source_total"] = [sum(acc_list + quar_list, Decimal("0.0000"))]

        # 8. Row and Financial Reconciliation
        active_fin_controls = [c for c in financial.all_controls() if c.is_fixture]
        reconciliation_summary = self.reconciliation_engine.reconcile_package(
            section_manifest_counts=manifest_counts_by_section,
            raw_captured_counts=raw_captured_counts,
            accepted_counts=accepted_counts,
            quarantined_counts=quarantined_counts,
            excluded_counts=None,
            financial_controls=active_fin_controls,
            monetary_data=monetary_accounting,
        )

        # 9. Publication Gate Evaluation (PUB-D01)
        all_findings = list(pipeline_result.findings) + list(replay_findings) + list(dq_summary.findings) + list(reconciliation_summary.findings)

        has_critical = any(
            getattr(f, "severity", None) in (FindingSeverity.FATAL, FindingSeverity.CRITICAL)
            for f in all_findings
        )
        has_error = any(
            getattr(f, "severity", None) == FindingSeverity.ERROR
            for f in all_findings
        ) or (quarantine_ledger.count() > 0)

        if has_critical or not dq_summary.completeness_passed or not reconciliation_summary.all_balanced:
            disposition = RecordDisposition.QUARANTINED
            passed = False
        elif has_error:
            disposition = RecordDisposition.QUARANTINED
            passed = False
        else:
            disposition = RecordDisposition.ACCEPTED
            passed = True

        # 10. Write Artifacts if output_dir specified
        artifact_checksums: dict[str, str] = {}
        if output_dir is not None:
            writer = OutputArtifactWriter(output_dir)
            artifact_checksums = writer.write_run_artifacts(
                run_id=active_run_id,
                package_id=active_package_id,
                business_date=manifest.business_date,
                execution_mode=execution_mode,
                curated_entities=curated_entities,
                quarantine_ledger=quarantine_ledger,
                lineage_ledger=lineage_ledger,
                dq_summary=dq_summary,
                reconciliation_summary=reconciliation_summary,
            )

        return ProcessingResult(
            run_id=active_run_id,
            package_id=active_package_id,
            business_date=manifest.business_date,
            execution_mode=execution_mode,
            disposition=disposition,
            passed=passed,
            curated_entities=curated_entities,
            quarantine_ledger=quarantine_ledger,
            lineage_ledger=lineage_ledger,
            dq_summary=dq_summary,
            reconciliation_summary=reconciliation_summary,
            artifact_checksums=artifact_checksums,
            findings=tuple(all_findings),
        )
