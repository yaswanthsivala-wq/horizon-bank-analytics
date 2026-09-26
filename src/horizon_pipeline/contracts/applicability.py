"""PD-04 Conditional Applicability Engine.

Enforces:
- Dispositions: received, generated, resolved, derived
- Applicability states: always, optional, conditional, inapplicable
- Cell result states: absent, blank, null, invalid, inapplicable, unresolved
- Core invariants:
    blank != inapplicable
    invalid != inapplicable
    Missing/invalid evidence never silently becomes inapplicable
- Deterministic predicate evaluation
- Fail closed when a conditional predicate is unresolved (0 active production predicates)
- DD-09 completeness denominator accounting
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Mapping, Sequence

from .findings import Disposition, FindingSeverity, ValidationFinding
from .states import ContractState, PendingContractError, UnsupportedContractError


class FieldDisposition(str, Enum):
    """Field disposition / origin."""

    RECEIVED = "received"      # Physical CSV cell
    GENERATED = "generated"    # Surrogate key or technical audit field
    RESOLVED = "resolved"      # Target foreign key joined/resolved
    DERIVED = "derived"        # Business formula or calculation


class ApplicabilityState(str, Enum):
    """Applicability categorization of a field."""

    ALWAYS = "always"
    OPTIONAL = "optional"
    CONDITIONAL = "conditional"
    INAPPLICABLE = "inapplicable"


class CellState(str, Enum):
    """Evaluation state of a single data cell."""

    ABSENT = "absent"              # Column missing or row width short
    BLANK = "blank"                # Whitespace-only or literal empty string where required
    NULL = "null"                  # Recognized null representation (empty CSV cell per G3)
    INVALID = "invalid"            # Nonblank value failing type/format/domain
    INAPPLICABLE = "inapplicable"  # Validly excluded by active approved predicate
    UNRESOLVED = "applicability unresolved"  # Predicate missing, pending, or evidence invalid
    VALID = "valid"                # Valid nonblank supplied value


@dataclass(frozen=True)
class CompletenessMetrics:
    """DD-09 completeness denominator and numerator accounting."""

    applicable_required_denominator: int
    present_required_numerator: int
    inapplicable_cells: int
    optional_cells: int
    invalid_cells: int
    unresolved_cells: int

    @property
    def is_computable(self) -> bool:
        """Completeness ratio is computable only if zero cells have unresolved applicability."""
        return self.unresolved_cells == 0

    @property
    def ratio(self) -> float | None:
        """Compute unrounded completeness ratio, or None if unavailable/uncomputable."""
        if not self.is_computable or self.applicable_required_denominator == 0:
            return None
        return self.present_required_numerator / self.applicable_required_denominator


@dataclass(frozen=True)
class ApplicabilityPredicateContract:
    """An approved deterministic condition for a conditional field."""

    predicate_id: str
    source: str
    section: str
    schema_version: str
    field_name: str
    disposition: FieldDisposition
    state: ContractState
    evaluator: Callable[[Mapping[str, str]], bool] | None = None
    description: str = ""
    is_fixture: bool = False


class ApplicabilityRegistry:
    """Registry managing conditional applicability predicates."""

    def __init__(self) -> None:
        self._predicates: dict[tuple[str, str, str, str], ApplicabilityPredicateContract] = {}

    def register(self, predicate: ApplicabilityPredicateContract) -> None:
        """Register a predicate contract."""
        key = (predicate.source, predicate.section, predicate.schema_version, predicate.field_name)
        if key in self._predicates:
            raise ValueError(f"Predicate already registered for {key}")
        self._predicates[key] = predicate

    def get(
        self,
        source: str,
        section: str,
        schema_version: str,
        field_name: str,
    ) -> ApplicabilityPredicateContract | None:
        """Retrieve predicate contract by (source, section, schema_version, field_name)."""
        return self._predicates.get((source, section, schema_version, field_name))

    def evaluate_cell_state(
        self,
        source: str,
        section: str,
        schema_version: str,
        field_name: str,
        raw_value: str | None,
        row_record: Mapping[str, str],
        applicability: ApplicabilityState,
        is_required: bool,
        is_valid_type: bool,
    ) -> tuple[CellState, list[ValidationFinding]]:
        """Evaluate exact cell state following PD-04 and DD-09 rules.

        Fails closed on unresolved conditional predicate.
        Preserves blank != inapplicable and invalid != inapplicable.
        """
        findings: list[ValidationFinding] = []

        if raw_value is None:
            findings.append(
                ValidationFinding(
                    code="APP-CELL-ABSENT",
                    severity=FindingSeverity.ERROR,
                    source=source,
                    section=section,
                    field_name=field_name,
                    contract_type="PD-04",
                    message=f"Field '{field_name}' is absent from row",
                    disposition=Disposition.QUARANTINED,
                )
            )
            return CellState.ABSENT, findings

        # Check conditional applicability
        if applicability == ApplicabilityState.CONDITIONAL:
            predicate = self.get(source, section, schema_version, field_name)
            if predicate is None:
                findings.append(
                    ValidationFinding(
                        code="APP-PREDICATE-UNSUPPORTED",
                        severity=FindingSeverity.ERROR,
                        source=source,
                        section=section,
                        field_name=field_name,
                        contract_type="PD-04",
                        message=f"Conditional field '{field_name}' has no registered predicate contract",
                        disposition=Disposition.QUARANTINED,
                    )
                )
                return CellState.UNRESOLVED, findings

            if predicate.state == ContractState.PENDING:
                findings.append(
                    ValidationFinding(
                        code="APP-PREDICATE-PENDING",
                        severity=FindingSeverity.ERROR,
                        source=source,
                        section=section,
                        field_name=field_name,
                        contract_type="PD-04",
                        evidence=f"predicate_id={predicate.predicate_id}",
                        message=(
                            f"Conditional predicate for '{field_name}' is PENDING confirmation; "
                            "cannot evaluate condition; fails closed."
                        ),
                        disposition=Disposition.QUARANTINED,
                    )
                )
                return CellState.UNRESOLVED, findings

            if predicate.state == ContractState.UNSUPPORTED or predicate.evaluator is None:
                findings.append(
                    ValidationFinding(
                        code="APP-PREDICATE-UNSUPPORTED",
                        severity=FindingSeverity.ERROR,
                        source=source,
                        section=section,
                        field_name=field_name,
                        contract_type="PD-04",
                        message=f"Conditional predicate '{predicate.predicate_id}' is UNSUPPORTED",
                        disposition=Disposition.QUARANTINED,
                    )
                )
                return CellState.UNRESOLVED, findings

            try:
                is_applicable = predicate.evaluator(row_record)
            except Exception as exc:
                findings.append(
                    ValidationFinding(
                        code="APP-PREDICATE-EVAL-ERROR",
                        severity=FindingSeverity.ERROR,
                        source=source,
                        section=section,
                        field_name=field_name,
                        contract_type="PD-04",
                        evidence=str(exc),
                        message=f"Error evaluating predicate for '{field_name}': {exc}",
                        disposition=Disposition.QUARANTINED,
                    )
                )
                return CellState.UNRESOLVED, findings

            if not is_applicable:
                # Validly inapplicable under approved active predicate
                if raw_value.strip():
                    findings.append(
                        ValidationFinding(
                            code="APP-INAPPLICABLE-HAS-VALUE",
                            severity=FindingSeverity.ERROR,
                            source=source,
                            section=section,
                            field_name=field_name,
                            contract_type="PD-04",
                            evidence=f"raw_value='{raw_value}'",
                            message=f"Field '{field_name}' is inapplicable under predicate but received non-empty value",
                            disposition=Disposition.QUARANTINED,
                        )
                    )
                return CellState.INAPPLICABLE, findings

        elif applicability == ApplicabilityState.INAPPLICABLE:
            return CellState.INAPPLICABLE, findings

        # If here, field is applicable (ALWAYS, OPTIONAL, or CONDITIONAL=True)
        is_empty_cell = (raw_value == "")
        is_whitespace_only = (raw_value != "" and not raw_value.strip())

        if is_empty_cell:
            # Recognized empty cell represents null per G3
            if is_required:
                findings.append(
                    ValidationFinding(
                        code="APP-MISSING-REQUIRED",
                        severity=FindingSeverity.ERROR,
                        source=source,
                        section=section,
                        field_name=field_name,
                        contract_type="PD-04",
                        message=f"Required field '{field_name}' is null/empty",
                        disposition=Disposition.QUARANTINED,
                    )
                )
            return CellState.NULL, findings

        if is_whitespace_only:
            # Literal whitespace is invalid blank, never inapplicable
            findings.append(
                ValidationFinding(
                    code="APP-BLANK-CELL",
                    severity=FindingSeverity.ERROR,
                    source=source,
                    section=section,
                    field_name=field_name,
                    contract_type="PD-04",
                    evidence=f"raw_value='{raw_value}'",
                    message=f"Field '{field_name}' contains whitespace-only text; blank != inapplicable",
                    disposition=Disposition.QUARANTINED,
                )
            )
            return CellState.BLANK, findings

        # Supplied non-blank value
        if not is_valid_type:
            findings.append(
                ValidationFinding(
                    code="APP-INVALID-CELL",
                    severity=FindingSeverity.ERROR,
                    source=source,
                    section=section,
                    field_name=field_name,
                    contract_type="PD-04",
                    evidence=f"raw_value='{raw_value}'",
                    message=f"Field '{field_name}' value '{raw_value}' fails type/domain validation",
                    disposition=Disposition.QUARANTINED,
                )
            )
            return CellState.INVALID, findings

        return CellState.VALID, findings
