"""Customer-level classification from the five approved risk conditions.

The classifier preserves condition evidence and versions. It does not compute a
numeric score or activate pending production contracts.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Mapping, Sequence

from .risk_conditions import ConditionState, RiskConditionResult


class RiskClassification(str, Enum):
    PROVISIONAL_HIGH_RISK = "Provisional high risk"
    INCOMPLETE_EVIDENCE = "Incomplete evidence - classification unavailable"
    NOT_HIGH_RISK = "Not high risk under current rule"
    UNAVAILABLE = "Classification unavailable"


class EvidenceState(str, Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass(frozen=True)
class RiskAssessment:
    assessment_id: str
    customer_id: str
    business_date: date
    assessment_at: datetime
    classification: RiskClassification
    evidence_state: EvidenceState
    triggered_count: int | None
    unknown_count: int | None
    classification_rule_version: str | None
    catalog_version: str | None
    condition_results: tuple[RiskConditionResult, ...]
    lineage_references: tuple[str, ...]
    publication_version: str | None = None
    unavailable_reason: str | None = None
    is_fixture: bool = False


class RiskClassificationEngine:
    """Apply the ordered DD-04 classification policy to five condition results."""

    CONDITION_IDS = ("RC-01", "RC-02", "RC-03", "RC-04", "RC-05")

    @staticmethod
    def _deduplicate(values: Sequence[str]) -> tuple[str, ...]:
        return tuple(dict.fromkeys(values))

    @classmethod
    def _unavailable(
        cls, *, assessment_id: str, customer_id: str, business_date: date,
        assessment_at: datetime, reason: str, catalog_version: str | None,
        classification_rule_version: str | None, lineage_references: Sequence[str],
        publication_version: str | None, fixture_mode: bool,
    ) -> RiskAssessment:
        return RiskAssessment(
            assessment_id=assessment_id, customer_id=customer_id,
            business_date=business_date, assessment_at=assessment_at,
            classification=RiskClassification.UNAVAILABLE,
            evidence_state=EvidenceState.UNAVAILABLE,
            triggered_count=None, unknown_count=None,
            classification_rule_version=classification_rule_version,
            catalog_version=catalog_version, condition_results=(),
            lineage_references=cls._deduplicate(lineage_references),
            publication_version=publication_version,
            unavailable_reason=reason, is_fixture=fixture_mode,
        )

    @classmethod
    def classify(
        cls, *, assessment_id: str, customer_id: str, business_date: date,
        assessment_at: datetime, condition_results: Sequence[RiskConditionResult],
        catalog_version: str | None, classification_rule_version: str | None,
        expected_condition_versions: Mapping[str, str] | None,
        lineage_references: Sequence[str] = (), publication_version: str | None = None,
        fixture_mode: bool = False, catalog_is_fixture: bool = False,
    ) -> RiskAssessment:
        """Classify once, preserving exact catalog, condition, and lineage evidence."""
        common = dict(
            assessment_id=assessment_id, customer_id=customer_id,
            business_date=business_date, assessment_at=assessment_at,
            catalog_version=catalog_version,
            classification_rule_version=classification_rule_version,
            lineage_references=lineage_references,
            publication_version=publication_version, fixture_mode=fixture_mode,
        )
        if not catalog_version:
            return cls._unavailable(reason="MISSING_CATALOG_VERSION", **common)
        if not classification_rule_version:
            return cls._unavailable(reason="MISSING_CLASSIFICATION_RULE_VERSION", **common)
        if expected_condition_versions is None:
            return cls._unavailable(reason="MISSING_CATALOG_RULE_MEMBERS", **common)
        if catalog_is_fixture and not fixture_mode:
            return cls._unavailable(reason="FIXTURE_CATALOG_PROHIBITED_IN_PRODUCTION", **common)

        expected_ids = set(cls.CONDITION_IDS)
        if set(expected_condition_versions) != expected_ids:
            return cls._unavailable(reason="INVALID_CATALOG_CONDITION_MEMBERSHIP", **common)
        actual_ids = [result.condition_id for result in condition_results]
        if len(actual_ids) != 5 or set(actual_ids) != expected_ids:
            reason = "DUPLICATE_CONDITION_RESULT" if len(actual_ids) != len(set(actual_ids)) else "INVALID_CONDITION_RESULT_MEMBERSHIP"
            return cls._unavailable(reason=reason, **common)
        for result in condition_results:
            if not result.rule_version:
                return cls._unavailable(reason=f"MISSING_RULE_VERSION:{result.condition_id}", **common)
            if result.rule_version != expected_condition_versions[result.condition_id]:
                return cls._unavailable(reason=f"RULE_VERSION_MISMATCH:{result.condition_id}", **common)

        ordered = tuple(sorted(condition_results, key=lambda item: cls.CONDITION_IDS.index(item.condition_id)))
        triggered = sum(item.state == ConditionState.TRIGGERED for item in ordered)
        unknown = sum(item.state == ConditionState.UNKNOWN for item in ordered)
        if triggered >= 2:
            classification = RiskClassification.PROVISIONAL_HIGH_RISK
        elif triggered + unknown >= 2:
            classification = RiskClassification.INCOMPLETE_EVIDENCE
        else:
            classification = RiskClassification.NOT_HIGH_RISK
        evidence_state = EvidenceState.INCOMPLETE if unknown else EvidenceState.COMPLETE
        combined_lineage = list(lineage_references)
        for result in ordered:
            combined_lineage.extend(result.lineage_references)
        return RiskAssessment(
            assessment_id=assessment_id, customer_id=customer_id,
            business_date=business_date, assessment_at=assessment_at,
            classification=classification, evidence_state=evidence_state,
            triggered_count=triggered, unknown_count=unknown,
            classification_rule_version=classification_rule_version,
            catalog_version=catalog_version, condition_results=ordered,
            lineage_references=cls._deduplicate(combined_lineage),
            publication_version=publication_version, unavailable_reason=None,
            is_fixture=fixture_mode,
        )
