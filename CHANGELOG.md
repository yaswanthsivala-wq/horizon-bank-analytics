# Changelog

Record meaningful repository and documentation changes here. Entries describe actual work and explicitly recorded approvals.

## Combined integration candidate prepared — 2026-09-21

Prepared an unstaged candidate on `integration/r1-cr002-wp-pd01` from the published CR-002 follow-up, retaining R1 and transferring the preserved WP-PD01 delta. Reconciled the four overlapping current-status/history documents without changing approved design or WP-PD01 physical-design/SQL content. Historical entries remain intact and dated; added [fresh combined-tree validation](docs/04-monitoring-and-control/quality-reviews/integration-r1-cr002-wp-pd01-validation-2026-09-21.md). Removed the quality-reviews placeholder because that directory now contains substantive evidence.

No main update, commit, push, independent review, runtime/deployment validation, PD02 work or new gate approval. Original source commits and branches remain unchanged; candidate approval is pending.

## CR-002 project-owner decision follow-up — 2026-09-21

Recorded H01–H03 Option A confirmations of intended reconciled documentation and H05 authority clarification, dated 2026-09-21 while preserving G2's historical 2026-09-09 approval date. Added [decision evidence and Planning supplement traceability](docs/04-monitoring-and-control/change-control/CR-002-project-owner-decisions-2026-09-21.md); appended CR-002's disposition without rewriting its history; updated Monitoring and Control inventory and project status.

No independent bank/stakeholder/persona approval is claimed. No protected baseline, approved design decision, KPI, requirement, G3 status or WP-PD01 content changes. No new gate, PD02 or implementation authorization. This follow-up is not integrated into main.

## Sprint 2 documentation remediation R1 — 2026-09-20

Corrected current Sprint 2 status labels while preserving superseded history (A1); derived the relationship register and appended G3 link-count errata (A2); documented 41/109 ERD coverage and added five dependency views covering the other 68 entities (A3/B2). Added retrospective KPI/risk and baseline-change records CR-001/CR-002 (A4/A5), with content hunks Pending sponsor confirmation, and mapped Monitoring and Control registers (A6). Recorded the BO objective-order mismatch as Pending confirmation (B1); clarified the five source systems/domains (B3); reordered existing changelog entries without changing their text (B5).

No approval status changed; no design decision changed; no implementation. R1 is on `remediation/sprint-02-r1`, not merged to main, and awaiting user review. The isolated R1 baseline excludes the separately preserved WP-PD01 work.

Rationale for the Restricted classification of `rc01_comparison` fields: Pending confirmation.

Deferred to Sprint 3 design: strategy for `typed entity reference` / `internal key` fields (F-13); sizing of ~4.38 M loan-position and up to 3.65 M complaint-snapshot rows against NFR-04 (F-14); enriching thin field definitions (F-10). Adding SSN, KYC or AML fields is not in scope; none added.

## WP-PD01 - 2026-09-17

User-authorized physical architecture, exhaustive 109-entity/982-field proposed mapping, constraint/reference plan, temporal/publication, indexing, security, lifecycle and safe-cleanup documentation. Added foundation SQL limited to schemas, NOLOGIN roles, ownership/default privileges, extension declaration and migration ledger; static review only. G3 semantics unchanged; PD02 requires separate authorization. No execution, generated data, dependency installation or remote/Git publication. See [validation](docs/03-execution/sprint-03-physical-design/static-validation.md).

## G3 approved - 2026-09-17

Requesting user explicitly issued /approve G3 for the complete consolidated Sprint 2 logical-design package under the synthetic-project scope. [Gate decision](docs/04-monitoring-and-control/g3-data-design-approval.md) references g3-closure-validation.md and g3-prerequisite-register.md. Updated gate/lifecycle records only. No physical design, generation, implementation, runtime/security results, production readiness, KPI achievement, UAT or publication readiness is implied. Separate authorization is required for post-G3 work. Material grain/cardinality/formula/security/retention/source-semantic changes require change control. No other gate approved; no staging, commit, push or remote contact.

## G3 synthetic prerequisite closure - 2026-09-16

Requesting user authorized documentation-only gate-scope clarification: fictional sources and persona responsibilities, no real source/personnel validation. No conflict with protected baselines or approved business decisions found before edits. Finalized synthetic contract, temporal conventions, generation specification, expected controls, full entity/field trace and prerequisite register; reconciled current status while preserving history. G3 is not approved. No schemas, data, implementation, runtime tests, stage, commit, push or remote contact.

## DD-12 approved logical attribution - 2026-09-16

Approval evidence: requesting user explicitly approved the 25 controlling DD-12 decisions. Pre-edit review found no conflict with Planning, Sprint 1 or DD-01 through DD-11. Updated hierarchy/assignment versions, historical attribution, current authorization mapping, corrections, quality, retention and source prerequisites across the documentation. No verified source availability or actual owner review claimed. DD-01 through DD-12 logical decisions approved; source evidence, physical design and G3 pending. Documentation validation only; no staging, commit, push or implementation.

## DD-11 approved logical payment design - 2026-09-16

Approval evidence: requesting user explicitly approved DD-11 with 20 controlling decisions. Pre-edit compatibility review found no conflict with Planning, Sprint 1 or DD-01 through DD-10. Rationale: separate contractual obligations from actual payments; preserve immutable corrections and business adjustments; prevent guessed account links and financial fanout. Updated the authoritative inventory, models, logical source contracts/mappings, DD-09 controls, DD-10 schedule, traceability and current status. Source schemas/coverage, adjustment application timing and reviewed aliases remain prerequisites, not verified availability. Loan Operations Manager and Data Owner are review responsibilities, not claimed actual review evidence. DD-12 and G3 remain pending. Documentation validation only; no implementation, staging, commit, push or remote contact.

## DD-10 lifecycle policy approved - 2026-09-16

- Recorded supplied retention/minimization/backup/hold/disposal policy and explicit narrow DD-08 supersession; no general Administrator deletion permission.
- Added complete entity schedules and sole-inventory provenance-envelope, retention, hold, exact-batch disposal, backup/restore and denied-access contracts.
- Coordinated retained-date corrections and expired-publication fallback; synchronized governance, traceability and lifecycle status.
- Documentation validation recorded in dd10-validation.md. DD-11/DD-12 remain pending; no staging, commit, push, G3 approval or implementation.

## DD-09 quality and publication controls approved - 2026-09-16

- Recorded user approval after pre-edit compatibility review; preserved Planning, Sprint 1 and prior business semantics.
- Approved 17-rule severity/escalation catalog, five mandatory sources, exact reconciliation, received/curated completeness gates, bounded exclusions and independent atomic publication.
- Extended sole logical inventory for checksum metadata and all-candidate control, exclusion, review, decision and notification evidence; updated governance, traceability and lifecycle status.
- Corrected the three confirmed DD-08 range separators to UTF-8 en dashes. Full documentation checks recorded in dd09-validation.md.
- DD-10 through DD-12 and actual source contracts/appointments remain pending. No staging, commit, push, G3 approval or implementation.

## DD-08 access, ownership and export policy approved - 2026-09-16

- Recorded user approval after compatibility review; preserved Planning, Sprint 1 and earlier decision semantics.
- Extended the sole logical field inventory for scoped entitlements, independent governance reviews, export evidence and sanitized RC-01 investigation detail.
- Synchronized lifecycle status, ownership, identity governance, traceability and DD-09/DD-10 dependencies. Documentation validation is recorded in dd08-validation.md.
- No staging, commit, push, G3 approval or technical implementation.

## DD-07 logical field standard approved - 2026-09-16

- Recorded user approval after conflict review against Planning, Sprint 1 and DD-01 through DD-06; business formulas, attribution and evidence policies preserved.
- Consolidated one authoritative inventory with bounded types, explicit conditionality, immutable version keys, defined version parents and structured evidence/mapping/control/filter children. Removed duplicate base/supplement definitions and ambiguous scalar mappings.
- Updated affected Sprint 2 designs, traceability, status and control records. Physical implementation choices explicitly deferred; DD-08 through DD-12 and source alias details remain pending. No G3 approval, implementation or Git metadata writes.

## DD-06 KPI and canonical policy approved - 2026-09-16

- Recorded approved populations, canonical groups/risk subsets, time/comparison/calendar-SLA rules, reopened/final-closure behavior, daily RC-01 population and revision policy.
- Preserved K06 formula with no positive-principal population filter; separated positive/zero valid, negative quarantine and missing-evidence dispositions with raw lineage/reconciliation controls.
- Updated affected designs, source/field contracts, traceability, status and controls; preserved protected baselines. Source aliases require versioned mapping before publication. DD-07 through DD-12 remain pending; no G3 approval, implementation or Git metadata writes.

## DD-05 RC-01 comparison policy approved - 2026-09-15

- Recorded explicit RC-01-only supersession of DD-04 attribution: valid source initiator, absent-identifier sole-owner fallback, joint-owner Unknown, and invalid/unmapped-identifier exception without fallback.
- Applied full 90-calendar-day coverage, five-prior minimum, same currency/no conversion, finalized-status eligibility/exclusions, absolute nonzero comparison, retained signed audit values and controlled revised evidence.
- Preserved DD-02 exposure, other risk-condition attribution and protected baselines. Updated affected designs/status/traceability/control records. DD-06 mappings and remaining assessment-population detail remain pending. No implementation, G3 approval or Git metadata writes.

## DD-04 catalog and evidence policy approved - 2026-09-15

- Applied corrected RC-03 DPD > 30 and the supplied five-condition catalog. Preserved Planning/Sprint 1 KPI boundaries and the at-least-two-Triggered requirement.
- Recorded RC-02 through RC-05 and Unknown/incomplete-evidence handling as Sprint 2 decisions; kept DD-05/DD-06 dependencies pending.
- Added catalog and updated affected designs, field/evidence contracts, traceability, status and controls. No baseline edits, Git metadata writes, G3 approval, data generation or implementation.

## DD-03 historical snapshot design approved - 2026-09-15

- Recorded approval of daily loan/business-date and complaint/business-date snapshots preserving as-of knowledge, batch revision, source version, publication lineage and controlled corrections.
- Updated Sprint 2 models, mappings/dictionary, source/quality/KPI/security/identity guidance, future scenarios and traceability, plus status/control records.
- Unsupported historical states remain unavailable; no backward filling, future-information use or summation of daily stocks. Protected baselines and Sprint 1 evidence preserved. No G3 approval, implementation or Git metadata writes.

## DD-02 relationship design approved - 2026-09-15

- Recorded explicit approval of all owners/co-borrowers, effective-dated roles and non-additive customer relationship exposure.
- Updated ERD, logical bridges, source mappings, field dictionary, identity rules, KPI/security/quality design, future fixture specification and traceability. Bank totals stay at natural fact grain; no owner allocation policy introduced.
- Updated current status and control records; preserved approved baselines and Sprint 1 evidence. DD-03 through DD-12 remain pending; G3 and implementation unapproved. No staging, commit, push or data generation.

## DD-01 delivery approach approved - 2026-09-15

- Recorded the user's "Approve DD-01" decision and synchronized source, mapping, quality, synthetic-specification and traceability documentation.
- Updated Sprint 2 and phase status summaries; eleven other decisions remain pending, together with unspecified detailed source-contract values.
- Preserved approved baselines and Sprint 1 evidence. No G3 approval, implementation, data generation or Git metadata writes.

## Sprint 2 Data Design package - 2026-09-15

- Recorded current `/start sprint-2-data-design` authorization for local design documentation only.
- Expanded six existing untracked Sprint 2 drafts; corrected unsupported earlier draft authorization dating and added source-system definitions, logical model, field-level dictionary/mappings, identity rules, KPI mappings and security/masking design.
- Added design links for all 32 Sprint 1 acceptance criteria; retained the 14 FR / 9 NFR baseline and future-test references. Recorded pending source, risk, temporal, quality and security decisions.
- Added Sprint 2 Monitoring and Control record and updated current lifecycle indexes/status. Preserved approved Initiation/Planning content, all Sprint 1 files and the Sprint 1 approval evidence.
- No generated data, database objects, ETL code, implementation/test results, remote operations or Git metadata writes. Sprint 2 design remains Draft — not approved; G3 pending.

## Sprint 1 BA approval recorded - 2026-09-14

- Recorded the received `/approve sprint-1-ba` user approval and successful synchronization of published commit `b44fc5be7bbbc3ead6b9252a0077ec244e1352e8`.
- Updated lifecycle summaries and gate documentation; added a dated Monitoring and Control approval/evidence record.
- Preserved the approved business and Planning baselines and Sprint 1 backlog, process flows, and traceability content. Approval covers BA documentation, not implementation, testing, KPI achievement, UAT, or release acceptance.
- Sprint 2 Data Design and technical implementation remain not started; explicit authorization to start Sprint 2 is still required.

Earlier entries below retain historical status as recorded at their dates.

## Baseline and lifecycle reconciliation — 2026-09-10

- Reconciled the approved Initiation purpose, business problems, objectives, scope, exclusions, assumptions, constraints, and stakeholder-role documentation.
- Recorded the confirmed September 9, 2026 Planning approval in the Planning baseline approval record, G2 row, entry-criteria context, and footer; identified Sprint 1 BA user approval as the next gate after required verification.
- Retained the published Planning and Sprint 1 artifact inventory, links, and historical GitHub publication evidence. Distinguished documented definitions from pending validation evidence and unconfirmed assignments.
- Preserved approved Planning content and all Sprint 1 BA files. Sprint 2 Data Design and technical implementation remain not started; no implementation, test, KPI-achievement, UAT, or acceptance results are claimed.

The entries below record historical publication activities and status at those dates. Their references to unchanged Initiation files describe that earlier publication, before this authorized baseline correction.

## Planning and Sprint 1 BA — 2026-09-09

### Added

- Approved Project Planning Baseline under `docs/02-planning/`.
- Sprint 1 business-analysis index under `docs/03-execution/sprint-01-business-analysis/`.
- Eight user stories with thirty-two Given–When–Then acceptance criteria.
- AS-IS, TO-BE, role-access, and customer-risk process flows.
- Functional and nonfunctional requirements traceability matrices.

### Updated

- Planning and Execution phase READMEs with current artifact inventories and approval status.
- Root README with current lifecycle status, navigation, Release 1 direction, and repository safeguards.
- Project status with completed validation, remaining local synchronization control, and the next gate.

### Preserved

- All existing Initiation documentation under `docs/01-initiation/`.
- Reserved technical directories and existing repository instructions.

### Control note

Planning was explicitly approved by the user. Sprint 2 remains blocked until this GitHub state is pulled into the permanent local VS Code folder and verified.

## Initiation documentation — 2026-09-09

### Added

- Project charter recording the confirmed project identity, user confirmation of existing Initiation approval, current authorization, constraints, and pending decisions.
- Stakeholder register recording the requesting user's evidenced participation without inventing stakeholder identities or assignments.

### Updated

- Root README, Initiation README, and project status to reflect the user's synchronization and approval confirmation and the newly prepared documents.
- Recorded the evidence limitation: no detailed approved business brief or named stakeholder roster was present at that stage.
- Kept Planning pending explicit authorization at that stage; no Planning, analysis, or technical implementation was performed.

## Initial scaffold — 2026-09-09

### Added

- Five-phase project lifecycle documentation scaffold.
- Repository instructions, README, and project status document.
- Reserved source, SQL, data, dashboard, test, and workflow directories.
- Ignore rules for Python, VS Code, environment files, credentials, generated data, and temporary files.
