"""PD-05 Financial Control and Exact-Decimal Reconciliation Engine.

Enforces:
- Exact decimal arithmetic using decimal.Decimal exclusively (no binary float)
- Scale 4 monetary precision (0.0001)
- Disjoint population reconciliation:
    source_control_total = accepted_total + quarantined_total + approved_excluded_total
    residual = source_control_total - (accepted_total + quarantined_total + approved_excluded_total)
- Production tolerance remains PENDING confirmation (never defaulted to 0.0000 or numeric zero)
- Missing/unresolved tolerance fails closed when reconciliation depends on it
- Missing/unavailable control is NOT numeric zero (never fabricate zero)
- Strict currency segregation (cross-currency aggregation forbidden)
- Candidate production financial populations (FC-C01..FC-C07) remain PENDING
- Isolated test fixtures may explicitly define test-fixture-only tolerance (e.g. Decimal("0.0000"))
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN
from enum import Enum
from typing import Mapping, Sequence

from .findings import Disposition, FindingSeverity, ValidationFinding
from .states import ContractState, PendingContractError, UnsupportedContractError

SCALE_4 = Decimal("0.0001")


class ControlAvailability(str, Enum):
    """Availability state of a financial control."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True)
class FinancialControlContract:
    """Versioned financial control specification for a section/currency population."""

    control_id: str
    source: str
    section: str
    schema_version: str
    amount_field: str
    currency_field: str
    currency: str
    state: ContractState
    sign_convention: str = "SIGNED"
    tolerance: Decimal | None = None
    tolerance_state: ContractState = ContractState.PENDING
    is_fixture: bool = False
    description: str = ""


@dataclass(frozen=True)
class ReconciliationResult:
    """Result of exact-decimal financial reconciliation."""

    control_id: str
    source: str
    section: str
    currency: str
    source_control_total: Decimal | None
    accepted_total: Decimal
    quarantined_total: Decimal
    approved_excluded_total: Decimal
    reconciled_component_total: Decimal
    residual: Decimal | None
    is_balanced: bool
    availability: ControlAvailability
    unavailable_reason: str | None = None


def parse_decimal_exact(value: str | Decimal, scale: int = 4) -> Decimal:
    """Parse string to exact Decimal with scale validation.

    Does not accept binary float inputs.
    """
    if isinstance(value, float):
        raise TypeError("Binary float is strictly forbidden for financial calculations; use str or Decimal")
    if isinstance(value, Decimal):
        d = value
    else:
        try:
            d = Decimal(str(value).strip())
        except InvalidOperation as exc:
            raise ValueError(f"Invalid monetary decimal string '{value}': {exc}") from exc

    # Validate scale does not exceed allowed scale
    sign, digits, exponent = d.as_tuple()
    fractional = max(-exponent, 0)
    if fractional > scale:
        raise ValueError(f"Monetary value '{value}' exceeds maximum scale {scale}")
    return d.quantize(SCALE_4)


class FinancialControlEngine:
    """Engine executing exact-decimal financial reconciliation."""

    def __init__(self) -> None:
        self._controls: dict[tuple[str, str, str, str], FinancialControlContract] = {}

    def register(self, control: FinancialControlContract) -> None:
        """Register a financial control contract."""
        key = (control.source, control.section, control.schema_version, control.currency)
        if key in self._controls:
            raise ValueError(f"Financial control already registered for {key}")
        self._controls[key] = control

    def get(
        self,
        source: str,
        section: str,
        schema_version: str,
        currency: str,
    ) -> FinancialControlContract | None:
        """Retrieve financial control contract."""
        return self._controls.get((source, section, schema_version, currency))

    def reconcile_population(
        self,
        source: str,
        section: str,
        schema_version: str,
        currency: str,
        source_control_total: Decimal | str | None,
        accepted_amounts: Sequence[Decimal | str],
        quarantined_amounts: Sequence[Decimal | str] = (),
        approved_excluded_amounts: Sequence[Decimal | str] = (),
        availability: ControlAvailability = ControlAvailability.AVAILABLE,
        unavailable_reason: str | None = None,
    ) -> tuple[ReconciliationResult, list[ValidationFinding]]:
        """Reconcile a monetary population using exact decimal arithmetic.

        Fails closed on PENDING, UNSUPPORTED, unavailable, or cross-currency controls.
        """
        findings: list[ValidationFinding] = []
        contract = self.get(source, section, schema_version, currency)

        if contract is None:
            findings.append(
                ValidationFinding(
                    code="FIN-UNSUPPORTED-CONTROL",
                    severity=FindingSeverity.FATAL,
                    source=source,
                    section=section,
                    contract_type="PD-05",
                    evidence=f"currency={currency}, schema={schema_version}",
                    message=f"No financial control contract registered for {source}/{section} ({currency})",
                    disposition=Disposition.REJECTED,
                )
            )
            return (
                ReconciliationResult(
                    control_id="UNKNOWN",
                    source=source,
                    section=section,
                    currency=currency,
                    source_control_total=None,
                    accepted_total=Decimal("0.0000"),
                    quarantined_total=Decimal("0.0000"),
                    approved_excluded_total=Decimal("0.0000"),
                    reconciled_component_total=Decimal("0.0000"),
                    residual=None,
                    is_balanced=False,
                    availability=ControlAvailability.UNAVAILABLE,
                    unavailable_reason="Contract not registered",
                ),
                findings,
            )

        if contract.state == ContractState.PENDING:
            findings.append(
                ValidationFinding(
                    code="FIN-CONTROL-PENDING",
                    severity=FindingSeverity.FATAL,
                    source=source,
                    section=section,
                    contract_type="PD-05",
                    evidence=f"control_id={contract.control_id}",
                    message=(
                        f"Financial control '{contract.control_id}' for {source}/{section} is PENDING confirmation; "
                        "cannot execute reconciliation."
                    ),
                    disposition=Disposition.REJECTED,
                )
            )
            if contract.tolerance is None or contract.tolerance_state != ContractState.ACTIVE:
                findings.append(
                    ValidationFinding(
                        code="FIN-TOLERANCE-UNRESOLVED",
                        severity=FindingSeverity.FATAL,
                        source=source,
                        section=section,
                        contract_type="PD-05",
                        evidence=f"control_id={contract.control_id}, tolerance_state={contract.tolerance_state.value}",
                        message=(
                            f"Financial control '{contract.control_id}' tolerance is unresolved "
                            f"({contract.tolerance_state.value}); cannot execute reconciliation without confirmed tolerance."
                        ),
                        disposition=Disposition.REJECTED,
                    )
                )
            return (
                ReconciliationResult(
                    control_id=contract.control_id,
                    source=source,
                    section=section,
                    currency=currency,
                    source_control_total=None,
                    accepted_total=Decimal("0.0000"),
                    quarantined_total=Decimal("0.0000"),
                    approved_excluded_total=Decimal("0.0000"),
                    reconciled_component_total=Decimal("0.0000"),
                    residual=None,
                    is_balanced=False,
                    availability=ControlAvailability.UNAVAILABLE,
                    unavailable_reason="Contract and/or tolerance is pending confirmation",
                ),
                findings,
            )

        if contract.tolerance is None or contract.tolerance_state != ContractState.ACTIVE:
            findings.append(
                ValidationFinding(
                    code="FIN-TOLERANCE-UNRESOLVED",
                    severity=FindingSeverity.FATAL,
                    source=source,
                    section=section,
                    contract_type="PD-05",
                    evidence=f"control_id={contract.control_id}, tolerance_state={contract.tolerance_state.value}",
                    message=(
                        f"Financial control '{contract.control_id}' tolerance is unresolved "
                        f"({contract.tolerance_state.value}); cannot execute reconciliation without confirmed tolerance."
                    ),
                    disposition=Disposition.REJECTED,
                )
            )
            return (
                ReconciliationResult(
                    control_id=contract.control_id,
                    source=source,
                    section=section,
                    currency=currency,
                    source_control_total=None,
                    accepted_total=Decimal("0.0000"),
                    quarantined_total=Decimal("0.0000"),
                    approved_excluded_total=Decimal("0.0000"),
                    reconciled_component_total=Decimal("0.0000"),
                    residual=None,
                    is_balanced=False,
                    availability=ControlAvailability.UNAVAILABLE,
                    unavailable_reason="Financial tolerance is unresolved",
                ),
                findings,
            )

        if availability == ControlAvailability.UNAVAILABLE:
            reason = unavailable_reason or "Control total not supplied"
            findings.append(
                ValidationFinding(
                    code="FIN-CONTROL-UNAVAILABLE",
                    severity=FindingSeverity.FATAL,
                    source=source,
                    section=section,
                    contract_type="PD-05",
                    evidence=f"reason={reason}",
                    message=f"Required financial control is UNAVAILABLE: {reason}; missing control is NOT zero.",
                    disposition=Disposition.REJECTED,
                )
            )
            return (
                ReconciliationResult(
                    control_id=contract.control_id,
                    source=source,
                    section=section,
                    currency=currency,
                    source_control_total=None,
                    accepted_total=Decimal("0.0000"),
                    quarantined_total=Decimal("0.0000"),
                    approved_excluded_total=Decimal("0.0000"),
                    reconciled_component_total=Decimal("0.0000"),
                    residual=None,
                    is_balanced=False,
                    availability=ControlAvailability.UNAVAILABLE,
                    unavailable_reason=reason,
                ),
                findings,
            )

        if source_control_total is None:
            findings.append(
                ValidationFinding(
                    code="FIN-MISSING-SOURCE-TOTAL",
                    severity=FindingSeverity.FATAL,
                    source=source,
                    section=section,
                    contract_type="PD-05",
                    message="Missing required source control total; missing control is NOT zero.",
                    disposition=Disposition.REJECTED,
                )
            )
            return (
                ReconciliationResult(
                    control_id=contract.control_id,
                    source=source,
                    section=section,
                    currency=currency,
                    source_control_total=None,
                    accepted_total=Decimal("0.0000"),
                    quarantined_total=Decimal("0.0000"),
                    approved_excluded_total=Decimal("0.0000"),
                    reconciled_component_total=Decimal("0.0000"),
                    residual=None,
                    is_balanced=False,
                    availability=ControlAvailability.UNAVAILABLE,
                    unavailable_reason="Missing source control total",
                ),
                findings,
            )

        # Parse exact decimals
        try:
            ctrl_total = parse_decimal_exact(source_control_total)
            acc_total = sum((parse_decimal_exact(a) for a in accepted_amounts), Decimal("0.0000"))
            q_total = sum((parse_decimal_exact(q) for q in quarantined_amounts), Decimal("0.0000"))
            exc_total = sum((parse_decimal_exact(e) for e in approved_excluded_amounts), Decimal("0.0000"))
        except (ValueError, TypeError) as exc:
            findings.append(
                ValidationFinding(
                    code="FIN-INVALID-DECIMAL",
                    severity=FindingSeverity.FATAL,
                    source=source,
                    section=section,
                    contract_type="PD-05",
                    message=f"Monetary arithmetic error: {exc}",
                    disposition=Disposition.REJECTED,
                )
            )
            return (
                ReconciliationResult(
                    control_id=contract.control_id,
                    source=source,
                    section=section,
                    currency=currency,
                    source_control_total=None,
                    accepted_total=Decimal("0.0000"),
                    quarantined_total=Decimal("0.0000"),
                    approved_excluded_total=Decimal("0.0000"),
                    reconciled_component_total=Decimal("0.0000"),
                    residual=None,
                    is_balanced=False,
                    availability=ControlAvailability.UNAVAILABLE,
                    unavailable_reason="Invalid decimal input",
                ),
                findings,
            )

        reconciled_total = (acc_total + q_total + exc_total).quantize(SCALE_4)
        residual = (ctrl_total - reconciled_total).quantize(SCALE_4)
        is_balanced = abs(residual) <= contract.tolerance

        if not is_balanced:
            findings.append(
                ValidationFinding(
                    code="FIN-RECONCILIATION-IMBALANCE",
                    severity=FindingSeverity.FATAL,
                    source=source,
                    section=section,
                    contract_type="PD-05",
                    evidence=(
                        f"source_total={ctrl_total}, accepted={acc_total}, quarantined={q_total}, "
                        f"excluded={exc_total}, residual={residual}, tolerance={contract.tolerance}"
                    ),
                    message=f"Financial reconciliation imbalance: residual {residual} != {contract.tolerance}",
                    disposition=Disposition.REJECTED,
                )
            )

        return (
            ReconciliationResult(
                control_id=contract.control_id,
                source=source,
                section=section,
                currency=currency,
                source_control_total=ctrl_total,
                accepted_total=acc_total,
                quarantined_total=q_total,
                approved_excluded_total=exc_total,
                reconciled_component_total=reconciled_total,
                residual=residual,
                is_balanced=is_balanced,
                availability=ControlAvailability.AVAILABLE,
            ),
            findings,
        )
