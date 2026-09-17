# DD-06 approved KPI and canonical mapping policy

Approved by user; recorded 2026-09-16, including the K06 clarification. Source-specific aliases remain versioned contract details to finalize before publication. Physical representations remain Draft — not approved. G3 and implementation remain unapproved.

## Time, comparison and reporting

Use America/Chicago and half-open periods [start, end). Missing populations and zero denominators display Unavailable. A confirmed valid empty population is distinct from a missing delivery; RC-01's zero-event rule is below. Recompute ratios from filtered numerators and denominators, never average branch rates. Custom periods compare with immediately preceding equal-length periods. Complete calendar months/quarters compare with the preceding complete calendar period. Stock measures compare with the preceding comparable as-of position, never sums across dates. Rate changes are percentage points. Use one explicitly selected successful publication version per report. Label any risk rule-version change in comparisons.

## Canonical transaction policy

| Canonical status | Processed / K01 | K02 numerator | K03 numerator | K02/K03/K04 denominator |
| --- | --- | --- | --- | --- |
| SUCCESSFUL | Yes | Yes | No | Yes |
| POSTED | Yes | Yes | No | Yes |
| FAILED | Yes | No | Yes | Yes |
| DECLINED | Yes | No | Yes | Yes |
| CANCELLED | Yes; separately reportable | No | No | No |
| VOIDED | Yes; separately reportable | No | No | No |
| REVERSED | Yes; separately reportable | No | No | No |
| PENDING | No | No | No | No |

Processed means a terminal outcome. K04 uses the same four-status eligible population and counts distinct transactions with at least one linked fraud alert; multiple alerts count once. Unlinked alerts cannot enter its numerator. Do not silently force unmapped source values into a listed status. Versioned source-to-canonical mappings must be finalized before publication.

DD-05 RC-01 finalized eligibility remains separate from the K02/K03 denominator: DECLINED remains excluded from RC-01 even though it belongs in that denominator. The precise source mapping of finalized-for-RC-01 is a versioned contract detail; do not assume FAILED is eligible merely because it is terminal.

## Loans and K06 data quality

Canonical groups: ACTIVE, DELINQUENT_ACTIVE, FORBEARANCE_ACTIVE, PAID_OFF, CLOSED, CHARGED_OFF, UNKNOWN. The active set for K05 and active-loan risk condition RC-03 is ACTIVE, DELINQUENT_ACTIVE, FORBEARANCE_ACTIVE. K05 numerator additionally requires DPD > 30; its denominator is all active loans. UNKNOWN is not evidence of an active or inactive state; affected risk evidence is Unknown and publication completeness follows DD-09.

**K06 approved formula is preserved exactly: Outstanding Delinquent Balance is the sum of outstanding principal for loans with DPD > 30.** Do not add outstanding_principal > 0 as a population criterion or inherit K05's active-only filter. Disclose status composition and keep currencies separate.

| Principal evidence | Separate quality disposition |
| --- | --- |
| Positive | Valid; included for DPD > 30 |
| Zero | Valid; contributes zero for DPD > 30 |
| Negative | Invalid; quarantine from published K06; record quality exception |
| Missing | Exclude as incomplete evidence; apply DD-09 publication controls |

Retain raw principal, source identity/version, batch/revision, publication lineage, exception reason and reconciliation impact. Proposed reason codes: PRINCIPAL_NEGATIVE and PRINCIPAL_MISSING (spellings are draft). Missing principal is not zero; a missing amount cannot produce a fabricated reconciled total. Negative values remain visible in raw/quarantine controls, not erased or converted to absolute values. DD-09 now blocks the candidate for negative/missing principal on DPD > 30 loans until valid evidence is supplied; no misleading partial K06 is authorized.

## Complaint policy

Use elapsed calendar hours, no pauses. Start at original created_at. Open complaints use selected as-of time; closed complaints use closed_at. Priority at creation determines the Release 1 SLA: Critical 4h, High 24h, Medium 72h, Low 120h. Breach requires elapsed hours strictly greater than the threshold.

REOPENED returns to the open population and continues the original clock without reset. The reopened as-of state has no current closure timestamp; retain prior closure events in history. K08 selects finally closed complaints by final closure date and measures original creation to final closure, as known in the selected publication. Do not use a future closure to classify an earlier state. K09 counts complaints open as-of with no closure timestamp, preserving the baseline non-Closed-status predicate. K10 evaluates eligible open and closed complaints. Contradictory status/closure evidence is quarantined.

Versioned complaint-status mappings must be finalized before publication. CLOSED and REOPENED behavior is defined here; other source status aliases and open/closed mapping membership are contract details, not invented canonical states. Store immutable priority_at_creation separately from changing current priority. No paused-time deduction or business-hours calendar is introduced.

## Canonical risk mappings

- Significant fraud severities: HIGH and CRITICAL.
- Restricted account states: RESTRICTED, FROZEN and BLOCKED.
- Unmapped values produce Unknown, never a negative finding.
- Finalize versioned source aliases, including fraud open-state and complaint open/closed mappings, before publication. A known qualifying severity still needs valid open-alert evidence for RC-02; a known restriction still needs valid relationship/as-of evidence for RC-05.

These sets are not a complete invented account lifecycle or fraud case-status dictionary. Non-significant/non-restricted source values require explicit mappings before they can prove Not triggered.

## RC-01 daily population and revisions

Current transactions are selected by occurred_at business date in America/Chicago using the selected successful publication revision. At least one valid attributable trigger gives Triggered. No trigger with complete valid evidence gives Not triggered. A manifest-confirmed zero-event delivery can give Not triggered; missing/incomplete delivery gives Unknown. Multiple triggering events are child evidence and count once as a condition. DD-05 attribution hierarchy, full preceding 90-calendar-day window, five-prior minimum, amount/status/currency rules remain unchanged for each current eligible comparison. Zero current events do not invent prior history or override unknown events in a nonempty delivery.

Recalculate affected customers from a corrected event date through the following 90 days and publish a new revision. If attribution changes, affected customers include both former and corrected attribution. Preserve original/corrected evidence and publication references. Only evidence valid at the relevant as-of instant can revise that instant; later business activity cannot be copied backward.

## Late data and publication

Preserve original and corrected publications. Publish corrected results only after validation and reconciliation; retain the last successful publication if critical controls fail. Reports select one explicit version, including matching KPI/risk inputs and lineage. Label risk comparisons across rule versions. Exact source lateness allowance remains a source-contract prerequisite; DD-09 resolves correction/release authority and critical-control/exclusion policy; DD-10 logical retention mechanics are approved; physical implementation remains deferred.

## Baseline compatibility

Planning and Sprint 1 remain byte-preserved. Formula names and DPD > 30 boundaries are retained. DD-06 supplies approved populations/status groups, time/comparison/SLA semantics and risk mappings, not claims of earlier baseline detail. The originally suggested positive-principal KPI filter was superseded by the user's explicit K06 formula-preservation and separate quality rules. DD-01 batch lineage, DD-02 non-additive exposure, DD-03 as-of history, DD-04 classification and DD-05 comparison/attribution remain in force.

## DD-07 logical contracts - 2026-09-16

DD-07 supplies the authoritative logical field contracts for this policy. Immutable complaint.created_at is original creation; final closure derives from selected-publication history. Applied mappings, population controls and correction scopes use logical children/version parents. DD-06 formulas, canonical populations and complaint clocks are unchanged. See the [authoritative inventory](field-level-dictionary.md).

## DD-09 approved coordination - 2026-09-16

DD-09 resolves publication gating without changing K06: a DPD > 30 loan with negative or missing principal blocks the candidate until corrected or valid evidence supplied by the approved source. Signed negative evidence remains in raw/quarantine reconciliation; no exclusion or positive-principal filter can disguise incomplete K06. Record/financial controls are exact, currency-separated, with zero unexplained residual. Reports default to latest successful version, preserve explicit historical selection and never mix versions. Blocked candidates retain prior success with date/version/age/stale reason, or Data unavailable if none. Restatements require independent release review and immediate notification evidence. Source cutoff/allowance values and DD-10 mechanics remain pending. See [approved quality policy](data-quality-and-reconciliation.md) and [authoritative inventory](field-level-dictionary.md).

## DD-10 approved lifecycle coordination - 2026-09-16

Original/corrected analytical versions retain their original business/event anchors. DD-06 90-day affected-customer recalculation is limited to retained analytical dates; expired periods are not automatically recreated. Late corrections retain audit impact; rehydration requires Compliance, Data Owner and business-owner approval with valid evidence. Latest-successful reporting cannot serve expired underlying detail. KPI formulas and exact arithmetic remain unchanged. See [retention and disposal policy](retention-and-disposal-design.md) and [authoritative inventory](field-level-dictionary.md).
