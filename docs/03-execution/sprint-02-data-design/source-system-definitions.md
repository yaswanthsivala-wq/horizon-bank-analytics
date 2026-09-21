# Source-system definitions

Current portfolio interpretation (2026-09-16): [G3 prerequisite register](g3-prerequisite-register.md) replaces real-source verification with finalized [synthetic contracts](synthetic-source-contract.md). Logical fields/policies remain approved; physical aliases are proposed until fixture implementation. Review roles are personas, not actual independent organizational approvals. Prior source-evidence prerequisites now mean synthetic contract/specification at G3 and executed fixture validation before publication. G3 remains unapproved.

Status: **Sprint 2 logical design — approved; Gate G3 approved 2026-09-17 (logical design only)** — see [G3 decision](../../04-monitoring-and-control/g3-data-design-approval.md). Proposed physical aliases and domains remain unconfirmed until authorized implementation. The earlier "Draft — not approved" label reflects the state before DD-01–DD-12 and G3 approval and is retained in dated history. Reviewed against Planning sections 4, 5, 9 and 10 and US-08; no source discovery or connection occurred.

### Historical status (superseded)

Status: **Draft — not approved**. Reviewed against Planning sections 4, 5, 9 and 10 and US-08; no source discovery or connection occurred.

## DD-01 approval - 2026-09-15

Evidence: the user stated "Approve DD-01" after reviewing the consolidated register. Approved option: entity-specific delivery modes using master/case snapshots, transaction/payment events, and daily loan positions. Manifests must identify source, entity, business date, delivery mode, revision, schema version, counts, checksums and financial controls. Rationale: complete, reproducible daily deliveries with explicit corrections and repeat submissions. Approval does not establish source-owner review or approve other design decisions.

## Daily contracts

Logical entity fields and delivery policies are approved; synthetic documentary contracts are finalized. Physical aliases remain proposed until generated-fixture implementation; no real-source availability is claimed.

One extract means one logical source batch with a manifest and multiple entity sections; file packaging is Pending confirmation. Names below are design aliases, not existing systems or files.

| ID / approved simulated system | Proposed entity sections and natural keys | Business meaning / DD-01 delivery approach | Baseline review role |
| --- | --- | --- | --- |
| SRC-01 Core Banking | customers(customer_id), accounts(account_id), holders(account_id, customer_id, relationship_role, ownership_start), transactions(transaction_id) | Customer/account master snapshots and transaction events through cutoff | Director of Banking Operations |
| SRC-02 Loan Servicing | loans(loan_id), borrowers(loan_id, borrower_customer_id, relationship_role, relationship_start), positions(loan_id, business_date), payments(payment_id) | Loan master, daily balances/status/DPD, actual payment events; required DD-11 schedules/obligations, allocations, unapplied states, adjustments and effective REPORTING links (availability unverified) | Loan Operations Manager |
| SRC-03 Fraud Monitoring | alerts(alert_id) | Alert case snapshot with creation time and current status; optional source-qualified transaction reference | Fraud Manager |
| SRC-04 CRM | complaints(complaint_id) | Daily case snapshot retaining creation and closure times, priority, channel and branch | Customer Service Manager |
| SRC-05 Branch Reference | branches(branch_id, valid_from) | Effective branch/region hierarchy; parent reference for the other sources | Branch Administration Manager |

The master/case snapshot, transaction/payment event and daily loan-position delivery approach is approved under DD-01. Branch effective-history logical policy is approved under DD-12; actual coverage remains unverified. Named owners, actual schema versions, file formats/encoding, delivery location, cutoff, late-arrival allowance, timezone of source values, status codes, delete/correction semantics and schema approval: **Pending confirmation**. These roles are baseline responsibilities, not evidence of consultation.

## Manifest and common lineage

Required manifest categories are approved under DD-01. The [authoritative inventory](field-level-dictionary.md) defines source_extract, run_extract, source_financial_control and structured population members. Extract identity is source/entity/business-date/revision; multiple applied mappings are child references to version parents. A zero-row section is explicit; absent is not empty. Exact source aliases, cutoff/version conventions and packaging remain Pending confirmation.

Each row retains source_record_id, source_updated_at and record_operation where supplied. Ingestion would attach extract_id, source_system, row_number, run_id and ingestion instant; missing supplied update times require a contract decision, never substitution presented as source evidence. Natural keys are qualified by source_system. Stable account and transaction references across systems require explicit source namespace or a reviewed crosswalk.

Proposed logical flow: immutable raw source revision -> staging normalization -> curated entities -> analytical facts/dimensions; separate audit lineage. Validate all five manifests before publication, validate parent references before accepting child rows, and retain a single publication version across all outputs. No delivery, load, schema or publication is created here.

## History, corrections and reconciliation

Retain 24 months of analytical history as approved. Initial snapshots alone cannot reconstruct past balances, ownership or complaint status: historical extracts or an approved reconstruction contract are required. Corrected revisions retain original audit provenance; identical replay produces no duplicate curated events. No hard-delete inference from absent rows until snapshot scope and delete semantics are approved.

Counts reconcile per source/entity/date/revision; amounts reconcile per monetary field and currency at native entity grain. Alert and complaint counts are not transaction counts. Review [quality controls](data-quality-and-reconciliation.md), [field contracts](field-level-dictionary.md) and [identity rules](customer-identity-reconciliation.md).

## DD-02 approved relationship policy - 2026-09-15

DD-02 approved by the user on 2026-09-15: retain all owners and co-borrowers with effective-dated relationship roles. Monetary facts remain at their natural account, transaction, payment or loan grain. Customer-level shared balances are labeled "Relationship exposure" and are non-additive across customers; bank totals are computed from distinct natural-grain facts, never by summing customer exposures. Equal or weighted allocation requires a separately approved policy.

## DD-03 approved historical snapshot policy - 2026-09-15

DD-03 approved by the user on 2026-09-15: daily historical loan-position snapshots at loan plus business-date grain and complaint-state snapshots at complaint plus business-date grain. Preserve values known for each as-of date, batch revision, source version, publication lineage and controlled correction history. Historical states that cannot be supplied or reliably reconstructed are unavailable. Do not carry current values backward, use future information or sum daily stock measures across dates.

DD-03 requires historical positions and complaint states with source evidence valid at each as-of cutoff. A current extract alone is insufficient. Historical deliveries must identify business date separately from extraction/receipt date, batch revision, source-state version and schema version. Corrections must reference prior state and retain evidence; exact source cutoff/version conventions remain DD-01 contract details. If reliable reconstruction is used, retain the contributing source versions, method and review evidence. This approval does not assert that historical source evidence has been supplied.

## DD-04 source-state requirements

The [approved catalog](customer-risk-catalog.md) requires Fraud alert open/severity state at assessment time and Core account risk-restriction state at assessment time. Proposed source fields: risk_restriction_status, state_as_of_at, effective_from/effective_to and source_version. Retain versioned alert status/severity history or source-supported as-of snapshots; current master values cannot reconstruct past conditions. Exact source representation, cutoff and canonical mappings remain pending; no mapping values or source availability are assumed. Loan and complaint historical inputs follow DD-03.

## DD-05 source requirements

Supply signed amount, debit/credit direction, currency, source status and initiating-customer identifier when available. Preserve absence versus supplied-invalid identifiers. Source coverage must establish the complete preceding 90-calendar-day window within the 24-month dataset; five events alone do not prove coverage. No extra history or Release 1 currency conversion is authorized. Exact source fields/domains remain draft contracts; status/currency source aliases must satisfy approved DD-06 before publication. See [comparison policy](customer-risk-catalog.md).

## DD-06 approved policy integration

[DD-06](kpi-policy-dd06.md) defines KPI status populations, time/comparison rules and source mapping prerequisites. Complaint history must preserve creation priority, original creation, final closure and prior closures; REOPENED current state has no closure timestamp. K06 keeps all DPD > 30 loans without an active-only or positive-principal filter; invalid negative and incomplete missing principal are separate quality dispositions with raw lineage. RC-01 daily current population uses occurred_at business date; revision lineage supports the corrected event date through following 90 days. No physical objects or source mappings are implemented; aliases must be finalized before publication.

## DD-08 coordination - 2026-09-16

Source contracts and each source mapping require the applicable source owner plus Data Owner review evidence. Approved source owners: Core Banking ? Director of Banking Operations; Loan Servicing ? Loan Operations Manager; Fraud Monitoring ? Fraud Manager; CRM ? Customer Service Manager; Branch Reference ? Branch Administration Manager. Actual reviews and named appointments remain Pending confirmation. Ownership grants no automatic business-detail access. See [approved policy](security-and-masking-design.md) and [authoritative inventory](field-level-dictionary.md).

## DD-09 approved coordination - 2026-09-16

All five sources and required entity sections are mandatory under DD-09. Identity remains source/entity/business date/revision; verify SHA-256 against agreed delivered content and retain algorithm, digest encoding, content encoding and checksum-scope contract. Missing, corrupt, conflicting same-revision or stale required delivery is CRITICAL; verified identical replay is INFO with no duplicate facts. Source cutoffs and allowances remain mandatory contract values, Pending confirmation. At the 6:00 a.m. America/Chicago gate, delivery outside its approved allowance is stale; missing contract evidence cannot be assumed to pass. Applicable source owner authorizes source-data correction, Data Owner independently validates, and corrected releases require applicable business/source-owner review. No actual contract or delivery is claimed. See [approved quality policy](data-quality-and-reconciliation.md) and [authoritative inventory](field-level-dictionary.md).

## DD-10 approved lifecycle coordination - 2026-09-16

Raw deliveries/quarantine payloads follow original business/event 24-month anchors; source manifests/checksums/schema metadata remain seven-year minimized audit. Corrections/reingestion never reset analytical clocks. After payload expiry, source pointers use explicit PAYLOAD_EXPIRED envelopes with deletion evidence; decision/control traceability survives, not promised raw replay. DD-11 original-date application is approved; DD-12 application follows the approved historical-attribution policy. See [retention and disposal policy](retention-and-disposal-design.md) and [authoritative inventory](field-level-dictionary.md).

## DD-11 required logical source contracts - 2026-09-16

The [approved DD-11 policy](loan-payment-and-schedule-policy.md) approves required logical coverage, not verified source availability. SRC-02 must supply the inventory fields for loan contractual_currency, positive actual payment events/status, immutable schedule and obligation identities/versions/due dates, component allocations, separate unapplied amounts, reversal/refund events referencing original POSTED payments, and effective loan-account REPORTING references resolving SRC-01 accounts. Every contract must preserve source-qualified identity, original anchor, predecessor/correction lineage, effective/event dates, currency, revision and reviewed mapping. Optional payment-to-transaction references require supplied evidence or independent review, never inferred matching.

Loan Operations Manager plus Data Owner review is required; cross-source account/transaction mappings also require the applicable Core Banking source owner. Actual aliases, schemas, delivery modes for added entity sections, status/component mappings, interval conventions, adjustment effects on allocations/unapplied balances and gross/net controls remain Pending confirmation. DD-01 manifest/revision/checksum and DD-09 exact comparable currency/status controls apply to every required section. Missing verified coverage blocks implementation/publication readiness; a contract requirement does not assert that the source supplies it.

## DD-12 approved coordination - 2026-09-16

[DD-12 approved policy](historical-branch-attribution-policy.md). Earlier dated dependency notes retain historical status; DD-12 logical policy is now approved, actual source coverage remains unverified.

Required logical coverage: SRC-05 stable region/branch identity, effective region membership, closures and explicit successor history; SRC-01 account SERVICING/ORIGINATION and customer home histories; SRC-02 loan SERVICING/ORIGINATION history and source posting timestamp; SRC-04 responsible complaint intervals and as-of branches; supplied event/alert branches with business role/effective time. Date-only attribution requires reviewed cutoffs; no assumed midnight. Validate supplied event/snapshot branches against history, and review mismatches. SRC-03 alert branch may use only the explicitly approved linked-transaction alternative, otherwise Unavailable. Actual field aliases, transitions, delivery sections, revisions and sample reconciliation are NOT verified. Applicable source owners plus Data Owner must review before implementation/publication. Source ownership itself grants no access.
