# DD-04 customer-risk catalog and classification

Status: DD-04 policy **Approved by user 2026-09-15**. Physical/field representations are Draft — not approved. DD-05 comparison/attribution is approved; DD-06 canonical groups and daily current-transaction population are approved; source aliases must be finalized before publication. G3 and implementation are not approved.

## Approval basis and baseline compatibility

Evidence: the user supplied RC-01 through RC-05 and classification policy, then explicitly corrected RC-03 to DPD > 30 and instructed application of the catalog. The correction aligns RC-03 with Planning loan-delinquency KPIs and Sprint 1 US-04. At exactly 30 DPD a loan does not satisfy RC-03. A customer's condition is Not triggered only when no other related active loan satisfies it and all required evidence is complete and valid.

Only RC-01 and its 3x/90-day basis are inherited from the approved baseline. RC-02 through RC-05 and Unknown/incomplete-evidence handling are approved Sprint 2 design decisions. The at-least-two-Triggered requirement remains inherited from Planning FR-07 and US-06; incomplete evidence refines the BA flow without changing that threshold. No earlier baseline document is amended or retroactively credited with these new rules.

Namespace: RC-01 through RC-05 in this document are risk condition IDs. Sprint 1 also uses RC-01 as a reconciliation test ID; refer to "risk condition RC-01" versus "reconciliation test RC-01" explicitly.

## Approved catalog

T denotes the assessment instant. All inputs must be valid for the applicable as-of date/time and selected publication; current values cannot be projected backward. Non-additive effective owner/co-borrower relationships follow DD-02. Shared relationship membership is not proof of who initiated activity.

| Risk condition | Triggered | Not triggered | Unknown / dependencies |
| --- | --- | --- | --- |
| RC-01 Unusual transaction | At least one eligible transaction is >= 3 times the customer's preceding 90-day eligible average | Complete valid eligible evaluation population with no qualifying transaction | Approved DD-05 requires full 90-day window, >=5 eligible priors, same currency and resolved initiator/sole owner; missing evidence is Unknown; daily occurred_at population approved in DD-06 |
| RC-02 Significant active fraud alert | At least one open fraud alert has severity included in the approved significant-severity mapping as of T | Complete valid alert population and approved open/severity mappings with no qualifying alert | Missing/unapproved canonical open or significant-severity mapping, unresolved attribution, or evidence insufficient to evaluate existence |
| RC-03 Material loan delinquency | At least one customer-related active loan has DPD > 30 in the daily loan-position snapshot | Complete valid loan/relationship/snapshot evidence and approved active mapping, with no related active loan above 30 DPD | Missing/unapproved active mapping, unavailable daily snapshot or incomplete relationship/evaluation evidence |
| RC-04 Complaint SLA breach | At least one complaint is open as of T and has exceeded its approved SLA | Complete valid population, approved open/priority mappings and SLA semantics, with no qualifying open breach | Missing/unapproved mappings, missing as-of complaint state, or unresolved DD-06 clock/population semantics |
| RC-05 Restricted account relationship | At least one related account has a current risk-restriction status included in the approved restricted-status mapping | Complete valid related-account status population and approved restricted mapping, with no qualifying restriction | Missing/unapproved restricted mapping, missing as-of restriction state or incomplete relationship/evaluation evidence |

Status-dependent conditions remain Unknown until their canonical mappings are approved under DD-06. Do not invent significant severities, open/active codes or restricted statuses. An absence of rows proves Not triggered only with complete, valid population evidence; missing data is not an empty population. If an approved/evaluable existential rule has a valid qualifying witness, it is Triggered; absent a valid witness and complete evidence it is Unknown. Mapping prerequisites still apply even when a raw label appears to qualify.

## Inputs, thresholds and observation logic

| Condition | Required source and proposed entity fields | Threshold/window and attribution |
| --- | --- | --- |
| RC-01 | Core transactions: transaction/account keys, occurred_at, signed amount, absolute comparison amount, currency, canonical status, and initiating-customer identifier when supplied; effective account_customer roles/intervals; identity crosswalk; rule configuration | Trigger when the current eligible absolute amount is at least 3× the preceding 90-day eligible average within the same currency, using `[event timestamp − 90 days, event timestamp)`, a complete window, and at least 5 eligible prior transactions. Attribute first to a valid mapped source initiator; only if no initiator is supplied, use the sole distinct effective owner. A supplied invalid/unmapped initiator yields Unknown and an identity/data-quality exception without fallback. For a joint account with no supplied initiator, retain evidence at transaction/account grain and set individual RC-01 results to `Unknown` with reason `JOINT_ACCOUNT_INITIATOR_UNRESOLVED`. Do not attribute initiation to all owners. DD-05 governs eligibility, status exclusions, evidence sufficiency, recalculation, and lineage. |
| RC-02 | Fraud alerts: alert/customer keys, alert_time, case_status, severity; source state version/as_of evidence; customer crosswalk; mapping version | Existence (>=1) of an open significant alert at T; no historical lookback count introduced. Use resolved source customer, not every customer sharing a transaction account |
| RC-03 | Loan positions: loan_key, business_date, days_past_due, status, snapshot/source/publication versions; loan_customer customer/role/effective intervals | Existence (>=1), DPD > 30, active at selected daily position. All effective borrowers/co-borrowers; do not sum DPD or allocate balances. DD-03 unavailable-history rules apply |
| RC-04 | CRM complaint state: complaint/customer keys, created_at, closed_at, status, priority, business_date, as-of/source/publication evidence; SLA/mapping versions | Existence (>=1), open at T and elapsed SLA strictly exceeded. Existing priority SLA values 4/24/72/120 hours remain unchanged; DD-06 calendar-clock/no-pause and open/closed semantics apply. Resolve complaint's source customer |
| RC-05 | Core account restriction state: account_key, risk_restriction_status, effective/state-as-of time, source version; account_customer roles/intervals | Existence (>=1) of a mapped restriction current at T. All effective related owners; never use today's restriction for a past T |

For daily sources, do not claim an intraday state newer than evidenced cutoff. Exact cutoff conventions and late-source tolerance remain source-contract/DD-09 details. Retain missing/late-state reasons and original publication lineage. Re-evaluation after validated late/corrected input creates traceable versioned evidence; do not silently rewrite prior results. Publication blocking is separate from per-customer classification and follows approved DD-09 gates.

## Approved classification policy (ordered)

Let t = number of Triggered conditions and u = number of Unknown conditions among the five distinct conditions.

| Priority | Predicate | Classification |
| --- | --- | --- |
| 1 | Missing rule catalog or rule version | Classification unavailable |
| 2 | Valid catalog/version and t >= 2 | Provisional high risk, even if u > 0 |
| 3 | Valid catalog/version, t < 2 and t + u >= 2 | Incomplete evidence — classification unavailable |
| 4 | Valid catalog/version, t < 2 and t + u < 2 | Not high risk under current rule |

Unknown is never converted into Not triggered. All five conditions need defined catalog entries, but all five need not be evaluable. Keep the evidence completeness flag independently from classification: a customer may be provisionally high risk with incomplete evidence, or not high risk with one Unknown when the maximum possible triggered count remains below two. Count conditions, not qualifying records: many alerts still contribute only one Triggered condition.

Illustrative policy checks (not executed business tests): t=2,u=3 -> Provisional high risk; t=1,u=1 -> Incomplete evidence; t=0,u=1 -> Not high risk; t=0,u=2 -> Incomplete evidence; missing version overrides any counts. RC-03 DPD=30 does not qualify; DPD=31 qualifies for an active related loan with valid mappings/evidence.

## Versioning and evidence design

Version every rule and retain a catalog version identifying all five rule versions, effective intervals and approval references. Preserve thresholds, mapping versions, condition state, observed values, source references, missing-evidence reasons and assessment lineage. Existing rule_config/assessment fields are extended in the dictionary; exact storage is proposed, not implemented.

Keep one condition outcome per assessment/condition, plus proposed child evidence references for multiple qualifying records. Record assessment T/business_date, rule/catalog versions, run, source batch/revision/version, publication and correction lineage. Do not overwrite earlier decisions when a rule or mapping changes. A missing catalog/version yields an unavailable assessment attempt with the missing reason rather than an invented version.

Retention: risk assessments/evidence fall under the documented 24-month analytics design unless separately approved; seven-year pipeline/quality/export audit is not automatically a seven-year retention approval for all risk evidence. DD-10 now defines the approved lifecycle schedule and expired-reference rules. Restricted source pointers and missing reasons must not leak raw sensitive payloads.

## Related documents

- [Field contracts](field-level-dictionary.md)
- [KPI mappings](kpi-to-data-mappings.md)
- [Quality controls](data-quality-and-reconciliation.md)
- [Decision traceability](design-traceability-and-review.md)
- [Approval evidence](../../04-monitoring-and-control/sprint-02-control-record.md)

## DD-05 approved RC-01 comparison policy - 2026-09-15

DD-05 is approved by the user. It supersedes DD-04 all-effective-owner attribution for RC-01 only. DD-02 effective-dated non-additive relationship exposure and RC-02 through RC-05 attribution are unchanged. Ownership exposure and transaction initiation are separate concepts.

### Eligibility, window and comparison

Use [transaction timestamp minus 90 calendar days, transaction timestamp). Exclude the current transaction, every event at the same timestamp and future evidence. Require the complete 90-day window within the approved 24-month dataset and at least 5 eligible prior transactions for the same customer and currency. Do not add warm-up history beyond those 24 months. Missing full-window coverage remains Unknown even if five records exist.

Use only finalized transactions under the approved canonical status mapping; exclude pending, declined, cancelled, voided and reversed transactions. Apply these eligibility rules to both current and prior transactions. Compare absolute nonzero monetary amounts while preserving source signed amount and debit/credit direction for audit. Compare only within the same currency; no Release 1 currency conversion. Unknown/unmapped currency or status cannot be treated as eligible or a negative finding. DD-06 canonical groups are approved; versioned source mappings must be finalized before publication.

For a current eligible transaction with complete valid evidence: absolute current amount >= 3 x mean(absolute eligible prior amounts) is Triggered; below that threshold is Not triggered. Unknown applies when the window is incomplete, fewer than 5 eligible prior transactions exist, prior average is zero, currency/status is unmapped, source evidence is missing or attribution is unresolved. Known excluded transactions do not create a Triggered or negative eligible comparison. A zero average is an explicit Unknown guard even though valid nonzero absolute prior amounts should yield a positive average.

### Attribution hierarchy (current and prior activity)

1. Use a valid mapped source initiating-customer identifier when supplied.
2. If the identifier is absent and exactly one distinct effective owner exists at the transaction timestamp, use that owner.
3. If it is absent and multiple distinct effective owners exist, preserve the flag/evidence at transaction/account grain and set individual RC-01 results to Unknown with reason `JOINT_ACCOUNT_INITIATOR_UNRESOLVED`.
4. If supplied but invalid/unmapped, produce Unknown and an identity/data-quality exception. Do not fall back to the sole owner or all owners.
5. If no owner or valid initiator can be resolved, retain Unknown with the missing attribution reason. Never infer that every joint owner initiated the transaction.

Deduplicate overlapping relationship records and multiple role paths before counting distinct owners or events. Preserve conflicting relationship findings for review. A mapped initiator does not grant report access or change ownership exposure. Unattributed joint activity must not contaminate a customer's preceding average. Transaction/account evidence retention does not authorize inventing a customer comparator when none can be resolved.

### Corrections, evidence and customer aggregation

Late/corrected evidence requires controlled recalculation and a new revision. Preserve old results, source versions and publication lineage. Later evidence may correct an earlier state only with valid as-of support; future activity must never enter the earlier window.

Retain history count, prior average, current absolute amount, signed amount/direction, multiplier, window boundaries, currency, eligibility/status mapping version, attribution method, missing-evidence reason and source lineage. Retain rule version, assessment time, recalculation revision and publication/correction references. DD-07 logical contracts are consolidated in the [authoritative inventory](field-level-dictionary.md); physical storage is deferred.

DD-04's condition and final-classification policy remains in force. An unresolved joint event cannot itself trigger an individual's condition. A separate valid qualifying event may establish the existential RC-01 trigger; unknown events remain in evidence. A customer-level negative requires complete valid evaluation evidence. DD-06 selects current events by occurred_at business date in the selected successful publication, with manifest-confirmed zero-event handling and controlled recalculation through the following 90 days. The preceding-average window remains DD-05.

## DD-06 approved mappings and daily evaluation

See [DD-06 policy](kpi-policy-dd06.md). Significant severity = HIGH/CRITICAL; restricted states = RESTRICTED/FROZEN/BLOCKED. Active loan groups = ACTIVE/DELINQUENT_ACTIVE/FORBEARANCE_ACTIVE. Unmapped values remain Unknown; exact source aliases and open-state mappings must be finalized before publication. RC-04 uses original creation, creation priority, elapsed calendar hours without pauses and open-as-of state; REOPENED continues the original clock. RC-01 selects occurred_at business-date events from the selected successful revision; one valid attributable trigger suffices, complete no-trigger evidence is Not triggered, manifest-confirmed zero events can be Not triggered, missing/incomplete delivery is Unknown. Corrected events trigger affected-customer recalculation from event date through following 90 days. DD-04 final classification and DD-05 initiation hierarchy are unchanged.

## DD-07 logical contracts - 2026-09-16

DD-07 uses one risk_evidence row per assessment/condition with deduplicated risk_evidence_item children and transaction/account rc01_comparison evidence. window_end is the current event instant. Exact prior sum/count preserves the unrounded mean; no rounded comparison. Missing rule/catalog versions are permitted only on an unavailable attempt with reason, not a published evaluated classification. Existing DD-04 classification and DD-05 attribution remain unchanged. See the [authoritative inventory](field-level-dictionary.md).

## DD-08 coordination - 2026-09-16

Catalog/threshold changes require joint Risk Manager and Compliance approval. Assigned Fraud/Risk Analysts receive only the sanitized RC-01 investigation projection for an authorized case; raw RC-01 evidence and source references remain Restricted. This preserves DD-07 exact comparison and DD-05 attribution. See [approved policy](security-and-masking-design.md) and [authoritative inventory](field-level-dictionary.md).

## DD-09 approved coordination - 2026-09-16

Legitimate customer-level Unknown/unavailable results may publish only when correctly calculated, noncritical, disclosed through coverage and all DD-09 gates pass. Missing catalog/rule version or unavailable required configuration is CRITICAL and blocks the atomic candidate; the unavailable assessment attempt remains auditable. Required unmapped KPI/risk domains follow DQ-D06 escalation. DD-04 classification and DD-05 attribution/window remain unchanged. Risk Manager and Compliance jointly approve rule/configuration corrections; corrected publication also requires Data Owner validation, applicable business/source review and independent Data Publication Approver approval. Corrected RC-01 evidence retains affected former/corrected customers and event-date-through-next-90-days recalculation. See [approved quality policy](data-quality-and-reconciliation.md) and [authoritative inventory](field-level-dictionary.md).

## DD-10 approved lifecycle coordination - 2026-09-16

Raw RC-01 and other risk assessment/evidence payloads remain on the 24-month original assessment/event schedule. Investigation projections cannot outlive evidence; no added warm-up history. Missing-window Unknown behavior remains unchanged. Seven-year correction/decision traceability uses minimized tokens/envelopes; full row recalculation is not promised after raw expiry. RC-01 following-90-day corrections are limited to retained dates. See [retention and disposal policy](retention-and-disposal-design.md) and [authoritative inventory](field-level-dictionary.md).

## DD-12 approved coordination - 2026-09-16

[DD-12 approved policy](historical-branch-attribution-policy.md). Earlier dated dependency notes retain historical status; DD-12 logical policy is now approved, actual source coverage remains unverified.

RC-01 uses transaction branch. RC-02 uses approved supplied alert branch, otherwise valid linked transaction branch, otherwise Unavailable. RC-03 uses qualifying loan snapshot; RC-04 qualifying complaint as-of; RC-05 restricted account SERVICING at assessment time. Each observation retains its own branch; condition counts are not multiplied. Customer home history is separate: K07 branch/region uses assessment-date home branch; missing home does not remove enterprise high-risk customers. Case authorization and sanitized RC-01 projection restrictions remain unchanged. Corrected intervals recalculate retained affected evidence/projections through controlled publication.
