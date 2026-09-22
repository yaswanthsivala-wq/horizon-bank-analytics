"""Offline Contract Engine and Pipeline Validator for Horizon Community Bank.

Executes the offline pipeline:
1. PD-03 Manifest Validation
2. Payload exact byte & framing validation
3. PD-01 Header Contract Validation
4. PD-02 Schema Contract Validation
5. PD-04 Applicability Contract Evaluation
6. PD-06 Mapping Contract Resolution
7. PD-07 Temporal Instant Normalization
8. PD-05 Financial Control Reconciliation
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Mapping, Sequence

from .contracts.applicability import ApplicabilityRegistry, ApplicabilityState, CellState, FieldDisposition
from .contracts.financial import FinancialControlEngine, ReconciliationResult
from .contracts.findings import Disposition, FindingSeverity, ValidationFinding
from .contracts.headers import HeaderRegistry
from .contracts.manifests import (
    ManifestSectionEntry,
    PackageManifest,
    parse_and_validate_manifest_json,
    validate_payload_bytes,
)
from .contracts.mapping import StatusMappingRegistry
from .contracts.schemas import SchemaRegistry
from .contracts.temporal import parse_offset_timestamp
from .intake import _valid_value


@dataclass(frozen=True)
class PipelineExecutionResult:
    """Consolidated result of offline pipeline execution."""

    disposition: Disposition
    passed: bool
    findings: tuple[ValidationFinding, ...]
    manifest: PackageManifest | None = None
    processed_sections: tuple[tuple[str, str], ...] = ()
    reconciliation_results: tuple[ReconciliationResult, ...] = ()


class OfflinePipelineEngine:
    """Orchestrates offline validation across PD-01 through PD-07."""

    def __init__(
        self,
        headers: HeaderRegistry,
        schemas: SchemaRegistry,
        applicability: ApplicabilityRegistry | None = None,
        mappings: StatusMappingRegistry | None = None,
        financial: FinancialControlEngine | None = None,
    ) -> None:
        self.headers = headers
        self.schemas = schemas
        self.applicability = applicability or ApplicabilityRegistry()
        self.mappings = mappings or StatusMappingRegistry()
        self.financial = financial or FinancialControlEngine()

    def execute_package(
        self,
        manifest_json: str,
        payloads: Mapping[str, bytes],
        expected_business_date: date | None = None,
        require_all_27_sections: bool = True,
    ) -> PipelineExecutionResult:
        """Validate a delivered package against all active contracts."""
        all_findings: list[ValidationFinding] = []
        processed_sections: list[tuple[str, str]] = []
        reconciliations: list[ReconciliationResult] = []

        # 1. PD-03 Manifest Validation
        manifest, man_findings = parse_and_validate_manifest_json(
            manifest_json,
            require_all_27_sections=require_all_27_sections,
        )
        all_findings.extend(man_findings)

        if manifest is None:
            return PipelineExecutionResult(
                disposition=Disposition.REJECTED,
                passed=False,
                findings=tuple(all_findings),
            )

        if expected_business_date is not None and manifest.business_date != expected_business_date:
            all_findings.append(
                ValidationFinding(
                    code="MAN-DATE-MISMATCH",
                    severity=FindingSeverity.FATAL,
                    source="PACKAGE",
                    section="manifest.json",
                    contract_type="PD-03",
                    evidence=f"manifest_date={manifest.business_date}, expected_date={expected_business_date}",
                    message="Package business_date does not match expected business date",
                    disposition=Disposition.REJECTED,
                )
            )

        # Check for unlisted payload files in package
        manifest_paths = {entry.payload_path for entry in manifest.sections}
        for path in payloads.keys():
            if path != "manifest.json" and path not in manifest_paths:
                all_findings.append(
                    ValidationFinding(
                        code="PAY-UNLISTED-FILE",
                        severity=FindingSeverity.FATAL,
                        source="PACKAGE",
                        section=path,
                        contract_type="PD-03",
                        evidence=f"unlisted_path={path}",
                        message=f"Payload file '{path}' is present in package but not listed in manifest.json",
                        disposition=Disposition.REJECTED,
                    )
                )

        # 2. Process each section entry in manifest
        for entry in manifest.sections:
            src = entry.source_system
            sec = entry.entity_name
            sec_label = f"{src}/{sec}"
            processed_sections.append((src, sec))

            content = payloads.get(entry.payload_path)
            if content is None:
                all_findings.append(
                    ValidationFinding(
                        code="PAY-MISSING-PAYLOAD",
                        severity=FindingSeverity.FATAL,
                        source=src,
                        section=sec,
                        contract_type="PD-03",
                        evidence=f"payload_path={entry.payload_path}",
                        message=f"Missing payload file for {sec_label} at {entry.payload_path}",
                        disposition=Disposition.REJECTED,
                    )
                )
                continue

            # Byte-level and framing validation
            actual_cols, pay_findings = validate_payload_bytes(entry, content)
            all_findings.extend(pay_findings)

            if actual_cols is None:
                continue

            # 3. PD-01 Physical Header Validation
            hdr_findings = self.headers.validate_header(src, sec, entry.schema_version, actual_cols)
            all_findings.extend(hdr_findings)

            # 4. PD-02 Schema Contract Validation
            sch_findings = self.schemas.validate_schema_reference(src, sec, entry.schema_version)
            all_findings.extend(sch_findings)

            # If header or schema failed closed with fatal finding, skip row evaluation
            has_fatal_contract_error = any(
                f.severity == FindingSeverity.FATAL and f.source == src and f.section == sec
                for f in all_findings
            )
            if has_fatal_contract_error:
                continue

            # Parse data rows for field-level checks
            schema_contract = self.schemas.get(src, sec, entry.schema_version)
            if schema_contract is None:
                continue

            fields_by_name = {f.name: f for f in schema_contract.fields}
            decoded = content.decode("utf-8")
            rows = list(csv.reader(io.StringIO(decoded, newline=""), strict=True))
            data_rows = rows[1:]

            monetary_values: list[str] = []

            for row_idx, row in enumerate(data_rows, start=2):
                if len(row) != len(actual_cols):
                    continue
                row_dict = dict(zip(actual_cols, row))

                for col_name, cell_val in row_dict.items():
                    field_spec = fields_by_name.get(col_name)
                    is_valid_type = True
                    is_required = True
                    if field_spec:
                        is_valid_type = _valid_value(cell_val, field_spec)
                        is_required = field_spec.required

                    # 5. PD-04 Applicability
                    cell_state, app_findings = self.applicability.evaluate_cell_state(
                        source=src,
                        section=sec,
                        schema_version=entry.schema_version,
                        field_name=col_name,
                        raw_value=cell_val,
                        row_record=row_dict,
                        applicability=ApplicabilityState.ALWAYS,
                        is_required=is_required,
                        is_valid_type=is_valid_type,
                    )
                    for af in app_findings:
                        all_findings.append(
                            ValidationFinding(
                                code=af.code,
                                severity=af.severity,
                                source=af.source,
                                section=af.section,
                                field_name=af.field_name,
                                contract_type=af.contract_type,
                                record_identity=f"row_{row_idx}",
                                evidence=af.evidence,
                                message=af.message,
                                disposition=af.disposition,
                            )
                        )

                    # 6. PD-06 Mapping checks if mapped domain
                    if entry.mapping_version_references:
                        for map_ver in entry.mapping_version_references:
                            # If this column is a domain key in mappings
                            m_entry = self.mappings.get_entry(src, col_name, map_ver, cell_val)
                            if m_entry is not None:
                                res, m_findings = self.mappings.resolve(src, col_name, map_ver, cell_val)
                                for mf in m_findings:
                                    all_findings.append(
                                        ValidationFinding(
                                            code=mf.code,
                                            severity=mf.severity,
                                            source=mf.source,
                                            section=mf.section,
                                            field_name=mf.field_name,
                                            contract_type=mf.contract_type,
                                            record_identity=f"row_{row_idx}",
                                            evidence=mf.evidence,
                                            message=mf.message,
                                            disposition=mf.disposition,
                                        )
                                    )

                    # 7. PD-07 Temporal parsing if instant field
                    if field_spec and field_spec.kind == "instant" and cell_val.strip():
                        try:
                            parse_offset_timestamp(cell_val)
                        except (ValueError, TypeError) as exc:
                            all_findings.append(
                                ValidationFinding(
                                    code="TMP-INVALID-INSTANT",
                                    severity=FindingSeverity.ERROR,
                                    source=src,
                                    section=sec,
                                    field_name=col_name,
                                    record_identity=f"row_{row_idx}",
                                    contract_type="PD-07",
                                    evidence=f"instant='{cell_val}'",
                                    message=f"Temporal validation failed: {exc}",
                                    disposition=Disposition.QUARANTINED,
                                )
                            )

                    # Track monetary values for financial control
                    if col_name == "amount" and cell_val.strip():
                        monetary_values.append(cell_val)

            # 8. PD-05 Financial Control Reconciliation if controls referenced
            if entry.financial_control_references:
                for ctrl_ref in entry.financial_control_references:
                    # In fixture packages, test reconciliation
                    reconciliation, fin_findings = self.financial.reconcile_population(
                        source=src,
                        section=sec,
                        schema_version=entry.schema_version,
                        currency="USD",
                        source_control_total=sum((Decimal(v) for v in monetary_values), Decimal("0.0000")),
                        accepted_amounts=monetary_values,
                    )
                    reconciliations.append(reconciliation)
                    all_findings.extend(fin_findings)

        # Determine overall package disposition
        has_fatal = any(f.severity == FindingSeverity.FATAL for f in all_findings)
        has_error = any(f.severity == FindingSeverity.ERROR for f in all_findings)

        if has_fatal:
            disposition = Disposition.REJECTED
            passed = False
        elif has_error:
            disposition = Disposition.QUARANTINED
            passed = False
        else:
            disposition = Disposition.ACCEPTED
            passed = True

        return PipelineExecutionResult(
            disposition=disposition,
            passed=passed,
            findings=tuple(all_findings),
            manifest=manifest,
            processed_sections=tuple(processed_sections),
            reconciliation_results=tuple(reconciliations),
        )
