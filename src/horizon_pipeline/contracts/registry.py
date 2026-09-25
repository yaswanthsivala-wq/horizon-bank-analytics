"""Master Contract Registry for Horizon Community Bank.

Initializes production registries strictly reflecting approved documentary baselines:
- PD-01: 27 section headers registered as PENDING
- PD-02: 27 schema candidate IDs registered as PENDING
- PD-04: 51 candidate conditional predicates registered as PENDING (0 active)
- PD-05: 7 candidate financial controls registered as PENDING (0 active)
- PD-06: 23 candidate domain mapping groups registered as PENDING (0 active)
- PD-07: America/Chicago temporal engine; runtime tzdb 2026a unverified (PENDING)
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from ..intake import REQUIRED_SECTIONS
from .applicability import (
    ApplicabilityPredicateContract,
    ApplicabilityRegistry,
    ApplicabilityState,
    FieldDisposition,
)
from .financial import FinancialControlContract, FinancialControlEngine
from .headers import HeaderRegistry, PhysicalHeaderContract
from .mapping import MappingEntry, StatusMappingRegistry
from .schemas import SchemaContract, SchemaRegistry
from .risk import RiskRuleCatalogRegistry
from .states import ContractState
from .temporal import get_tzdb_runtime_proof

# Approved candidate schema ID template
CANDIDATE_SCHEMA_TEMPLATE = "HCB.SYN.{source}.{section}.v001"

# The 51 candidate logical conditional fields across 22 sections from PD-04 annex
PD04_CANDIDATE_PREDICATES: tuple[tuple[str, str, str, str, str], ...] = (
    ("SRC-01", "customers", "customer_identity.approval_reference", "C: approved identity mapping", "source/governance"),
    ("SRC-01", "accounts", "account.closed_date", "C: closed account", "source/target provenance"),
    ("SRC-01", "transactions", "transaction.absolute_comparison_amount", "C: eligible RC-01 comparison", "derived/selected"),
    ("SRC-01", "account_restriction_state", "account_restriction_state.publication_version", "C: published state", "derived/selected"),
    ("SRC-01", "account_restriction_state", "account_restriction_state.risk_restriction_status", "C: valid approved mapping", "PD-06"),
    ("SRC-01", "account_branch_assignment", "account_branch_assignment.original_effective_end", "C: ended interval", "PD-07"),
    ("SRC-01", "account_branch_assignment", "account_branch_assignment.supersedes_version", "C: correction", "source/governance"),
    ("SRC-01", "account_branch_assignment", "account_branch_assignment.correction_reason", "C: correction", "source/governance"),
    ("SRC-01", "account_branch_assignment", "account_branch_assignment.affected_from", "C: correction", "PD-07"),
    ("SRC-02", "positions", "loan_snapshot.reconstruction_reference", "C: reliably reconstructed snapshot", "PD-07"),
    ("SRC-02", "positions", "loan_snapshot.correction_reference", "C: corrected version", "source/governance"),
    ("SRC-02", "payments", "loan_payment.correction_reference", "C: corrected event version", "source/governance"),
    ("SRC-02", "payments", "loan_payment.posted_at", "C: POSTED", "PD-06/PD-07"),
    ("SRC-02", "loan_schedule", "loan_schedule.correction_reference", "C: corrected version", "source/governance"),
    ("SRC-02", "loan_obligation", "loan_obligation.correction_reference", "C: corrected version", "source/governance"),
    ("SRC-02", "payment_allocation", "payment_allocation.correction_reference", "C: corrected version", "source/governance"),
    ("SRC-02", "payment_unapplied", "payment_unapplied.correction_reference", "C: corrected version", "source/governance"),
    ("SRC-02", "payment_adjustment", "payment_adjustment.correction_reference", "C: corrected version", "source/governance"),
    ("SRC-02", "loan_account", "loan_account.correction_reference", "C: corrected version", "source/governance"),
    ("SRC-02", "loan_branch_assignment", "loan_branch_assignment.original_effective_end", "C: ended interval", "PD-07"),
    ("SRC-02", "loan_branch_assignment", "loan_branch_assignment.supersedes_version", "C: correction", "source/governance"),
    ("SRC-02", "loan_branch_assignment", "loan_branch_assignment.correction_reason", "C: correction", "source/governance"),
    ("SRC-02", "loan_branch_assignment", "loan_branch_assignment.affected_from", "C: correction", "PD-07"),
    ("SRC-03", "alerts", "fraud_alert.account_id", "C: account-level alert", "source/governance"),
    ("SRC-03", "alerts", "fraud_alert.transaction_id", "C: transaction-level alert", "source/governance"),
    ("SRC-03", "alerts", "fraud_alert.resolved_at", "C: resolved case", "PD-07"),
    ("SRC-03", "fraud_alert_state", "fraud_alert_state.original_effective_end", "C: ended interval", "PD-07"),
    ("SRC-03", "fraud_alert_state", "fraud_alert_state.supersedes_version", "C: correction", "source/governance"),
    ("SRC-03", "fraud_alert_state", "fraud_alert_state.correction_reason", "C: correction", "source/governance"),
    ("SRC-03", "fraud_alert_state", "fraud_alert_state.affected_from", "C: correction", "PD-07"),
    ("SRC-04", "complaints", "complaint.account_id", "C: account complaint", "source/governance"),
    ("SRC-04", "complaints", "complaint.loan_id", "C: loan complaint", "source/governance"),
    ("SRC-04", "complaints", "complaint.final_closed_at", "C: closed complaint", "PD-07"),
    ("SRC-04", "complaint_snapshot", "complaint_snapshot.reconstruction_reference", "C: reconstructed snapshot", "PD-07"),
    ("SRC-04", "complaint_snapshot", "complaint_snapshot.correction_reference", "C: corrected version", "source/governance"),
    ("SRC-04", "complaint_history_event", "complaint_history_event.preceding_event_id", "C: event chain", "source/governance"),
    ("SRC-04", "complaint_history_event", "complaint_history_event.superseded_at", "C: superseded event", "PD-07"),
    ("SRC-04", "complaint_branch_assignment", "complaint_branch_assignment.original_effective_end", "C: ended interval", "PD-07"),
    ("SRC-04", "complaint_branch_assignment", "complaint_branch_assignment.supersedes_version", "C: correction", "source/governance"),
    ("SRC-04", "complaint_branch_assignment", "complaint_branch_assignment.correction_reason", "C: correction", "source/governance"),
    ("SRC-04", "complaint_branch_assignment", "complaint_branch_assignment.affected_from", "C: correction", "PD-07"),
    ("SRC-05", "organizational_unit", "organizational_unit.parent_unit_id", "C: child unit", "source/governance"),
    ("SRC-05", "region", "region.valid_to", "C: ended interval", "PD-07"),
    ("SRC-05", "branches", "branch.valid_to", "C: closed/ended branch", "PD-07"),
    ("SRC-05", "branches", "branch.closure_date", "C: closed branch", "source/governance"),
    ("SRC-05", "branches", "branch.replacement_branch_id", "C: replaced branch", "source/governance"),
    ("SRC-05", "organizational_successor", "organizational_successor.successor_unit_id", "C: designated successor", "source/governance"),
    ("SRC-05", "organizational_successor", "organizational_successor.valid_to", "C: ended succession", "PD-07"),
    ("SRC-05", "organizational_successor", "organizational_successor.supersedes_version", "C: correction", "source/governance"),
    ("SRC-05", "organizational_successor", "organizational_successor.correction_reason", "C: correction", "source/governance"),
    ("SRC-05", "organizational_successor", "organizational_successor.affected_from", "C: correction", "PD-07"),
)

# The 7 candidate financial control populations from PD-05 annex
PD05_CANDIDATE_CONTROLS: tuple[tuple[str, str, str, str, str, str], ...] = (
    ("FC-C01", "SRC-01", "transactions", "amount", "currency", "USD"),
    ("FC-C02", "SRC-02", "positions", "outstanding_principal", "currency", "USD"),
    ("FC-C03", "SRC-02", "payments", "amount", "currency", "USD"),
    ("FC-C04", "SRC-02", "loan_obligation", "scheduled_amount", "currency", "USD"),
    ("FC-C05", "SRC-02", "payment_allocation", "amount", "currency", "USD"),
    ("FC-C06", "SRC-02", "payment_unapplied", "amount", "currency", "USD"),
    ("FC-C07", "SRC-02", "payment_adjustment", "amount", "currency", "USD"),
)

# The 23 candidate domain mapping groups from PD-06 annex
PD06_CANDIDATE_DOMAINS: tuple[tuple[str, str, str], ...] = (
    ("SRC-01", "customers", "customer_segment"),
    ("SRC-01", "accounts", "account_type"),
    ("SRC-01", "holders", "relationship_role"),
    ("SRC-01", "transactions", "transaction_type"),
    ("SRC-01", "transactions", "transaction_status"),
    ("SRC-01", "account_restriction_state", "restriction_status"),
    ("SRC-01", "account_branch_assignment", "branch_role"),
    ("SRC-02", "loans", "loan_type"),
    ("SRC-02", "borrowers", "borrower_role"),
    ("SRC-02", "positions", "loan_status"),
    ("SRC-02", "payments", "payment_status"),
    ("SRC-02", "payment_allocation", "allocation_component"),
    ("SRC-02", "payment_adjustment", "adjustment_kind"),
    ("SRC-02", "loan_account", "relationship_role"),
    ("SRC-02", "loan_branch_assignment", "branch_role"),
    ("SRC-03", "alerts", "fraud_case_status"),
    ("SRC-03", "alerts", "fraud_severity"),
    ("SRC-03", "alerts", "alert_reason"),
    ("SRC-04", "complaints", "complaint_status"),
    ("SRC-04", "complaints", "complaint_priority"),
    ("SRC-04", "complaints", "complaint_channel"),
    ("SRC-04", "complaint_branch_assignment", "branch_role"),
    ("SRC-05", "organizational_unit", "unit_type"),
)


class MasterProductionRegistry:
    """Central container for official Horizon Community Bank contract registries.

    Guarantees:
    - All unresolved production contracts remain in PENDING state
    - Zero active physical predicates
    - Zero active production mappings
    - Zero active production financial controls
    - Fails closed when executing unconfirmed banking rules
    """

    def __init__(self) -> None:
        self.headers = HeaderRegistry()
        self.schemas = SchemaRegistry()
        self.applicability = ApplicabilityRegistry()
        self.financial = FinancialControlEngine()
        self.mappings = StatusMappingRegistry()
        # No production catalog is registered until an approved, versioned
        # catalog and approval reference exist.
        self.risk_catalogs = RiskRuleCatalogRegistry()
        self._init_production_registries()

    def _init_production_registries(self) -> None:
        # Register all 27 sections in PD-01 and PD-02 as PENDING
        for source, sections in REQUIRED_SECTIONS.items():
            for section in sorted(sections):
                schema_id = CANDIDATE_SCHEMA_TEMPLATE.format(source=source, section=section)

                # PD-01: Header is PENDING confirmation
                self.headers.register(
                    PhysicalHeaderContract(
                        source=source,
                        section=section,
                        schema_version=schema_id,
                        columns=(),
                        state=ContractState.PENDING,
                        is_fixture=False,
                    )
                )

                # PD-02: Schema is PENDING confirmation
                self.schemas.register(
                    SchemaContract(
                        source=source,
                        section=section,
                        schema_version=schema_id,
                        fields=(),
                        state=ContractState.PENDING,
                        is_fixture=False,
                    )
                )

        # Register 51 candidate predicates as PENDING (PD-04)
        for idx, (source, section, target_field, cond_desc, dep) in enumerate(PD04_CANDIDATE_PREDICATES, start=1):
            schema_id = CANDIDATE_SCHEMA_TEMPLATE.format(source=source, section=section)
            pred_id = f"PRED-C{idx:02d}"
            field_alias = target_field.split(".")[-1]
            self.applicability.register(
                ApplicabilityPredicateContract(
                    predicate_id=pred_id,
                    source=source,
                    section=section,
                    schema_version=schema_id,
                    field_name=field_alias,
                    disposition=FieldDisposition.RECEIVED,
                    state=ContractState.PENDING,
                    description=f"{cond_desc} (blocked by {dep})",
                    is_fixture=False,
                )
            )

        # Register 7 candidate financial controls as PENDING (PD-05)
        for ctrl_id, source, section, amt_field, cur_field, currency in PD05_CANDIDATE_CONTROLS:
            schema_id = CANDIDATE_SCHEMA_TEMPLATE.format(source=source, section=section)
            self.financial.register(
                FinancialControlContract(
                    control_id=ctrl_id,
                    source=source,
                    section=section,
                    schema_version=schema_id,
                    amount_field=amt_field,
                    currency_field=cur_field,
                    currency=currency,
                    state=ContractState.PENDING,
                    tolerance=None,
                    tolerance_state=ContractState.PENDING,
                    is_fixture=False,
                    description=f"Candidate control {ctrl_id} pending confirmation",
                )
            )

        # Register 23 candidate domain mapping groups as PENDING (PD-06)
        for source, section, domain in PD06_CANDIDATE_DOMAINS:
            self.mappings.register_version(
                source_system=source,
                domain_code=domain,
                mapping_version="IDENTITY_SYN_V1",
                state=ContractState.PENDING,
            )
