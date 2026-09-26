"""PD-03 Physical Manifest Contract and Validation.

Implements the approved PD-03 physical manifest contract:
- manifest.json specification
- Approved manifest vocabulary
- Exact payload relative paths: sections/<SRC-ID>/<section>.csv
- Rejection of path traversal (.., absolute paths, drive letters, UNC, backslashes)
- Exact-byte SHA-256 verification (lowercase hex, 64 chars)
- Strict row count verification
- UTF-8 without BOM, LF only
- Zero-row section handling
- Duplicate manifest entry and duplicate payload path rejection
- Missing and unlisted payload detection
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Mapping, Sequence

from ..intake import REQUIRED_SECTIONS
from .findings import Disposition, FindingSeverity, ValidationFinding

APPROVED_MANIFEST_VERSION = "HCB.SYN.MANIFEST.v001"
APPROVED_DELIVERY_MODES = frozenset({"FULL_STATE", "EFFECTIVE_HISTORY", "DAILY_STATE", "IMMUTABLE_EVENT"})
APPROVED_CHECKSUM_ALGORITHM = "SHA-256"
APPROVED_CHECKSUM_ENCODING = "LOWERCASE_HEX"
APPROVED_CONTENT_ENCODING = "UTF-8"
APPROVED_CHECKSUM_SCOPE = "CSV_EXACT_BYTES_V1"

HEX_64_PATTERN = re.compile(r"^[0-9a-f]{64}$")
UTC_MICROSECOND_Z_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass(frozen=True)
class ManifestSectionEntry:
    """A validated section entry within manifest.json."""

    extract_id: str
    source_system: str
    entity_name: str
    business_date: date
    revision: int
    delivery_mode: str
    schema_version: str
    cutoff_at: str
    extracted_at: str
    payload_path: str
    row_count: int
    checksum_algorithm: str
    checksum_encoding: str
    checksum: str
    content_encoding: str
    checksum_scope_reference: str
    mapping_version_references: tuple[str, ...]
    financial_control_references: tuple[str, ...]


@dataclass(frozen=True)
class PackageManifest:
    """The root parsed manifest.json."""

    manifest_version: str
    business_date: date
    sections: tuple[ManifestSectionEntry, ...]


def validate_path_safety(payload_path: str, source_system: str, entity_name: str) -> str | None:
    """Check that payload_path strictly conforms to sections/<SRC>/<entity>.csv.

    Rejects path traversal (.., .), leading slashes, drive letters, UNC, backslashes.
    """
    if not isinstance(payload_path, str) or not payload_path.strip():
        return "payload_path must be a nonempty string"
    if "\\" in payload_path:
        return "payload_path must use forward slashes only, backslashes forbidden"
    if payload_path.startswith("/") or payload_path.startswith("./"):
        return "payload_path must be relative without leading / or ./"
    parts = payload_path.split("/")
    if any(p in {"..", ".", ""} for p in parts):
        return "payload_path contains path traversal (. or ..) or empty segments"
    if ":" in payload_path:
        return "payload_path contains drive letter or protocol separator"
    expected_path = f"sections/{source_system}/{entity_name}.csv"
    if payload_path != expected_path:
        return f"payload_path '{payload_path}' must exactly match expected path '{expected_path}'"
    return None


def parse_and_validate_manifest_json(
    raw_json_str: str,
    require_all_27_sections: bool = True,
) -> tuple[PackageManifest | None, list[ValidationFinding]]:
    """Parse and validate manifest.json structure and vocabulary."""
    findings: list[ValidationFinding] = []

    try:
        data = json.loads(raw_json_str)
    except json.JSONDecodeError as exc:
        findings.append(
            ValidationFinding(
                code="MAN-MALFORMED-JSON",
                severity=FindingSeverity.FATAL,
                source="PACKAGE",
                section="manifest.json",
                contract_type="PD-03",
                message=f"manifest.json is malformed JSON: {exc.msg} at line {exc.lineno}",
                disposition=Disposition.REJECTED,
            )
        )
        return None, findings

    if not isinstance(data, dict):
        findings.append(
            ValidationFinding(
                code="MAN-NOT-OBJECT",
                severity=FindingSeverity.FATAL,
                source="PACKAGE",
                section="manifest.json",
                contract_type="PD-03",
                message="manifest.json root must be a JSON object",
                disposition=Disposition.REJECTED,
            )
        )
        return None, findings

    # Check manifest_version
    manifest_version = data.get("manifest_version")
    if manifest_version != APPROVED_MANIFEST_VERSION:
        findings.append(
            ValidationFinding(
                code="MAN-INVALID-VERSION",
                severity=FindingSeverity.FATAL,
                source="PACKAGE",
                section="manifest.json",
                contract_type="PD-03",
                evidence=f"manifest_version={manifest_version}",
                message=f"Invalid manifest_version: expected '{APPROVED_MANIFEST_VERSION}'",
                disposition=Disposition.REJECTED,
            )
        )

    # Check business_date
    raw_bdate = data.get("business_date")
    pkg_business_date: date | None = None
    if not isinstance(raw_bdate, str) or not DATE_PATTERN.fullmatch(raw_bdate):
        findings.append(
            ValidationFinding(
                code="MAN-INVALID-DATE",
                severity=FindingSeverity.FATAL,
                source="PACKAGE",
                section="manifest.json",
                contract_type="PD-03",
                evidence=f"business_date={raw_bdate}",
                message="manifest.json business_date must be YYYY-MM-DD",
                disposition=Disposition.REJECTED,
            )
        )
    else:
        try:
            pkg_business_date = date.fromisoformat(raw_bdate)
        except ValueError:
            findings.append(
                ValidationFinding(
                    code="MAN-INVALID-DATE-VALUE",
                    severity=FindingSeverity.FATAL,
                    source="PACKAGE",
                    section="manifest.json",
                    contract_type="PD-03",
                    evidence=f"business_date={raw_bdate}",
                    message="manifest.json business_date is not a valid calendar date",
                    disposition=Disposition.REJECTED,
                )
            )

    # Check sections array
    sections_raw = data.get("sections")
    if not isinstance(sections_raw, list):
        findings.append(
            ValidationFinding(
                code="MAN-SECTIONS-NOT-ARRAY",
                severity=FindingSeverity.FATAL,
                source="PACKAGE",
                section="manifest.json",
                contract_type="PD-03",
                message="manifest.json 'sections' must be a JSON array",
                disposition=Disposition.REJECTED,
            )
        )
        return None, findings

    parsed_entries: list[ManifestSectionEntry] = []
    seen_identities: set[tuple[str, str]] = set()
    seen_paths: set[str] = set()

    for idx, sec in enumerate(sections_raw):
        sec_label = f"sections[{idx}]"
        if not isinstance(sec, dict):
            findings.append(
                ValidationFinding(
                    code="MAN-SECTION-NOT-OBJECT",
                    severity=FindingSeverity.FATAL,
                    source="PACKAGE",
                    section=sec_label,
                    contract_type="PD-03",
                    message="Section entry must be a JSON object",
                    disposition=Disposition.REJECTED,
                )
            )
            continue

        src = sec.get("source_system", "")
        entity = sec.get("entity_name", "")
        extract_id = sec.get("extract_id", "")
        sec_date_raw = sec.get("business_date", "")
        rev = sec.get("revision")
        mode = sec.get("delivery_mode", "")
        s_ver = sec.get("schema_version", "")
        cutoff = sec.get("cutoff_at", "")
        extracted = sec.get("extracted_at", "")
        p_path = sec.get("payload_path", "")
        rc = sec.get("row_count")
        alg = sec.get("checksum_algorithm", "")
        enc = sec.get("checksum_encoding", "")
        csum = sec.get("checksum", "")
        c_enc = sec.get("content_encoding", "")
        scope = sec.get("checksum_scope_reference", "")
        map_refs = sec.get("mapping_version_references", [])
        fin_refs = sec.get("financial_control_references", [])

        # Validate identity
        if src not in REQUIRED_SECTIONS:
            findings.append(
                ValidationFinding(
                    code="MAN-UNKNOWN-SOURCE",
                    severity=FindingSeverity.FATAL,
                    source=src or "UNKNOWN",
                    section=entity or sec_label,
                    contract_type="PD-03",
                    message=f"Unknown source_system '{src}'",
                    disposition=Disposition.REJECTED,
                )
            )
        elif entity not in REQUIRED_SECTIONS[src]:
            findings.append(
                ValidationFinding(
                    code="MAN-UNKNOWN-ENTITY",
                    severity=FindingSeverity.FATAL,
                    source=src,
                    section=entity or sec_label,
                    contract_type="PD-03",
                    message=f"Unknown entity_name '{entity}' for source '{src}'",
                    disposition=Disposition.REJECTED,
                )
            )

        identity_key = (src, entity)
        if identity_key in seen_identities:
            findings.append(
                ValidationFinding(
                    code="MAN-DUPLICATE-SECTION",
                    severity=FindingSeverity.FATAL,
                    source=src,
                    section=entity,
                    contract_type="PD-03",
                    message=f"Duplicate manifest section entry for {src}/{entity}",
                    disposition=Disposition.REJECTED,
                )
            )
        seen_identities.add(identity_key)

        # Validate extract_id
        if not isinstance(extract_id, str) or not extract_id.strip() or len(extract_id) > 128:
            findings.append(
                ValidationFinding(
                    code="MAN-INVALID-EXTRACT-ID",
                    severity=FindingSeverity.FATAL,
                    source=src,
                    section=entity,
                    contract_type="PD-03",
                    message="extract_id must be a non-empty string <= 128 characters",
                    disposition=Disposition.REJECTED,
                )
            )

        # Validate business date agreement
        if sec_date_raw != raw_bdate:
            findings.append(
                ValidationFinding(
                    code="MAN-DATE-MISMATCH",
                    severity=FindingSeverity.FATAL,
                    source=src,
                    section=entity,
                    contract_type="PD-03",
                    evidence=f"section_date={sec_date_raw}, package_date={raw_bdate}",
                    message="Section business_date differs from package business_date",
                    disposition=Disposition.REJECTED,
                )
            )

        # Validate revision (integer >= 1, not bool)
        if type(rev) is not int or rev < 1:
            findings.append(
                ValidationFinding(
                    code="MAN-INVALID-REVISION",
                    severity=FindingSeverity.FATAL,
                    source=src,
                    section=entity,
                    contract_type="PD-03",
                    evidence=f"revision={rev}",
                    message="revision must be a positive integer >= 1 (Boolean rejected)",
                    disposition=Disposition.REJECTED,
                )
            )

        # Validate delivery_mode
        if mode not in APPROVED_DELIVERY_MODES:
            findings.append(
                ValidationFinding(
                    code="MAN-INVALID-DELIVERY-MODE",
                    severity=FindingSeverity.FATAL,
                    source=src,
                    section=entity,
                    contract_type="PD-03",
                    evidence=f"delivery_mode={mode}",
                    message=f"delivery_mode must be one of {sorted(APPROVED_DELIVERY_MODES)}",
                    disposition=Disposition.REJECTED,
                )
            )

        # Validate schema_version
        if not isinstance(s_ver, str) or not s_ver.strip() or len(s_ver) > 128:
            findings.append(
                ValidationFinding(
                    code="MAN-INVALID-SCHEMA-VERSION",
                    severity=FindingSeverity.FATAL,
                    source=src,
                    section=entity,
                    contract_type="PD-03",
                    message="schema_version must be a non-empty string <= 128 characters",
                    disposition=Disposition.REJECTED,
                )
            )

        # Validate cutoff_at and extracted_at
        for instant_field, instant_val in (("cutoff_at", cutoff), ("extracted_at", extracted)):
            if not isinstance(instant_val, str) or not UTC_MICROSECOND_Z_PATTERN.fullmatch(instant_val):
                findings.append(
                    ValidationFinding(
                        code=f"MAN-INVALID-{instant_field.upper()}",
                        severity=FindingSeverity.FATAL,
                        source=src,
                        section=entity,
                        contract_type="PD-03",
                        evidence=f"{instant_field}={instant_val}",
                        message=f"{instant_field} must be UTC instant YYYY-MM-DDTHH:MM:SS.ffffffZ with exactly 6 fractional digits and Z",
                        disposition=Disposition.REJECTED,
                    )
                )

        # Validate payload_path safety and format
        path_error = validate_path_safety(p_path, src, entity)
        if path_error:
            findings.append(
                ValidationFinding(
                    code="MAN-UNSAFE-PATH",
                    severity=FindingSeverity.FATAL,
                    source=src,
                    section=entity,
                    contract_type="PD-03",
                    evidence=f"payload_path={p_path}",
                    message=path_error,
                    disposition=Disposition.REJECTED,
                )
            )
        if p_path in seen_paths:
            findings.append(
                ValidationFinding(
                    code="MAN-DUPLICATE-PATH",
                    severity=FindingSeverity.FATAL,
                    source=src,
                    section=entity,
                    contract_type="PD-03",
                    evidence=f"payload_path={p_path}",
                    message=f"Duplicate payload_path '{p_path}' in manifest",
                    disposition=Disposition.REJECTED,
                )
            )
        seen_paths.add(p_path)

        # Validate row_count
        if type(rc) is not int or rc < 0:
            findings.append(
                ValidationFinding(
                    code="MAN-INVALID-ROW-COUNT",
                    severity=FindingSeverity.FATAL,
                    source=src,
                    section=entity,
                    contract_type="PD-03",
                    evidence=f"row_count={rc}",
                    message="row_count must be a non-negative integer >= 0 (Boolean rejected)",
                    disposition=Disposition.REJECTED,
                )
            )

        # Validate checksum vocabulary and hex format
        if alg != APPROVED_CHECKSUM_ALGORITHM:
            findings.append(
                ValidationFinding(
                    code="MAN-INVALID-ALGORITHM",
                    severity=FindingSeverity.FATAL,
                    source=src,
                    section=entity,
                    contract_type="PD-03",
                    evidence=f"checksum_algorithm={alg}",
                    message=f"checksum_algorithm must be '{APPROVED_CHECKSUM_ALGORITHM}'",
                    disposition=Disposition.REJECTED,
                )
            )
        if enc != APPROVED_CHECKSUM_ENCODING:
            findings.append(
                ValidationFinding(
                    code="MAN-INVALID-CHECKSUM-ENCODING",
                    severity=FindingSeverity.FATAL,
                    source=src,
                    section=entity,
                    contract_type="PD-03",
                    evidence=f"checksum_encoding={enc}",
                    message=f"checksum_encoding must be '{APPROVED_CHECKSUM_ENCODING}'",
                    disposition=Disposition.REJECTED,
                )
            )
        if not isinstance(csum, str) or not HEX_64_PATTERN.fullmatch(csum):
            findings.append(
                ValidationFinding(
                    code="MAN-INVALID-CHECKSUM-FORMAT",
                    severity=FindingSeverity.FATAL,
                    source=src,
                    section=entity,
                    contract_type="PD-03",
                    evidence=f"checksum={csum}",
                    message="checksum must be exactly 64 lowercase hexadecimal characters",
                    disposition=Disposition.REJECTED,
                )
            )
        if c_enc != APPROVED_CONTENT_ENCODING:
            findings.append(
                ValidationFinding(
                    code="MAN-INVALID-CONTENT-ENCODING",
                    severity=FindingSeverity.FATAL,
                    source=src,
                    section=entity,
                    contract_type="PD-03",
                    evidence=f"content_encoding={c_enc}",
                    message=f"content_encoding must be '{APPROVED_CONTENT_ENCODING}'",
                    disposition=Disposition.REJECTED,
                )
            )
        if scope != APPROVED_CHECKSUM_SCOPE:
            findings.append(
                ValidationFinding(
                    code="MAN-INVALID-CHECKSUM-SCOPE",
                    severity=FindingSeverity.FATAL,
                    source=src,
                    section=entity,
                    contract_type="PD-03",
                    evidence=f"checksum_scope_reference={scope}",
                    message=f"checksum_scope_reference must be '{APPROVED_CHECKSUM_SCOPE}'",
                    disposition=Disposition.REJECTED,
                )
            )

        # Validate reference arrays
        if not isinstance(map_refs, list) or any(not isinstance(r, str) or not r.strip() for r in map_refs):
            findings.append(
                ValidationFinding(
                    code="MAN-INVALID-MAPPING-REFS",
                    severity=FindingSeverity.FATAL,
                    source=src,
                    section=entity,
                    contract_type="PD-03",
                    message="mapping_version_references must be an array of non-empty strings",
                    disposition=Disposition.REJECTED,
                )
            )
        if not isinstance(fin_refs, list) or any(not isinstance(r, str) or not r.strip() for r in fin_refs):
            findings.append(
                ValidationFinding(
                    code="MAN-INVALID-FINANCIAL-REFS",
                    severity=FindingSeverity.FATAL,
                    source=src,
                    section=entity,
                    contract_type="PD-03",
                    message="financial_control_references must be an array of non-empty strings",
                    disposition=Disposition.REJECTED,
                )
            )

        entry_date = date.fromisoformat(sec_date_raw) if DATE_PATTERN.fullmatch(str(sec_date_raw)) else date.min
        parsed_entries.append(
            ManifestSectionEntry(
                extract_id=str(extract_id),
                source_system=str(src),
                entity_name=str(entity),
                business_date=entry_date,
                revision=rev if isinstance(rev, int) else -1,
                delivery_mode=str(mode),
                schema_version=str(s_ver),
                cutoff_at=str(cutoff),
                extracted_at=str(extracted),
                payload_path=str(p_path),
                row_count=rc if isinstance(rc, int) else -1,
                checksum_algorithm=str(alg),
                checksum_encoding=str(enc),
                checksum=str(csum),
                content_encoding=str(c_enc),
                checksum_scope_reference=str(scope),
                mapping_version_references=tuple(map_refs) if isinstance(map_refs, list) else (),
                financial_control_references=tuple(fin_refs) if isinstance(fin_refs, list) else (),
            )
        )

    # Check mandatory section coverage if full package is required
    if require_all_27_sections:
        for src, entities in REQUIRED_SECTIONS.items():
            for entity in sorted(entities):
                if (src, entity) not in seen_identities:
                    findings.append(
                        ValidationFinding(
                            code="MAN-MISSING-SECTION",
                            severity=FindingSeverity.FATAL,
                            source=src,
                            section=entity,
                            contract_type="PD-03",
                            message=f"Mandatory section {src}/{entity} missing from manifest",
                            disposition=Disposition.REJECTED,
                        )
                    )

    if pkg_business_date is None:
        return None, findings

    manifest = PackageManifest(
        manifest_version=str(manifest_version),
        business_date=pkg_business_date,
        sections=tuple(parsed_entries),
    )
    return manifest, findings


def validate_payload_bytes(
    entry: ManifestSectionEntry,
    content: bytes,
) -> tuple[list[str] | None, list[ValidationFinding]]:
    """Validate exact payload bytes against manifest entry.

    Checks:
    - UTF-8 BOM is forbidden
    - LF only, no CR, ends with LF
    - SHA-256 matches entry.checksum
    - Strict CSV row count matches entry.row_count
    - Returns (header_columns, findings)
    """
    findings: list[ValidationFinding] = []

    # Check BOM
    if content.startswith(b"\xef\xbb\xbf"):
        findings.append(
            ValidationFinding(
                code="PAY-BOM-FORBIDDEN",
                severity=FindingSeverity.FATAL,
                source=entry.source_system,
                section=entry.entity_name,
                contract_type="PD-03",
                message="UTF-8 BOM is forbidden; delivered CSV must be UTF-8 without BOM",
                disposition=Disposition.REJECTED,
            )
        )

    # Check line endings: LF only, no CR, must end with LF
    if b"\r" in content or not content.endswith(b"\n"):
        findings.append(
            ValidationFinding(
                code="PAY-INVALID-LINE-ENDINGS",
                severity=FindingSeverity.FATAL,
                source=entry.source_system,
                section=entry.entity_name,
                contract_type="PD-03",
                message="Section payload must use LF line endings and end with LF (CR forbidden)",
                disposition=Disposition.REJECTED,
            )
        )

    # Check exact byte SHA-256 digest
    actual_digest = hashlib.sha256(content).hexdigest()
    if actual_digest != entry.checksum:
        findings.append(
            ValidationFinding(
                code="PAY-CHECKSUM-MISMATCH",
                severity=FindingSeverity.FATAL,
                source=entry.source_system,
                section=entry.entity_name,
                contract_type="PD-03",
                evidence=f"manifest_checksum={entry.checksum}, actual_sha256={actual_digest}",
                message="Payload exact-byte SHA-256 checksum mismatch",
                disposition=Disposition.REJECTED,
            )
        )

    # Decode and parse CSV strictly
    try:
        decoded = content.decode("utf-8")
        reader = csv.reader(io.StringIO(decoded, newline=""), strict=True)
        rows = list(reader)
    except (UnicodeDecodeError, csv.Error) as exc:
        findings.append(
            ValidationFinding(
                code="PAY-INVALID-CSV",
                severity=FindingSeverity.FATAL,
                source=entry.source_system,
                section=entry.entity_name,
                contract_type="PD-03",
                message=f"Invalid UTF-8 or CSV framing: {exc}",
                disposition=Disposition.REJECTED,
            )
        )
        return None, findings

    if not rows or not rows[0] or any(not name.strip() for name in rows[0]):
        findings.append(
            ValidationFinding(
                code="PAY-MISSING-HEADER",
                severity=FindingSeverity.FATAL,
                source=entry.source_system,
                section=entry.entity_name,
                contract_type="PD-01",
                message="Missing, empty, or whitespace-only CSV header",
                disposition=Disposition.REJECTED,
            )
        )
        return None, findings

    header_columns = rows[0]

    # Row count verification
    actual_row_count = len(rows) - 1
    if actual_row_count != entry.row_count:
        findings.append(
            ValidationFinding(
                code="PAY-ROW-COUNT-MISMATCH",
                severity=FindingSeverity.FATAL,
                source=entry.source_system,
                section=entry.entity_name,
                contract_type="PD-03",
                evidence=f"manifest_row_count={entry.row_count}, actual_data_rows={actual_row_count}",
                message=f"Payload data row count ({actual_row_count}) differs from manifest ({entry.row_count})",
                disposition=Disposition.REJECTED,
            )
        )

    # Check row width uniformity
    for row_num, row in enumerate(rows[1:], start=2):
        if len(row) != len(header_columns):
            findings.append(
                ValidationFinding(
                    code="PAY-ROW-WIDTH-MISMATCH",
                    severity=FindingSeverity.FATAL,
                    source=entry.source_system,
                    section=entry.entity_name,
                    record_identity=f"row_{row_num}",
                    contract_type="PD-03",
                    evidence=f"header_cols={len(header_columns)}, row_cols={len(row)}",
                    message=f"Row {row_num} width mismatch",
                    disposition=Disposition.REJECTED,
                )
            )

    return header_columns, findings
