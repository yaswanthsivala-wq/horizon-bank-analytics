# Synthetic-data specification

Status: finalized documentary specification v1 under the user-authorized G3 closure scope; G3 approval remains pending. No data generation authorized or performed.

## Approved scenario constraints

Synthetic data only; five source systems; twenty-four months of history; one-person delivery; local tools. Planning section 10 supplies these approximate entity sizes:

| Entity | Planning quantity |
| --- | ---: |
| Branches | 50 |
| Customers | 10,000 |
| Accounts | 15,000 |
| Transactions | 250,000 |
| Loans | 6,000 |
| Loan payments | 50,000 |
| Fraud alerts | 8,000 |
| Complaints | 5,000 |
| Risk assessments | Derived |

These are design assumptions, not produced row counts. Daily loan-position and complaint-state snapshot grains are approved under DD-03; physical storage estimates and other history-table choices remain pending. Snapshot row counts are not generated results. Do not interpret each listed count as a per-day volume.

## Proposed generation approach for later authorization

Use a fixed seed and configurable as-of date, generate parent entities before children, and maintain a private synthetic master-ID map for deterministic reconciliation fixtures. Export source-specific aliases to demonstrate identity differences without using real identities. Use unmistakably synthetic names and non-deliverable contact examples; no sampled customer records or live banking connections.

The v1 profile below fixes date range, bounded volumes, synthetic distributions and expected outcomes. These are fictional test-design choices, not observed bank behavior.

## Proposed scenario families

- Valid referential chains spanning all five sources and each approved report filter.
- Duplicate IDs, missing required fields, orphan references, inconsistent status labels, and ambiguous crosswalks.
- Late/corrected extracts and repeat delivery of identical batches.
- Boundary cases for 30/31 days past due, 3x 90-day comparison, complaint SLA limits, zero denominators, and insufficient history.
- Branch/segment changes, all-owner and co-borrower relationships with effective-dated roles, account closure, and out-of-order source updates.
- Positive/negative role and export simulations; restricted values must never leak through audit/filter metadata.

Keep valid baseline scenarios distinct from controlled anomaly fixtures; expected outcomes must be documented before executing tests. The v1 profiles below define fixture counts and expected outcomes; execution remains post-G3.

## Historical sufficiency issue

Twenty-four months of displayed analytics may need earlier history for the first 90-day comparison and pre-window account/loan/complaint state. DD-05 selects Unknown for incomplete 90-day windows; no history beyond the approved 24 months is authorized. Historical snapshot sufficiency remains subject to DD-03.

## DD-01 decision status - 2026-09-15

DD-01 was approved by the user on 2026-09-15: entity-specific delivery modes and required batch manifests. DD-02 is also approved: all owners/co-borrowers, effective-dated roles and non-additive relationship exposure. DD-03 is approved for daily historical snapshots and controlled lineage/corrections. DD-08 through DD-12 remain Pending confirmation. Detailed DD-01 contract values remain pending where unspecified; G3 and technical implementation are not approved. See [source contracts](source-system-definitions.md) for the approved delivery approach and remaining contract details. This approval does not authorize data generation or ETL.

## DD-02 approved relationship policy - 2026-09-15

DD-02 approved by the user on 2026-09-15: retain all owners and co-borrowers with effective-dated relationship roles. Monetary facts remain at their natural account, transaction, payment or loan grain. Customer-level shared balances are labeled "Relationship exposure" and are non-additive across customers; bank totals are computed from distinct natural-grain facts, never by summing customer exposures. Equal or weighted allocation requires a separately approved policy.

Future fixtures should cover shared accounts, co-borrowed loans, multiple roles for one customer, ownership start/end boundaries and conflicting intervals. Expected behavior: preserve all valid relationships, count a fact once per customer exposure, and once in bank totals. This specifies scenarios only; no data generation is authorized.

## DD-03 approved historical snapshot policy - 2026-09-15

DD-03 approved by the user on 2026-09-15: daily historical loan-position snapshots at loan plus business-date grain and complaint-state snapshots at complaint plus business-date grain. Preserve values known for each as-of date, batch revision, source version, publication lineage and controlled correction history. Historical states that cannot be supplied or reliably reconstructed are unavailable. Do not carry current values backward, use future information or sum daily stock measures across dates.

Future scenarios: missing historical loan/complaint states; closure after an earlier as-of date; changed priority/DPD/balance; repeated batch; evidence-supported correction with original publication reproducibility; unsupported reconstruction remaining unavailable. Record expected outcomes before later authorized generation. DD-05 forbids extra warm-up history outside twenty-four months; no extra history or dataset is generated.

## DD-04 future scenarios

Use the [approved catalog](customer-risk-catalog.md) for later authorized fixtures: risk RC-01 3x boundary; RC-02 mapped/unmapped open severity; RC-03 valid active loans at 30 and 31 DPD; RC-04 strict SLA exceedance; RC-05 mapped/unmapped restrictions. Include t=2/u=3, t=1/u=1, t=0/u=1, t=0/u=2, missing catalog/version and late-source states. No mappings, generated records or executed results are supplied here.

## DD-05 future fixture design

No extra warm-up history beyond 24 months. Later authorized fixtures should cover complete/incomplete windows, four/five priors, different currencies, signed debit/credit values, zero amounts, each excluded status, unknown mappings, valid/absent/invalid initiators, one/multiple owners and deduplicated intervals, plus corrected evidence. Expected comparisons follow [DD-05](customer-risk-catalog.md); no generated data or runtime evidence is created.

## DD-06 future cases

Use [approved DD-06](kpi-policy-dd06.md) for future status combinations, zero/negative/missing principal dispositions, SLA boundaries, creation-priority changes, reopened case history, custom/calendar comparisons, zero-event manifests and corrected revisions. No source aliases or generated records are invented; generation remains unauthorized.

## DD-07 logical contracts - 2026-09-16

Future contract-check scenarios include maximum lengths, leading-zero identifiers, currency excess scale, count/DPD/revision limits, DST ambiguity, nullable unavailable attempts, duplicate child evidence and cyclic correction rejection. These are documentation scenarios only; no data or executable tests were generated. See the [authoritative inventory](field-level-dictionary.md).

## DD-09 approved coordination - 2026-09-16

Future fixtures must cover the 17 approved DD-09 rule dispositions, ERROR escalation, verified replay versus conflict, all mandatory sources, valid empty versus missing, received/curated 98% per-source/entity and overall gates, post-exclusion non-substitution, exact currency totals, blocked K06, legitimate Unknown versus missing configuration, independent release/no critical override, prior-success fallback, restatement and notification evidence. Fixture creation and execution remain unauthorized; these are planned scenarios only. See [approved quality policy](data-quality-and-reconciliation.md) and [authoritative inventory](field-level-dictionary.md).

## DD-10 approved lifecycle coordination - 2026-09-16

Future authorized fixtures should test anniversary/expiry boundaries, scoped holds, exact disposal scope, failed eligibility, payload-envelope transitions, seven-year minimized denials, backup 35-day maximum and restore revocation/purge application. No fixtures, backups or purge jobs are generated in this documentation task. See [retention and disposal policy](retention-and-disposal-design.md) and [authoritative inventory](field-level-dictionary.md).

## DD-11 approved coordination

See [approved DD-11 policy](loan-payment-and-schedule-policy.md). US-04 uses snapshot-authoritative DPD/outstanding principal and exactly one effective REPORTING account through loan_account for masked drill-through. Schedules and actual events are distinct; component allocations and unapplied balances reconcile without fanout, and reversals/refunds preserve originals. K05, K06 and RC-03 including DPD > 30 remain unchanged. Existing scoped access and original-date retention apply. Source coverage remains unverified; fixture/runtime validation is planned, not executed.

## DD-12 approved coordination - 2026-09-16

[DD-12 approved policy](historical-branch-attribution-policy.md). Earlier dated dependency notes retain historical status; DD-12 logical policy is now approved, actual source coverage remains unverified.

Future verification must cover same-instant transfer boundaries, gap/overlap, branch region reassignment, closure/merger without access inheritance, current region access with historical labels, explicit historical scope, source branch mismatch, loan/account multi-role fanout, payment/obligation different branches, posted_at availability, complaint closure/reopening attribution, multi-branch risk observations, missing-home enterprise K07, correction interval selection and original-anchor disposal. These are planned scenarios, not generated fixtures or executed tests.

## Finalized v1 documentary profile - 2026-09-16

The requesting user's synthetic-project gate-scope decision controls this profile. See [synthetic contract](synthetic-source-contract.md), [full field trace](synthetic-contract-traceability.md) and [prerequisite register](g3-prerequisite-register.md). Earlier dated pending statements are historical. Nothing below is generated data, executed verification or persona approval.

Seed is integer 20260916, specification SYN_V1, mappings IDENTITY_SYN_V1. Deterministic selection/ranking uses SHA-256 of UTF-8 seed|spec_version|scenario_id|entity|stable_ordinal|field; bytes interpreted unsigned big-endian, modulo the declared choice count. No runtime random-library defaults. IDs depend on source/entity/ordinal, not generated row order. Same inputs must yield identical logical rows and canonical delivered bytes. Changing seed or specification creates a new labeled fixture edition, never a silent revision of expected outputs.

Date range: 2024-09-01 through 2026-08-31 inclusive, 730 dates. Baseline as-of is the last business date; negative cases are isolated candidate overlays, not corruption of every baseline day. Exact start/end and all timezone conventions are in the synthetic contract. No out-of-window RC-01 warm-up.

| Entity category | Baseline volume/profile |
| --- | --- |
| Stable regions/branches | 5 regions, 50 branches, ten original branches per region; 1-4 effective versions per identity |
| Customers/accounts | 10,000 customers, 15,000 accounts; at least one owner each; first 1,500 accounts have two distinct owners; no more than three |
| Transactions | 250,000 natural events, allocated by date ordinal using quotient/remainder over 730 days |
| Loans | 6,000; one or two borrowers, first 600 have two; one SERVICING assignment and one effective REPORTING account at each applicable instant |
| Loan positions | One per loan per applicable business date; baseline all 6,000 over 730 days = 4,380,000 selected rows; revisions are additional immutable versions, not extra selected facts |
| Payments | 50,000 natural events; separate schedule/obligation entities are not included in this count |
| Schedules/obligations | One initial schedule per loan, at most two corrected/rescheduled versions; 24 obligations per loan = 144,000 natural obligations, at most two versions each |
| Allocations/unapplied/adjustments | 1-4 allocations per POSTED payment; exactly one selected unapplied state per POSTED payment; 0-2 adjustments per eligible posted event, 100 designated adjustment cases |
| Fraud alerts | 8,000 natural alerts; 0-1 transaction reference per alert via source-supported paths; multiple alerts may reference one transaction |
| Complaints | 5,000 cases; 0-4 lifecycle events beyond creation; daily snapshots from creation through retained relevant state, bounded by 3,650,000 rows |
| Assignments/classification | 1-4 effective intervals per subject/role across the window; all required instants covered in baseline |
| Risk outputs | One assessment per customer/applicable date, five distinct condition results when catalog valid; <=7,300,000 assessments and <=36,500,000 condition rows; evidence items 0-5 per condition in this profile |
| Control/configuration/governance | One manifest per required source/entity/date/revision; one baseline run/candidate per day; one configured version initially and one correction version where scenario requires. Child counts bounded by entity/rule/decision populations |
| Negative/correction overlays | Each scenario below has one minimal candidate unless variants are enumerated; each variant is a separate candidate with at most ten modified business rows and required dependent rows |

These are logical/bounded fixture sizes, not performance claims or physical storage estimates. Parent entities precede children in later generation. Closed states remain as legitimate history; their existence does not imply an active KPI population.

## Deterministic distributions

Apply quotas to stable ordinal-ranked natural records; largest-remainder allocation resolves fractional quotas by listed order. Scenario overlays take precedence only in their isolated candidates. Monetary baseline transaction magnitude = 1 + (ordinal modulo 100000)/100 units; debit ordinals odd are negative, credit even positive. Loan principal = 1000 + ordinal units, zero only in designated tests. Posted payments = 100 units; their supplied allocations are 70 principal + 20 interest + 5 fee + 5 unapplied unless a scenario overrides. Obligations are 100 units. No expectation of reconstructing loan principal/DPD from payments.

| Domain | Baseline distribution |
| --- | --- |
| Currency | USD 90%, EUR 10%; assign once at loan contract and inherit all children; transaction currency assigned independently |
| Transaction status | SUCCESSFUL 50%, POSTED 30%, FAILED 5%, DECLINED 5%, CANCELLED 3%, VOIDED 2%, REVERSED 2%, PENDING 3% |
| Loan state | ACTIVE 70%, DELINQUENT_ACTIVE 15%, FORBEARANCE_ACTIVE 5%, PAID_OFF 5%, CLOSED 3%, CHARGED_OFF 2% |
| DPD | ACTIVE/PAID_OFF/CLOSED baseline 0; DELINQUENT_ACTIVE 31; FORBEARANCE_ACTIVE 30; CHARGED_OFF 60; targeted overlays cover other boundaries |
| Payment status | POSTED 90%, PENDING 5%, FAILED 3%, CANCELLED 2%; posted_at = paid_at + 1 minute in baseline |
| Complaint priority | Critical 10%, High 20%, Medium 40%, Low 30% |
| Complaint final state | CLOSED 60%, OPEN 20%, IN_PROGRESS 15%, REOPENED 5%; earlier snapshots obey actual transition times |
| Fraud severity/case | LOW 40%, MEDIUM 30%, HIGH 20%, CRITICAL 10%; OPEN/CLOSED 50/50 |
| Restriction state | NONE 95%, RESTRICTED 3%, FROZEN 1%, BLOCKED 1% |
| Customer segment | RETAIL 80%, SMALL_BUSINESS 20%; home branches round-robin 50 |
| Remaining listed classification domains | Equal quotas in contract-listed order; no observed-business distribution claim |

## Scenario and expected-outcome catalog

Each expected outcome is an assertion to implement and test later, NOT a result. All financial equations are evaluated separately by source/entity/date/revision/field/currency/comparable status. A blocked candidate cannot expose its rows as a successful publication.

| ID / specification | Expected control outcome |
| --- | --- |
| S01 valid baseline with all required manifests | Exact counts and required cells; 100% applicable completeness; zero unexplained financial residual; gates eligible for independent simulated release decision, not automatically released |
| S02 missing each source; corrupt checksum; missing required section (seven variants) | DQ-D01/D11 CRITICAL, atomic block; prior successful version served with stale reason |
| S03 explicit zero-row event manifest | Valid empty is Not applicable/Unavailable, not missing or 100%; no invented facts |
| S04 identical replay; conflicting same revision; valid correction (three variants) | INFO/no duplicate facts; CRITICAL; preserved predecessor/new selected revision with exact controls respectively |
| S05 required cell blank, orphan reference, ambiguous customer mapping, leading-zero normalization collision (four variants) | DQ-D03/D04/D08 quarantine or suppression with no inferred match; critical escalation when required control/coverage/security fails |
| S06 100 applicable cells with 2 versus 3 missing; repeat per entity and overall (four variants) | Received 98% versus 97%; 97% CRITICAL; 98% does not excuse orphan/financial/security failures |
| S07 exclusion attempts: self approval, indefinite scope, prohibited critical amount; valid isolated noncritical exclusion (four variants) | First three denied; fourth needs independent required personas/evidence; received completeness unchanged, curated/post-exclusion separately measured |
| S08 duplicate fact and multiplied owner/borrower join (two variants) | RC-D03 CRITICAL; distinct native-grain totals invariant across valid relationship joins |
| S09 signed controls: nonzero residual, missing control, cross-currency offset (+1 USD/-1 EUR) (three variants) | RC-D02 CRITICAL in every variant; no netting/tolerance |
| S10 DPD 30/31; DPD>30 principal zero/negative/missing (five variants) | Strict >30 boundary; zero valid; negative/missing blocks K06 completeness, preserves raw signed quarantine evidence |
| S11 payment 0/-100, POSTED missing posted_at, nonposted with posted_at (four variants) | Invalid contract, quarantine; required financial/attribution control unavailable => CRITICAL; no timestamp substitution |
| S12 two 100 payments, two obligations: P1 allocates 60/35 +5 unapplied; P2 40/55 +5 unapplied | Many-to-many supported; each payment exactly 100; components source-supplied, no waterfall/fanout |
| S13 overpayment 120: allocations 100, unapplied20; allocation gap 1; currency mismatch (three variants) | First balances; other two quarantine/block required reconciliation; no FX |
| S14 original100; reversal20 and refund10; separate excess101 adjustment variant | Cumulative30<=100, original gross evidence unchanged, net cash70; component application references total30; excess variant CRITICAL |
| S15 corrected allocation versus business reversal | Correction predecessor selects replacement once; reversal remains separate immutable event; no duplicate original payment |
| S16 missing/ambiguous REPORTING account; inferred transaction link (three variants) | Required drill-through Unavailable/critical; inferred link rejected; mask suffix never a key |
| S17 account/loan transfer at 2025-06-01 00:00 Chicago; one microsecond before/at | Old/new half-open assignment respectively; native monetary totals unchanged |
| S18 branch closure, merger, region reassignment (three variants) | Preserve earlier labels/identity; explicit successors; no automatic access inheritance; current assignments covered or candidate fails |
| S19 interval gap, overlap, supplied-branch mismatch (three variants) | No fallback; overlap CRITICAL; mismatch review required; unresolved required coverage/control blocks |
| S20 payment after transfer versus obligation before transfer; later adjustment | Cash-flow/payment and obligation branches retained separately; adjustment-time and original-payment branch preserved |
| S21 complaint each priority at SLA threshold and threshold+1 microsecond (eight variants) | Equality not breached; greater breached; UTC elapsed calendar time and original priority |
| S22 close/reopen/final close; responsibility transfer; later closure | Reopen has null current closure, original clock retained; K08 final closure branch, K09 selected snapshot, K10 approved open/closed instant; no future leakage |
| S23 RC-01 four/five priors, exact3x, <3x, missing90-day window, zero-event day (six variants) | Four priors => Unknown; five valid priors and exact3x => Triggered, <3x with complete evidence => Not_triggered; missing window => Unknown; confirmed zero-event day => Not_triggered if delivery complete |
| S24 RC-01 initiator valid/absent sole owner/ambiguous joint/invalid supplied (four variants) | Approved attribution hierarchy only; invalid supplied ID never falls back; unresolved evidence disclosed |
| S25 RC-02 supplied alert branch, linked transaction, neither; RC-03 30/31; RC-04 strict SLA; RC-05 restricted state (seven variants) | Approved per-condition evidence/branch; missing alert branch path Unavailable; condition count never multiplied by observations |
| S26 t=2/u=3, t=1/u=1, t=0/u=1, t=0/u=2; missing catalog (five variants) | Respectively Provisional high risk; Incomplete evidence; Not high risk; Incomplete evidence; missing catalog => Classification unavailable and CRITICAL, not fabricated five outcomes |
| S27 missing customer home with high-risk evidence | Enterprise K07 retains customer once; branch attribution Unavailable and coverage disclosed; required coverage gate separately evaluated |
| S28 corrected attribution interval; correction outside retained window | Only retained matching timestamps restated; new approved candidate preserves predecessor; expired raw history not silently rehydrated |
| S29 oversized field, amount excess scale, integer overflow, cyclic predecessor, X_UNMAPPED (five variants) | DD-07 rejection/quarantine, no truncation/rounding/guessed enum; critical escalation per DD-09 |
| S30 valid DST offsets; ambiguous fall time; nonexistent spring time; midnight due date (four variants) | Explicit valid offsets convert; ambiguous/nonexistent rejected; date remains date and branch lookup uses local midnight UTC conversion |
| S31 all control success but no release approval; failed first candidate | No publication without required decision; with no successful predecessor show Data unavailable |
| S32 blocked/restated candidate notifications | Required persona recipients, time/reason/status evidence; no restricted payload in message specification |
| S33 effective end +24-month anniversary, audit +7-year anniversary, open-ended dependency (three variants) | Through-anniversary retention, next approved monthly purge eligibility; active/required versions retained; corrections do not reset anchor |
| S34 hold active/released, wrong disposal scope, self approval (four variants) | Held/wrong-scope items not deleted; failure evidence; release re-evaluates original expiry; separated approval required |
| S35 backup 35-day limit, restore expired/revoked evidence, temporary export24h/restore7d (four variants) | No accessible resurrection; reapply deletion/revocation/holds; specified bounded expiry; no successful operation claimed |

## Security persona specifications

Personas are invented fixture identities; no real independent appointment/review exists. One role selected per session. All allowed rows remain within current unrevoked scope and all explicit denies win.

| Persona/scenario | Expected allow/deny |
| --- | --- |
| Executive E1 | Authorized enterprise/regional aggregate allowed; any business detail denied; aggregate CSV/PDF allowed |
| Operations O1 current region R2 | Aggregate for currently assigned stable branches allowed including historical R1 labels; outside scope and detail denied |
| Loan L1 / Service C1 | Masked assigned-scope domain detail allowed; detail export denied without EXPORT_MASKED_DETAIL, allowed with applicable standing grant |
| Fraud F1 / Risk R1 | Assigned-case linked evidence allowed; unrelated case/domain dataset denied; raw restricted evidence not implied by case projection |
| Analyst A1 | Aggregate/deidentified curated view allowed; names/contacts/full account/source aliases/raw payload denied |
| Source owner S1 | Own-source evidence allowed under explicit scope; cross-source detail denied |
| Administrator ADM1 | Operations/sanitized audit allowed; business detail and discretionary deletion denied; exact approved disposal execution only |
| Compliance CO1 | Sanitized security/export audit allowed; restricted inspection denied without recorded time-bound entitlement |
| Steward submitter/approver | Proposal permitted to submitter; self approval denied; distinct approver persona required in simulated evidence |
| Historical branch/merger | Closed/predecessor outside current scope denied absent explicit current historical entitlement or approved successor mapping; merger alone denied |
| Revocation/expiry during export | Execution denies; no sensitive output, sanitized denied-attempt evidence |
| Unmapped role, conflicting allow/deny, unselected second role | Deny; never automatic union |
| Mask/filter/cache surfaces | Fixed mask+final four only; prohibited values absent from tooltip/download/API/audit/filter text; caches cannot outlive permission/underlying data controls |

## Reconciliation expectations and traceability

Received = accepted + quarantined + approved excluded, disjoint and exact. Identical replay adds no accepted natural facts. For each financial control, signed source total = explained independently approved adjustments + compared disposition totals with exact zero unexplained residual; record each population once. Positive POSTED payment = active gross allocations + unapplied; cumulative adjustments <= original; component adjustment references sum to adjustment magnitude; report net cash separately. No general tolerance or cross-currency netting. Every accepted FK/typed full key resolves the selected parent, all interval matches are unambiguous, and native-grain totals are invariant to dimensional/ownership joins.

S01-S09/S29/S31-S32 cover FR-01/03/04/13 and US-08; S10-S16/S20 cover FR-05/06 and US-04; S17-S20/S27-S28/S30 cover FR-02/05/09/10 and US-01/02/04; S21-S22 cover US-05; S23-S27 cover FR-07/08 and US-03/06; security personas cover FR-10/11/12/14 and US-07 plus each role's stories; S33-S35 cover NFR-07/08. NFR timing/capacity/usability/performance goals remain later measurement, not simulated achieved metrics. The existing 32 AC rows and FR/NFR matrix remain authoritative coverage; field trace supplies exhaustive entity/field references. No fixture or test is executed here.

## Concrete sample specifications (not generated records)

For S23, prescribe five eligible same-currency prior amounts of 10.00 each within a complete 90-day window: prior_sum=50.00, prior_average=10.00; current30.00 triggers at exactly3x, current29.99 does not. Remove one prior for the four-history Unknown case. Use valid resolved initiator and SUCCESSFUL/POSTED identity mapping; changing currency removes that prior from the comparison, never converts it.

For S09, prescribe received signed amounts +100.00 and -20.00 USD: source control80.00, accepted80.00, other dispositions0.00, residual0.00. A corrupted control81.00 gives unexplained residual1.00 and CRITICAL. Quarantining -20.00 preserves accepted100.00 plus quarantine-20.00 = received80.00; it does not silently reconcile a missing required business result.

For S17, use branch B01 before and B02 from 2025-06-01T05:00:00Z (Chicago midnight). Fact at 04:59:59.999999Z belongs B01; fact at 05:00:00Z belongs B02. Due_date 2025-06-01 matches B02 at local midnight. History labels remain unchanged if B02 later moves region. These symbolic IDs represent specification examples, not fixture files or source records.
