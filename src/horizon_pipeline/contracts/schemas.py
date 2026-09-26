"""PD-02 Physical Schema Version Contract and Registry.

Enforces:
- Versioned section-level schema identity keyed by (source, section, schema_version)
- Exact-string version lookup
- Unknown-version rejection (fail closed)
- Pending-schema rejection (fail closed)
- Immutable version concepts
- Distinction between schema version and batch revision
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from ..intake import FieldContract
from .findings import Disposition, FindingSeverity, ValidationFinding
from .states import ContractState, PendingContractError, UnsupportedContractError


@dataclass(frozen=True)
class SchemaContract:
    """Versioned physical schema contract for a section."""

    source: str
    section: str
    schema_version: str
    fields: tuple[FieldContract, ...]
    state: ContractState
    predecessor: str | None = None
    is_fixture: bool = False

    def __post_init__(self) -> None:
        if self.state == ContractState.ACTIVE and not self.fields:
            raise ValueError("Active schema contract must define at least one field")


class SchemaRegistry:
    """Registry managing versioned physical schema contracts."""

    def __init__(self) -> None:
        self._registry: dict[tuple[str, str, str], SchemaContract] = {}

    def register(self, contract: SchemaContract) -> None:
        """Register a schema contract. Immutable once registered."""
        key = (contract.source, contract.section, contract.schema_version)
        if key in self._registry:
            raise ValueError(f"Schema contract already registered for {key}")
        self._registry[key] = contract

    def get(self, source: str, section: str, schema_version: str) -> SchemaContract | None:
        """Look up schema by (source, section, schema_version)."""
        return self._registry.get((source, section, schema_version))

    def require_active(self, source: str, section: str, schema_version: str) -> SchemaContract:
        """Retrieve active schema contract or fail closed with explicit exception."""
        contract = self.get(source, section, schema_version)
        if contract is None:
            raise UnsupportedContractError(
                f"Unknown schema version '{schema_version}' for {source}/{section}",
                contract_type="PD-02",
                source=source,
                section=section,
                identifier=schema_version,
            )
        if contract.state == ContractState.PENDING:
            raise PendingContractError(
                f"Schema version '{schema_version}' for {source}/{section} is PENDING confirmation; cannot execute.",
                contract_type="PD-02",
                source=source,
                section=section,
                identifier=schema_version,
            )
        if contract.state == ContractState.UNSUPPORTED:
            raise UnsupportedContractError(
                f"Schema version '{schema_version}' for {source}/{section} is UNSUPPORTED",
                contract_type="PD-02",
                source=source,
                section=section,
                identifier=schema_version,
            )
        return contract

    def validate_schema_reference(
        self,
        source: str,
        section: str,
        schema_version: str,
    ) -> list[ValidationFinding]:
        """Validate that a referenced schema is active and available.

        Fails closed on unknown or pending schema.
        """
        findings: list[ValidationFinding] = []
        contract = self.get(source, section, schema_version)
        if contract is None:
            findings.append(
                ValidationFinding(
                    code="SCH-UNKNOWN",
                    severity=FindingSeverity.FATAL,
                    source=source,
                    section=section,
                    contract_type="PD-02",
                    evidence=f"schema_version={schema_version}",
                    message=f"Unknown or unapproved schema version: {schema_version}",
                    disposition=Disposition.REJECTED,
                )
            )
        elif contract.state == ContractState.PENDING:
            findings.append(
                ValidationFinding(
                    code="SCH-PENDING",
                    severity=FindingSeverity.FATAL,
                    source=source,
                    section=section,
                    contract_type="PD-02",
                    evidence=f"schema_version={schema_version}",
                    message=(
                        f"Schema version '{schema_version}' for {source}/{section} is PENDING confirmation; "
                        "activation requires approved physical header contract."
                    ),
                    disposition=Disposition.REJECTED,
                )
            )
        elif contract.state == ContractState.UNSUPPORTED:
            findings.append(
                ValidationFinding(
                    code="SCH-UNSUPPORTED",
                    severity=FindingSeverity.FATAL,
                    source=source,
                    section=section,
                    contract_type="PD-02",
                    evidence=f"schema_version={schema_version}",
                    message=f"Schema version '{schema_version}' is marked UNSUPPORTED",
                    disposition=Disposition.REJECTED,
                )
            )
        return findings
