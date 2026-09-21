# Monitoring and Control

Current Sprint 2 decision status (2026-09-17): DD-01 through DD-12 and G3 logical Data Design approved. Physical design, generation and implementation require separate authorization.

Purpose: track project progress and controls throughout every phase.

Current artifacts:

- [Sprint 1 BA approval and synchronization record](sprint-01-approval-record.md): received user approval, dated evidence, scope, and next authorization.

- [Sprint 2 control record](sprint-02-control-record.md): dated authorization, progress, open risks/issues, proposed decisions, change control and documentation validation.

## Register map — 2026-09-20

| Register | Where it currently lives |
| --- | --- |
| change-control/ | [CR-001](change-control/CR-001-kpi-and-risk-refinements.md); [CR-002](change-control/CR-002-baseline-lifecycle-corrections.md) |
| Risks and issues | [Sprint 2 control record](sprint-02-control-record.md) and [Planning §15](../02-planning/Horizon_Community_Bank_Project_Planning_Baseline.md#15-risk-register) |
| Decisions | [Sprint 2 control record](sprint-02-control-record.md) and [design traceability decision register](../03-execution/sprint-02-data-design/design-traceability-and-review.md) |
| Approvals | [Sprint 1 approval](sprint-01-approval-record.md); [G3 decision](g3-data-design-approval.md) |
| quality-reviews/ and status-reports/ | No separate records; validation evidence is in the DD-07…DD-12 validation files and [g3-closure-validation.md](../03-execution/sprint-02-data-design/g3-closure-validation.md) |

The other reserved register directories retain their placeholders. This map changes no approval status.

Reserved artifact locations:

- `status-reports/`: dated progress reports and confirmed measures.
- `risks-and-issues/`: risk and issue registers, owners, and responses.
- `change-control/`: change requests, impact assessments, and approvals.
- `decision-log/`: dated decisions, rationale, and approval evidence.
- `quality-reviews/`: review findings, corrective actions, and follow-up evidence.

Progress: Sprint 1 BA approval and September 14, 2026 synchronization evidence recorded. Sprint 2 draft design package is prepared under current authorization; G3 review is pending. Technical implementation has not started.
Open questions: Sprint 2 DD-11 and DD-12 and remaining DD-01 contract details, named review owners and actual review evidence are Pending confirmation.
Approval status: Sprint 1 BA approval recorded; Sprint 2 logical design and Gate G3 approved 2026-09-17 (logical design only); no other gate is approved; no separate Monitoring and Control baseline approval is asserted.

### Historical status (superseded)

Approval status: Sprint 1 BA user approval recorded; Sprint 2 design is Draft — not approved; no separate Monitoring and Control baseline approval is asserted.

Maintain this inventory and status as work proceeds; follow the root AGENTS.md.

## DD-01 approval update - 2026-09-15

DD-01 was approved by the user on 2026-09-15: entity-specific delivery modes and required batch manifests. DD-02 is also approved: all owners/co-borrowers, effective-dated roles and non-additive relationship exposure. DD-03 is approved for daily historical snapshots and controlled lineage/corrections. DD-07 through DD-12 remain Pending confirmation. Detailed DD-01 contract values remain pending where unspecified; G3 and technical implementation are not approved.

## DD-04 approval - 2026-09-15

DD-04 catalog and incomplete-evidence classification approved by user with RC-03 DPD > 30. RC-02 through RC-05 and Unknown handling are Sprint 2 decisions; original baselines preserved. DD-07 through DD-12 remain pending; no G3 approval or implementation.

## DD-05 approval - 2026-09-15

DD-05 comparison/initiator hierarchy approved; it supersedes DD-04 RC-01 all-owner attribution only. DD-01 through DD-05 approved; six decisions and remaining source/assessment-population details pending. G3 and implementation remain unapproved.

## DD-06 approval - 2026-09-16

DD-06 approved with original K06 formula intact, separate negative/missing-principal quality controls, explicit risk subsets, KPI/time/SLA rules and daily RC-01 population/revisions. DD-01 through DD-06 approved; DD-07 through DD-12 pending. Versioned source aliases required before publication. No G3 approval or implementation.

## DD-07 update - 2026-09-16

DD-01 through DD-07 are approved at decision level. The [authoritative inventory](../03-execution/sprint-02-data-design/field-level-dictionary.md) consolidates logical field contracts and version/evidence children; [validation evidence](../03-execution/sprint-02-data-design/dd07-validation.md) records document checks. DD-08 through DD-12 and actual source contracts remain pending. G3 and implementation remain unapproved; earlier updates retain historical context.

## DD-08 approval update - 2026-09-16

User-approved [DD-08 policy](../03-execution/sprint-02-data-design/security-and-masking-design.md) and logical entitlement/export inventory synchronized after no baseline conflict was found. [Validation evidence](../03-execution/sprint-02-data-design/dd08-validation.md) records documentation checks. Next: DD-09 quality exclusions/publication authority and DD-10 retention mechanics, then remaining DD-11/DD-12 and source-contract details. Named appointments, case assignments and actual approvals/grants remain Pending confirmation. Earlier entries are historical. G3 remains pending; no implementation authorized.

## DD-09 approval update - 2026-09-16

[DD-09 policy](../03-execution/sprint-02-data-design/data-quality-and-reconciliation.md) approved by user after no baseline conflict was found. Updated quality rules, logical inventory, governance and traceability; corrected exactly three confirmed encoding errors in dd08-validation.md. [Validation evidence](../03-execution/sprint-02-data-design/dd09-validation.md) records documentation-only checks. Next: DD-10 retention, DD-11 payment contracts and DD-12 branch history; finalize source cutoffs/allowances/content contracts and named independent appointments before their use. No critical override or actual release approval granted. Earlier entries retain historical status. G3 and implementation remain unapproved.

## DD-10 approval update - 2026-09-16

User approved [DD-10 lifecycle policy](../03-execution/sprint-02-data-design/retention-and-disposal-design.md), resolving the DD-08 conflict with a narrow exact-batch disposal exception. Approved Planning/Sprint 1 durations remain unchanged; current/dependency rules, minimization, holds, backups and expired-reference contracts are documented. [Validation](../03-execution/sprint-02-data-design/dd10-validation.md) records documentation-only results. Next: DD-11 payment semantics and DD-12 branch history; actual contracts/appointments and later physical implementation remain pending. No actual disposal, hold, restore or backup configuration. G3 remains unapproved; earlier dated entries are historical.

## DD-11 documentation update - 2026-09-16

DD-01 through DD-12 approved; synthetic documentary prerequisites closed; G3 pending. DD-11 adds logical schedules, obligations, allocations, unapplied amounts, adjustment events and effective loan-account links while preserving snapshot/KPI authority. Required source availability and reviewed mappings remain unverified prerequisites; G3 and implementation remain unapproved. Earlier dated entries retain historical status.

## DD-12 documentation update - 2026-09-16

DD-01 through DD-12 approved; synthetic documentary prerequisites closed; G3 pending. Historical hierarchy/assignment and attribution policy separates historical report labels from current effective authorization. Required source contracts remain unverified; no implementation or G3 approval. Earlier dated records retain historical status.

## Synthetic G3 prerequisite closure - 2026-09-16

User-authorized fictional-project scope clarification replaces real-source verification with synthetic logical contracts, proposed aliases, deterministic temporal conventions and unexecuted scenario expectations. Documentary prerequisites are finalized; full consolidated Sprint 2 G3 approval remains pending. Physical confirmation, generation and all runtime/security/publication evidence remain post-G3 and require authorization. No real independent personnel or approvals are claimed.

## G3 logical design approval - 2026-09-17

The requesting user approved the complete consolidated Sprint 2 logical package. See [gate decision](g3-data-design-approval.md). This updates lifecycle status only: no real-source verification, production readiness, physical implementation, generated fixtures, executed reconciliation, implemented RLS/security, KPI achievement, UAT or publication readiness is claimed. All post-G3 work requires separate authorization; material design changes require change control. Dated prior statuses remain historical.
