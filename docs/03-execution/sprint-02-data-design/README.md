# Sprint 02 - Data Design

Current authorization recorded: 2026-09-15

Status: Sprint 2 logical Data Design **approved**. Gate G3 approved by requesting user 2026-09-17; post-G3 work requires separate authorization.

## Authorization and scope

The current user issued `/start sprint-2-data-design`; this authorization is recorded September 15, 2026. Sprint 1 approval and historical synchronization evidence are preserved. Existing untracked Sprint 2 drafts were present at inspection; their earlier start-date assertion is not independently verified. This authorizes data-design documentation. It does not approve the design or authorize ETL construction, data generation, database deployment, or other technical implementation.

The [Planning baseline](../../02-planning/Horizon_Community_Bank_Project_Planning_Baseline.md) and [Sprint 1 BA package](../sprint-01-business-analysis/README.md) remain the approved requirements. DD-01 through DD-12 record approved Sprint 2 design decisions (G3 approved 2026-09-17). Proposed physical aliases remain unconfirmed until authorized implementation; these decisions do not rewrite the approved requirements.

### Historical status (superseded)

The [Planning baseline](../../02-planning/Horizon_Community_Bank_Project_Planning_Baseline.md) and [Sprint 1 BA package](../sprint-01-business-analysis/README.md) remain the approved requirements. DD-01 through DD-10 record approved Sprint 2 design decisions. Remaining choices are proposals unless explicitly approved; these decisions do not rewrite the approved requirements.

## Artifact inventory

- [Relationship register](relationship-register.md): dictionary-derived declared FK references; no cardinality or physical-constraint assertion.
- [Data model and ERD](data-model.md): grains, identity, history, relationships, and analytical model.
- [Data dictionary and source mappings](data-dictionary-and-mappings.md): source-to-target navigation and links to authoritative contracts.
- [Data-quality and reconciliation design](data-quality-and-reconciliation.md): blocking controls, reruns, and planned evidence.
- [Synthetic-data specification](synthetic-data-specification.md): approved size assumptions and proposed scenarios; no generated data.
- [Design traceability and review](design-traceability-and-review.md): requirements coverage, unresolved choices, and G3 checklist.
- [Sprint start and control record](../../04-monitoring-and-control/sprint-02-control-record.md): authorization, risks, issues, and proposed decisions.

## Detailed package inventory

- [Source-system definitions](source-system-definitions.md): five daily source contracts and provenance.
- [Logical data model](logical-data-model.md): entity keys, constraints, relationships and analytical projection.
- [Field-level dictionary and mappings](field-level-dictionary.md): authoritative DD-07 fields, types, requiredness, lineage and derivations.
- [Customer-identity rules](customer-identity-reconciliation.md): deterministic crosswalk, conflicts and review.
- [KPI-to-data mappings](kpi-to-data-mappings.md): all ten KPIs, time/filter semantics and risk inputs.
- [Security and masking](security-and-masking-design.md): role scopes, last-four masking, exports and retention.

## Progress and next gate

Current status (2026-09-20): DD-01 through DD-12 and Gate G3 (logical design) are approved. No source schemas, DDL, generated data, ETL, Power BI model or test results exist; post-G3 work requires separate authorization.

### Historical status as of 2026-09-15 (superseded)

Design package expanded from the existing untracked drafts for review. DD-01 through DD-11 are approved at the decision level; exact source-contract content remains pending. No source schemas have been approved or implemented; no sample data, executable DDL, ETL, Power BI model, or test results were produced.

Gate G3 requires review of the ERD, dictionary, mappings, and unresolved decisions before ETL construction. Sprint 2 remains in progress; this draft package is not a completed or approved sprint.

## Decision approval update - 2026-09-15

DD-01 was approved by the user on 2026-09-15: entity-specific delivery modes and required batch manifests. DD-02 is also approved: all owners/co-borrowers, effective-dated roles and non-additive relationship exposure. DD-03 is approved for daily historical snapshots and controlled lineage/corrections. DD-08 through DD-12 remain Pending confirmation. Detailed DD-01 contract values remain pending where unspecified; G3 and technical implementation are not approved. See [decision register](design-traceability-and-review.md).

## DD-02 approval - 2026-09-15

DD-02 approved by the user on 2026-09-15: retain all owners and co-borrowers with effective-dated relationship roles. Monetary facts remain at their natural account, transaction, payment or loan grain. Customer-level shared balances are labeled "Relationship exposure" and are non-additive across customers; bank totals are computed from distinct natural-grain facts, never by summing customer exposures. Equal or weighted allocation requires a separately approved policy. DD-08 through DD-12 remain pending; package-level G3 approval is not granted.

## DD-03 approved historical snapshot policy - 2026-09-15

DD-03 approved by the user on 2026-09-15: daily historical loan-position snapshots at loan plus business-date grain and complaint-state snapshots at complaint plus business-date grain. Preserve values known for each as-of date, batch revision, source version, publication lineage and controlled correction history. Historical states that cannot be supplied or reliably reconstructed are unavailable. Do not carry current values backward, use future information or sum daily stock measures across dates.

## DD-04 approval - 2026-09-15

- [Approved customer-risk catalog and classification](customer-risk-catalog.md): five conditions, corrected RC-03 DPD > 30, threshold-aware Unknown handling and evidence/version design.

DD-01 through DD-04 are approved; DD-08 through DD-12 and remaining source-contract details are pending. RC-02 through RC-05 and incomplete-evidence handling are Sprint 2 approvals. G3 and implementation remain unapproved.

## DD-05 approval - 2026-09-15

DD-01 through DD-05 are approved. See [RC-01 comparison and attribution policy](customer-risk-catalog.md). DD-05 supersedes DD-04 for RC-01 initiation only; relationship exposure and other condition attribution are unchanged. DD-08 through DD-12 and source-contract details remain pending; no G3 approval or implementation.

## DD-06 approval - 2026-09-16

- [Approved DD-06 KPI and canonical policy](kpi-policy-dd06.md)

DD-01 through DD-06 are approved. Source aliases remain versioned contract details required before publication. DD-08 through DD-12 remain pending. G3 and implementation remain unapproved.

## DD-07 logical field-contract approval - 2026-09-16

User approval recorded after no business conflict was found. The [authoritative inventory](field-level-dictionary.md) consolidates the base and DD-03 through DD-06 fields, version parents and logical children. [DD-07 validation](dd07-validation.md) records documentation checks and protected-file hashes. DD-08 entitlements, DD-09 publication controls, DD-10 retention, DD-11 payments and DD-12 branch history remain pending. G3 and implementation remain unapproved.

## DD-08 approval - 2026-09-16

[Access, ownership and export policy](security-and-masking-design.md) approved by the user after compatibility review. The [inventory](field-level-dictionary.md) now records entitlement, governance and export evidence plus a sanitized RC-01 projection. See [DD-08 validation](dd08-validation.md). DD-09 through DD-12, actual source contracts, named appointments and actual grants/review evidence remain pending. Earlier dated updates retain their historical status. G3 and implementation remain unapproved.

## DD-09 approval - 2026-09-16

User-approved [quality, reconciliation and publication policy](data-quality-and-reconciliation.md) resolves the 17-rule severity catalog, mandatory-source controls, completeness/exclusions, exact reconciliation and independent atomic release. [Inventory](field-level-dictionary.md) now includes all-candidate control, review and notification evidence. [DD-09 validation](dd09-validation.md) records documentation checks and the three corrected DD-08 encoding errors. DD-10 retention, DD-11 payments and DD-12 branch history remain pending, as do actual source contracts, named appointments and evidence. G3 and implementation remain unapproved. Earlier dated entries retain historical status.

## DD-10 approval - 2026-09-16

[Retention and disposal policy](retention-and-disposal-design.md) records the user-approved schedules, full entity coverage and narrow DD-08 lifecycle refinement. [Inventory](field-level-dictionary.md) defines provenance, hold, disposal, backup/restore and denied-access contracts. [DD-10 validation](dd10-validation.md) records documentation checks. DD-11/DD-12 business semantics, source contracts, named appointments and physical operations remain pending. G3 and implementation remain unapproved; earlier dated entries retain historical status.

## DD-11 documentation update - 2026-09-16

DD-01 through DD-12 approved; synthetic documentary prerequisites closed; G3 pending. DD-11 adds logical schedules, obligations, allocations, unapplied amounts, adjustment events and effective loan-account links while preserving snapshot/KPI authority. Required source availability and reviewed mappings remain unverified prerequisites; G3 and implementation remain unapproved. Earlier dated entries retain historical status.

Artifacts: [DD-11 policy](loan-payment-and-schedule-policy.md), [authoritative inventory](field-level-dictionary.md), [DD-11 validation](dd11-validation.md).

## DD-12 documentation update - 2026-09-16

DD-01 through DD-12 approved; synthetic documentary prerequisites closed; G3 pending. Historical hierarchy/assignment and attribution policy separates historical report labels from current effective authorization. Required source contracts remain unverified; no implementation or G3 approval. Earlier dated records retain historical status.

Artifacts: [DD-12 policy](historical-branch-attribution-policy.md), [inventory](field-level-dictionary.md), [validation](dd12-validation.md).

## Synthetic G3 prerequisite closure - 2026-09-16

User-authorized fictional-project scope clarification replaces real-source verification with synthetic logical contracts, proposed aliases, deterministic temporal conventions and unexecuted scenario expectations. Documentary prerequisites are finalized; full consolidated Sprint 2 G3 approval remains pending. Physical confirmation, generation and all runtime/security/publication evidence remain post-G3 and require authorization. No real independent personnel or approvals are claimed.

Artifacts: [register](g3-prerequisite-register.md), [contract](synthetic-source-contract.md), [field trace](synthetic-contract-traceability.md), [closure validation](g3-closure-validation.md).

## G3 logical design approval - 2026-09-17

The requesting user approved the complete consolidated Sprint 2 logical package. See [gate decision](../../04-monitoring-and-control/g3-data-design-approval.md). This updates lifecycle status only: no real-source verification, production readiness, physical implementation, generated fixtures, executed reconciliation, implemented RLS/security, KPI achievement, UAT or publication readiness is claimed. All post-G3 work requires separate authorization; material design changes require change control. Dated prior statuses remain historical.
