# KPI-to-data mappings

Status: **Draft — not approved**. Formulas below preserve Planning section 8. K01–K10 are Sprint 2 cross-reference labels only. Field paths refer to proposed logical entities.

| ID / approved KPI | Approved formula / DD-06 population | Grain and date | Controls |
| --- | --- | --- | --- |
| K01 Transaction Volume | Count all terminal processed transactions | Transaction; occurred_at period | Exclude PENDING; terminal status groups in DD-06 policy |
| K02 Transaction Success Rate | SUCCESSFUL + POSTED / eligible processed x 100 | Transaction; occurred_at period | Denominator SUCCESSFUL, POSTED, FAILED, DECLINED |
| K03 Transaction Failure Rate | FAILED + DECLINED / eligible processed x 100 | Transaction; occurred_at period | Same denominator as K02; CANCELLED/VOIDED/REVERSED separate |
| K04 Fraud-Alert Rate | Distinct eligible transactions with linked alert / eligible transactions x 100 | Transaction cohort; occurred_at period | Same eligible population as K02/K03; multiple alerts count once |
| K05 Loan Delinquency Rate | Active loans DPD > 30 / active loans x 100 | Loan/business-date snapshot | ACTIVE, DELINQUENT_ACTIVE, FORBEARANCE_ACTIVE |
| K06 Outstanding Delinquent Balance | Sum outstanding principal for loans with DPD > 30 | Loan/business-date snapshot; separate currencies | All statuses; no positive-principal population filter; negative/missing principal handled by quality controls |
| K07 High-Risk Customers | Distinct customers with >=2 Triggered conditions | Customer/as-of assessment/configuration | DD-04 Unknown policy; DD-06 daily RC-01 population; label version changes |
| K08 Average Complaint Resolution Time | Average original-creation to final-closure hours | Finally closed complaint; final closure period | Elapsed calendar hours, no pauses; as-of publication knowledge |
| K09 Open Complaints | No current closure timestamp AND open/non-Closed status | Complaint/business-date snapshot | REOPENED open; contradictory evidence quarantined |
| K10 SLA Breach Rate | Eligible complaints exceeding SLA / eligible complaints x 100 | Eligible open/closed complaint at selected state | Creation priority; open to as-of, closed to closure; strict > 4/24/72/120h |

Definitions and provenance: [approved DD-06 policy](kpi-policy-dd06.md). Missing populations and zero denominators display Unavailable; counts, durations and ratios use identical authorized filters and selected publication.

## Shared date, filter and comparison contract

Approved DD-06: America/Chicago; half-open [start, end) periods; custom periods compare to immediately preceding equal-length periods; complete calendar months/quarters compare to preceding complete calendar periods. Stock measures compare to preceding comparable as-of positions, never sums of daily stocks. Rate changes use percentage points. Recompute ratios from filtered numerators and denominators. Missing populations/zero denominators are Unavailable. Preserve DD-03 historical state and one explicitly selected publication version.

Filters: date and effective branch/region are conformed across facts; account/transaction type and status apply to transactions; loan type/aging apply to loan snapshots; priority/channel/status to complaints; severity/status/reason to alerts; risk classification to customer assessments. Cross-domain filtering uses the DD-02 effective owner/co-borrower bridges with non-additive customer attribution, not a direct fact-to-fact join. Aggregates must preserve the user's authorized row scope.

## Unusual-transaction and customer-risk inputs

FR-08 retains the 3x/90-day basis. The [approved DD-05 comparison policy](customer-risk-catalog.md) specifies full-window coverage, >=5 eligible priors, same currency, absolute nonzero finalized amounts, initiator-first attribution and revisioned recalculation. Raw signed amounts remain unchanged for financial KPIs and reconciliation; do not replace K01-K06 populations or monetary totals with RC-01 eligibility rules.

DD-04 approves the five-condition catalog and threshold-aware Unknown classification in [customer-risk-catalog.md](customer-risk-catalog.md). RC-03 uses DPD > 30, consistent with loan KPIs. RC-02 through RC-05 and incomplete-evidence handling are Sprint 2 decisions. Unknown is never Not triggered; two Triggered conditions suffice even with other Unknowns. No automated lending/fraud decision is introduced.

## DD-02 approved relationship policy - 2026-09-15

DD-02 approved by the user on 2026-09-15: retain all owners and co-borrowers with effective-dated relationship roles. Monetary facts remain at their natural account, transaction, payment or loan grain. Customer-level shared balances are labeled "Relationship exposure" and are non-additive across customers; bank totals are computed from distinct natural-grain facts, never by summing customer exposures. Equal or weighted allocation requires a separately approved policy.

Customer shared-balance displays and exports must say "Relationship exposure (non-additive across customers)". Recompute bank totals from distinct loan/account facts at the same date/currency/filter scope; never sum customer rows. Payment and transaction totals remain at event grain. Relationship membership does not establish the initiating customer. The DD-04 catalog is approved; DD-05 comparison and attribution are approved; DD-06 canonical sets approved; versioned source aliases required before publication. Relationship membership still does not establish causal attribution.

## DD-03 approved historical snapshot policy - 2026-09-15

DD-03 approved by the user on 2026-09-15: daily historical loan-position snapshots at loan plus business-date grain and complaint-state snapshots at complaint plus business-date grain. Preserve values known for each as-of date, batch revision, source version, publication lineage and controlled correction history. Historical states that cannot be supplied or reliably reconstructed are unavailable. Do not carry current values backward, use future information or sum daily stock measures across dates.

K05/K06 use the selected business-date loan position, and K09/K10 use the corresponding complaint state under the selected publication. Missing required states make the affected measure unavailable or explicitly incomplete under the approved DD-09 publication policy; do not silently carry an older/current value into the date or treat missing state as zero. Prior-period stock comparisons use separate as-of snapshots, not accumulated daily stocks. Complaint closure/priority/status must reflect only knowledge valid at that cutoff, including for K08 historical reporting. DD-06 final-closure/SLA rules apply. Historical exports identify publication version so corrected and original results are distinguishable.

## DD-07 logical contracts - 2026-09-16

DD-07 fixes logical numeric/time contracts without changing KPI formulas. Financial controls are currency-separated decimal(28,4); ratios retain numerator/denominator evidence and use decimal(28,8) only without silent rounding. Snapshot membership selects one entity/date/publication. Publication controls and quality dispositions remain DD-09. See the [authoritative inventory](field-level-dictionary.md).

## DD-08 coordination - 2026-09-16

KPI mappings require the applicable business KPI owner plus Data Owner review. Data Analyst/Business Analyst may prepare and recommend, never give final business approval. Customer-risk catalog/threshold changes require joint Risk Manager and Compliance approval; no self-approval, and rule authors cannot be sole approver or publisher. See [approved policy](security-and-masking-design.md) and [authoritative inventory](field-level-dictionary.md).

## DD-09 approved coordination - 2026-09-16

DD-09 requires per-source/entity and overall received/curated business-field completeness >=98%, exact currency-separated controls and no misleading KPI. K06 negative/missing principal at DPD > 30 blocks release; K08-K10 misleading closure/coverage failures escalate to CRITICAL. Formula population exclusions do not authorize quality exclusions. Corrected/restated publications need Data Owner validation, applicable business/source-owner review and Data Publication Approver release approval; notify affected KPI owners immediately on gate miss, restatement or critical discovery. See [approved quality policy](data-quality-and-reconciliation.md) and [authoritative inventory](field-level-dictionary.md).

## DD-10 approved lifecycle coordination - 2026-09-16

DD-10 keeps the complete rolling 24-month analytical reporting window; aggregates/caches cannot outlive source evidence and caches expire within 24 hours. Superseded metadata may remain audit-visible after analytical expiry but cannot expose expired report detail. Formula definitions and DD-09 publication gates are unchanged. See [retention and disposal policy](retention-and-disposal-design.md) and [authoritative inventory](field-level-dictionary.md).

## DD-11 approved coordination

See [approved DD-11 policy](loan-payment-and-schedule-policy.md). US-04 uses snapshot-authoritative DPD/outstanding principal and exactly one effective REPORTING account through loan_account for masked drill-through. Schedules and actual events are distinct; component allocations and unapplied balances reconcile without fanout, and reversals/refunds preserve originals. K05, K06 and RC-03 including DPD > 30 remain unchanged. Existing scoped access and original-date retention apply. Source coverage remains unverified; fixture/runtime validation is planned, not executed.

## DD-12 approved coordination - 2026-09-16

[DD-12 approved policy](historical-branch-attribution-policy.md). Earlier dated dependency notes retain historical status; DD-12 logical policy is now approved, actual source coverage remains unverified.

K01-K04 use account SERVICING at occurred_at; K05/K06 use loan SERVICING at snapshot business date/cutoff. Complaint creation uses created_at; K08 uses final_closed_at; K09 uses selected snapshot date; K10 uses selected open-case as-of or closed-case final_closed_at. K07 branch/region uses home branch at assessment date; enterprise distinct high-risk count retains missing-home customers with coverage disclosure. Filters preserve historical region labels even where current region authorization admits historical branches. Formulas/populations unchanged; ratios recomputed from filtered numerators/denominators and no fact multiplication.
