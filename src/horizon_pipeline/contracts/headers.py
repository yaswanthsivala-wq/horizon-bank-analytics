"""PD-01 Physical Header Contract and Registry.

Enforces:
- Versioned physical-header registry keyed by (source, section, schema_version)
- Exact header spelling
- Exact column order
- Duplicate-column rejection
- Missing-column rejection
- Unexpected-column rejection
- Fail closed on PENDING or UNSUPPORTED header contracts
- Critical safety guard: 27 production sections remain PENDING
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .findings import Disposition, FindingSeverity, ValidationFinding
from .states import ContractState, PendingContractError, UnsupportedContractError


@dataclass(frozen=True)
class PhysicalHeaderContract:
    """Versioned physical CSV header specification."""

    source: str
    section: str
    schema_version: str
    columns: tuple[str, ...]
    state: ContractState
    disposition_map: Mapping[str, str] | None = None
    is_fixture: bool = False

    def __post_init__(self) -> None:
        if self.state == ContractState.ACTIVE and not self.columns:
            raise ValueError("Active header contract must define at least one column")
        if self.columns and len(set(self.columns)) != len(self.columns):
            raise ValueError("Header contract definition contains duplicate column names")


class HeaderRegistry:
    """Registry managing versioned physical header contracts."""

    def __init__(self) -> None:
        self._registry: dict[tuple[str, str, str], PhysicalHeaderContract] = {}

    def register(self, contract: PhysicalHeaderContract) -> None:
        """Register a physical header contract. Contracts are immutable once registered."""
        key = (contract.source, contract.section, contract.schema_version)
        if key in self._registry:
            raise ValueError(f"Header contract already registered for {key}")
        self._registry[key] = contract

    def get(self, source: str, section: str, schema_version: str) -> PhysicalHeaderContract | None:
        """Look up a header contract by (source, section, schema_version)."""
        return self._registry.get((source, section, schema_version))

    def validate_header(
        self,
        source: str,
        section: str,
        schema_version: str,
        actual_columns: list[str],
    ) -> list[ValidationFinding]:
        """Validate received header columns against the registered contract.

        Fails closed if the contract is missing, UNSUPPORTED, or PENDING.
        """
        findings: list[ValidationFinding] = []
        contract = self.get(source, section, schema_version)

        if contract is None:
            findings.append(
                ValidationFinding(
                    code="HDR-UNSUPPORTED",
                    severity=FindingSeverity.FATAL,
                    source=source,
                    section=section,
                    contract_type="PD-01",
                    message=f"No header contract registered for {source}/{section} ({schema_version})",
                    disposition=Disposition.REJECTED,
                )
            )
            return findings

        if contract.state == ContractState.PENDING:
            findings.append(
                ValidationFinding(
                    code="HDR-PENDING",
                    severity=FindingSeverity.FATAL,
                    source=source,
                    section=section,
                    contract_type="PD-01",
                    evidence=f"schema_version={schema_version}",
                    message=(
                        f"Physical header contract for {source}/{section} is PENDING confirmation; "
                        "execution fails closed per approved PD-01 annex."
                    ),
                    disposition=Disposition.REJECTED,
                )
            )
            return findings

        if contract.state == ContractState.UNSUPPORTED:
            findings.append(
                ValidationFinding(
                    code="HDR-UNSUPPORTED",
                    severity=FindingSeverity.FATAL,
                    source=source,
                    section=section,
                    contract_type="PD-01",
                    message=f"Header contract for {source}/{section} ({schema_version}) is UNSUPPORTED",
                    disposition=Disposition.REJECTED,
                )
            )
            return findings

        # Active contract validation
        if not actual_columns or any(not col.strip() for col in actual_columns):
            findings.append(
                ValidationFinding(
                    code="HDR-EMPTY-COLUMN",
                    severity=FindingSeverity.FATAL,
                    source=source,
                    section=section,
                    contract_type="PD-01",
                    message="Header contains empty or whitespace-only column name",
                    disposition=Disposition.REJECTED,
                )
            )
            return findings

        # Check for duplicates in actual header
        seen: set[str] = set()
        duplicates: list[str] = []
        for col in actual_columns:
            if col in seen:
                duplicates.append(col)
            seen.add(col)
        if duplicates:
            findings.append(
                ValidationFinding(
                    code="HDR-DUPLICATE",
                    severity=FindingSeverity.FATAL,
                    source=source,
                    section=section,
                    contract_type="PD-01",
                    evidence=f"duplicate_columns={duplicates}",
                    message=f"Duplicate column names in header: {duplicates}",
                    disposition=Disposition.REJECTED,
                )
            )

        # Check missing columns
        expected_set = set(contract.columns)
        actual_set = set(actual_columns)
        missing = [c for c in contract.columns if c not in actual_set]
        if missing:
            findings.append(
                ValidationFinding(
                    code="HDR-MISSING-COLUMN",
                    severity=FindingSeverity.FATAL,
                    source=source,
                    section=section,
                    contract_type="PD-01",
                    evidence=f"missing={missing}",
                    message=f"Missing expected header columns: {missing}",
                    disposition=Disposition.REJECTED,
                )
            )

        # Check unexpected columns
        unexpected = [c for c in actual_columns if c not in expected_set]
        if unexpected:
            findings.append(
                ValidationFinding(
                    code="HDR-UNEXPECTED-COLUMN",
                    severity=FindingSeverity.FATAL,
                    source=source,
                    section=section,
                    contract_type="PD-01",
                    evidence=f"unexpected={unexpected}",
                    message=f"Unexpected header columns: {unexpected}",
                    disposition=Disposition.REJECTED,
                )
            )

        # Check exact column ordering (if set of columns matches)
        if not missing and not unexpected and not duplicates:
            if tuple(actual_columns) != contract.columns:
                findings.append(
                    ValidationFinding(
                        code="HDR-ORDER-MISMATCH",
                        severity=FindingSeverity.FATAL,
                        source=source,
                        section=section,
                        contract_type="PD-01",
                        evidence=f"expected={list(contract.columns)}, actual={actual_columns}",
                        message="Header column order does not match approved contract",
                        disposition=Disposition.REJECTED,
                    )
                )

        return findings

    def require_active(self, source: str, section: str, schema_version: str) -> PhysicalHeaderContract:
        """Retrieve an active header contract or raise explicit error."""
        contract = self.get(source, section, schema_version)
        if contract is None:
            raise UnsupportedContractError(
                f"No header contract registered for {source}/{section} ({schema_version})",
                contract_type="PD-01",
                source=source,
                section=section,
                identifier=schema_version,
            )
        if contract.state == ContractState.PENDING:
            raise PendingContractError(
                f"Header contract for {source}/{section} ({schema_version}) is PENDING confirmation",
                contract_type="PD-01",
                source=source,
                section=section,
                identifier=schema_version,
            )
        if contract.state == ContractState.UNSUPPORTED:
            raise UnsupportedContractError(
                f"Header contract for {source}/{section} ({schema_version}) is UNSUPPORTED",
                contract_type="PD-01",
                source=source,
                section=section,
                identifier=schema_version,
            )
        return contract
