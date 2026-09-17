# Data dictionary and source-mapping navigation

DD-07 logical field-contract standard approved by the user on 2026-09-16. The [authoritative inventory](field-level-dictionary.md) is the sole definition of fields, types, limits, nullability, logical keys, classification and derivations. This file is a source-system navigation map; its former duplicate field/type tables have been consolidated there. Unknown source aliases remain Pending confirmation; G3 and physical implementation remain Draft — not approved.

| Source / entity | Target and business transform |
| --- | --- |
| Branch Reference / branches | branch dimension; preserve source IDs, reject overlapping intervals |
| Core Banking / customers | customer + customer_identity + customer_version; restricted identity, effective segment history |
| Core Banking / accounts | account; preserve raw number restricted; derive masked final four digits for reporting |
| Core Banking / account holders | account_customer; valid-time bridge; no implicit duplication of financial totals |
| Core Banking / transactions | transaction; typed timestamps/decimal; preserve raw status and mapped canonical status |
| Loan Servicing / loans | loan at natural grain; customer relationships held separately |
| Loan Servicing / borrowers | loan_customer; all co-borrowers resolved through source crosswalk with effective roles; no allocation |
| Loan Servicing / loan positions | loan_snapshot; unique loan/date within selected publication; classify over 30 days past due using approved rule |
| Loan Servicing / payments | loan_payment; immutable positive actual events; DD-11 schedules, obligations, allocations, unapplied amounts and adjustments |
| Fraud Monitoring / alerts | fraud_alert; crosswalk customer; validate supplied transaction reference |
| CRM / complaints | complaint + DD-03 approved daily historical state snapshot; normalize priority; retain source closure evidence |
| Derived / risk assessments | risk_assessment + risk_evidence; evaluate known conditions only; missing evidence is unknown |
| Derived / audits | pipeline_run, source_extract, quality_exception, reconciliation_result |
| Simulated / exports | export_event; redact sensitive filter values and record allow/deny decision |

Source aliases are design contracts, not discovered schemas. Do not normalize away source identifier leading zeros. Source namespaces qualify natural keys; snapshots select one immutable entity/date version per publication. Source manifests, financial controls, population members and source references are logical entities in the inventory. Multiple mapping versions are child references, never one ambiguous scalar.

## Approved policy references

- [Source definitions and DD-01 manifests](source-system-definitions.md).
- [Logical model](logical-data-model.md): DD-02 effective non-additive ownership exposure and DD-03 historical state.
- [Risk catalog](customer-risk-catalog.md): DD-04 conditions and DD-05 transaction initiation/90-day comparison; account ownership never implies transaction initiation.
- [DD-06 KPI policy](kpi-policy-dd06.md): canonical transaction and loan groups, significant HIGH/CRITICAL severity, restricted RESTRICTED/FROZEN/BLOCKED states, complaint creation-priority and no-pause elapsed SLA.
- [KPI mappings](kpi-to-data-mappings.md): all approved formulas retained, including K06 sum of principal for DPD > 30 without active-only or positive-only filtering; negative/missing principal handled separately.
- [Security](security-and-masking-design.md) and [quality](data-quality-and-reconciliation.md): field classification, masking, raw preservation and approved DD-08/DD-09 controls.

No executable transformations, source objects or generated data are created. DD-01 through DD-12 logical decisions are approved. Synthetic contracts and proposed aliases are finalized documentarily; fixture-based physical confirmation remains post-G3.

## DD-08 coordination - 2026-09-16

DD-08 extends the authoritative inventory with scoped effective entitlements, independent governance reviews, sanitized RC-01 investigation projection and structured export evidence. No second field inventory is introduced. See [approved policy](security-and-masking-design.md) and [authoritative inventory](field-level-dictionary.md).

## DD-09 approved coordination - 2026-09-16

DD-09 extends the authoritative inventory with checksum metadata, candidate/ruleset/source expectations, control/population/coverage evidence, bounded exclusions, decision participants and notification acknowledgments. Severity uses CRITICAL/ERROR/WARNING/INFO. Received and curated completeness remain separate; no fabricated measurement for failed early attempts. This document remains navigation only. See [approved quality policy](data-quality-and-reconciliation.md) and [authoritative inventory](field-level-dictionary.md).

## DD-10 approved lifecycle coordination - 2026-09-16

The sole field inventory now includes DD-10 provenance-envelope, lifecycle references, schedules, holds, disposal, backup/restore and denied-access contracts. The retention design contains complete entity/category schedule coverage. No duplicate field inventory is created. See [retention and disposal policy](retention-and-disposal-design.md) and [authoritative inventory](field-level-dictionary.md).

## DD-11 mapping contract

See [approved DD-11 policy](loan-payment-and-schedule-policy.md). Source aliases and accepted raw-domain mappings require Loan Operations Manager and independent Data Owner review evidence. Map contractual due dates to obligations only, loan currency to all monetary children, raw payment status to PENDING/POSTED/FAILED/CANCELLED, and source allocation components to PRINCIPAL/INTEREST/FEE. Preserve raw signed invalid payment evidence and source adjustment sign interpretation. Do not manufacture allocations, links or schedule coverage. The authoritative inventory contains every logical field; this navigation document is not another inventory.

## DD-12 approved coordination - 2026-09-16

[DD-12 approved policy](historical-branch-attribution-policy.md). Earlier dated dependency notes retain historical status; DD-12 logical policy is now approved, actual source coverage remains unverified.

The sole inventory adds region, stable organization identity, successor history, account/loan/complaint assignment versions, attribution, organization publication membership, successor scope mappings and scope-resolution evidence. account.branch_key and loan.branch_key are current convenience projections only. Raw source IDs resolve through approved source-qualified identities; supplied role/time must validate against history. Current region expansion and historical report region are separate mappings. No inferred assignment. See the policy attribution matrix for every timestamp and source prerequisite.
