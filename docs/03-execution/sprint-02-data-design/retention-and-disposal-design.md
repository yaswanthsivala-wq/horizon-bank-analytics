# DD-10 approved retention, minimization, backup and disposal policy

Approved by the requesting user on 2026-09-16, including the explicit narrow DD-08 supersession clarification. Logical documentation only. G3 and implementation remain **Draft — not approved**. No disposal batch, backup, hold, restore or notification has been executed or configured.

## Compatibility and decision evidence

The pre-edit review identified DD-08's unconditional Administrator deletion prohibition as conflicting with execution of approved end-of-retention disposal. The user explicitly resolved that conflict: DD-10 supersedes it only for expired, unheld, dependency-cleared evidence inside a specifically approved disposal batch. This is a narrow lifecycle refinement, not general Administrator deletion permission. All other DD-08 separation-of-duties and access controls remain intact.

No other business-baseline conflict found with Planning, Sprint 1 or DD-01 through DD-09. Planning FR-02/NFR-08 durations and raw/curated scope are preserved. DD-06 recalculation and DD-09 last-successful serving are now bounded by retained analytical dates/detail; they never implied indefinite possession. Seven-year minimized decision evidence is distinct from 24-month payload and does not promise full recalculation after raw expiry. Exact retention representation below implements the supplied logical policy; no legal obligation, actual appointment or executed result is invented.

## Retention meaning

- Active reporting, audit/archive availability and total possession are separate states.
- The complete rolling 24-month analytical window remains available for reporting.
- Seven-year minimized audit evidence remains searchable for authorized audit purposes; target retrieval is within one business day.
- Moving data out of reporting is not deletion. Total disposal includes active stores, archives, temporary copies and eventual backup expiry.

## Time calculation

- Calculate analytical retention from the applicable business date, event date, snapshot date or assessment date in America/Chicago.
- Retain through the 24-month anniversary and make the record eligible for the next monthly purge afterward.
- Calculate audit retention from the audit event, decision, completed/denied attempt or publication-decision timestamp in UTC.
- Retain through the seventh anniversary and purge during the next monthly cycle.
- Reingestion, correction, republication or archive movement does not restart the analytical clock.
- Hold release does not restart a retention clock.

## 24-month analytics

- Retain raw deliveries, accepted curated facts, transactions, payments, snapshots, complaint/fraud states, risk assessments/evidence and analytical publication membership for 24 months using their original business/event anchors.
- Retain original and corrected analytical versions within that same window; correction does not extend the business record indefinitely.
- Retain aggregate caches and report projections no longer than their underlying analytical data.
- Risk investigation projections follow the retention of their underlying evidence and are not separate longer-lived copies.
- The 24-month period does not add RC-01 warm-up history beyond the approved dataset.

## Current and open-ended records

- Keep current customers, accounts, loans, branches, identity mappings, ownership relationships, open complaints, open fraud cases and active configurations while they remain active and are required by retained records.
- After closure, retirement or effective end, retain their historical detail for 24 months or until no retained analytical child depends on it, whichever is later.
- Preserve versions that began earlier when they intersect the retained analytical window.
- Do not expire an open-ended record solely because valid_from or creation date is old.
- Current-master exceptions do not authorize indefinite retention of obsolete source aliases or narratives.

## Seven-year minimized audit

- Retain pipeline runs, manifests, source-extract metadata, checksums, schema/mapping versions, quality exceptions, reconciliation results, financial controls, publication decisions, correction/recalculation decisions, notifications, export events including denials, access/entitlement decisions, identity-governance decisions, approvals, holds and disposal evidence for seven years from their event or decision timestamp.
- Retain configuration/rule/catalog/mapping versions while active and until seven years after the last retained audit decision that depends on them.
- Retain publication and supersession metadata for seven years, while detailed analytical membership remains limited to 24 months.
- Retain rejected identity/access decisions as minimized audit evidence for seven years. Their supplied restricted payload follows the shorter analytical/source schedule.
- Retain denied access and export attempts for seven years as sanitized events without sensitive requested values.

## Audit minimization

- Long-term audit evidence may contain opaque actor IDs, decision IDs, record tokens, source/entity/date/revision, publication IDs, rule/mapping versions, timestamps, reason codes, counts, currency-separated totals, digests and approval references.
- Do not copy names, contact information, full account numbers, unrestricted narratives, source customer aliases or rejected raw rows into seven-year audit records.
- Do not use unkeyed hashes of identity values as anonymization.
- When individual-record accountability is necessary, use opaque tokens. Keep any reversible token mapping in a separate Restricted store only while a valid analytical, audit or hold dependency requires it.
- Audit narratives use bounded reason codes and sanitized references.

## Expired-reference handling

- Add a minimized provenance-envelope/tombstone design containing an opaque token, source namespace, entity, business date, revision/version, digest, disposition, expiry timestamp and deletion-evidence reference.
- After payload expiry, surviving audit references point to the envelope and explicitly state PAYLOAD_EXPIRED.
- Do not silently null mandatory audit links, cascade-delete surviving evidence or keep Restricted parents indefinitely.
- After raw detail expires, the system promises decision/control traceability, not full row-level recalculation.

## Raw and quarantine

- Raw delivered payloads follow the 24-month analytical schedule because Sprint 1 maps the approved history to raw and curated layers.
- Quarantined row payloads follow the same 24-month business/event anchor unless a narrower approved hold scope applies.
- Seven-year quality logs retain reason, counts, amounts, tokens and disposition, not the quarantined payload.
- Temporary processing files are deleted within 7 days after a successful or terminal failed run, subject to a hold.

## Temporary outputs

- Server-side export files expire within 24 hours after creation; the audit event remains seven years.
- Temporary restore copies expire within 7 days after restore validation.
- Rebuildable dashboard caches expire within 24 hours and cannot outlive their underlying source publication.
- Copies downloaded by users are outside system-controlled storage but remain governed by export policy and classification.

## Corrections and expired periods

- Corrections within the retained analytical window create controlled revised versions and preserve original lineage.
- A correction received after detailed analytical data has expired does not automatically recreate the expired reporting period.
- Record the late correction and its audit impact; any exceptional historical rehydration requires Compliance, Data Owner and applicable business-owner approval plus available valid source evidence.
- The DD-06 RC-01 90-day recalculation applies only where the affected analytical dates remain retained.
- A last-successful publication cannot be served after its underlying detail expires; display Data unavailable until a valid retained publication exists.

## Backups

- Use encrypted daily backups with a rolling 35-day expiry.
- Backup copies, replicas, snapshots and transaction logs may delay total physical deletion by no more than 35 days after live-store expiry.
- Do not refresh or recopy backups to extend expired data indefinitely.
- Restore into an isolated environment.
- Before restored data becomes accessible, reapply purge/deletion records, current entitlement revocations and active holds.
- Validate that expired records cannot appear in reports, APIs or exports.
- Delete temporary recovery copies within 7 days and record restore validation.
- Holds apply only to identified backup scope; one held record does not justify indefinite retention of every backup.

## Hold governance

- Compliance and an independent Data Owner approve holds. Add designated Legal approval if a real legal obligation applies.
- The requester cannot solely approve or release their hold.
- Record hold ID, reason, categories/records, date range, systems, dependency scope, backup scope, effective time, approvers and evidence.
- Review active holds quarterly and escalate overdue reviews.
- Release requires independent Compliance and Data Owner approval with reason and time.
- A hold suspends disposal only for its defined scope. It does not grant access or bypass DD-08/DD-09 controls.

## Disposal

- Compliance and an independent Data Owner approve disposal batches.
- Administrator executes the approved purge but cannot approve it or alter approval evidence.
- Use the dependency-aware purge sequence documented in the DD-10 review: outputs/memberships, evidence children, analytical parents, retired dimensions/relationships, raw/quarantine payloads, then expired audit dependency groups.
- Handle publication/candidate/run cycles as reviewed dependency groups rather than uncontrolled cascades.
- Verify surviving references, counts, hold exclusions, token mappings and backup obligations after every purge.
- Retain sanitized disposal evidence for seven years from the disposal decision.

## DD-11 and DD-12

- DD-11 approves payment/schedule original-anchor application. DD-12 branch-history application is approved.
- Do not invent payment or historical-branch rules to complete DD-10.

## Narrow DD-08 lifecycle refinement: controlled disposal

- Compliance and an independent Data Owner define and approve the exact disposal scope.
- The retention engine determines eligibility from the approved schedule, holds and dependencies.
- Administrator may initiate or operate the approved disposal job but cannot add records, expand scope, shorten retention or independently select evidence.
- Every item must be expired, unheld and dependency-cleared. Recheck against the approved scope and current holds/dependencies at execution; prior eligibility alone is insufficient.
- Administrator cannot alter approval content, timestamps, reviewers, reasons, retention anchors, hold state or disposal evidence. Manual or discretionary deletion of approval evidence remains prohibited.
- Failed eligibility, scope mismatch or active hold stops deletion for the affected item and records failure. No silent skipped approval or cascade bypass.
- The job records approved batch ID, approvers, executor, ruleset version, start/end time, eligible/deleted/skipped/failed counts, item-category totals, hold/dependency exclusions and verification results. Eligibility count is a measured subset, not an additional disjoint outcome bucket; deleted/skipped/failed outcomes are mutually exclusive per terminal item.
- Disposal evidence starts its own seven-year retention from the disposal decision. The current job cannot dispose of its own newly created evidence.
- Backup expiry follows the bounded lag and cannot restore disposed evidence into accessible service.

## Logical enforcement and reference migration

The [authoritative inventory](field-level-dictionary.md) contains the only field contracts. Every scheduled logical item/copy has a retention binding to its original anchor and schedule version. Approval scopes, holds and disposal members are structured children, not serialized sensitive text. An engine-created eligibility result is not business approval; independent reviewers approve exact batch scope before execution.

DD-10 explicitly refines DD-07's live-parent-only audit-reference contract: live analytical FKs still require existing parents. Surviving minimized audit links instead resolve an existing provenance_envelope after payload expiry, with PAYLOAD_EXPIRED and deletion evidence. They must not resolve a nonexistent business parent or silently null a mandatory link. This applies to typed owners, source locators, correction/customer links and scope references, not just scalar FKs. Required pre-expiry data and lineage are validated before any migration. Preserve the immutable historical decision and append lifecycle evidence; do not rewrite approval content.

An opaque token is not proof of anonymization. Separate reversible mappings remain Restricted, must have a valid analytical/audit/hold dependency, and are removed when none remains. The current-master exception does not retain obsolete identity values/narratives indefinitely. Minimized tombstones survive only for their dependent audit/hold purpose and disposal evidence schedule, not as an invented perpetual business archive.

Monthly eligibility does not mean reporting availability beyond the rolling window. Distinguish anniversary expiry, monthly live-store purge and final backup expiry in evidence. Backups/replicas/logs must meet the 35-day maximum from live-store expiry; archive movement, copying or a late purge cannot reset that deadline. Any inability to satisfy both deadlines is a recorded failure, not a silent extension. Holds affect only their approved scope.

## Dependencies and future verification

DD-11 payment schedules are approved; DD-12 branch-history schedules now follow approved DD-12 semantics. Source contract facts, named independent appointments, physical storage/job configuration and actual evidence remain Pending confirmation. Calendar anniversary edge cases (for example February 29), exact monthly job timing and operational escalation routing must be documented before execution without shortening the approved through-anniversary periods. These are implementation/contract prerequisites, not unapproved replacement retention periods.

Future AR-02/ST-07 and relevant security/integrity checks: through-anniversary boundaries; no clock restart; current/closed dependency rules; 75-entity coverage plus new lifecycle entities; payload-to-envelope transitions; minimized rejected/denied evidence; quarterly holds; exact disposal scope and per-item execution checks; seven-year disposal evidence; 35-day backup bound; isolated restore with revocation/deletion reapplication; Data unavailable after underlying publication expiry. All remain planned, not executed runtime or acceptance tests.


## DD-12 lifecycle application

Effective organizational and assignment versions remain while active/required, then 24 months after original effective end or until no retained analytical child depends, whichever later. Correction does not reset the original end anchor. Attribution/membership follows underlying original analytical dates. Successor access mapping is approved configuration with dependent-audit retention; scope-resolution evidence is minimized seven-year decision audit. Stable identities persist only while active or required by retained versions/references; nonreuse remains enforceable through minimized provenance. Holds, approved disposal, backup expiry and explicit audit envelopes remain unchanged.

## Complete authoritative entity schedule

A24 means reporting for the complete rolling 24-month window, retained through the original Chicago-date anniversary and eligible for the next monthly purge afterward. A7 means minimized audit searchable within one business day through the seventh UTC anniversary, then next monthly purge. CURRENT and CONFIG exceptions are defined in the policy above; they do not restart original analytical clocks. All schedules remain subject to exact holds/dependencies and approved disposal. A child cannot force longer raw/Restricted retention merely through a seven-year audit FK: migrate permitted surviving audit to the envelope contract.

For every category below: archives are part of total possession and follow the same expiry; no archive-clock reset. Purge is dependency-aware after approval, with Restricted mappings evaluated separately; no unapproved anonymized dataset is retained instead of disposal. Backup copies have the bounded 35-day lag and isolated-restore controls. Holds suspend disposal only for the approved record/dependency/backup scope. References resolve live parents or the explicit DD-10 audit-envelope alternative, never dangling. These are approved schedules, not executed disposal results.

| Category | Inventory entities | Classification / purpose | Approved schedule and anchor |
| --- | --- | --- | --- |
| Current effective state | `organizational_unit`, `region`, `organizational_successor`, `account_branch_assignment`, `loan_branch_assignment`, `complaint_branch_assignment`, `branch`, `customer_version`, `account_customer`, `loan_customer`, `customer`, `customer_identity`, `account`, `loan`, `fraud_alert`, `complaint`, `investigation_case` | Controlled/Restricted as inventory; current business purpose | CURRENT: while active and required; after closure/retirement/effective end 24 months or until no retained analytical child depends, whichever later. Preserve earlier intersecting versions; no indefinite obsolete aliases/narratives. |
| Loan schedule and allocation history | `loan_schedule`, `loan_obligation`, `payment_allocation`, `payment_unapplied`, `payment_transaction_link` | Controlled; contractual and payment evidence | A24 from original obligation/effective dates; retain effective versions intersecting the window and necessary analytical dependencies. Rescheduling/correction does not reset clocks; due_date changes preserve original_obligation_date. |
| Loan reporting relationship | `loan_account` | Controlled; effective reporting account | CURRENT while active/required, then 24 months after effective end or until retained analytical children no longer depend, whichever later; preserve original effective anchor and intersecting history. |
| Financial events | `transaction`, `loan_payment`, `payment_adjustment` | Controlled; Restricted transaction identity fields | A24: original event/business date in Chicago; original/corrected versions same clock. DD-11 payment event anchors apply; corrections/adjustments do not reset the original payment clock. |
| Snapshots and state history | `loan_snapshot`, `complaint_snapshot`, `complaint_history_event`, `account_restriction_state`, `fraud_alert_state`, `historical_coverage` | Controlled; as-of history | A24: original snapshot/business/event date; effective states intersect retained window. Branch-history application conditional on DD-12. |
| Risk and investigation evidence | `risk_assessment`, `risk_evidence`, `risk_evidence_item`, `rc01_comparison`, `rc01_investigation_projection`, `case_evidence_link` | Controlled; raw RC-01 and case links Restricted | A24: assessment/event/business anchor; projection/link cannot outlive underlying evidence; no extra warm-up. |
| Analytical membership | `loan_snapshot_publication`, `complaint_snapshot_publication`, `transaction_publication`, `loan_payment_publication`, `loan_contract_publication`, `organization_publication`, `branch_attribution` | Controlled; selected analytical versions | A24: original member business/event date, not republication date; DD-11 membership follows the original selected entity anchor. |
| Business configuration | `catalog_version`, `rule_version`, `configuration_version`, `rule_config`, `catalog_rule`, `mapping_version`, `mapping_entry`, `mapping_eligibility`, `date_dimension` | Configuration; Audit except Controlled rule_config | CONFIG: while active and until seven years after last retained dependent audit decision; child definitions follow parent; non-sensitive calendar remains while needed. |
| Source/mapping lineage | `applied_mapping`, `source_reference` | Audit with inherited payload sensitivity | SPLIT: payload/alias locators A24 or CURRENT; minimized envelopes/associations A7 from dependent audit event/decision, preserving dependencies. |
| Pipeline/manifests | `pipeline_run`, `source_extract`, `run_extract` | Audit; processing and source metadata | A7: UTC processing/audit event timestamp; delivery metadata audit event. Raw files remain A24. |
| Quality/reconciliation | `quality_exception`, `reconciliation_result`, `control_population`, `population_member`, `source_financial_control` | Audit; controls and findings | A7: UTC finding/control/decision timestamp; child population definitions follow retained control; no raw row payload. |
| Exports | `export_event`, `export_filter`, `export_entitlement`, `export_approval` | Audit; export accountability | A7: completed/denied attempt UTC timestamp, including denials; sanitized children follow event, not output-file lifespan. |
| Correction decisions | `recalculation_impact`, `recalculation_customer` | Audit; correction scope | A7: UTC correction decision; customer detail becomes envelope/token when shorter-lived payload expires. |
| Access configuration and decisions | `access_policy`, `access_entitlement`, `entitlement_scope`, `successor_scope_mapping` | Audit/configuration; authorization | Active policy CONFIG; entitlement decisions A7 from UTC decision with effective/revoked state retained; scope children follow parent, sensitive subjects use envelope alternative. |
| Governance approvals | `governance_action`, `governance_review` | Audit; independent approvals/rejections | A7: UTC action/review decision, including rejected identity/access decisions; restricted supplied payload follows A24/CURRENT, not seven-year audit. |
| Gate definitions | `gate_ruleset`, `gate_rule` | Audit/configuration; gate interpretation | CONFIG: while active and until seven years after last retained dependent audit decision. |
| Publication/candidate metadata | `publication`, `publication_candidate`, `candidate_source`, `candidate_control`, `candidate_population`, `candidate_coverage`, `candidate_evidence` | Audit; publication lineage and gate evidence | A7: UTC candidate/control/publication decision; metadata/supersession preserved independently of A24 membership; missing candidate outcome never fabricated. |
| Exclusion decisions | `quality_exclusion`, `exclusion_record`, `exclusion_impact` | Audit; bounded exclusion evidence | A7: UTC exclusion decision; exact record accountability via opaque tokens/envelopes, not retained raw rows. |
| Release decisions | `publication_decision`, `decision_participant` | Audit; approval and execution history | A7: UTC publication decision; participants/reviews remain evidence, not business access grants. |
| Notifications | `publication_notification`, `notification_recipient` | Audit; delivery/acknowledgment evidence | A7: UTC notification/acknowledgment event; no restricted content. |
| Retention definitions and item registry | `retention_schedule`, `retention_item` | Audit/configuration; approved schedules and anchors | Schedules CONFIG; item registry A7 for lifecycle decision evidence plus valid dependencies; no identity payload. |
| Provenance envelopes | `provenance_envelope`, `lifecycle_reference` | Audit; minimized expired-record provenance | A7: governing audit/disposal event or decision with surviving dependency protection; PAYLOAD_EXPIRED after payload expiry, not perpetual raw retention. |
| Reversible mapping | `restricted_token_mapping` | Restricted; necessary token reversal | Only while valid analytical/audit/hold dependency requires mapping; remove once none remains; approved hold scope respected. |
| Holds | `retention_hold`, `hold_scope`, `hold_review` | Audit; scoped preservation approvals | A7: each UTC hold/review/release decision with active-hold dependency protection; quarterly review; release does not restart payload clock. |
| Disposal evidence | `disposal_batch`, `disposal_scope`, `disposal_job`, `disposal_item`, `disposal_category_total` | Audit; exact authorized disposal and verification | A7: disposal decision UTC timestamp; its own seven-year period, never removed in the job creating it. |
| Backup/restore evidence | `backup_copy`, `restore_validation` | Audit; copy and recovery control metadata | A7: backup/restore audit event or validation decision; actual encrypted copies expire in 35 days, temporary restored copies within 7 days after validation. |
| Denied access attempts | `access_attempt`, `scope_resolution` | Audit; sanitized access denial | A7: UTC attempt decision; no sensitive requested values. |

Raw/quarantine delivered payloads: A24 on original business/event anchor, distinct from A7 manifests/findings. Temporary processing files: within 7 days after successful or terminal failed run, subject to scoped hold. Server-side exports: within 24 hours of creation; downloaded user copies outside system control still follow export policy/classification. Dashboard caches: within 24 hours and never beyond underlying publication. Analytical/report/risk projections: no longer than underlying evidence. Temporary restore copies: within 7 days after validation. These storage categories do not add invented banking entities or authorize physical storage.
