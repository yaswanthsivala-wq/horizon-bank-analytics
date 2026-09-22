"""Validate delivered section bytes without loading or publishing data.

The manifest is supplied by the caller because physical manifest packaging is
still pending confirmation. No customer records are retained by this module.
"""

from __future__ import annotations

import csv
import hashlib
import io
import re
from dataclasses import dataclass
from datetime import date
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Mapping


REQUIRED_SECTIONS = {
    "SRC-01": frozenset({"customers", "accounts", "holders", "transactions", "account_restriction_state", "account_branch_assignment"}),
    "SRC-02": frozenset({"loans", "borrowers", "positions", "payments", "loan_schedule", "loan_obligation", "payment_allocation", "payment_unapplied", "payment_adjustment", "loan_account", "loan_branch_assignment"}),
    "SRC-03": frozenset({"alerts", "fraud_alert_state"}),
    "SRC-04": frozenset({"complaints", "complaint_snapshot", "complaint_history_event", "complaint_branch_assignment"}),
    "SRC-05": frozenset({"organizational_unit", "region", "branches", "organizational_successor"}),
}


@dataclass(frozen=True)
class SectionManifest:
    source: str
    section: str
    business_date: date
    revision: int
    row_count: int
    sha256: str
    schema_version: str = ""


@dataclass(frozen=True)
class FieldContract:
    name: str
    kind: str
    required: bool = True
    max_length: int | None = None
    precision: int | None = None
    scale: int | None = None


@dataclass(frozen=True)
class SectionContract:
    schema_version: str
    fields: tuple[FieldContract, ...]


def _valid_value(value: str, field: FieldContract) -> bool:
    if not value.strip():
        return not field.required
    kind = field.kind
    if kind == "text":
        return field.max_length is None or len(value) <= field.max_length
    if kind == "date":
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            return False
        try:
            return date.fromisoformat(value).isoformat() == value
        except ValueError:
            return False
    if kind in {"integer", "int64", "revision"}:
        if not re.fullmatch(r"-?(0|[1-9][0-9]*)", value):
            return False
        number = int(value)
        return (kind != "revision" or number >= 1) and (kind != "int64" or 0 <= number <= 2**63 - 1)
    if kind == "decimal":
        if not re.fullmatch(r"-?(0|[1-9][0-9]*)(\.[0-9]+)?", value):
            return False
        try:
            number = Decimal(value)
        except InvalidOperation:
            return False
        sign, digits, exponent = number.as_tuple()
        fractional = max(-exponent, 0)
        integer_digits = max(len(digits) + exponent, 0)
        return (field.scale is None or fractional <= field.scale) and (
            field.precision is None or integer_digits + fractional <= field.precision
        )
    if kind == "instant":
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})", value):
            return False
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).utcoffset() is not None
        except ValueError:
            return False
    if kind == "currency":
        return bool(re.fullmatch(r"[A-Z]{3}", value))
    raise ValueError(f"unsupported approved field kind: {kind}")


@dataclass(frozen=True)
class ValidationResult:
    passed: bool
    findings: tuple[str, ...]


def _section_findings(manifest: SectionManifest, content: bytes, contract: SectionContract | None) -> list[str]:
    findings: list[str] = []
    if type(manifest.revision) is not int or manifest.revision < 1:
        findings.append("invalid revision")
    if type(manifest.row_count) is not int or manifest.row_count < 0:
        findings.append("invalid row count")
    if not isinstance(manifest.schema_version, str) or not manifest.schema_version.strip() or len(manifest.schema_version) > 128:
        findings.append("missing or invalid schema version")
    if type(manifest.business_date) is not date:
        findings.append("invalid manifest business date")
    if contract is None:
        findings.append("approved physical field/schema contract unavailable")
    elif manifest.schema_version != contract.schema_version:
        findings.append("schema-version mismatch")
    digest = hashlib.sha256(content).hexdigest()
    if len(manifest.sha256) != 64 or any(c not in "0123456789abcdef" for c in manifest.sha256):
        findings.append("invalid lowercase SHA-256 digest")
    elif digest != manifest.sha256:
        findings.append("checksum mismatch")
    if content.startswith(b"\xef\xbb\xbf"):
        findings.append("UTF-8 BOM is forbidden")
    if b"\r" in content or not content.endswith(b"\n"):
        findings.append("section must use LF and end with LF")
    try:
        decoded = content.decode("utf-8")
        rows = list(csv.reader(io.StringIO(decoded, newline=""), strict=True))
    except (UnicodeDecodeError, csv.Error):
        findings.append("invalid UTF-8 or CSV")
        return findings
    if not rows or not rows[0] or any(not name.strip() for name in rows[0]):
        findings.append("missing or invalid header")
        return findings
    if len(set(rows[0])) != len(rows[0]):
        findings.append("duplicate header field")
    if any(len(row) != len(rows[0]) for row in rows[1:]):
        findings.append("row width mismatch")
    if type(manifest.row_count) is int and len(rows) - 1 != manifest.row_count:
        findings.append("row count mismatch")
    if contract is not None:
        expected = {field.name for field in contract.fields}
        actual = set(rows[0])
        for name in sorted(expected - actual):
            findings.append(f"missing field: {name}")
        for name in sorted(actual - expected):
            findings.append(f"unexpected field: {name}")
        if len(set(rows[0])) == len(rows[0]):
            fields = {field.name: field for field in contract.fields}
            for row_number, row in enumerate(rows[1:], start=2):
                if len(row) != len(rows[0]):
                    continue
                values = dict(zip(rows[0], row))
                for name, field in fields.items():
                    if name in values and not _valid_value(values[name], field):
                        findings.append(f"row {row_number}: invalid {name} ({field.kind})")
                manifest_date = manifest.business_date.isoformat() if type(manifest.business_date) is date else None
                for name, expected_value in (("source_system", manifest.source), ("entity_name", manifest.section), ("business_date", manifest_date), ("revision", str(manifest.revision))):
                    if name in values and values[name] != expected_value:
                        findings.append(f"row {row_number}: {name} differs from manifest")
    return findings


def validate_delivery(
    business_date: date,
    sections: Mapping[tuple[str, str], tuple[SectionManifest, bytes]],
    contracts: Mapping[tuple[str, str], SectionContract] | None = None,
) -> ValidationResult:
    """Check mandatory presence and byte-level controls for one business date.

    A passing result covers only these intake controls. It is not a publication
    decision, financial reconciliation, or freshness check. Field validation
    fails closed where a reviewed section schema is unavailable.
    """
    findings: list[str] = []
    for source, names in REQUIRED_SECTIONS.items():
        for name in sorted(names):
            if (source, name) not in sections:
                findings.append(f"{source}/{name}: missing required section")
    for (source, name), (manifest, content) in sections.items():
        label = f"{source}/{name}"
        if source not in REQUIRED_SECTIONS:
            findings.append(f"{label}: unknown source")
        if (manifest.source, manifest.section) != (source, name):
            findings.append(f"{label}: manifest identity mismatch")
        if type(manifest.business_date) is not date or manifest.business_date != business_date:
            findings.append(f"{label}: business date mismatch")
        contract = contracts.get((source, name)) if contracts is not None else None
        findings.extend(f"{label}: {finding}" for finding in _section_findings(manifest, content, contract))
    return ValidationResult(not findings, tuple(sorted(findings)))
