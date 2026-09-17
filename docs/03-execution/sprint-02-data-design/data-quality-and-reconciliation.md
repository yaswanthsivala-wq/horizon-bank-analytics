# DD-09 approved quality, reconciliation and publication controls

Current portfolio interpretation (2026-09-16): [G3 prerequisite register](g3-prerequisite-register.md) replaces real-source verification with finalized [synthetic contracts](synthetic-source-contract.md). Logical fields/policies remain approved; physical aliases are proposed until fixture implementation. Review roles are personas, not actual independent organizational approvals. Prior source-evidence prerequisites now mean synthetic contract/specification at G3 and executed fixture validation before publication. G3 remains unapproved.

Approved by the requesting user on 2026-09-16 following pre-edit compatibility review. Evidence: the user's supplied DD-09 policy. Logical design only; G3 and implementation remain **Draft — not approved**. No controls, runs, notifications or releases have been executed.

## Compatibility and authority

No conflict found with Planning, Sprint 1 or DD-01 through DD-08; reported before edits. This resolves deferred criticality, exclusions and publication authority. Planning's >=98% completeness, exact reconciliation, 6:00 a.m. CT target and >=95% on-time test-run target are preserved. K06's DPD > 30 principal sum is unchanged. Legitimate DD-04/DD-05 Unknown results remain distinct from missing mandatory configuration. DD-08 separation-of-duties waivers cannot override a critical failure. Earlier design proposals in this document are superseded by this approved policy.

## Severity model

| Severity | Approved meaning |
| --- | --- |
| CRITICAL | Blocks the affected daily candidate and therefore the atomic publication |
| ERROR | Quarantines invalid rows/evidence; escalates to CRITICAL when reconciliation fails, a required control is unavailable, completeness falls below threshold, or a published KPI/risk result would be misleading |
| WARNING | Valid, usable data with a documented nonblocking limitation; never missing required data, financial imbalance, security failure or unresolved identity |
| INFO | Successful control, verified identical replay or informational observation |

## Approved rule catalog

The common ERROR escalation rule above applies to every ERROR below. Each finding retains its original and effective severity plus escalation reason. All rule dispositions below are approved under DD-09; source-specific aliases and contract values remain pending where unspecified.

| Rule / name | Scope and validation logic | Severity and disposition | Impact / traceability |
| --- | --- | --- | --- |
| DQ-D01 Source presence/checksum | All five sources and required entity sections present; agreed delivered content verifies SHA-256 | CRITICAL; block candidate for missing/corrupt delivery | All reporting; FR-01, US-08.1 |
| DQ-D02 Duplicate/revision conflict | Source-qualified entity keys and source/entity/date/revision content; distinguish identical replay | Conflicting duplicate/revision CRITICAL; verified identical replay INFO and no duplicate facts | Counts, balances and lineage; FR-04/FR-13 |
| DQ-D03 Required-value validity | Required IDs, timestamps, amounts and currency satisfy inventory contracts | ERROR; quarantine row; CRITICAL for unavailable key control, failed reconciliation or completeness below threshold | Required business inputs; FR-04/NFR-02 |
| DQ-D04 Referential integrity/identity | Parents exist; crosswalk unambiguous and Approved; no guessed attribution | ERROR; quarantine; CRITICAL when dependent facts cannot reconcile or coverage falls below threshold | Customer attribution and orphan prevention; FR-03/FR-04 |
| DQ-D05 Dates/effective intervals | Date ordering valid; half-open effective intervals ordered and nonoverlapping for the same business identity | CRITICAL for affected dataset/date, blocking atomic candidate | Historical joins; DD-02/DD-03/DD-07 |
| DQ-D06 Domain mapping | Status/priority/domain maps through approved version | ERROR with Unknown where applicable; CRITICAL for unavailable required KPI/risk mappings or deficient coverage | KPI populations/risk; FR-04/FR-05, DD-04/DD-06 |
| DQ-D07 Amount precision/currency | Exact parsing, approved precision/scale/currency minor units; no silent overflow or rounding | ERROR; quarantine; CRITICAL when financial reconciliation unavailable or nonzero | Monetary KPIs and risk RC-01; DD-05/DD-07 |
| DQ-D08 Masking/normalization | Fixed mask plus final four supported; normalization collision-free | Suppress affected detail and ERROR; CRITICAL if raw sensitive exposure possible or required masked reporting unavailable | FR-11/FR-12; DD-08 |
| DQ-D09 Integer/snapshot integrity | DPD integer 0..36500, nonnegative integer counts, revision >=1; selected entity/date snapshot unique | CRITICAL for affected snapshots/date | K05/K06, complaints/history; DD-03/DD-07 |
| DQ-D10 Completeness | Received and curated applicable required business cells meet >=98% per required source/entity and overall | Below 98% CRITICAL; valid empty is Unavailable/Not applicable, never 100% | NFR-02, US-08.4 |
| DQ-D11 Freshness/required state | Required source state delivered within approved allowance, with valid as-of/history evidence | Missing/stale required state CRITICAL; valid explicitly designed unavailable history is not source failure and must be disclosed | DD-01/DD-03/DD-05; NFR-01 |
| DQ-D12 Complaint consistency | Status/closure agree; original creation/priority retained; REOPENED has no current closure; no future state | ERROR; quarantine; CRITICAL for CRM reconciliation/coverage failure or misleading K08-K10 | DD-03/DD-06/DD-07 |
| DQ-D13 Risk evidence | Required catalog/rule/configuration available; condition/window/threshold/version/source/date evidence and five distinct outcomes consistent | Legitimate customer Unknown may publish only with disclosed coverage and all gates passing; missing catalog/rule version or unavailable required rule configuration CRITICAL | FR-07/FR-08; DD-04-DD-07 |
| RC-D01 Row reconciliation | Received = accepted + quarantined + approved excluded, disjoint; raw count = manifest | Mismatch CRITICAL | FR-13, US-08.3 |
| RC-D02 Financial reconciliation | Signed currency-separated exact controls, no unexplained residual, all required controls available | Mismatch or unavailable required control CRITICAL | NFR-03, US-08.3 |
| RC-D03 Join multiplication | Native-grain counts/balances preserved across ownership/dimension joins | Multiplication CRITICAL | FR-05; DD-02/DD-03 |
| PUB-D01 Critical publication gate | No unresolved effective CRITICAL finding | CRITICAL and publication blocked; no override | Atomic daily version; US-08 |

ID-01 through ID-08 in [identity rules](customer-identity-reconciliation.md) remain applicable: identity ambiguity maps to DQ-D04, normalization/masking to DQ-D08, interval failures to DQ-D05 and duplicate conflicts to DQ-D02. DD-07 field/lineage/typed-reference contracts apply through DQ-D03/DQ-D04/DQ-D07/DQ-D09/DQ-D13 and reconciliation controls. A valid Unknown is not automatically an ERROR or WARNING; record its reason and coverage, and assess the underlying condition under these gates. No invented blanket tolerance is introduced.

## Mandatory sources, freshness and replay

Core Banking, Loan Servicing, Fraud Monitoring, CRM and Branch Reference are all mandatory for each Release 1 daily publication, including their required entity sections. Manifest-confirmed zero-row entities are distinct from missing entities and may be valid. Missing source/entity, corrupt checksum, conflicting same-revision content or stale required delivery blocks publication.

Extract identity is source + entity + business date + revision. SHA-256 verifies the agreed delivered content; retain checksum algorithm, digest encoding and delivered-content encoding/scope metadata. Exact delivered-byte/content contract, source cutoffs and delivery-time allowances remain mandatory source-contract values, Pending confirmation; do not invent them or assume absent values pass. At the 6:00 a.m. America/Chicago publication gate, delivery outside its approved allowance is stale. Required controls with unavailable contract evidence cannot pass.

Verified identical replay is INFO and retains the same accepted fact versions; processing attempts retain separate run evidence. Corrected delivery uses a new controlled revision with old/new lineage, validation and reconciliation. No silent overwrite, duplicate facts or inferred deletes from an absent snapshot row; deletion semantics remain source-contract dependencies.

## Completeness populations and formulas

For each required source/entity and overall, measure received and curated completeness separately across applicable required business fields. Each nonempty applicable population must reach >=98%. The threshold originates in Planning NFR-02 and Sprint 1 DQ-04; DD-09 approves the per-source/entity and overall publication gates. Report field-level supporting counts as well.

Let R_s be applicable required business cells and P_s their present cells at stage s:

- Received completeness = 100 * P_received / R_received.
- Curated completeness = 100 * P_curated / R_curated.
- Post-exclusion received completeness = 100 * (P_received - P_excluded) / (R_received - R_excluded), with P_excluded/R_excluded taken from the same identified received population. This supplementary measure never replaces received completeness or its gate.
- Zero applicable denominator for a confirmed valid empty population is Unavailable/Not applicable, not 100%. Missing source is CRITICAL absence, never a valid empty denominator. Exact numerator/denominator evidence prevents rounded percentages from turning a value below 98% into a pass; retain DD-07 precision rules.

Required inventory business fields count when applicable; conditional fields only when their documented condition applies. Optional fields do not count merely because they exist. Generated technical IDs and runtime audit fields are excluded from source-business completeness. Blank/whitespace values are missing. Invalid nonblank values are measured separately for validity and fail applicable rules. Quarantined rows remain in received completeness; quality exclusions also remain visible in that denominator. Do not declare a field inapplicable merely because evidence to determine its condition is invalid or missing; retain the unresolved applicability/control reason, without fabricating counts or a pass.

A row can have several findings but exactly one final disposition. Overall counts aggregate the comparable source/entity cell populations, not an unweighted average of percentages. An empty curated result created by quarantining a nonempty received population is not evidence of a confirmed valid empty business population. The 2% margin never authorizes financial imbalance, orphan/duplicate facts, security failure or arbitrary removal.

## Exact reconciliation and K06

For each source/entity/business-date/revision:

- Raw captured rows = manifest rows, exactly.
- Received rows = accepted source rows + quarantined rows + approved excluded rows, mutually exclusive, exactly.
- Source signed financial total = accepted curated signed total + quarantine signed total + approved exclusion signed total for the same population. Where an explained adjustment is necessary, retain its signed components, explicit equation/effect, evidence and independent approval; unexplained residual must still be exactly zero. Adjustments never disguise missing values or authorize imbalance.

Reconcile separately by source, entity, business date, revision, monetary field, currency and comparable status population. No cross-currency netting or general nonzero tolerance. Source-to-target lineage compares distinct accepted source keys; reconcile expected child counts separately for one-to-many transformations. Payments and principal have separate controls; daily stock balances are never summed across dates. KPI reconciliation compares the same selected publication, role, period and filters with zero unexplained variance.

Missing/unparseable control amounts make the required control Unavailable and CRITICAL, never zero or PASS. Preserve negative K06 principal in raw/quarantine signed totals. For any DPD > 30 loan with negative or missing principal, K06 cannot be presented as complete: block the candidate until corrected or the approved source supplies valid evidence. No exclusion can bypass this. K06 retains the principal sum for DPD > 30, with zero valid and no positive-only or active-only filter. DD-06 principal reason-code spellings remain draft.

## Quality exclusions

Only isolated noncritical records may be excluded, and only where removal creates no financial imbalance, identity guessing, security exposure, KPI distortion or risk misclassification. Formula-defined KPI population exclusions remain separate from these quality exclusions.

Exclusions are prohibited for missing critical sources, checksum failures, unexplained residuals, duplicate facts, broken masking, missing rule/catalog versions and unresolved critical keys/amounts. They cannot override the 98% requirement or atomic-publication block.

Require applicable source-owner approval and an independent Data Owner approval; add Compliance when sensitive access, masking or risk evidence is involved. Investigator cannot approve their own exclusion. Approval identifies source/entity/business date/revision and exact records, with no standing indefinite scope. Record reason, affected rows/cells/amounts/KPIs, completeness before/after, approvers, effective scope and evidence. Missing amounts remain unavailable, not invented exclusion totals. [Inventory](field-level-dictionary.md) child records retain record/field/KPI/currency scope without serialized sensitive text.

## Correction and publication authority

| Responsibility | Approved authority and separation |
| --- | --- |
| Source-data correction | Applicable source owner authorizes; Data Owner independently validates corrected data and reconciliation |
| Identity correction | Independent Senior Data Steward approval under DD-08, with submitter separation and history/correction evidence |
| Risk-rule/configuration correction | Joint Risk Manager and Compliance approval |
| Replay/publication execution | Administrator executes approved operations; cannot approve them |
| Release decision | Data Publication Approver, separate from investigator, rule author and Administrator, may approve only a candidate passing every automated gate with complete evidence |
| Corrected/restated release | Additionally requires Data Owner validation and applicable business/source-owner review |
| Critical override | No person, role or Sponsor waiver may override unresolved CRITICAL failure |

Data Publication Approver is a governance responsibility, not an automatic reporting, raw-evidence or export grant. DD-08 current entitlements and independent reviews apply. Named appointments and actual review evidence remain Pending confirmation. Independently approved explained adjustments require recorded approver authority/evidence; the exact responsibility for adjustment types not already covered by correction/exclusion governance must be confirmed before use, not assumed.

## Atomic publication and service behavior

Publish one atomic, internally consistent daily version across all five sources. Do not label partial datasets successful or expose half-replaced versions. Legitimate customer-level Unknown/unavailable results may appear only when correctly calculated, noncritical, coverage disclosed and every publication control passes. Missing catalog/rule/configuration is a blocking configuration failure, not a publishable customer Unknown.

If blocked, preserve and continue serving the last successful version with its business date, publication version, age and prominent stale-data reason. Under DD-10, a prior version whose underlying detail expired cannot be served. If no valid retained prior success exists, show Data unavailable and never expose the failed candidate. Reports default to the latest successful publication and never silently combine versions; explicit historical selections remain version-consistent and use current DD-08 entitlements.

Preserve superseded publications and correction lineage. Corrected RC-01 events recalculate affected customers, including former and corrected attribution, from event date through the following 90 days. No future business activity is copied backward. Label risk-rule-version changes in comparisons as DD-06 requires.

Immediately notify Data Owner, Data Publication Approver and affected source/KPI owners when the 6:00 a.m. gate is missed, a published version is restated, or a critical failure is discovered. Record notification time, recipients, reason and acknowledgment/status. No restricted payload in notifications. This approves the logical notification requirement, not sending messages in this documentation task; channel and operational delivery mechanics remain for later authorized design/implementation.

## Publication decision evidence

Every released, blocked, deferred, failed or corrected candidate requires:

- Candidate/run/publication identities and business date; a candidate exists before successful publication and never fabricates a released version.
- Gate-ruleset version; source/entity revisions, checksums and schema/mapping versions, with explicit absence/unavailable evidence where a delivery failed.
- Control results and severities; received/accepted/quarantined/excluded counts; received/curated and before/after-exclusion completeness.
- Currency-separated financial totals/residuals and Unknown/unavailable coverage, with unavailable reasons for unmeasured early failures.
- Exclusion/correction references; prior successful publication retained or explicit no-prior-success state.
- Decision, sanitized reason, timestamp; requester/investigator, Data Owner, business/source reviewers, Data Publication Approver and executing Administrator, preserving unassigned/not-performed status rather than inventing people or approvals.
- Notification evidence; predecessor/superseded publication and affected historical range where applicable.

The [authoritative inventory](field-level-dictionary.md) is the only field contract. Preserve approval evidence against Administrator modification/deletion under DD-08. Apply approved DD-10 retention, anchoring and controlled purge mechanics; do not extend seven-year retention to every raw/risk payload by implication. Baseline analytics 24 months and pipeline/quality/export audit seven years remain unchanged.

## Remaining dependencies and planned validation

DD-09 logical policy is approved. Mandatory actual source cutoffs, delivery allowances, agreed checksum content/encoding, source aliases, named independent appointments and actual evidence remain Pending confirmation. DD-10 retention policy is approved; DD-11 payment semantics are approved; DD-12 historical attribution is approved, with actual source evidence still required. G3 and physical implementation remain unapproved.

Future checks cover all rule severity/escalation paths; all five mandatory sources; valid empty versus missing; identical replay versus revision conflict; received/curated thresholds per entity and overall; exclusion denominator invariance; exact signed currency controls; K06 blocking; legitimate Unknown versus missing configuration; independent review and no critical override; atomic/latest-successful fallback; correction/90-day scope; notification and all-candidate audit evidence. These are planned DQ-01 through DQ-04, IT-01/IT-02, reconciliation RC-01, risk UT-01 through UT-07 and applicable ST-01 through ST-07 checks, not executed runtime tests.

## DD-10 approved lifecycle coordination - 2026-09-16

DD-10 bounds the DD-09 fallback: never serve a last-successful version after underlying detail expires; show Data unavailable until valid retained publication exists. Seven-year minimized candidate/decision/control/notification evidence survives via provenance envelopes, not retained raw rows. Corrections do not restart analytical clocks. RC-01 recalculation applies only to retained affected dates; exceptional rehydration requires Compliance, Data Owner and applicable business-owner approval plus valid source evidence. DD-09 critical controls cannot be bypassed by a hold or disposal approval. See [retention and disposal policy](retention-and-disposal-design.md) and [authoritative inventory](field-level-dictionary.md).

## DD-11 control application - 2026-09-16

The [approved DD-11 policy](loan-payment-and-schedule-policy.md) applies existing DD-09 controls; it does not relax severities or atomic publication.

| Existing rules | DD-11 required control | Disposition |
| --- | --- | --- |
| DQ-D01/D02/D11 | Required deliveries, source-qualified identities/revisions, checksum and verified coverage; identical replay adds no facts | Missing/conflicting/stale required evidence CRITICAL; identical replay INFO |
| DQ-D03/D06/D07 | Positive canonical payments; four mapped statuses; contractual currency throughout, no conversion; preserve invalid signed raw evidence | Invalid rows ERROR/quarantine; unavailable required control or financial residual CRITICAL |
| DQ-D04/D05/D08 | Resolved same-loan allocation parents, valid immutable intervals, exactly one effective REPORTING account and producible fixed mask | Missing/ambiguous REPORTING linkage makes drill-through Unavailable and CRITICAL; no inferred link |
| DQ-D09/D13 | Daily snapshot DPD/principal/status authoritative; K05/K06/RC-03 unchanged | Existing snapshot/risk controls apply; payment history cannot fill missing DPD |
| RC-D01/D02/D03 | Exact counts; POSTED payment = active allocations + unapplied; cumulative REVERSAL/REFUND <= original POSTED amount; separate currency/status/version populations | Unexplained residual, missing control, cap violation or join multiplication CRITICAL |
| DQ-D10/PUB-D01 | Required applicable business cells in all added entities; >=98% received and curated per entity and overall; every critical resolved | Atomic publication blocked on failure |

Only POSTED is financially effective. A source-confirmed zero unapplied amount is distinct from absent evidence. Schedule totals, obligation/component controls and adjustment effects require comparable source evidence; no invented waterfall or general tolerance. Never subtract an adjustment from the original immutable payment or silently reinterpret the approved gross allocation equation as a net equation. Source-supported adjustment application and allocation/unapplied timing must be reviewed and reconcile before release. Correction authority, exclusions and independent release remain DD-09/DD-08 controls; no critical override.

## DD-12 approved coordination - 2026-09-16

[DD-12 approved policy](historical-branch-attribution-policy.md). Earlier dated dependency notes retain historical status; DD-12 logical policy is now approved, actual source coverage remains unverified.

Apply the existing 17-rule catalog to DD-12: DQ-D01/D11 mandatory source coverage; DQ-D03/D04 missing/unresolved assignment quarantine and escalation; DQ-D05 invalid/overlapping intervals CRITICAL; RC-D03 join multiplication CRITICAL; DQ-D10 required attribution coverage below 98% per required applicable population and overall CRITICAL. Never infer across gaps, overlaps or mismatches; source-supplied mismatch needs review. Passing coverage never permits security exposure or guessed attribution. Preserve missing home-branch customers in enterprise K07 while independently evaluating branch coverage and all gates. Exact counts and currency-separated financial totals must remain unchanged by grouping except explicitly reviewed corrections. All unresolved critical controls block atomic publication without override. Corrections affect only retained facts with attribution instants in the corrected interval; recalculate KPI/risk/scope/membership, preserve predecessor publication, independently approve restatement and notify under DD-09.
