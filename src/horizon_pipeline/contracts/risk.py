"""Versioned risk-rule catalog contracts with strict fixture isolation."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .states import ContractState


@dataclass(frozen=True)
class RiskRuleCatalogContract:
    catalog_version: str
    classification_rule_version: str
    condition_versions: Mapping[str, str]
    state: ContractState
    is_fixture: bool
    approval_reference: str = ""

    def __post_init__(self) -> None:
        # A frozen dataclass does not freeze a caller-owned dictionary. Copy it
        # so catalog membership cannot change after registry admission.
        object.__setattr__(self, "condition_versions", MappingProxyType(dict(self.condition_versions)))


class RiskRuleCatalogRegistry:
    """Resolve complete catalog versions; never infer approval from caller data."""

    def __init__(self) -> None:
        self._catalogs: dict[str, RiskRuleCatalogContract] = {}

    def register(self, contract: RiskRuleCatalogContract) -> None:
        if contract.catalog_version in self._catalogs:
            raise ValueError(f"Risk catalog already registered: {contract.catalog_version}")
        self._catalogs[contract.catalog_version] = contract

    def resolve(
        self, catalog_version: str, execution_mode: object
    ) -> tuple[RiskRuleCatalogContract | None, str | None]:
        # Deferred import avoids a package-initialization cycle while enforcing
        # the canonical enum identity at the public registry boundary.
        from ..processing.records import ExecutionMode
        if type(execution_mode) is not ExecutionMode:
            raise TypeError("execution_mode must be an ExecutionMode enum member")
        contract = self._catalogs.get(catalog_version)
        if contract is None:
            return None, "CATALOG_NOT_REGISTERED"
        if contract.state != ContractState.ACTIVE:
            return None, f"CATALOG_{contract.state.value}"
        if execution_mode is ExecutionMode.PRODUCTION:
            if contract.is_fixture:
                return None, "FIXTURE_CATALOG_PROHIBITED_IN_PRODUCTION"
            if not contract.approval_reference:
                return None, "CATALOG_APPROVAL_EVIDENCE_MISSING"
        elif not contract.is_fixture:
            return None, "PRODUCTION_CATALOG_PROHIBITED_IN_FIXTURE_MODE"
        return contract, None

    def all_catalogs(self) -> tuple[RiskRuleCatalogContract, ...]:
        return tuple(self._catalogs.values())
