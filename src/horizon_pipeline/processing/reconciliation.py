"""Row and Financial Reconciliation Accounting Engine.

Implements DD-09 exact reconciliation rules:
- RC-D01: Row reconciliation (Received = accepted + quarantined + approved_excluded)
- RC-D02: Financial reconciliation using the PD-05 arithmetic engine
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Mapping, Sequence

from ..contracts.financial import FinancialControlEngine, ReconciliationResult
from ..contracts.findings import FindingSeverity
from .quality import RecordFinding
from .records import RecordDisposition

SCALE_4 = Decimal("0.0001")


@dataclass(frozen=True)
class RowReconciliationResult:
    """Row count reconciliation accounting per section under RC-D01."""

    source: str
    section: str
    manifest_count: int
    raw_captured_count: int
    received_count: int
    accepted_count: int
    quarantined_count: int
    excluded_count: int
    balanced: bool
    residual: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "source": self.source,
            "section": self.section,
            "manifest_count": self.manifest_count,
            "raw_captured_count": self.raw_captured_count,
            "received_count": self.received_count,
            "accepted_count": self.accepted_count,
            "quarantined_count": self.quarantined_count,
            "excluded_count": self.excluded_count,
            "balanced": self.balanced,
            "residual": self.residual,
        }


@dataclass(frozen=True)
class FinancialReconciliationResult:
    """Financial reconciliation result per monetary control under RC-D02."""

    control_id: str
    source: str
    section: str
    currency: str
    source_control_total: Decimal
    accepted_total: Decimal
    quarantined_total: Decimal
    excluded_total: Decimal
    residual: Decimal
    tolerance: Decimal | None
    balanced: bool
    status: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "control_id": self.control_id,
            "source": self.source,
            "section": self.section,
            "currency": self.currency,
            "source_control_total": str(self.source_control_total),
            "accepted_total": str(self.accepted_total),
            "quarantined_total": str(self.quarantined_total),
            "excluded_total": str(self.excluded_total),
            "residual": str(self.residual),
            "tolerance": str(self.tolerance) if self.tolerance is not None else None,
            "balanced": self.balanced,
            "status": self.status,
        }


@dataclass(frozen=True)
class ReconciliationSummary:
    """Consolidated reconciliation accounting across all sections and controls."""

    row_results: tuple[RowReconciliationResult, ...]
    financial_results: tuple[FinancialReconciliationResult, ...]
    all_balanced: bool
    findings: tuple[RecordFinding, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "all_balanced": self.all_balanced,
            "row_reconciliations": [r.to_dict() for r in self.row_results],
            "financial_reconciliations": [f.to_dict() for f in self.financial_results],
            "findings_count": len(self.findings),
        }


class OfflineReconciliationEngine:
    """Evaluates row and financial reconciliation for a processed package."""

    def __init__(self, financial_engine: FinancialControlEngine | None = None) -> None:
        self.financial_engine = financial_engine or FinancialControlEngine()

    def reconcile_package(
        self,
        section_manifest_counts: Mapping[tuple[str, str], int],
        raw_captured_counts: Mapping[tuple[str, str], int],
        accepted_counts: Mapping[tuple[str, str], int],
        quarantined_counts: Mapping[tuple[str, str], int],
        excluded_counts: Mapping[tuple[str, str], int] | None = None,
        financial_controls: Sequence[Any] = (),
        monetary_data: Mapping[tuple[str, str], dict[str, list[Decimal]]] | None = None,
    ) -> ReconciliationSummary:
        """Perform row and financial reconciliation across all processed sections."""
        excluded = excluded_counts or {}
        mon_data = monetary_data or {}
        row_results: list[RowReconciliationResult] = []
        fin_results: list[FinancialReconciliationResult] = []
        findings: list[RecordFinding] = []

        all_sections = set(section_manifest_counts.keys()) | set(raw_captured_counts.keys())

        # 1. Row reconciliation (RC-D01)
        for (source, section) in sorted(all_sections):
            man_count = section_manifest_counts.get((source, section), 0)
            raw_count = raw_captured_counts.get((source, section), 0)
            acc_count = accepted_counts.get((source, section), 0)
            quar_count = quarantined_counts.get((source, section), 0)
            excl_count = excluded.get((source, section), 0)

            # Received = accepted + quarantined + excluded
            reconciled_sum = acc_count + quar_count + excl_count
            raw_matches_manifest = (raw_count == man_count)
            sum_matches_raw = (reconciled_sum == raw_count)
            balanced = raw_matches_manifest and sum_matches_raw
            residual = raw_count - reconciled_sum

            if not balanced:
                findings.append(
                    RecordFinding(
                        rule_id="RC-D01",
                        source=source,
                        section=section,
                        record_identity=f"{source}.{section}",
                        field_name="row_count",
                        severity=FindingSeverity.CRITICAL,
                        original_severity=FindingSeverity.CRITICAL,
                        escalation_reason="Row count reconciliation mismatch",
                        disposition=RecordDisposition.QUARANTINED,
                        observed_value=f"manifest={man_count}, raw={raw_count}, sum={reconciled_sum}",
                        expected_rule="manifest == raw == (accepted + quarantined + excluded)",
                        message=f"Row reconciliation failed for {source}.{section}: residual {residual}",
                    )
                )

            row_results.append(
                RowReconciliationResult(
                    source=source,
                    section=section,
                    manifest_count=man_count,
                    raw_captured_count=raw_count,
                    received_count=raw_count,
                    accepted_count=acc_count,
                    quarantined_count=quar_count,
                    excluded_count=excl_count,
                    balanced=balanced,
                    residual=residual,
                )
            )

        # 2. Financial reconciliation (RC-D02)
        for ctrl in financial_controls:
            key = (ctrl.source, ctrl.section)
            sec_mon = mon_data.get(key, {})
            accepted_amounts = sec_mon.get("accepted", [])
            quarantined_amounts = sec_mon.get("quarantined", [])
            excluded_amounts = sec_mon.get("excluded", [])

            acc_tot = sum(accepted_amounts, Decimal("0.0000")).quantize(SCALE_4)
            quar_tot = sum(quarantined_amounts, Decimal("0.0000")).quantize(SCALE_4)
            excl_tot = sum(excluded_amounts, Decimal("0.0000")).quantize(SCALE_4)

            # Source control total
            src_tot = sec_mon.get("source_total", [acc_tot + quar_tot + excl_tot])[0].quantize(SCALE_4)

            residual = src_tot - (acc_tot + quar_tot + excl_tot)

            # Check tolerance
            if ctrl.tolerance is not None:
                balanced = abs(residual) <= ctrl.tolerance
                status = "PASS" if balanced else "FAIL"
            else:
                balanced = False
                status = "PENDING_TOLERANCE"

            if not balanced and ctrl.is_fixture:
                findings.append(
                    RecordFinding(
                        rule_id="RC-D02",
                        source=ctrl.source,
                        section=ctrl.section,
                        record_identity=ctrl.control_id,
                        field_name="financial_total",
                        severity=FindingSeverity.CRITICAL,
                        original_severity=FindingSeverity.CRITICAL,
                        escalation_reason="Financial control residual exceeded tolerance",
                        disposition=RecordDisposition.QUARANTINED,
                        observed_value=f"source={src_tot}, sum={acc_tot + quar_tot + excl_tot}, residual={residual}",
                        expected_rule=f"abs(residual) <= {ctrl.tolerance}",
                        message=f"Financial reconciliation failed for control {ctrl.control_id}: residual {residual}",
                    )
                )

            fin_results.append(
                FinancialReconciliationResult(
                    control_id=ctrl.control_id,
                    source=ctrl.source,
                    section=ctrl.section,
                    currency=ctrl.currency,
                    source_control_total=src_tot,
                    accepted_total=acc_tot,
                    quarantined_total=quar_tot,
                    excluded_total=excl_tot,
                    residual=residual,
                    tolerance=ctrl.tolerance,
                    balanced=balanced,
                    status=status,
                )
            )

        all_balanced = all(r.balanced for r in row_results) and all(f.balanced for f in fin_results if f.tolerance is not None)

        return ReconciliationSummary(
            row_results=tuple(row_results),
            financial_results=tuple(fin_results),
            all_balanced=all_balanced,
            findings=tuple(findings),
        )
