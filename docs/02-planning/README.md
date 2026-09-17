# Planning

Purpose: define the authorized work, delivery approach, requirements, controls, and approval gates.

## Current artifacts

- [Project Planning Baseline](Horizon_Community_Bank_Project_Planning_Baseline.md): approved scope, requirements, KPI definitions, architecture, schedule, backlog, quality plan, risks, governance, and gates.

## Reserved supporting locations

- `scope-and-requirements/`: supplemental scope, acceptance, and traceability artifacts.
- `delivery-plan/`: supplemental estimates and schedule evidence.
- `data-and-governance/`: data inventory, access, handling, and governance plans.
- `quality-and-validation/`: quality expectations and validation approach.
- `communications/`: reporting and stakeholder communication plans.
- `approvals/`: planning review and approval evidence.

## Status

Planning was explicitly approved by the user on 2026-09-09. The baseline has been published. Execution Sprint 1 business-analysis artifacts are stored under [Sprint 01 — Business Analysis](../03-execution/sprint-01-business-analysis/README.md).

Sprint 1 BA user approval and synchronization verification are recorded in the [approval record](../04-monitoring-and-control/sprint-01-approval-record.md). Sprint 2 Data Design documentation is now authorized by the current user request recorded September 15, 2026. See the [draft design package](../03-execution/sprint-02-data-design/README.md). The approved Planning baseline is preserved unchanged; its historical start-gate text is superseded for current status by this authorization. No requirement changes or implementation results are asserted.

Open questions: actual source contracts, named appointments and DD-11/DD-12 remain Pending confirmation. DD-01 through DD-10 are approved logical refinements; G3 remains pending.

## DD-08 governance supplement - 2026-09-16

The user approved [logical access, ownership and export policy](../03-execution/sprint-02-data-design/security-and-masking-design.md), consistent with FR-03/FR-10/FR-11/FR-12/FR-14 and existing KPI ownership. Joint Risk Manager/Compliance change approval, independent stewards and source/KPI owner plus Data Owner reviews refine governance. The approved Planning baseline is unchanged. Named appointments and actual review evidence remain Pending confirmation; G3 and physical security are not approved.

## DD-09 quality/publication supplement - 2026-09-16

The user approved [DD-09 logical policy](../03-execution/sprint-02-data-design/data-quality-and-reconciliation.md) after compatibility review. It preserves Planning's 98% completeness, zero unexplained variance and 6:00 a.m./95% targets while defining per-source/entity gates, mandatory sources, bounded independent exclusions and Data Publication Approver responsibility. Approved requirements remain in the unchanged baseline; this design supplement does not claim tests, business release or G3 approval. Source contract values, named appointments and DD-10 through DD-12 remain pending.

## DD-10 approval update - 2026-09-16

User approved [DD-10 lifecycle policy](../03-execution/sprint-02-data-design/retention-and-disposal-design.md), resolving the DD-08 conflict with a narrow exact-batch disposal exception. Approved Planning/Sprint 1 durations remain unchanged; current/dependency rules, minimization, holds, backups and expired-reference contracts are documented. [Validation](../03-execution/sprint-02-data-design/dd10-validation.md) records documentation-only results. Next: DD-11 payment semantics and DD-12 branch history; actual contracts/appointments and later physical implementation remain pending. No actual disposal, hold, restore or backup configuration. G3 remains unapproved; earlier dated entries are historical.

## DD-11 documentation update - 2026-09-16

DD-01 through DD-12 approved; synthetic documentary prerequisites closed; G3 pending. DD-11 adds logical schedules, obligations, allocations, unapplied amounts, adjustment events and effective loan-account links while preserving snapshot/KPI authority. Required source availability and reviewed mappings remain unverified prerequisites; G3 and implementation remain unapproved. Earlier dated entries retain historical status.

## DD-12 documentation update - 2026-09-16

DD-01 through DD-12 approved; synthetic documentary prerequisites closed; G3 pending. Historical hierarchy/assignment and attribution policy separates historical report labels from current effective authorization. Required source contracts remain unverified; no implementation or G3 approval. Earlier dated records retain historical status.

## Synthetic G3 prerequisite closure - 2026-09-16

User-authorized fictional-project scope clarification replaces real-source verification with synthetic logical contracts, proposed aliases, deterministic temporal conventions and unexecuted scenario expectations. Documentary prerequisites are finalized; full consolidated Sprint 2 G3 approval remains pending. Physical confirmation, generation and all runtime/security/publication evidence remain post-G3 and require authorization. No real independent personnel or approvals are claimed.

## G3 logical design approval - 2026-09-17

The requesting user approved the complete consolidated Sprint 2 logical package. See [gate decision](../04-monitoring-and-control/g3-data-design-approval.md). This updates lifecycle status only: no real-source verification, production readiness, physical implementation, generated fixtures, executed reconciliation, implemented RLS/security, KPI achievement, UAT or publication readiness is claimed. All post-G3 work requires separate authorization; material design changes require change control. Dated prior statuses remain historical.
