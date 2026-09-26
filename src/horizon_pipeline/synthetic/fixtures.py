"""Test Fixture Contracts and Serialization Helpers.

CRITICAL NOTICE: TEST FIXTURE ONLY.
These contracts and packages are explicitly isolated for offline pipeline
unit and integration testing. They are NOT approved Horizon Community Bank
production contracts and must never enter production registries.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Mapping

from ..contracts.applicability import (
    ApplicabilityPredicateContract,
    ApplicabilityRegistry,
    ApplicabilityState,
    FieldDisposition,
)
from ..contracts.financial import (
    FinancialControlContract,
    FinancialControlEngine,
)
from ..contracts.headers import HeaderRegistry, PhysicalHeaderContract
from ..contracts.mapping import MappingEntry, StatusMappingRegistry
from ..contracts.schemas import FieldContract, SchemaContract, SchemaRegistry
from ..contracts.states import ContractState
from ..intake import REQUIRED_SECTIONS
from .generator import SyntheticDataset

FIXTURE_SCHEMA_PREFIX = "FIXTURE.SYN."
FIXTURE_MAPPING_VERSION = "FIXTURE_MAP_V1"

# Fixture-only column definitions for all 27 sections
FIXTURE_SECTION_COLUMNS: dict[tuple[str, str], tuple[str, ...]] = {
    ("SRC-01", "customers"): ("customer_id", "tax_identifier_masked", "customer_name", "customer_segment", "primary_branch_id", "business_date"),
    ("SRC-01", "accounts"): ("account_id", "customer_id", "account_type", "currency", "branch_id", "account_status", "business_date"),
    ("SRC-01", "holders"): ("account_id", "customer_id", "relationship_role", "effective_start"),
    ("SRC-01", "transactions"): ("transaction_id", "account_id", "business_date", "amount", "currency", "transaction_type", "transaction_status", "posted_at"),
    ("SRC-01", "account_restriction_state"): ("account_id", "restriction_status", "effective_start"),
    ("SRC-01", "account_branch_assignment"): ("account_id", "branch_id", "branch_role", "effective_start"),
    ("SRC-02", "loans"): ("loan_id", "customer_id", "loan_type", "original_principal", "currency", "origination_date", "branch_id"),
    ("SRC-02", "borrowers"): ("loan_id", "customer_id", "relationship_role", "effective_start"),
    ("SRC-02", "positions"): ("loan_id", "business_date", "outstanding_principal", "currency", "days_past_due", "loan_status"),
    ("SRC-02", "payments"): ("payment_id", "loan_id", "amount", "currency", "payment_status", "paid_at", "posted_at"),
    ("SRC-02", "loan_schedule"): ("schedule_id", "loan_id", "payment_frequency", "installment_amount", "currency"),
    ("SRC-02", "loan_obligation"): ("obligation_id", "loan_id", "due_date", "scheduled_amount", "currency"),
    ("SRC-02", "payment_allocation"): ("allocation_id", "payment_id", "allocation_component", "amount", "currency"),
    ("SRC-02", "payment_unapplied"): ("payment_id", "amount", "currency"),
    ("SRC-02", "payment_adjustment"): ("adjustment_id", "payment_id", "adjustment_kind", "amount", "currency"),
    ("SRC-02", "loan_account"): ("loan_id", "account_id", "relationship_role"),
    ("SRC-02", "loan_branch_assignment"): ("loan_id", "branch_id", "branch_role", "effective_start"),
    ("SRC-03", "alerts"): ("alert_id", "customer_id", "account_id", "severity", "alert_reason", "case_status", "created_at"),
    ("SRC-03", "fraud_alert_state"): ("alert_id", "case_status", "effective_start"),
    ("SRC-04", "complaints"): ("complaint_id", "customer_id", "channel", "priority", "complaint_status", "branch_id", "created_at"),
    ("SRC-04", "complaint_snapshot"): ("complaint_id", "business_date", "complaint_status", "priority"),
    ("SRC-04", "complaint_history_event"): ("event_id", "complaint_id", "event_type", "event_at"),
    ("SRC-04", "complaint_branch_assignment"): ("complaint_id", "branch_id", "branch_role", "effective_start"),
    ("SRC-05", "organizational_unit"): ("unit_id", "unit_type", "parent_id"),
    ("SRC-05", "region"): ("region_id", "region_name", "valid_from"),
    ("SRC-05", "branches"): ("branch_id", "region_id", "branch_name", "valid_from"),
    ("SRC-05", "organizational_successor"): ("predecessor_id", "successor_id", "valid_from"),
}


def build_test_fixture_registries() -> tuple[
    HeaderRegistry,
    SchemaRegistry,
    ApplicabilityRegistry,
    StatusMappingRegistry,
    FinancialControlEngine,
]:
    """Construct isolated test-fixture registries for offline end-to-end testing.

    All contracts created here have is_fixture=True.
    """
    headers = HeaderRegistry()
    schemas = SchemaRegistry()
    applicability = ApplicabilityRegistry()
    mappings = StatusMappingRegistry()
    financial = FinancialControlEngine()

    for (source, section), cols in FIXTURE_SECTION_COLUMNS.items():
        s_ver = f"{FIXTURE_SCHEMA_PREFIX}{source}.{section}.v001"

        # 1. Header fixture contract
        headers.register(
            PhysicalHeaderContract(
                source=source,
                section=section,
                schema_version=s_ver,
                columns=cols,
                state=ContractState.ACTIVE,
                is_fixture=True,
            )
        )

        # 2. Schema fixture contract
        fields = tuple(FieldContract(name=col, kind="text", required=False) for col in cols)
        schemas.register(
            SchemaContract(
                source=source,
                section=section,
                schema_version=s_ver,
                fields=fields,
                state=ContractState.ACTIVE,
                is_fixture=True,
            )
        )

    # 3. Fixture predicate: SRC-02 payments posted_at is required only when payment_status == 'POSTED'
    s_ver_pmt = f"{FIXTURE_SCHEMA_PREFIX}SRC-02.payments.v001"
    applicability.register(
        ApplicabilityPredicateContract(
            predicate_id="FIXTURE-PRED-POSTED",
            source="SRC-02",
            section="payments",
            schema_version=s_ver_pmt,
            field_name="posted_at",
            disposition=FieldDisposition.RECEIVED,
            state=ContractState.ACTIVE,
            evaluator=lambda row: row.get("payment_status") == "POSTED",
            description="TEST FIXTURE: posted_at applicable only if payment_status is POSTED",
            is_fixture=True,
        )
    )

    # 4. Fixture status mapping: transaction status mapping in SRC-01
    mappings.register_version("SRC-01", "transaction_status", FIXTURE_MAPPING_VERSION, ContractState.ACTIVE)
    for raw_c, can_c in (("SUCCESSFUL", "POSTED"), ("FAILED", "FAILED"), ("PENDING", "PENDING")):
        mappings.register_entry(
            MappingEntry(
                source_system="SRC-01",
                domain_code="transaction_status",
                mapping_version=FIXTURE_MAPPING_VERSION,
                raw_value=raw_c,
                canonical_value=can_c,
                kpi_eligible=(can_c == "POSTED"),
                risk_eligible=True,
                applicability_eligible=True,
                state=ContractState.ACTIVE,
                is_fixture=True,
            )
        )

    # Fixture-only mappings needed by RC-02 through RC-05 evaluation.
    risk_domains = {
        ("SRC-02", "loan_status"): ("ACTIVE", "DELINQUENT_ACTIVE", "FORBEARANCE_ACTIVE", "PAID_OFF", "CLOSED", "CHARGED_OFF"),
        ("SRC-03", "fraud_case_status"): ("OPEN", "CLOSED"),
        ("SRC-03", "fraud_severity"): ("LOW", "MEDIUM", "HIGH", "CRITICAL"),
        ("SRC-04", "complaint_status"): ("OPEN", "IN_PROGRESS", "REOPENED", "CLOSED"),
        ("SRC-04", "complaint_priority"): ("Critical", "High", "Medium", "Low"),
        ("SRC-01", "restriction_status"): ("NONE", "RESTRICTED", "FROZEN", "BLOCKED"),
    }
    for (source, domain), values in risk_domains.items():
        mappings.register_version(source, domain, FIXTURE_MAPPING_VERSION, ContractState.ACTIVE)
        for value in values:
            mappings.register_entry(MappingEntry(
                source_system=source, domain_code=domain,
                mapping_version=FIXTURE_MAPPING_VERSION, raw_value=value,
                canonical_value=value, state=ContractState.ACTIVE,
                is_fixture=True, evidence_reference="G3 synthetic fixture vocabulary",
            ))

    # 5. Fixture financial control: SRC-01 transactions USD flow control
    s_ver_tx = f"{FIXTURE_SCHEMA_PREFIX}SRC-01.transactions.v001"
    financial.register(
        FinancialControlContract(
            control_id="FIXTURE-FC-TX",
            source="SRC-01",
            section="transactions",
            schema_version=s_ver_tx,
            amount_field="amount",
            currency_field="currency",
            currency="USD",
            state=ContractState.ACTIVE,
            tolerance=Decimal("0.0000"),
            tolerance_state=ContractState.ACTIVE,
            is_fixture=True,
            description="TEST FIXTURE ONLY: SRC-01 transactions USD flow control with exact-zero fixture tolerance",
        )
    )

    return headers, schemas, applicability, mappings, financial


def serialize_csv_exact_bytes(columns: tuple[str, ...], rows: list[dict[str, Any]]) -> bytes:
    """Serialize columns and rows to RFC-4180 CSV bytes with UTF-8 and LF line endings."""
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(columns)
    for row in rows:
        writer.writerow([str(row.get(col, "")) for col in columns])
    return out.getvalue().encode("utf-8")


@dataclass(frozen=True)
class SerializedPackage:
    """An in-memory delivered package containing manifest.json and payload CSV bytes."""

    manifest_json: str
    payloads: dict[str, bytes]  # keyed by relative payload_path, e.g. "sections/SRC-01/customers.csv"
    business_date: date
    revision: int


def build_serialized_fixture_package(
    dataset: SyntheticDataset,
    revision: int = 1,
) -> SerializedPackage:
    """Construct a full 27-section serialized package adhering to PD-03 specification.

    Uses fixture schema IDs and column definitions.
    """
    payloads: dict[str, bytes] = {}
    manifest_sections: list[dict[str, Any]] = []

    bdate_str = dataset.business_date.isoformat()
    cutoff_str = f"{bdate_str}T23:59:59.999999Z"
    extracted_str = f"{bdate_str}T04:30:00.000000Z"

    for (source, section), rows in sorted(dataset.sections.items()):
        cols = FIXTURE_SECTION_COLUMNS.get((source, section), ("id",))
        content = serialize_csv_exact_bytes(cols, rows)
        rel_path = f"sections/{source}/{section}.csv"
        payloads[rel_path] = content

        digest = hashlib.sha256(content).hexdigest()
        s_ver = f"{FIXTURE_SCHEMA_PREFIX}{source}.{section}.v001"

        manifest_sections.append({
            "extract_id": f"EXT-{source}-{section}-{dataset.seed:04d}",
            "source_system": source,
            "entity_name": section,
            "business_date": bdate_str,
            "revision": revision,
            "delivery_mode": "FULL_STATE" if section in {"customers", "accounts", "loans"} else "DAILY_STATE" if section in {"positions", "complaint_snapshot"} else "IMMUTABLE_EVENT",
            "schema_version": s_ver,
            "cutoff_at": cutoff_str,
            "extracted_at": extracted_str,
            "payload_path": rel_path,
            "row_count": len(rows),
            "checksum_algorithm": "SHA-256",
            "checksum_encoding": "LOWERCASE_HEX",
            "checksum": digest,
            "content_encoding": "UTF-8",
            "checksum_scope_reference": "CSV_EXACT_BYTES_V1",
            "mapping_version_references": [FIXTURE_MAPPING_VERSION] if (source, section) == ("SRC-01", "transactions") else [],
            "financial_control_references": ["FIXTURE-FC-TX"] if (source, section) == ("SRC-01", "transactions") else [],
        })

    manifest_dict = {
        "manifest_version": "HCB.SYN.MANIFEST.v001",
        "business_date": bdate_str,
        "sections": manifest_sections,
    }
    manifest_json = json.dumps(manifest_dict, indent=2)

    return SerializedPackage(
        manifest_json=manifest_json,
        payloads=payloads,
        business_date=dataset.business_date,
        revision=revision,
    )
