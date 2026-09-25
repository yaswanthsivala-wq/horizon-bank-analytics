"""Consolidated Offline Pipeline Runner for Horizon Bank Analytics.

Coordinates the end-to-end execution of the offline banking analytics pipeline:
1. Intake & manifest validation (Package 1: pipeline.py)
2. Deduplication, data quality, transformation, and reconciliation (Package 2: processing/)
3. Customer risk assessment correlation (Package 3: analytics/risk_orchestrator.py)
4. Four dimensional analytical marts calculation (Package 3: analytics/marts.py)
5. Consolidated publication gating and deterministic packaging (processing/writer.py)

Enforces strict ExecutionMode:
- ExecutionMode.PRODUCTION: Binds to MasterProductionRegistry and fails closed immediately
  with zero output artifacts and zero downstream calculation.
- ExecutionMode.FIXTURE: Executes end-to-end against test fixture contracts with exact
  scale-4 Decimal arithmetic and scale-8 ratio precision.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from ..analytics.marts import AnalyticalMartsBuilder, AnalyticalMartsResult
from ..analytics.risk_classification import RiskAssessment
from ..analytics.risk_orchestrator import CustomerRiskOrchestrator
from ..contracts.registry import MasterProductionRegistry
from ..contracts.risk import RiskRuleCatalogRegistry
from ..contracts.states import PendingContractError
from ..contracts.temporal import CHICAGO_TZ
from ..processing.engine import OfflineProcessingEngine, ProcessingResult
from ..processing.records import ExecutionMode, RecordDisposition
from ..processing.replay import BatchStateTracker
from ..processing.writer import OutputArtifactWriter


@dataclass(frozen=True)
class ConsolidatedRunResult:
    """Consolidated outcome of an end-to-end pipeline run."""

    run_id: str
    package_id: str
    business_date: date
    execution_mode: ExecutionMode
    disposition: RecordDisposition
    passed: bool
    processing_result: ProcessingResult
    risk_assessments: tuple[RiskAssessment, ...]
    marts_result: AnalyticalMartsResult | None
    artifact_checksums: Mapping[str, str] = field(default_factory=dict)
    manifest_checksum: str | None = None
    manifest_path: Path | None = None
    findings: tuple[Any, ...] = field(default_factory=tuple)


class ConsolidatedPipelineRunner:
    """Coordinates the end-to-end offline pipeline from source package to analytical marts."""

    def __init__(
        self,
        batch_tracker: BatchStateTracker | None = None,
        catalog_registry: RiskRuleCatalogRegistry | None = None,
    ) -> None:
        self.batch_tracker = batch_tracker or BatchStateTracker()
        self.processing_engine = OfflineProcessingEngine(batch_tracker=self.batch_tracker)
        self.risk_orchestrator = CustomerRiskOrchestrator(catalog_registry=catalog_registry)

    def run_package(
        self,
        manifest_json: str,
        payloads: Mapping[str, bytes],
        execution_mode: ExecutionMode = ExecutionMode.FIXTURE,
        run_id: str | None = None,
        output_dir: Path | str | None = None,
        as_of_time: datetime | None = None,
        created_at_utc: datetime | str | None = None,
        period_start: datetime | None = None,
        period_end: datetime | None = None,
    ) -> ConsolidatedRunResult:
        """Execute the complete pipeline end-to-end.

        In ExecutionMode.PRODUCTION, immediately fails closed against MasterProductionRegistry,
        returning a quarantined result with zero output artifacts and no downstream execution.
        In ExecutionMode.FIXTURE, runs the complete intake, curated transformation, risk assessment,
        and dimensional marts calculation.
        """
        if type(execution_mode) is not ExecutionMode:
            raise TypeError("execution_mode must be an ExecutionMode enum member")

        # Deterministic run_id derivation if not supplied
        active_run_id = run_id or f"RUN-{hashlib.sha256(manifest_json.encode('utf-8')).hexdigest()[:12].upper()}"

        # 1. PRODUCTION Mode: Fail closed immediately without writing output artifacts or executing marts
        if execution_mode == ExecutionMode.PRODUCTION:
            proc_res = self.processing_engine.process_package(
                manifest_json=manifest_json,
                payloads=payloads,
                execution_mode=ExecutionMode.PRODUCTION,
                run_id=active_run_id,
                output_dir=None,
            )
            return ConsolidatedRunResult(
                run_id=proc_res.run_id,
                package_id=proc_res.package_id,
                business_date=proc_res.business_date,
                execution_mode=ExecutionMode.PRODUCTION,
                disposition=RecordDisposition.QUARANTINED,
                passed=False,
                processing_result=proc_res,
                risk_assessments=(),
                marts_result=None,
                artifact_checksums={},
                manifest_checksum=None,
                manifest_path=None,
                findings=proc_res.findings,
            )

        # 2. FIXTURE Mode: Execute intake, deduplication, DQ, transform, and reconciliation
        proc_res = self.processing_engine.process_package(
            manifest_json=manifest_json,
            payloads=payloads,
            execution_mode=ExecutionMode.FIXTURE,
            run_id=active_run_id,
            output_dir=None,
        )

        bdate = proc_res.business_date
        out_path = Path(output_dir) if output_dir is not None else None

        # 3. Publication Gating (PUB-D01)
        # If intake rejected, replay blocked, critical DQ finding, or reconciliation failed:
        if not proc_res.passed:
            artifact_checksums: dict[str, str] = {}
            manifest_digest: str | None = None
            man_file: Path | None = None

            if out_path is not None:
                writer = OutputArtifactWriter(out_path)
                artifact_checksums = writer.write_run_artifacts(
                    run_id=active_run_id,
                    package_id=proc_res.package_id,
                    business_date=bdate,
                    execution_mode=ExecutionMode.FIXTURE,
                    curated_entities=proc_res.curated_entities,
                    quarantine_ledger=proc_res.quarantine_ledger,
                    lineage_ledger=proc_res.lineage_ledger,
                    dq_summary=proc_res.dq_summary,
                    reconciliation_summary=proc_res.reconciliation_summary,
                    risk_assessments=None,
                    analytical_marts=None,
                    is_quarantined=True,
                    created_at_utc=created_at_utc,
                )
                man_file = out_path / "manifest.json"
                manifest_digest = artifact_checksums.get("manifest.json")

            return ConsolidatedRunResult(
                run_id=active_run_id,
                package_id=proc_res.package_id,
                business_date=bdate,
                execution_mode=ExecutionMode.FIXTURE,
                disposition=RecordDisposition.QUARANTINED,
                passed=False,
                processing_result=proc_res,
                risk_assessments=(),
                marts_result=None,
                artifact_checksums=artifact_checksums,
                manifest_checksum=manifest_digest,
                manifest_path=man_file,
                findings=proc_res.findings,
            )

        # 4. Upstream Accepted: Proceed to Customer Risk Assessment
        curated = proc_res.curated_entities
        customers = curated.get("customers", ())
        accounts = curated.get("accounts", ())
        holders = curated.get("holders", ())
        transactions = curated.get("transactions", ())
        loans = curated.get("loans", ())
        borrowers = curated.get("borrowers", ())
        positions = curated.get("positions", ())
        complaints = curated.get("complaints", ())
        alerts = curated.get("alerts", ())
        restrictions = curated.get("account_restriction_state", ())

        risk_assessments = self.risk_orchestrator.assess_customers(
            customers=customers,
            accounts=accounts,
            account_holders=holders,
            transactions=transactions,
            loans=loans,
            borrowers=borrowers,
            positions=positions,
            complaints=complaints,
            fraud_alerts=alerts,
            account_restrictions=restrictions,
            business_date=bdate,
            as_of_time=as_of_time,
            execution_mode=ExecutionMode.FIXTURE,
        )

        # 5. Build Four Dimensional Analytical Marts
        # Establish default temporal window [bdate 00:00, bdate+1 00:00) in Chicago timezone if not provided
        if period_start is None:
            period_start = datetime(bdate.year, bdate.month, bdate.day, 0, 0, 0, tzinfo=CHICAGO_TZ)
        if period_end is None:
            period_end = period_start + timedelta(days=1)

        marts_result = AnalyticalMartsBuilder.build_all(
            transactions=transactions,
            fraud_alerts=alerts,
            accounts=accounts,
            period_start=period_start,
            period_end=period_end,
            loan_positions=positions,
            loans=loans,
            business_date=bdate,
            assessments=risk_assessments,
            customers=customers,
            complaints=complaints,
            as_of_time=as_of_time,
            execution_mode=ExecutionMode.FIXTURE,
        )

        # 6. Consolidated Packaging & Writing
        artifact_checksums: dict[str, str] = {}
        manifest_digest: str | None = None
        man_file: Path | None = None

        if out_path is not None:
            writer = OutputArtifactWriter(out_path)
            artifact_checksums = writer.write_run_artifacts(
                run_id=active_run_id,
                package_id=proc_res.package_id,
                business_date=bdate,
                execution_mode=ExecutionMode.FIXTURE,
                curated_entities=curated,
                quarantine_ledger=proc_res.quarantine_ledger,
                lineage_ledger=proc_res.lineage_ledger,
                dq_summary=proc_res.dq_summary,
                reconciliation_summary=proc_res.reconciliation_summary,
                risk_assessments=risk_assessments,
                analytical_marts=marts_result,
                is_quarantined=False,
                created_at_utc=created_at_utc,
            )
            man_file = out_path / "manifest.json"
            manifest_digest = artifact_checksums.get("manifest.json")

        return ConsolidatedRunResult(
            run_id=active_run_id,
            package_id=proc_res.package_id,
            business_date=bdate,
            execution_mode=ExecutionMode.FIXTURE,
            disposition=RecordDisposition.ACCEPTED,
            passed=True,
            processing_result=proc_res,
            risk_assessments=risk_assessments,
            marts_result=marts_result,
            artifact_checksums=artifact_checksums,
            manifest_checksum=manifest_digest,
            manifest_path=man_file,
            findings=proc_res.findings,
        )
