# Design traceability and G3 review

Status: **G3 logical design approved 2026-09-17**; post-G3 work requires separate authorization.

## Coverage of approved requirements

This is a Sprint 2 design supplement to the unchanged [Sprint 1 traceability matrix](../sprint-01-business-analysis/requirements-traceability-matrix.md). All implementation and test statuses remain planned.

| Requirements | Proposed design evidence | Remaining review |
| --- | --- | --- |
| FR-01, FR-02 | Five-source manifests and history contracts in [dictionary](data-dictionary-and-mappings.md); [synthetic specification](synthetic-data-specification.md) | Detailed source contracts and history start; delivery approach approved in DD-01 |
| FR-03, FR-04 | Crosswalk, grains and intervals in [model](data-model.md); [quality rules](data-quality-and-reconciliation.md) | DD-09 disposition approved; actual source domains remain |
| FR-05, FR-06 | Separate facts, snapshot/as-of grains, conformed dates | DD-06 approved; source aliases and future validation remain |
| FR-07, FR-08 | Versioned assessment/evidence, DD-05 approved 90-day window | Catalog approved DD-04; DD-05 eligibility approved; DD-06 canonical groups approved; source aliases pending |
| FR-09, FR-10 | Conformed report dimensions and role-filtered facts | Customer attribution and final relationships |
| FR-11, FR-12, FR-14 | Restricted identity, masked reporting fields, export audit | Role simulation design and denied-path tests |
| FR-13 | Run, manifest, exception and reconciliation entities | DD-09 approved; actual evidence and future control execution remain |
| NFR-01, NFR-02, NFR-03 | Publication cutoff, completeness and financial controls | Later measured timing/quality evidence |
| NFR-04, NFR-05, NFR-06 | Separate facts and aggregates; Planning's 100-user design assumption retained | Physical design and later performance evidence; no concurrency result claimed |
| NFR-07, NFR-08, NFR-09 | Provenance, versioned rules, retention design | DD-10 logical lifecycle approved; physical mechanics and remaining source contracts deferred |

## Decision register

DD-01 was approved by the user on 2026-09-15: entity-specific delivery modes and required batch manifests. DD-02 is also approved: all owners/co-borrowers, effective-dated roles and non-additive relationship exposure. DD-03 is approved for daily historical snapshots and controlled lineage/corrections. DD-01 through DD-12 are approved at logical decision level. Detailed DD-01 contract values remain pending where unspecified; G3 logical design is approved 2026-09-17; technical implementation remains unauthorized.

| ID | Question / proposed direction | Approval status |
| --- | --- | --- |
| DD-01 | Entity-specific delivery: master/case snapshots, transaction/payment events and daily loan positions; required manifests with revision and delivery mode | Approved by user 2026-09-15; detailed contract values pending. See source-system definitions and control record |
| DD-02 | All owner/co-borrower relationships; effective-dated roles; non-additive relationship exposure; natural-grain monetary facts; no allocation without separate approval | Approved by user 2026-09-15; see control record |
| DD-03 | Daily historical loan-position and complaint-state snapshots; entity/business-date grain, as-of values, revision/source/publication lineage and controlled corrections; unavailable if unsupported | Approved by user 2026-09-15; see control record |
| DD-04 | RC-01 through RC-05; RC-03 DPD > 30; threshold-aware Unknown classification and versioned evidence | Approved by user 2026-09-15; DD-05 approved; DD-06 canonical groups approved; source aliases pending; see customer-risk-catalog.md |
| DD-05 | Full 90-calendar-day window within 24 months, >=5 eligible priors, same currency, absolute nonzero finalized amounts, initiator hierarchy and versioned recalculation | Approved by user 2026-09-15; supersedes RC-01 attribution only; DD-06 daily population and canonical groups approved; source aliases pending |
| DD-06 | Approved KPI populations/time/comparisons, canonical groups, calendar SLA/no pauses, daily RC-01 population and revised publications; K06 formula unchanged with separate quality rules | Approved by user 2026-09-16; source aliases must be finalized before publication; see kpi-policy-dd06.md |
| DD-07 | Authoritative logical field inventory, bounded types, keys/versions, child evidence and no silent coercion; physical choices explicitly deferred | Approved by user 2026-09-16; see field-level-dictionary.md and control record |
| DD-08 | Default deny, single active role, scoped entitlements, independent governance, masked exports and complete sanitized evidence | Approved by user 2026-09-16; logical responsibilities only; see security-and-masking-design.md |
| DD-09 | Four severities, mandatory sources, >=98% received/curated gates, exact reconciliation, bounded exclusions, independent atomic publication and all-candidate audit | Approved by user 2026-09-16; see data-quality-and-reconciliation.md; source-contract values and actual appointments pending |
| DD-10 | 24-month analytics, seven-year minimized audit, expired-reference envelopes, scoped holds, bounded backups and exact independently approved disposal | Approved by user 2026-09-16 including narrow DD-08 disposal supersession; see retention-and-disposal-design.md |
| DD-11 | Immutable schedules/obligations, positive actual payments, many-to-many allocations, unapplied state, separate capped adjustments, effective REPORTING links and original-date retention | Approved by user 2026-09-16; loan-payment-and-schedule-policy.md; required source coverage unverified |
| DD-12 | Effective hierarchy/assignments, historical attribution, current stable-branch access, corrections and retention | Approved by requesting user 2026-09-16; historical-branch-attribution-policy.md; source evidence pending |

## G3 readiness checklist

- Review the ERD and all entity grains, cardinalities, and historical joins.
- DD-07 logical field standard approved; review proposed synthetic aliases/domains and documented DD-12 history scenarios; confirm physical mappings after authorized generation.
- Review finalized synthetic hierarchy/assignment contracts and sample specifications; actual generation and execution remain post-G3.
- Confirm every KPI can be derived without double counting and with an agreed as-of window.
- Confirm all five manifests, missing-source controls, replay behavior, and reconciliation populations.
- Confirm synthetic fixture specification and historical sufficiency within approved scope.
- Review masking, role scope, exports, audit visibility and retention.
- Record design-review outcome and explicit Gate G3 approval before ETL construction.

The user explicitly approved the consolidated logical package at G3 on 2026-09-17 using the synthetic closure evidence. This is not approval inferred from checklist existence; technical implementation has not started.

## Approved decisions and remaining implementation prerequisites

DD-01 through DD-12 are approved. The [G3 prerequisite register](g3-prerequisite-register.md) applies the user's synthetic-project gate-scope decision. Finalized [synthetic contracts](synthetic-source-contract.md), [entity/field trace](synthetic-contract-traceability.md) and [scenario specification](synthetic-data-specification.md) replace impossible real-source evidence at this logical gate. Proposed physical aliases await generated-fixture confirmation; no real owners or independent operational approvals exist. The complete consolidated package received explicit user G3 approval on 2026-09-17. Physical work, data generation, executable joins, reconciliation, security and publication remain unauthorized/unexecuted.

## Story acceptance-criterion design traceability

AC identifiers below are local references to the numbered criteria in the unchanged Sprint 1 backlog: US-01.1 means US-01 criterion 1. Status for every row: **Draft design mapped; implementation planned; test not run; acceptance Pending confirmation**. Future test IDs are inherited from Sprint 1, not new results.

| AC | Design evidence / intended behavior | Future verification |
| --- | --- | --- |
| US-01.1 | [KPI mappings](kpi-to-data-mappings.md) K01–K10; [security](security-and-masking-design.md) executive aggregates | RC-01, UAT-01 |
| US-01.2 | KPI shared date/comparison contract, DD-06 | FT-01 |
| US-01.3 | Security executive projection and export boundary | ST-02–ST-05 |
| US-01.4 | [Dictionary](field-level-dictionary.md) pipeline_run.readiness_at and publication version | IT-02 |
| US-02.1 | Security effective region/branch entitlements | ST-02–ST-05 |
| US-02.2 | KPI K01–K03 and [logical dimensions](logical-data-model.md) | FT-02, RC-01 |
| US-02.3 | KPI K02/K03 cancelled and reversed exclusions | RC-01 |
| US-02.4 | Security scope persists when report filters clear | FT-02, ST-02–ST-05 |
| US-03.1 | Dictionary alert date/severity/status/reason and effective branch path | FT-02 |
| US-03.2 | KPI unusual-transaction window, DD-05 | UT-07 |
| US-03.3 | risk_evidence inputs and masked account; related alert lineage | UT-07, ST-01 |
| US-03.4 | KPI analytical indicator wording | UAT-03 |
| US-04.1 | KPI K05/K06 separate active-loan semantics | RC-01 |
| US-04.2 | DPD >30 preserved in K05/K06 | RC-01 |
| US-04.3 | Logical branch/loan-type dimensions; aging bands DD-06 | FT-02 |
| US-04.4 | loan/account/payment mappings, DD-11 and security mask | FT-02, ST-01 |
| US-05.1 | KPI K08–K10 | RC-01 |
| US-05.2 | K10 and rule_config baseline SLA thresholds | RC-01 |
| US-05.3 | K09 null closure AND non-Closed status | RC-01 |
| US-05.4 | Complaint snapshot priority/channel/branch/status | FT-02 |
| US-06.1 | K07 >=2; approved DD-04 catalog/classification; dependent mappings pending | UT-01–UT-06 |
| US-06.2 | risk_assessment/evidence date, source, observed value and threshold | UT-01–UT-06 |
| US-06.3 | Versioned rule_config and approval reference | MT-01 |
| US-06.4 | KPI provisional human-review wording | UAT-06 |
| US-07.1 | Security aggregate-only executive dataset | ST-02–ST-05 |
| US-07.2 | Security fixed mask plus final four | ST-01 |
| US-07.3 | Security default deny and direct-access boundary | ST-02–ST-05 |
| US-07.4 | export_event sanitized role/report/time/format/filter context | ST-06, ST-07 |
| US-08.1 | [Source manifests](source-system-definitions.md), DQ-D01/PUB-D01 | IT-01 |
| US-08.2 | [Quality catalog](data-quality-and-reconciliation.md) and exception reason codes | DQ-03 |
| US-08.3 | Quality row-disposition and financial equations | IT-02, RC-01 |
| US-08.4 | pipeline_run counts, timestamps, completeness/readiness design | IT-02, DQ-04, PT-01 |

## Detailed requirement supplement

The grouped requirement table above covers FR-01–FR-14 and NFR-01–NFR-09. Additional review pointers: FR-03 uses [identity rules](customer-identity-reconciliation.md); FR-05–FR-08 use [KPI mappings](kpi-to-data-mappings.md); FR-11/12/14 use [security design](security-and-masking-design.md); NFR-07/08/09 use audit/retention/configuration field contracts. NFR-04/05 performance testing and NFR-06 capacity review remain future work. FR-14 remains Should in Planning even though US-07 is Must; no priority change is inferred.

No story meets implementation Definition of Done from design coverage alone. Design checking is recorded in the [Sprint 2 control record](../../04-monitoring-and-control/sprint-02-control-record.md).

## DD-02 traceability update

DD-02 approved by the user on 2026-09-15: retain all owners and co-borrowers with effective-dated relationship roles. Monetary facts remain at their natural account, transaction, payment or loan grain. Customer-level shared balances are labeled "Relationship exposure" and are non-additive across customers; bank totals are computed from distinct natural-grain facts, never by summing customer exposures. Equal or weighted allocation requires a separately approved policy.

FR-03/FR-04: source-qualified bridges and interval validation. FR-05/FR-10: natural-grain totals and labeled non-additive drill-through (US-01.1, US-02.2, US-04.1/4). FR-07/FR-08: shared relationship context only; DD-04 catalog is approved; DD-05 eligibility is approved; DD-06 canonical groups approved; source aliases pending (US-03.2/3, US-06.1/2). FR-12/FR-14: role scope and export labels (US-07). FR-13: separate relationship and monetary reconciliation (US-08.2/3). Future DQ-02/DQ-03, RC-01, FT-02 and ST-02 through ST-06 checks remain unexecuted; no acceptance status is advanced.

## DD-03 traceability update

DD-03 approved by the user on 2026-09-15: daily historical loan-position snapshots at loan plus business-date grain and complaint-state snapshots at complaint plus business-date grain. Preserve values known for each as-of date, batch revision, source version, publication lineage and controlled correction history. Historical states that cannot be supplied or reliably reconstructed are unavailable. Do not carry current values backward, use future information or sum daily stock measures across dates.

FR-02/FR-04: historical coverage, unavailable-state and as-of validation (DQ-01/DQ-03). FR-05/FR-06: loan and complaint snapshot measures and comparable as-of dates (US-01.1/2, US-04.1/2, US-05.1/3; RC-01/FT-01). FR-13/NFR-07: source version, revision, publication and correction lineage (US-08.2/3/4; IT-02/ST-07). NFR-03: date/revision-specific reconciliation. DD-08 through DD-12 remain pending; DD-01 contract values still need confirmation. These are design links only; tests and acceptance remain unexecuted/pending.

## DD-04 traceability and provenance

[Risk catalog](customer-risk-catalog.md): risk RC-01 inherits FR-08/US-03 3x/90-day basis. Risk RC-02 through RC-05 are approved Sprint 2 refinements supporting FR-07/US-06, not previously enumerated requirements. RC-03 DPD > 30 preserves FR-05 loan KPI definitions and US-04. Unknown policy refines the BA flow while preserving >=2 Triggered. Evidence/versioning links FR-13, NFR-07/NFR-09, US-06.2/3 and US-08 to planned UT-01 through UT-07, MT-01 and ST-07 checks. "RC-01" in prior verification columns remains the reconciliation test ID, not the risk condition. No tests/acceptance advanced; DD-05 comparison policy is approved; DD-06 policy approved; source aliases pending.

## DD-05 approval traceability

FR-08/US-03 preserve 3x/90-day basis with approved eligibility and evidence rules. DD-05 explicitly supersedes DD-04 RC-01 all-owner attribution; DD-02 relationship exposure and RC-02 through RC-05 are unchanged. FR-03/FR-04 link initiator resolution/deduplication to planned DQ-02/DQ-03; FR-08 links boundaries/statuses/amount/history to UT-07; NFR-07/FR-13 link missing reasons and revision lineage to ST-07/IT-02. Tests remain unexecuted. DD-06 resolves daily current transactions by occurred_at business date.

## DD-06 traceability

[Approved policy](kpi-policy-dd06.md): FR-05/FR-06 and US-01.1/2, US-02.2/3 map KPI populations, comparisons and percentage-point changes to planned reconciliation test RC-01 and FT-01. US-04 retains DPD > 30; K06 formula remains unchanged with separate quality exceptions. US-05 maps creation-priority/calendar-SLA/final-closure/reopening to planned reconciliation and FT-02 checks. US-03/US-06 map daily RC-01 population and canonical risk subsets to UT-01 through UT-07. US-08/NFR-07 map revision/mapping lineage and validation gates to IT-02/ST-07. No test or acceptance claim is advanced. DD-08 through DD-12 and source-specific contract values remain pending.

## DD-07 approval and traceability - 2026-09-16

The user approved the logical field-contract standard after compatibility review. FR-03/FR-04 and US-08 map to bounded types, source-qualified keys, UTC instants, conditional nulls and no silent coercion. FR-07/FR-08 and US-03/US-06 map to exact RC-01 comparison, one condition outcome and deduplicated child evidence. FR-05/FR-06 and US-04/US-05 map to selected-publication snapshot uniqueness, immutable creation priority and original-creation/closure history. FR-13/NFR-07 map to version parents, applied mappings, source extracts and acyclic corrections. NFR-08 remains dependent on DD-10. These are documentation mappings to future checks, not executed data tests.

DD-01 through DD-07 approved; DD-08 through DD-12 pending. Logical contracts are in the [authoritative inventory](field-level-dictionary.md); [validation evidence](dd07-validation.md) records this review. No physical schema or G3 approval.

## DD-08 approval and traceability - 2026-09-16

FR-11/FR-12/FR-14 and US-01/US-02/US-07 map to single active role, default deny, final-four masking and scoped exports. FR-08/US-03 and FR-07/US-06 map to case-linked evidence and the sanitized RC-01 projection; US-06 source context remains a sanitized domain label, not a raw source locator. FR-03/US-08 map to independent steward approval and source/Data Owner reviews. NFR-07 maps to structured export and approval evidence; NFR-08 mechanics remain DD-10. Planned ST-01 through ST-07 cover these controls; no runtime/security acceptance is claimed.

DD-01 through DD-08 approved; DD-09 through DD-12 pending. [Validation](dd08-validation.md) records documentation checks. Historical decision entries above retain their original status. G3 and physical implementation remain unapproved.

## DD-09 approval and traceability - 2026-09-16

FR-01/FR-13 and US-08.1/3/4 map to five mandatory sources, checksum/revision integrity, exact disjoint row and signed currency controls, atomic publication and audit. FR-03/FR-04 map to quarantine, identity/interval integrity and severity escalation. NFR-02 maps to per-source/entity and overall received/curated >=98% business-field completeness; post-exclusion cannot replace received evidence. FR-05/FR-06 and US-04/US-05 preserve formulas while blocking misleading K06/K08-K10 results. FR-07/FR-08 and US-03/US-06 preserve legitimate Unknown and exact risk evidence while blocking missing required configuration. FR-11/FR-12 and US-07 map to masking escalation and independent DD-08 controls. NFR-01 retains the 6:00 a.m./95% target; NFR-07 maps to every candidate decision and notification evidence; DD-10 retains NFR-08 mechanics.

DD-01 through DD-09 approved; DD-10 through DD-12 pending. Tests DQ-01 through DQ-04, IT-01/IT-02, reconciliation RC-01, risk UT-01 through UT-07 and applicable security tests remain planned, not run. [DD-09 validation](dd09-validation.md) records documentation checks only. Historical approval entries retain their recorded status. G3 and implementation remain unapproved.

## DD-10 approval and traceability - 2026-09-16

FR-02/NFR-08 and planned AR-02 map to complete 24-month reporting, searchable seven-year audit, through-anniversary/monthly disposal, current-state exceptions and 35-day backup bounds. FR-13/NFR-07 map to minimized envelopes, explicit expired references and hold/disposal evidence. FR-11/FR-12/FR-14 and planned ST-01 through ST-07 map to sanitized denials, Restricted token separation, short-lived exports and restore revocations. FR-07/FR-08 preserve risk semantics with retained-date correction limits. DD-09 stale fallback ends when detail expires.

The user explicitly resolved DD-08's deletion conflict by authorizing only exact independently approved lifecycle batches, retention-engine eligibility and constrained Administrator operation. No general deletion permission. DD-01 through DD-10 approved; DD-11/DD-12 pending. [Validation](dd10-validation.md) records documentation checks, not executed lifecycle/security tests. G3 remains unapproved.

## DD-11 approval and traceability - 2026-09-16

User explicitly approved the 20 controlling decisions. Compatibility with Planning, Sprint 1 and DD-01 through DD-10 was reported before edits. US-04.4 now maps to effective REPORTING loan_account, immutable payment/schedule/allocation/adjustment contracts and existing masking; US-04 delinquency criteria retain snapshot authority. FR-05/FR-10/FR-11 and historical/reconciliation/retention controls remain mapped through existing rows. No new baseline requirement or executed test is claimed. DD-12, actual reviewed source schemas/coverage and G3 remain pending. See [policy](loan-payment-and-schedule-policy.md) and [validation](dd11-validation.md).

## DD-12 approval and traceability - 2026-09-16

Requesting user approved 25 controlling decisions after read-only review. No baseline conflict found before editing. FR-02/FR-04 history and quality, FR-05 KPI grouping, FR-10/FR-11 scoped security, FR-13 reconciliation and relevant NFRs map to US-02 regional drill-down, US-03 evidence, US-04 loan filters, US-05 complaint filters, US-06 risk and US-08 controls. All existing 32 AC rows remain; planned tests gain transfer/merger/current-entitlement/historical-label/correction coverage without claims of execution. [Policy](historical-branch-attribution-policy.md) and [validation](dd12-validation.md) hold evidence. All DD-01 through DD-12 logical decisions approved; source-owner reviews, coverage and G3 remain pending.

## G3 decision - 2026-09-17

[Approval record](../../04-monitoring-and-control/g3-data-design-approval.md): requesting user approved the complete consolidated logical package using closure validation and prerequisite register evidence. Logical approval only, not real-source verification or runtime/production readiness. Separate authorization is required for all post-G3 work. Material grain, cardinality, formula, security, retention or source-semantics changes require change control. Earlier dated status entries remain historical.

## Business objective identifier cross-reference — 2026-09-20

Pending confirmation: the proposed statement "Sprint 1 RTM identifiers BO-01…BO-06 correspond to Planning §3 objectives 1–6 in order" does not hold for all rows. The [Sprint 1 RTM](../sprint-01-business-analysis/requirements-traceability-matrix.md#business-objective-ids) already defines BO-01…BO-06. BO-01…BO-04 align thematically with [Planning §3](../../02-planning/Horizon_Community_Bank_Project_Planning_Baseline.md#3-business-objectives) objectives 1–4. BO-05 protects sensitive information (Planning objective 6); BO-06 enables management action/investigation (closest to Planning objective 5). This is a documentary observation, not an approved remapping. Sponsor confirmation of the cross-reference remains Pending confirmation; no Sprint 1 file is changed.
