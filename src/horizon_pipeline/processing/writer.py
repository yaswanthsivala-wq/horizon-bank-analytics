"""Deterministic Output Artifact Writer.

Writes standardized offline output artifacts:
- manifest.json (run metadata, counts, execution mode, SHA-256 digests)
- accepted/<entity>.json (curated domain records)
- quarantine/quarantine_records.json (quarantined records with raw fields & findings)
- lineage/lineage_records.json (audit lineage records)
- dq_summary.json (data quality and completeness metrics)
- reconciliation_summary.json (row and financial reconciliation balances)
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
from datetime import date, datetime
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
    ) -> dict[str, str]:
        """Write all run artifacts deterministically.

        Returns a dictionary mapping relative artifact paths to their SHA-256 checksums.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        accepted_dir = self.output_dir / "accepted"
        quarantine_dir = self.output_dir / "quarantine"
        lineage_dir = self.output_dir / "lineage"

        accepted_dir.mkdir(exist_ok=True)
        quarantine_dir.mkdir(exist_ok=True)
        lineage_dir.mkdir(exist_ok=True)

        file_checksums: dict[str, str] = {}

        def _write_json(rel_path: str, data: Any) -> None:
            full_path = self.output_dir / rel_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            content = json.dumps(data, indent=2, sort_keys=True, cls=OfflineOutputEncoder) + "\n"
            content_bytes = content.encode("utf-8")
            full_path.write_bytes(content_bytes)
            digest = hashlib.sha256(content_bytes).hexdigest()
            file_checksums[rel_path] = digest

        # 1. Accepted curated domain entities
        for entity_name, records in curated_entities.items():
            rel_file = f"accepted/{entity_name}.json"
            record_dicts = [dataclasses.asdict(r) for r in records]
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

        # 6. Run Manifest
        total_accepted = sum(len(r) for r in curated_entities.values())
        manifest_data = {
            "manifest_version": "HCB-RUN-MANIFEST-V1",
            "run_id": run_id,
            "package_id": package_id,
            "business_date": business_date.isoformat(),
            "execution_mode": execution_mode.value,
            "created_at_utc": datetime.now().isoformat(),
            "statistics": {
                "received_records": dq_summary.received_records,
                "accepted_records": total_accepted,
                "quarantined_records": quarantine_ledger.count(),
                "lineage_records": lineage_ledger.count(),
                "all_reconciliations_balanced": reconciliation_summary.all_balanced,
                "completeness_passed": dq_summary.completeness_passed,
            },
            "artifact_checksums": file_checksums,
        }
        _write_json("manifest.json", manifest_data)

        return file_checksums
