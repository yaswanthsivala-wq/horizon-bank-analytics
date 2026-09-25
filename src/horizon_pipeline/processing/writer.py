"""Deterministic Output Artifact Writer.

Writes standardized offline output artifacts:
- manifest.json (run metadata, counts, execution mode, SHA-256 digests)
- manifest.json.sha256 (companion SHA-256 digest file)
- accepted/<entity>.json (curated domain records)
- quarantine/quarantine_records.json (quarantined records with raw fields & findings)
- lineage/lineage_records.json (audit lineage records)
- dq_summary.json (data quality and completeness metrics)
- reconciliation_summary.json (row and financial reconciliation balances)
- risk/customer_risk_assessments.json (customer risk assessments)
- marts/mart_<domain>_kpis.json (four dimensional analytical marts)
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Sequence

from .lineage import LineageLedger, LineageRecord
from .quality import DQSummary
from .quarantine import QuarantineLedger, QuarantinedRecord
from .reconciliation import ReconciliationSummary
from .records import ExecutionMode


class OfflineOutputEncoder(json.JSONEncoder):
    """JSON encoder supporting Decimal, date/datetime, Enum, and dataclasses."""

    def default(self, o: Any) -> Any:
        if isinstance(o, Decimal):
            return str(o)
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if isinstance(o, Enum):
            return o.value
        if dataclasses.is_dataclass(o) and not isinstance(o, type):
            return dataclasses.asdict(o)
        return super().default(o)


class OutputArtifactWriter:
    """Writes pipeline output artifacts to target directory structure."""

    def __init__(self, output_dir: Path | str) -> None:
        self.output_dir = Path(output_dir)

    def write_run_artifacts(
        self,
        run_id: str,
        package_id: str,
        business_date: date,
        execution_mode: ExecutionMode,
        curated_entities: Mapping[str, Sequence[Any]],
        quarantine_ledger: QuarantineLedger,
        lineage_ledger: LineageLedger,
        dq_summary: DQSummary,
        reconciliation_summary: ReconciliationSummary,
        risk_assessments: Sequence[Any] | None = None,
        analytical_marts: Any | None = None,
        is_quarantined: bool = False,
        created_at_utc: datetime | str | None = None,
    ) -> dict[str, str]:
        """Write all run artifacts deterministically.

        When is_quarantined is True, writes diagnostic artifacts only (quarantine/,
        lineage/, dq_summary.json, reconciliation_summary.json, manifest.json,
        manifest.json.sha256) and strictly omits accepted/, risk/, and marts/.

        Returns a dictionary mapping relative artifact paths to their SHA-256 checksums.
        manifest.json is strictly excluded from its own artifact_checksums map.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        quarantine_dir = self.output_dir / "quarantine"
        lineage_dir = self.output_dir / "lineage"

        quarantine_dir.mkdir(exist_ok=True)
        lineage_dir.mkdir(exist_ok=True)

        file_checksums: dict[str, str] = {}

        def _write_json(rel_path: str, data: Any) -> str:
            full_path = self.output_dir / rel_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            content = json.dumps(data, indent=2, sort_keys=True, cls=OfflineOutputEncoder) + "\n"
            content_bytes = content.encode("utf-8")
            full_path.write_bytes(content_bytes)
            digest = hashlib.sha256(content_bytes).hexdigest()
            file_checksums[rel_path] = digest
            return digest

        # When package is ACCEPTED (not quarantined), write accepted curated entities
        if not is_quarantined:
            accepted_dir = self.output_dir / "accepted"
            accepted_dir.mkdir(exist_ok=True)
            for entity_name, records in curated_entities.items():
                rel_file = f"accepted/{entity_name}.json"
                record_dicts = [
                    dataclasses.asdict(r) if dataclasses.is_dataclass(r) and not isinstance(r, type) else r
                    for r in records
                ]
                _write_json(rel_file, record_dicts)

        # 2. Quarantine records
        quar_dicts = quarantine_ledger.to_dict()
        _write_json("quarantine/quarantine_records.json", quar_dicts)

        # 3. Lineage records
        lin_dicts = lineage_ledger.to_dict()
        _write_json("lineage/lineage_records.json", lin_dicts)

        # 4. Data Quality summary
        dq_dict = {
            "received_records": dq_summary.received_records,
            "accepted_records": dq_summary.accepted_records,
            "quarantined_records": dq_summary.quarantined_records,
            "excluded_records": dq_summary.excluded_records,
            "critical_findings_count": dq_summary.critical_findings_count,
            "error_findings_count": dq_summary.error_findings_count,
            "warning_findings_count": dq_summary.warning_findings_count,
            "info_findings_count": dq_summary.info_findings_count,
            "received_completeness_pct": str(dq_summary.received_completeness_pct),
            "curated_completeness_pct": str(dq_summary.curated_completeness_pct),
            "completeness_passed": dq_summary.completeness_passed,
            "findings": [
                {
                    "rule_id": f.rule_id,
                    "source": f.source,
                    "section": f.section,
                    "record_identity": f.record_identity,
                    "field_name": f.field_name,
                    "severity": f.severity.value,
                    "original_severity": f.original_severity.value,
                    "escalation_reason": f.escalation_reason,
                    "disposition": f.disposition.value,
                    "observed_value": f.observed_value,
                    "expected_rule": f.expected_rule,
                    "message": f.message,
                }
                for f in dq_summary.findings
            ],
        }
        _write_json("dq_summary.json", dq_dict)

        # 5. Reconciliation summary
        rec_dict = reconciliation_summary.to_dict()
        _write_json("reconciliation_summary.json", rec_dict)

        # When package is ACCEPTED, write risk assessments and analytical marts
        if not is_quarantined:
            if risk_assessments is not None:
                risk_dir = self.output_dir / "risk"
                risk_dir.mkdir(exist_ok=True)
                asm_dicts = [
                    dataclasses.asdict(a) if dataclasses.is_dataclass(a) and not isinstance(a, type) else a
                    for a in risk_assessments
                ]
                _write_json("risk/customer_risk_assessments.json", asm_dicts)

            if analytical_marts is not None:
                marts_dir = self.output_dir / "marts"
                marts_dir.mkdir(exist_ok=True)
                tx_mart = getattr(analytical_marts, "tx_mart", ())
                loan_mart = getattr(analytical_marts, "loan_mart", ())
                cust_mart = getattr(analytical_marts, "customer_risk_mart", ())
                comp_mart = getattr(analytical_marts, "complaint_mart", ())

                _write_json("marts/mart_transaction_kpis.json", [
                    dataclasses.asdict(r) if dataclasses.is_dataclass(r) and not isinstance(r, type) else r
                    for r in tx_mart
                ])
                _write_json("marts/mart_loan_delinquency_kpis.json", [
                    dataclasses.asdict(r) if dataclasses.is_dataclass(r) and not isinstance(r, type) else r
                    for r in loan_mart
                ])
                _write_json("marts/mart_customer_risk_kpis.json", [
                    dataclasses.asdict(r) if dataclasses.is_dataclass(r) and not isinstance(r, type) else r
                    for r in cust_mart
                ])
                _write_json("marts/mart_complaint_kpis.json", [
                    dataclasses.asdict(r) if dataclasses.is_dataclass(r) and not isinstance(r, type) else r
                    for r in comp_mart
                ])

        # 6. Run Manifest
        # Snapshot current file_checksums so manifest.json is NEVER inside artifact_checksums
        manifest_checksums_map = dict(file_checksums)

        total_accepted = 0 if is_quarantined else sum(len(r) for r in curated_entities.values())
        if created_at_utc is None:
            ts_str = datetime(business_date.year, business_date.month, business_date.day, 0, 0, 0, tzinfo=timezone.utc).isoformat()
        elif isinstance(created_at_utc, datetime):
            ts_str = created_at_utc.isoformat()
        else:
            ts_str = str(created_at_utc)

        manifest_data = {
            "manifest_version": "HCB-CONSOLIDATED-MANIFEST-V1",
            "run_id": run_id,
            "package_id": package_id,
            "business_date": business_date.isoformat(),
            "execution_mode": execution_mode.value,
            "disposition": "QUARANTINED" if is_quarantined else "ACCEPTED",
            "created_at_utc": ts_str,
            "statistics": {
                "received_records": dq_summary.received_records,
                "accepted_records": total_accepted,
                "quarantined_records": quarantine_ledger.count(),
                "lineage_records": lineage_ledger.count(),
                "customer_risk_assessments": len(risk_assessments) if risk_assessments is not None and not is_quarantined else 0,
                "all_reconciliations_balanced": reconciliation_summary.all_balanced,
                "completeness_passed": dq_summary.completeness_passed,
            },
            "artifact_checksums": manifest_checksums_map,
        }

        # Write manifest.json
        manifest_digest = _write_json("manifest.json", manifest_data)

        # Write companion manifest.json.sha256
        sha_file = self.output_dir / "manifest.json.sha256"
        sha_file.write_text(f"{manifest_digest} *manifest.json\n", encoding="utf-8")

        return file_checksums
