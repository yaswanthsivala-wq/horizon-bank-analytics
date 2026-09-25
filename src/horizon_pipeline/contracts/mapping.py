"""PD-06 Status and Domain Reference Mapping Engine.

Enforces:
- Mapping registry keyed by (source, domain, mapping_version, raw_code)
- Preserves raw value alongside canonical value (never overwrite raw value)
- Preserves applied mapping version lineage
- Rejects unknown raw codes (fail closed: no silent fallback to OTHER, UNKNOWN, or null)
- Rejects unknown, pending, or retired mapping versions
- Keeps candidate production mapping groups (23 groups) as PENDING (0 active production rows)
- Test fixtures isolated with explicit is_fixture=True
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .findings import Disposition, FindingSeverity, ValidationFinding
from .states import ContractState, PendingContractError, UnsupportedContractError


@dataclass(frozen=True)
class MappingEntry:
    """An approved raw-to-canonical mapping entry."""

    source_system: str
    domain_code: str
    mapping_version: str
    raw_value: str
    canonical_value: str
    kpi_eligible: bool = True
    risk_eligible: bool = True
    applicability_eligible: bool = True
    state: ContractState = ContractState.ACTIVE
    is_fixture: bool = False
    evidence_reference: str = ""


@dataclass(frozen=True)
class MappingResolution:
    """Result of mapping lookup, preserving raw and resolved values."""

    raw_value: str
    canonical_value: str | None
    applied_version: str
    kpi_eligible: bool
    risk_eligible: bool
    applicability_eligible: bool
    is_resolved: bool


class StatusMappingRegistry:
    """Registry managing versioned raw-to-canonical status and reference mappings."""

    def __init__(self) -> None:
        self._entries: dict[tuple[str, str, str, str], MappingEntry] = {}
        self._versions: dict[tuple[str, str, str], ContractState] = {}

    def register_version(
        self,
        source_system: str,
        domain_code: str,
        mapping_version: str,
        state: ContractState,
    ) -> None:
        """Register the lifecycle state of a mapping version."""
        key = (source_system, domain_code, mapping_version)
        self._versions[key] = state

    def register_entry(self, entry: MappingEntry) -> None:
        """Register an individual raw-to-canonical mapping row."""
        key = (entry.source_system, entry.domain_code, entry.mapping_version, entry.raw_value)
        if key in self._entries:
            raise ValueError(f"Mapping entry already registered for {key}")
        self._entries[key] = entry
        v_key = (entry.source_system, entry.domain_code, entry.mapping_version)
        if v_key not in self._versions:
            self._versions[v_key] = entry.state

    def get_entry(
        self,
        source_system: str,
        domain_code: str,
        mapping_version: str,
        raw_value: str,
    ) -> MappingEntry | None:
        """Look up mapping entry."""
        return self._entries.get((source_system, domain_code, mapping_version, raw_value))

    def version_state(
        self, source_system: str, domain_code: str, mapping_version: str
    ) -> ContractState | None:
        """Return registered lifecycle state without treating it as execution approval."""
        return self._versions.get((source_system, domain_code, mapping_version))

    def version_has_only_fixture_entries(
        self, source_system: str, domain_code: str, mapping_version: str
    ) -> bool:
        entries = [
            entry for key, entry in self._entries.items()
            if key[:3] == (source_system, domain_code, mapping_version)
        ]
        return bool(entries) and all(entry.is_fixture for entry in entries)

    def version_has_active_production_entries(
        self, source_system: str, domain_code: str, mapping_version: str
    ) -> bool:
        return any(
            key[:3] == (source_system, domain_code, mapping_version)
            and entry.state == ContractState.ACTIVE
            and not entry.is_fixture
            for key, entry in self._entries.items()
        )

    def resolve(
        self,
        source_system: str,
        domain_code: str,
        mapping_version: str,
        raw_value: str,
    ) -> tuple[MappingResolution, list[ValidationFinding]]:
        """Resolve a raw code to its canonical representation.

        Preserves raw value. Fails closed on unknown raw code, unknown version,
        or pending version (never coerces to OTHER, UNKNOWN, or null).
        """
        findings: list[ValidationFinding] = []
        v_key = (source_system, domain_code, mapping_version)
        version_state = self._versions.get(v_key)

        if version_state is None:
            findings.append(
                ValidationFinding(
                    code="MAP-UNKNOWN-VERSION",
                    severity=FindingSeverity.ERROR,
                    source=source_system,
                    section=domain_code,
                    field_name=domain_code,
                    contract_type="PD-06",
                    evidence=f"mapping_version={mapping_version}, raw_value={raw_value}",
                    message=f"Unknown mapping version '{mapping_version}' for domain '{domain_code}'",
                    disposition=Disposition.QUARANTINED,
                )
            )
            return (
                MappingResolution(
                    raw_value=raw_value,
                    canonical_value=None,
                    applied_version=mapping_version,
                    kpi_eligible=False,
                    risk_eligible=False,
                    applicability_eligible=False,
                    is_resolved=False,
                ),
                findings,
            )

        if version_state == ContractState.PENDING:
            findings.append(
                ValidationFinding(
                    code="MAP-PENDING-VERSION",
                    severity=FindingSeverity.ERROR,
                    source=source_system,
                    section=domain_code,
                    field_name=domain_code,
                    contract_type="PD-06",
                    evidence=f"mapping_version={mapping_version}",
                    message=(
                        f"Mapping version '{mapping_version}' for domain '{domain_code}' is PENDING confirmation; "
                        "cannot resolve raw code."
                    ),
                    disposition=Disposition.QUARANTINED,
                )
            )
            return (
                MappingResolution(
                    raw_value=raw_value,
                    canonical_value=None,
                    applied_version=mapping_version,
                    kpi_eligible=False,
                    risk_eligible=False,
                    applicability_eligible=False,
                    is_resolved=False,
                ),
                findings,
            )

        if version_state == ContractState.UNSUPPORTED:
            findings.append(
                ValidationFinding(
                    code="MAP-UNSUPPORTED-VERSION",
                    severity=FindingSeverity.ERROR,
                    source=source_system,
                    section=domain_code,
                    field_name=domain_code,
                    contract_type="PD-06",
                    evidence=f"mapping_version={mapping_version}",
                    message=f"Mapping version '{mapping_version}' is UNSUPPORTED / retired",
                    disposition=Disposition.QUARANTINED,
                )
            )
            return (
                MappingResolution(
                    raw_value=raw_value,
                    canonical_value=None,
                    applied_version=mapping_version,
                    kpi_eligible=False,
                    risk_eligible=False,
                    applicability_eligible=False,
                    is_resolved=False,
                ),
                findings,
            )

        entry = self.get_entry(source_system, domain_code, mapping_version, raw_value)
        if entry is None:
            findings.append(
                ValidationFinding(
                    code="MAP-UNKNOWN-RAW-CODE",
                    severity=FindingSeverity.ERROR,
                    source=source_system,
                    section=domain_code,
                    field_name=domain_code,
                    contract_type="PD-06",
                    evidence=f"raw_value='{raw_value}', domain={domain_code}",
                    message=(
                        f"Unknown raw code '{raw_value}' in domain '{domain_code}'; "
                        "fail closed: cannot coerce to OTHER or UNKNOWN."
                    ),
                    disposition=Disposition.QUARANTINED,
                )
            )
            return (
                MappingResolution(
                    raw_value=raw_value,
                    canonical_value=None,
                    applied_version=mapping_version,
                    kpi_eligible=False,
                    risk_eligible=False,
                    applicability_eligible=False,
                    is_resolved=False,
                ),
                findings,
            )

        if entry.state != ContractState.ACTIVE:
            findings.append(
                ValidationFinding(
                    code="MAP-ENTRY-INACTIVE",
                    severity=FindingSeverity.ERROR,
                    source=source_system,
                    section=domain_code,
                    field_name=domain_code,
                    contract_type="PD-06",
                    evidence=f"raw_value='{raw_value}', state={entry.state.value}",
                    message=f"Mapping entry for '{raw_value}' is not ACTIVE (state={entry.state.value})",
                    disposition=Disposition.QUARANTINED,
                )
            )
            return (
                MappingResolution(
                    raw_value=raw_value,
                    canonical_value=None,
                    applied_version=mapping_version,
                    kpi_eligible=False,
                    risk_eligible=False,
                    applicability_eligible=False,
                    is_resolved=False,
                ),
                findings,
            )

        return (
            MappingResolution(
                raw_value=raw_value,
                canonical_value=entry.canonical_value,
                applied_version=mapping_version,
                kpi_eligible=entry.kpi_eligible,
                risk_eligible=entry.risk_eligible,
                applicability_eligible=entry.applicability_eligible,
                is_resolved=True,
            ),
            findings,
        )
