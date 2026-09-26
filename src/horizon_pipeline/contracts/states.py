"""Explicit contract lifecycle states and exceptions for Horizon Community Bank.

Operating principle: Fail closed when execution requires a PENDING or
UNSUPPORTED contract.
"""

from __future__ import annotations

from enum import Enum


class ContractState(str, Enum):
    """Lifecycle states for executable contracts."""

    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    UNSUPPORTED = "UNSUPPORTED"


class ContractError(Exception):
    """Base exception for all contract violations."""

    def __init__(
        self,
        message: str,
        *,
        contract_type: str | None = None,
        source: str | None = None,
        section: str | None = None,
        identifier: str | None = None,
        state: ContractState | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.contract_type = contract_type
        self.source = source
        self.section = section
        self.identifier = identifier
        self.state = state

    def __str__(self) -> str:
        parts = [self.message]
        details = []
        if self.contract_type:
            details.append(f"contract_type={self.contract_type}")
        if self.source:
            details.append(f"source={self.source}")
        if self.section:
            details.append(f"section={self.section}")
        if self.identifier:
            details.append(f"identifier={self.identifier}")
        if self.state:
            details.append(f"state={self.state.value}")
        if details:
            parts.append(f"({', '.join(details)})")
        return " ".join(parts)


class PendingContractError(ContractError):
    """Raised when attempting to execute against a required PENDING contract."""

    def __init__(
        self,
        message: str,
        *,
        contract_type: str | None = None,
        source: str | None = None,
        section: str | None = None,
        identifier: str | None = None,
    ) -> None:
        super().__init__(
            message,
            contract_type=contract_type,
            source=source,
            section=section,
            identifier=identifier,
            state=ContractState.PENDING,
        )


class UnsupportedContractError(ContractError):
    """Raised when attempting to execute against an UNSUPPORTED contract."""

    def __init__(
        self,
        message: str,
        *,
        contract_type: str | None = None,
        source: str | None = None,
        section: str | None = None,
        identifier: str | None = None,
    ) -> None:
        super().__init__(
            message,
            contract_type=contract_type,
            source=source,
            section=section,
            identifier=identifier,
            state=ContractState.UNSUPPORTED,
        )


class ContractValidationError(ContractError):
    """Raised when payload data fails an active contract rule."""

    def __init__(
        self,
        message: str,
        *,
        contract_type: str | None = None,
        source: str | None = None,
        section: str | None = None,
        identifier: str | None = None,
    ) -> None:
        super().__init__(
            message,
            contract_type=contract_type,
            source=source,
            section=section,
            identifier=identifier,
            state=ContractState.ACTIVE,
        )
