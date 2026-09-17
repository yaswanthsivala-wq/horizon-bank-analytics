# Authoritative logical field inventory - DD-07 through DD-12

Current portfolio interpretation (2026-09-16): [G3 prerequisite register](g3-prerequisite-register.md) replaces real-source verification with finalized [synthetic contracts](synthetic-source-contract.md). Logical fields/policies remain approved; physical aliases are proposed until fixture implementation. Review roles are personas, not actual independent organizational approvals. Prior source-evidence prerequisites now mean synthetic contract/specification at G3 and executed fixture validation before publication. G3 remains unapproved.

Logical field-contract standard approved by the user on 2026-09-16, subject to the recorded conflict review. This is the sole Sprint 2 field inventory and source-to-target attribute contract. It replaces the base dictionary and DD-03 through DD-06 supplemental field tables. These are logical documentation contracts, not discovered source schemas. Source alias content remains Pending confirmation. Package/G3 and physical implementation remain **Draft — not approved**.

## Reading the contracts

Each field row gives its logical type/limit, requiredness, definition/source/derivation and classification. R = required on an accepted entity; C = required only under the stated condition; O = genuinely optional under the stated condition. A supplied optional value must validate. PKs below are mandatory/non-null; referenced parents must exist. Generated internal keys are opaque logical identities (legacy bigint labels denote internal keys), never casts of source IDs; sequence/identity implementation is deferred.

The approved Planning and Sprint 1 documents define business requirements; DD-01 through DD-06 define their approved design refinements. DD-07 approves this logical standard, not new banking facts. Supporting child entity names and key representations organize those existing obligations. Exact source aliases and unknown domains remain Pending confirmation, not invented business codes.

## Universal field contracts

- Source/version identifiers are text up to 128 characters, preserved exactly including leading zeros. Canonical codes/domain values are at most 50; names at most 200; synthetic contact/email at most 254 and Restricted; short reason/reference codes at most 100; narratives at most 1,000. No unrestricted serialized collections: references, mapping members, filters and control populations use the child entities below.
- Currency is exactly three uppercase ISO 4217 characters. Source money is decimal(20,4), checked against permitted currency minor units. Calculated averages/multipliers/rates are decimal(28,8). Financial aggregates/controls are decimal(28,4), always separated by currency. Counts are nonnegative 64-bit integers; signed adjustments/differences are not counts. DPD is an integer from 0 through 36,500; revisions begin at 1.
- No silent truncation, overflow, excess-scale reduction or rounding. Preserve the raw value and lineage; quarantine invalid evidence. Reject invalid domains and null required accepted-entity keys/values. Missing optional values remain null; missing conditional values prevent the dependent evaluation. DD-09 determines severity and publication disposition, not whether invalid values become valid.
- No missing business value defaults to zero, empty text, current date, UNKNOWN or a fabricated key. Generated IDs and ingestion instants are derivations. Unavailable controls and failed early runs retain unavailable states/reasons, never invented counts or PASS results.
- Instants are timezone-aware UTC with microsecond precision; derive business dates in America/Chicago. Require a source offset unless its contract explicitly declares a timezone. Ambiguous/nonexistent DST-local times are invalid without a documented source resolution. Greater-than-microsecond source precision is not silently reduced.
- Effective intervals are half-open [valid_from, valid_to), also for effective_from/effective_to. A null end means open-ended. End must exceed start. Reject overlap for the same source-qualified business key within a selected version/publication; preserved superseded correction versions do not represent simultaneously effective records.
- Source natural keys always include source_system. Transaction/payment keys identify immutable accepted event versions; identical revision replay retains the same key, while a corrected version gets a new key and predecessor. Publication membership chooses one version per natural source event; foreign references resolve the selected version. Natural event uniqueness is source_system + source_event_id within the selected publication, not across all retained revisions. Account, transaction, loan, payment, alert and complaint source IDs identify their source entity; branch natural history key is source_system/branch_id/valid_from; customer aliases are source_system/source_customer_id/interval. Synthetic master IDs are governed identity evidence, never guessed from contact data.
- Version/correction FKs reference existing parent records; predecessor chains are acyclic. Published snapshot analytical uniqueness is entity + business_date + publication_version, while snapshot-version PKs are immutable. Membership must agree with snapshot entity/date. Unavailable historical states use historical_coverage, not fake snapshot business values.
- Published assessment uniqueness is customer_key + business_date + rule_version + catalog_version + publication_version. Missing rule/catalog is allowed only on an unavailable attempt with explicit reason; never publish it as evaluated. One risk_evidence row per assessment/condition; child observations cannot multiply the condition. Deduplicate supporting source references.
- Every source-derived version has source_reference children; every applied mapping has applied_mapping children. Derived evidence links to its contributing source references. Typed live-owner references are logical FKs to the named entity's full PK, not serialized composite IDs. DD-10 explicitly permits minimized surviving audit associations to resolve an existing provenance envelope after payload expiry; analytical FKs remain live-parent-only. Raw file hash is source_extract.checksum; row locator and ingestion/run lineage are in source_reference.
- Restricted: identity, contact, source customer identifiers and full account numbers; full account numbers only in restricted/raw access, reporting uses fixed masking plus final four. Controlled: financial, case and risk detail. Audit: operational controls/versions. Audit references to Restricted/Controlled data inherit its access restrictions. Narratives are Controlled/Restricted as appropriate and excluded from ordinary exports. Raw/crosswalk stores are excluded from ordinary exports; DD-08 approves logical entitlements, not weaker field classifications.

## Cross-field integrity

- Evaluate overlap by business identity without including interval start: source_system/source_customer_id for identity aliases; customer_key for customer_version; source_system/branch_id for branch; account_key/customer_key/relationship_role and loan_key/customer_key/relationship_role for bridges; account_key or alert_key for effective risk states. Apply selected-version scope so preserved correction history is not discarded. Deduplicate effective relationship paths before exposure or initiation lookup.
- An evaluated assessment has exactly one row for each of its catalog's five conditions, including explicit Unknown rows. Condition rule references must match catalog_rule; classification configuration and condition parameter versions resolve their defined parents. triggered_count/unknown_count agree with those five outcomes. Missing-catalog attempts do not fabricate condition outcomes.
- complaint_snapshot.created_at and priority_at_creation agree with the immutable source-supported creation evidence. Current priority may change independently. Historical closure/reopening events, their source references and selected publication determine final_closed_at; a future event cannot change an earlier as-of state.
- Every live typed owner reference resolves to the full declared PK of owner_entity; DD-10 expired-payload audit associations instead resolve their existing provenance envelope under the explicit lifecycle contract. Mapping eligibility rows resolve their four-column mapping_entry parent; source-reference/run/financial-control extract tuples resolve source_extract. Risk item assessment/condition pairs resolve risk_evidence. All supplied optional parent references resolve as well.
- Filter/configuration values have exactly one matching typed member. A code/numeric/date/reference value is validated against the selected parameter/filter/criterion domain; source aliases and domain content are not inferred from the storage limit. Narrative or serialized objects cannot be hidden inside these short values.

## Calculation precision and inherited rules

DD-05 requires the unrounded RC-01 average. Preserve exact same-currency prior sum and count: for count n > 0, compare current_absolute_amount * n >= 3 * prior_amount_sum using exact logical arithmetic, with checked precision/overflow and no rounded intermediate. decimal(28,8) prior_average holds an exactly representable result only; a repeating decimal is represented by its exact sum/count evidence, not silently rounded. This representation limit alone does not turn complete evidence into Unknown. Any display approximation or wider physical arithmetic is deferred for explicit review; the exact fractional value remains available. Other nonrepresentable calculated rates likewise retain numerator/denominator evidence; no implicit rounding policy is authorized.

DD-02 non-additive ownership exposure remains separate from DD-05 initiation. DD-04 RC-03 and K05/K06 retain DPD > 30. K06 retains the approved principal sum formula; zero is valid, negative quarantined, missing incomplete. DD-06 status populations, priority-at-creation SLA and publication revisions remain unchanged. All source-specific mapping content must be finalized before publication.

## Entity inventory


## branch

Logical PK: `branch_key`. Grain: One effective branch version. Proposed origin: SRC-05.branches.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| branch_key | bigint | R | generated | Controlled |
| branch_id | text(128) | R | branch_id | Controlled |
| branch_name | text(200) | R | branch_name | Controlled |
| region_id | text(128) | R | region_id | Controlled |
| valid_from | instant UTC(6) | R | valid_from | Controlled |
| valid_to | instant UTC(6) | O: open-ended interval | Exclusive interval end; null open-ended, never defaulted current date | Controlled |
| source_system | text(50) | R | Source namespace; natural source ID must be qualified by this value | Controlled |
| region_version | text(128) | R | FK region.region_version; applicable at branch interval; region_id remains source identity | Controlled |
| organization_key | text(128) | R | FK organizational_unit.organization_key; BRANCH stable identity | Controlled |
| source_version | text(128) | R | Reviewed source version | Controlled |
| supersedes_branch_key | bigint | C: correction | FK branch.branch_key; immutable correction predecessor | Controlled |
| correction_action_id | text(128) | C: correction | FK governance_action.action_id; reason, affected interval and independent review | Controlled |
| affected_from | instant UTC(6) | C: correction | Corrected interval start | Controlled |
| affected_to | instant UTC(6) | O: open-ended or not correction | Exclusive corrected interval end; null open-ended | Controlled |
| correction_reason | text(200) | C: correction | Sanitized correction reason | Controlled |
| original_effective_end | instant UTC(6) | C: ended interval | Original effective-end retention anchor; corrections do not restart clock | Controlled |


## customer

Logical PK: `customer_key`. Grain: One canonical customer. Proposed origin: SRC-01.customers.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| customer_key | bigint | R | generated | Controlled |
| display_name | text(200) | R | display_name | Restricted |
| synthetic_master_id | text(128) | R | synthetic_master_id | Restricted |
| contact | text(254) | O: not applicable or not supplied; supplied values must validate | contact | Restricted |
| source_system | text(50) | R | Source namespace; natural source ID must be qualified by this value | Controlled |
| source_customer_id | text(128) | R | SRC-01.customer_id; preserve source identifier, distinct from synthetic_master_id | Restricted |


## customer_identity

Logical PK: `identity_key`. Grain: One effective source alias mapping. Proposed origin: reviewed identity mapping.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| identity_key | bigint | R | generated | Controlled |
| customer_key | bigint | R | resolved customer; FK customer.customer_key | Controlled |
| source_system | text(50) | R | source namespace | Controlled |
| source_customer_id | text(128) | R | source customer_id | Restricted |
| valid_from | instant UTC(6) | R | reviewed effective start | Controlled |
| valid_to | instant UTC(6) | O: open-ended interval | Exclusive interval end; null open-ended, never defaulted current date | Controlled |
| match_method | text(50) | R | deterministic method | Controlled |
| review_state | text(50) | R | review outcome | Controlled |
| approval_reference | text(100) | C: approved identity mapping | Review evidence reference required before Approved | Controlled |


## customer_version

Logical PK: `customer_version_key`. Grain: One effective customer classification. Proposed origin: SRC-01.customers.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| customer_version_key | bigint | R | generated | Controlled |
| customer_key | bigint | R | customer_id resolved; FK customer.customer_key | Controlled |
| segment | text(50) | R | segment | Controlled |
| branch_key | bigint | R | home_branch_id resolved; FK branch.branch_key | Controlled |
| valid_from | instant UTC(6) | R | effective change boundary | Controlled |
| valid_to | instant UTC(6) | O: open-ended interval | Exclusive interval end; null open-ended, never defaulted current date | Controlled |


## account

Logical PK: `account_key`. Grain: One source-qualified account. Proposed origin: SRC-01.accounts.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| account_key | bigint | R | generated | Controlled |
| source_account_id | text(128) | R | account_id | Controlled |
| account_number | text(128) | R | account_number | Restricted |
| masked_account | text(128) | R | Fixed mask plus final four source account characters; not a relational key | Controlled |
| branch_key | bigint | R | Selected-current convenience projection only; historical authority is account_branch_assignment; FK branch.branch_key | Controlled |
| account_type | text(50) | R | account_type | Controlled |
| opened_date | date | R | opened_date | Controlled |
| closed_date | date | C: closed account | Source closure date; absent for an open account | Controlled |
| source_system | text(50) | R | Source namespace; natural source ID must be qualified by this value | Controlled |


## account_customer

Logical PK: `account_key + customer_key + relationship_role + valid_from`. Grain: One ownership role interval. Proposed origin: SRC-01.holders.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| account_key | bigint | R | account_id resolved; FK account.account_key | Controlled |
| customer_key | bigint | R | customer_id resolved; FK customer.customer_key | Controlled |
| relationship_role | text(50) | R | source ownership role; source code mapping Pending confirmation | Controlled |
| valid_from | instant UTC(6) | R | ownership_start | Controlled |
| valid_to | instant UTC(6) | O: open-ended interval | Exclusive interval end; null open-ended, never defaulted current date | Controlled |


## transaction

Logical PK: `transaction_key`. Grain: One immutable source-qualified event version; one selected natural event per publication. Proposed origin: SRC-01.transactions.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| transaction_key | bigint | R | generated | Controlled |
| source_transaction_id | text(128) | R | transaction_id | Controlled |
| account_key | bigint | R | account_id resolved; FK account.account_key | Controlled |
| branch_key | bigint | R | account branch at occurred_at; FK branch.branch_key | Controlled |
| occurred_at | instant UTC(6) | R | occurred_at | Controlled |
| amount | decimal(20,4) | R | amount | Controlled |
| currency | char(3) | R | currency | Controlled |
| transaction_type | text(50) | R | transaction_type | Controlled |
| raw_status | text(50) | R | status | Controlled |
| status | text(50) | R | versioned status mapping | Controlled |
| source_system | text(50) | R | Source namespace; natural source ID must be qualified by this value | Controlled |
| source_initiating_customer_id | text(128) | O: not applicable or not supplied; supplied values must validate | SRC-01 initiating-customer identifier when supplied; invalid supplied ID gives Unknown and identity exception, no fallback | Restricted |
| debit_credit_direction | text(50) | R | Source debit/credit direction retained; source alias mapping required | Controlled |
| absolute_comparison_amount | decimal(20,4) | C: eligible RC-01 comparison | abs(amount), nonzero; signed amount retained | Controlled |
| business_date | date | R | Derived Chicago event business date; source manifest date retained separately | Controlled |
| source_version | text(128) | R | Immutable source event version; source contract must supply or reliably identify it | Controlled |
| batch_revision | integer >= 1 | R | Delivered source_extract revision through source_reference | Controlled |
| supersedes_event_key | bigint | O | FK transaction.transaction_key; existing acyclic predecessor; correction retains original fields | Controlled |

## loan

Logical PK: `loan_key`. Grain: One source-qualified loan. Proposed origin: SRC-02.loans.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| loan_key | bigint | R | generated | Controlled |
| source_loan_id | text(128) | R | loan_id | Controlled |
| branch_key | bigint | R | Selected-current convenience projection only; historical authority is loan_branch_assignment; FK branch.branch_key | Controlled |
| loan_type | text(50) | R | loan_type | Controlled |
| originated_date | date | R | originated_date | Controlled |
| source_system | text(50) | R | Source namespace; natural source ID must be qualified by this value | Controlled |
| contractual_currency | char(3) | R | Source loan contractual currency; all DD-11 obligations/payments/allocations/unapplied/adjustments must agree; no conversion | Controlled |


## loan_customer

Logical PK: `loan_key + customer_key + relationship_role + valid_from`. Grain: One loan/customer/relationship-role interval. Proposed source section: SRC-02.borrowers; all borrower/co-borrower relationships are required by approved DD-02. Role source aliases remain Pending confirmation.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| loan_key | bigint | R | loan_id resolved; FK loan.loan_key | Controlled |
| customer_key | bigint | R | borrower_customer_id resolved through crosswalk; FK customer.customer_key | Controlled |
| relationship_role | text(50) | R | source borrower/co-borrower role; domain Pending confirmation | Controlled |
| valid_from | instant UTC(6) | R | relationship_start | Controlled |
| valid_to | instant UTC(6) | O: open-ended interval | Exclusive interval end; null open-ended, never defaulted current date | Controlled |


## loan_snapshot

Logical PK: `snapshot_version`. Grain: One immutable loan/date snapshot version; one selected version per publication. Proposed origin: SRC-02.positions.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| loan_key | bigint | R | loan_id resolved; FK loan.loan_key | Controlled |
| business_date | date | R | business_date | Controlled |
| currency | char(3) | R | currency | Controlled |
| days_past_due | integer [0,36500] | R | days_past_due | Controlled |
| status | text(50) | R | versioned status mapping | Controlled |
| as_of_cutoff_at | instant UTC(6) | R | source-supported knowledge cutoff for business_date; exact cutoff remains a source-contract detail | Controlled |
| batch_revision | integer >= 1 | R | source_extract.revision; exact delivered batch revision | Controlled |
| source_version | text(128) | R | source record/state version reference; if absent, source contract must define a reliable version identity | Controlled |
| snapshot_version | text(128) | R | proposed immutable version identifier linking preserved values to publication/correction history | Controlled |
| reconstruction_reference | text(100) | C: reliably reconstructed snapshot | required evidence/method/version for reconstructed state | Controlled |
| state_availability | text(50) | R | supplied or reliably_reconstructed for accepted snapshot; unavailable expectations go in historical_coverage | Controlled |
| supersedes_snapshot_version | text(128) | O: not applicable or not supplied; supplied values must validate | FK loan_snapshot.snapshot_version; existing predecessor; acyclic correction chain | Controlled |
| correction_reference | text(100) | C: corrected version | Correction approval/evidence reference; predecessor required for correction of existing version | Controlled |
| outstanding_principal | decimal(20,4) | R | SRC-02 outstanding_principal; zero valid; negative quarantined; missing incomplete DD-09; no absolute conversion or positive-only population filter | Controlled |


## loan_payment

Logical PK: `payment_key`. Grain: One immutable actual-payment version; one selected natural payment per publication. Proposed origin: SRC-02.payments.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| payment_key | bigint | R | generated | Controlled |
| source_payment_id | text(128) | R | payment_id | Controlled |
| loan_key | bigint | R | loan_id resolved; FK loan.loan_key | Controlled |
| paid_at | instant UTC(6) | R | paid_at | Controlled |
| amount | decimal(20,4) | R | Positive canonical actual-payment amount; zero/negative invalid, preserve raw signed quarantine evidence | Controlled |
| currency | char(3) | R | Must equal referenced loan.contractual_currency; no conversion | Controlled |
| source_system | text(50) | R | Source namespace; natural source ID must be qualified by this value | Controlled |
| business_date | date | R | Derived Chicago event business date; source manifest date retained separately | Controlled |
| source_version | text(128) | R | Immutable source event version; source contract must supply or reliably identify it | Controlled |
| batch_revision | integer >= 1 | R | Delivered source_extract revision through source_reference | Controlled |
| supersedes_event_key | bigint | O | FK loan_payment.payment_key; existing acyclic predecessor; correction retains original fields | Controlled |
| raw_status | text(50) | R | Source payment status; approved mapping required | Controlled |
| status | text(50) | R | PENDING, POSTED, FAILED or CANCELLED; only POSTED financially effective | Controlled |
| correction_reference | text(100) | C: corrected event version | Independent correction evidence; supersedes_event_key is data correction, not business adjustment | Controlled |
| posted_at | instant UTC(6) | C: POSTED | Synthetic SRC-02 posted_at: required for POSTED, null otherwise, >= paid_at; offset-qualified instant normalized UTC; paid_at remains event evidence | Controlled |


## fraud_alert

Logical PK: `alert_key`. Grain: One source-qualified alert. Proposed origin: SRC-03.alerts.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| alert_key | bigint | R | generated | Controlled |
| source_alert_id | text(128) | R | alert_id | Controlled |
| customer_key | bigint | R | customer_id resolved; FK customer.customer_key | Controlled |
| transaction_key | bigint | O: alert linked to transaction | FK transaction.transaction_key when supplied; unlinked alerts excluded from K04 numerator | Controlled |
| alert_time | instant UTC(6) | R | alert_time | Controlled |
| severity | text(50) | R | severity | Controlled |
| case_status | text(50) | R | case_status | Controlled |
| reason | text(1000) | R | reason; excluded from ordinary exports | Controlled |
| source_system | text(50) | R | Source namespace; natural source ID must be qualified by this value | Controlled |


## complaint

Logical PK: `complaint_key`. Grain: One source-qualified complaint. Proposed origin: SRC-04.complaints.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| complaint_key | bigint | R | generated | Controlled |
| source_complaint_id | text(128) | R | complaint_id | Controlled |
| customer_key | bigint | R | customer_id resolved; FK customer.customer_key | Controlled |
| branch_key | bigint | R | branch_id resolved; FK branch.branch_key | Controlled |
| priority | text(50) | R | priority | Controlled |
| channel | text(50) | R | channel | Controlled |
| status | text(50) | R | status | Controlled |
| source_system | text(50) | R | Source namespace; natural source ID must be qualified by this value | Controlled |
| created_at | instant UTC(6) | R | Immutable original SRC-04 creation instant; original_created_at may only be a documented source alias | Controlled |
| priority_at_creation | text(50) | C: SLA evaluation | Immutable creation priority, source or reliable historical reconstruction; Critical/High/Medium/Low | Controlled |
| closed_at | instant UTC(6) | C: closed selected state | SRC-04 closure known in selected as-of/publication; null for open/REOPENED; contradictory status/closure quarantined | Controlled |
| final_closed_at | instant UTC(6) | C: finally closed in selected publication | Derived original-creation-to-final-closure history; never use future closure evidence | Controlled |


## complaint_snapshot

Logical PK: `snapshot_version`. Grain: One immutable complaint/date snapshot version; one selected version per publication. Proposed origin: SRC-04.complaints daily state.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| complaint_key | bigint | R | complaint_id resolved; FK complaint.complaint_key | Controlled |
| business_date | date | R | manifest business_date | Controlled |
| branch_key | bigint | R | branch_id resolved at date; FK branch.branch_key | Controlled |
| priority | text(50) | R | priority at cutoff | Controlled |
| channel | text(50) | R | channel at cutoff | Controlled |
| status | text(50) | R | status at cutoff | Controlled |
| as_of_cutoff_at | instant UTC(6) | R | source-supported knowledge cutoff for business_date; exact cutoff remains a source-contract detail | Controlled |
| batch_revision | integer >= 1 | R | source_extract.revision; exact delivered batch revision | Controlled |
| source_version | text(128) | R | source record/state version reference; if absent, source contract must define a reliable version identity | Controlled |
| snapshot_version | text(128) | R | proposed immutable version identifier linking preserved values to publication/correction history | Controlled |
| reconstruction_reference | text(100) | C: reliably reconstructed snapshot | required evidence/method/version for reconstructed state | Controlled |
| created_at | instant UTC(6) | R | Immutable original SRC-04 creation instant; original_created_at may only be a documented source alias | Controlled |
| priority_at_creation | text(50) | C: SLA evaluation | Immutable creation priority, source or reliable historical reconstruction; Critical/High/Medium/Low | Controlled |
| closed_at | instant UTC(6) | C: closed selected state | SRC-04 closure known in selected as-of/publication; null for open/REOPENED; contradictory status/closure quarantined | Controlled |
| state_availability | text(50) | R | supplied or reliably_reconstructed for accepted snapshot; unavailable expectations go in historical_coverage | Controlled |
| supersedes_snapshot_version | text(128) | O: not applicable or not supplied; supplied values must validate | FK complaint_snapshot.snapshot_version; existing predecessor; acyclic correction chain | Controlled |
| correction_reference | text(100) | C: corrected version | Correction approval/evidence reference; predecessor required for correction of existing version | Controlled |


## risk_assessment

Logical PK: `assessment_key`. Grain: One assessment attempt; published uniqueness includes customer/date/rule/catalog/publication. Proposed origin: derived after validation.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| assessment_key | bigint | R | generated | Controlled |
| customer_key | bigint | R | resolved customer; FK customer.customer_key | Controlled |
| business_date | date | R | assessment date | Controlled |
| evidence_state | text(50) | R | complete or incomplete | Controlled |
| rule_version | text(128) | C: evaluated assessment | FK configuration_version.configuration_version; classification configuration, distinct from condition rule version | Controlled |
| catalog_version | text(128) | C: evaluated assessment | FK catalog_version.catalog_version | Controlled |
| assessment_at | instant UTC(6) | R | Assessment as-of instant | Controlled |
| unknown_count | int64 >= 0 | C: valid catalog evaluation | Number of Unknown conditions, at most five | Controlled |
| unavailable_reason | text(100) | C: unavailable assessment | Explicit missing version/catalog or evidence reason | Controlled |
| publication_version | text(128) | C: published assessment | FK publication.publication_version | Controlled |
| triggered_count | int64 >= 0 | C: valid catalog evaluation | Count of Triggered conditions, at most five; never fabricated zero on failed attempt | Controlled |
| classification | text(50) | R | DD-04 Provisional high risk / Incomplete evidence - classification unavailable / Not high risk under current rule / Classification unavailable | Controlled |


## risk_evidence

Logical PK: `assessment_key + condition_id`. Grain: One condition per assessment. Proposed origin: derived from validated facts.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| assessment_key | bigint | R | assessment reference; FK risk_assessment.assessment_key | Controlled |
| condition_id | text(50) | R | configured condition | Controlled |
| trigger_state | text(50) | R | Triggered Not_triggered or Unknown | Controlled |
| observed_value | decimal(28,8) | C: applicable valid numeric condition observation | Calculated numeric observation; supporting items retain individual values | Controlled |
| threshold | decimal(28,8) | C: numeric configured threshold | Approved numeric parameter; mapping/SLA thresholds also retain threshold_reference | Controlled |
| rule_version | text(128) | C: evaluable condition | FK rule_version.rule_version | Controlled |
| missing_evidence_reason | text(100) | C: Unknown | Missing evidence reason; Unknown never becomes Not triggered | Controlled |
| threshold_reference | text(100) | C: configured condition | Parameter or SLA/mapping reference; numeric threshold only when applicable | Controlled |


## rule_config

Logical PK: `configuration_version + parameter_id`. Typed parameters of one configuration version; no serialized value.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| parameter_id | text(50) | R | parameter name | Controlled |
| value_type | text(50) | R | type | Controlled |
| configuration_version | text(128) | R | FK configuration_version.configuration_version | Controlled |
| numeric_value | decimal(28,8) | C: matching value_type | Exactly one matching typed value required; no empty serialized configuration | Controlled |
| integer_value | int64 >= 0 | C: matching value_type | Exactly one matching typed value required; no empty serialized configuration | Controlled |
| code_value | text(50) | C: matching value_type | Exactly one matching typed value required; no empty serialized configuration | Controlled |
| reference_value | text(100) | C: matching value_type | Exactly one matching typed value required; no empty serialized configuration | Controlled |
| boolean_value | boolean | C: matching value_type | Exactly one matching typed value required; no empty serialized configuration | Controlled |


## pipeline_run

Logical PK: `run_id`. Grain: One attempted daily processing run. Proposed origin: future process audit.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| run_id | text(128) | R | generated | Audit |
| business_date | date | R | designated reporting date | Audit |
| started_at | instant UTC(6) | R | run start | Audit |
| status | text(50) | R | run state | Audit |
| source_rows | int64 >= 0 | C: corresponding measured control available | Observed count; null with unavailable reason for failed early/unmeasured run | Audit |
| accepted_rows | int64 >= 0 | C: corresponding measured control available | Observed count; null with unavailable reason for failed early/unmeasured run | Audit |
| rejected_rows | int64 >= 0 | C: corresponding measured control available | Observed count; null with unavailable reason for failed early/unmeasured run | Audit |
| excluded_rows | int64 >= 0 | C: corresponding measured control available | Observed count; null with unavailable reason for failed early/unmeasured run | Audit |
| required_cells | int64 >= 0 | C: corresponding measured control available | Observed count; null with unavailable reason for failed early/unmeasured run | Audit |
| present_cells | int64 >= 0 | C: corresponding measured control available | Observed count; null with unavailable reason for failed early/unmeasured run | Audit |
| unavailable_reason | text(100) | C: unavailable run control | Explain unavailable counters or incomplete early attempt | Audit |
| ended_at | instant UTC(6) | C: attempt ended | Completion instant; null while attempt open | Audit |
| readiness_at | instant UTC(6) | C: publication ready | Validated readiness instant, not fabricated on failure | Audit |
| publication_version | text(128) | C: successful publication | FK publication.publication_version | Audit |


## source_extract

Logical PK: `source_system + entity_name + business_date + revision`. One source/entity/business-date/revision manifest; replay associations are separate.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| extract_id | text(128) | R | batch identity | Audit |
| source_system | text(50) | R | source namespace | Audit |
| entity_name | text(50) | R | manifest section | Audit |
| business_date | date | R | manifest date | Audit |
| revision | integer >= 1 | R | revision | Audit |
| delivery_mode | text(50) | R | contract mode | Audit |
| schema_version | text(128) | R | contract version | Audit |
| cutoff_at | instant UTC(6) | R | manifest cutoff | Audit |
| extracted_at | instant UTC(6) | R | extraction instant | Audit |
| checksum | text(128) | R | manifest checksum | Audit |
| row_count | int64 >= 0 | R | manifest row count | Audit |
| checksum_algorithm | text(50) | R | SHA-256 under DD-09 | Audit |
| checksum_encoding | text(50) | R | Agreed digest representation; actual encoding Pending confirmation | Audit |
| content_encoding | text(50) | R | Agreed delivered-content encoding; no invented source value | Audit |
| checksum_scope_reference | text(100) | R | Approved delivered-content contract defining exact checksum coverage | Audit |


## quality_exception

Logical PK: `exception_key`. Grain: One rule finding for a source row or batch. Proposed origin: future validation audit.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| exception_key | bigint | R | generated | Audit |
| run_id | text(128) | R | run reference; FK pipeline_run.run_id | Audit |
| extract_id | text(128) | R | batch reference | Audit |
| row_locator | text(100) | O: not applicable or not supplied; supplied values must validate | restricted row pointer | Audit |
| rule_id | text(50) | R | quality rule | Audit |
| reason_code | text(100) | R | reason | Audit |
| severity | text(50) | R | Effective DD-09 CRITICAL, ERROR, WARNING or INFO; escalation retained in candidate_control | Audit |
| disposition | text(50) | R | DD-09 quarantine, suppressed detail, approved exclusion, corrected resolution or blocked candidate; never bypass CRITICAL | Audit |
| source_system | text(50) | R | Composite FK to source_extract; extract_id alone is not a qualified key | Audit |
| entity_name | text(50) | R | Composite FK to source_extract; extract_id alone is not a qualified key | Audit |
| business_date | date | R | Composite FK to source_extract; extract_id alone is not a qualified key | Audit |
| revision | integer >= 1 | R | Composite FK to source_extract; extract_id alone is not a qualified key | Audit |


## reconciliation_result

Logical PK: `reconciliation_key`. Grain: One population/measure comparison in a run. Proposed origin: future reconciliation audit.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| reconciliation_key | bigint | R | generated | Audit |
| run_id | text(128) | R | run reference; FK pipeline_run.run_id | Audit |
| extract_id | text(128) | R | batch reference | Audit |
| measure | text(50) | R | row count or financial field | Audit |
| currency | char(3) | O: not applicable or not supplied; supplied values must validate | required for financial measure | Audit |
| explanation_reference | text(100) | O: not applicable or not supplied; supplied values must validate | required for adjustment | Audit |
| population_key | internal key | R | FK control_population.population_key | Audit |
| source_value | decimal(28,4) | C: available financial comparison | Currency-separated signed financial control component; not used for count measures | Audit |
| target_value | decimal(28,4) | C: available financial comparison | Currency-separated signed financial control component; not used for count measures | Audit |
| explained_adjustment | decimal(28,4) | C: available financial comparison | Currency-separated signed financial control component; not used for count measures | Audit |
| variance | decimal(28,4) | C: available financial comparison | Currency-separated signed financial control component; not used for count measures | Audit |
| source_count | int64 >= 0 | C: available count comparison | Exact count control; adjustment and difference are signed, never an event count | Audit |
| target_count | int64 >= 0 | C: available count comparison | Exact count control; adjustment and difference are signed, never an event count | Audit |
| adjustment_count | int64 | C: available count comparison | Exact count control; adjustment and difference are signed, never an event count | Audit |
| count_variance | int64 | C: available count comparison | Exact count control; adjustment and difference are signed, never an event count | Audit |
| unavailable_reason | text(100) | C: unavailable comparison | Unavailable state, not PASS or fabricated counts | Audit |
| source_system | text(50) | R | Composite FK to source_extract; extract_id alone is not a qualified key | Audit |
| entity_name | text(50) | R | Composite FK to source_extract; extract_id alone is not a qualified key | Audit |
| business_date | date | R | Composite FK to source_extract; extract_id alone is not a qualified key | Audit |
| revision | integer >= 1 | R | Composite FK to source_extract; extract_id alone is not a qualified key | Audit |
| status | text(50) | R | Explicit pass/fail/unavailable comparison state; required unavailable or unexplained residual blocks under DD-09 | Audit |


## export_event

Logical PK: `event_key`. One attempted simulated export, including denied attempts. Filters, entitlements and approvals are child rows.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| event_key | bigint | R | Generated attempt identity | Audit |
| user_identity | text(128) | R | Opaque requesting principal ID; no customer identity or credentials | Audit |
| active_role | text(50) | C: selected role supplied | Exactly one selected role; missing or unauthorized selection denies; never union assigned roles | Audit |
| policy_version | text(128) | R | FK access_policy.policy_version | Audit |
| report | text(200) | R | Controlled report identifier; no free-text sensitive content | Audit |
| format | text(50) | R | Requested format; authorized CSV/PDF only, unsupported attempts denied | Audit |
| requested_at | instant UTC(6) | R | Request receipt instant; replaces ambiguous exported_at | Audit |
| authorization_checked_at | instant UTC(6) | C: execution or terminal denial | Current role/scope/entitlement check instant, including attempts with no matching grant | Audit |
| completed_at | instant UTC(6) | C: terminal attempt | Terminal allow/deny completion instant; >= requested_at; absent while preparing | Audit |
| decision | text(50) | C: terminal attempt | Allow or deny; no fabricated allow during preparation | Audit |
| denial_reason | text(100) | C: denied attempt | Sanitized reason code; no payload or narrative | Audit |
| publication_version | text(128) | C: selected publication exists | FK publication.publication_version; record selection even when denied | Audit |
| row_count | int64 >= 0 | C: measured output count | Released output rows; denied output is zero if measured; unavailable remains null | Audit |
| output_classification | text(50) | R | Requested output classification; no sensitive output on denial | Audit |
| duration_seconds | decimal(28,8) | C: completed measured attempt | Observed nonnegative duration | Audit |

## complaint_history_event

Logical PK: `history_event_key`. DD-06 SRC-04 closure/reopening history.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| history_event_key | internal key | R | Generated PK | Controlled |
| complaint_key | bigint | R | FK complaint.complaint_key | Controlled |
| event_type | text(50) | R | Source-mapped closure or reopening event; source aliases pending | Controlled |
| event_at | instant UTC(6) | R | SRC-04 event instant known for selected publication | Controlled |
| source_version | text(128) | R | Source state/version identity | Controlled |
| publication_version | text(128) | C: published history | FK publication.publication_version | Controlled |


## loan_snapshot_publication

Logical PK: `publication_version + loan_key + business_date`. DD-03 selected snapshot membership; entity/date must match snapshot.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| publication_version | text(128) | R | FK publication.publication_version | Controlled |
| loan_key | bigint | R | FK loan.loan_key | Controlled |
| business_date | date | R | America/Chicago business date | Controlled |
| snapshot_version | text(128) | R | FK loan_snapshot.snapshot_version | Controlled |


## complaint_snapshot_publication

Logical PK: `publication_version + complaint_key + business_date`. DD-03 selected snapshot membership; entity/date must match snapshot.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| publication_version | text(128) | R | FK publication.publication_version | Controlled |
| complaint_key | bigint | R | FK complaint.complaint_key | Controlled |
| business_date | date | R | America/Chicago business date | Controlled |
| snapshot_version | text(128) | R | FK complaint_snapshot.snapshot_version | Controlled |


## historical_coverage

Logical PK: `coverage_key`. DD-03 explicit unavailable state coverage; unique entity/source-qualified business key/date/publication.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| coverage_key | internal key | R | Generated PK | Controlled |
| entity_name | text(50) | R | Loan or complaint snapshot population | Controlled |
| source_system | text(50) | R | Source namespace | Controlled |
| source_record_id | text(128) | R | Expected source entity ID | Controlled |
| business_date | date | R | Expected Chicago business date | Controlled |
| publication_version | text(128) | C: published coverage | FK publication.publication_version | Controlled |
| state_availability | text(50) | R | Unavailable state, not a fabricated accepted snapshot | Controlled |
| unavailable_reason | text(100) | R | Missing or unreliable historical evidence reason | Controlled |


## risk_evidence_item

Logical PK: `evidence_item_key`. DD-04 multiple observations per one assessment/condition; unique assessment/condition/source reference/comparison.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| evidence_item_key | internal key | R | Generated PK | Controlled |
| assessment_key | bigint | R | Composite FK with condition_id to risk_evidence | Controlled |
| condition_id | text(50) | R | Composite FK with assessment_key to risk_evidence | Controlled |
| source_reference_key | internal key | R | FK source_reference.source_reference_key | Controlled |
| comparison_key | internal key | C: RC-01 comparison evidence | FK rc01_comparison.comparison_key | Controlled |
| observed_value | decimal(28,8) | C: numeric observation | Validated observation; nonnumeric observation through source reference | Controlled |
| observed_at | instant UTC(6) | R | Observation as-of instant supported by source evidence | Controlled |
| correction_reference | text(100) | C: corrected observation | Review/correction reference; original observation retained | Controlled |

## rc01_comparison

Logical PK: `comparison_key`. DD-05 transaction/account comparison; unresolved customer remains null; deduplicate transaction/rule/publication/recalculation revision.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| comparison_key | internal key | R | Generated PK | Restricted |
| transaction_key | bigint | R | FK transaction.transaction_key | Restricted |
| account_key | bigint | R | FK account.account_key; must match transaction | Restricted |
| customer_key | bigint | C: resolved valid initiator or sole owner | FK customer.customer_key; unresolved joint evidence stays account-grain | Restricted |
| signed_source_amount | decimal(20,4) | C: valid supplied amount | Source signed transaction.amount retained | Restricted |
| absolute_comparison_amount | decimal(20,4) | C: eligible comparison | Absolute nonzero signed_source_amount | Restricted |
| debit_credit_direction | text(50) | C: supplied valid direction | Retained source direction | Restricted |
| event_at | instant UTC(6) | R | Transaction occurred_at | Restricted |
| window_start | instant UTC(6) | R | Event minus 90 calendar days using America/Chicago semantics | Restricted |
| window_end | instant UTC(6) | R | Exactly event_at; current/future evidence excluded | Restricted |
| history_count | int64 >= 0 | C: available history | Eligible prior count; minimum five for valid comparison | Restricted |
| prior_amount_sum | decimal(28,4) | C: complete valid prior evidence | Exact eligible absolute amount sum in same currency; supports unrounded mean | Restricted |
| prior_average | decimal(28,8) | C: exactly representable valid mean | Sum/count; retain exact sum and count when decimal representation repeats; no rounding for decision | Restricted |
| multiplier | decimal(28,8) | R | Approved configured value 3 | Restricted |
| currency | char(3) | C: valid mapped currency | Same ISO 4217 currency for current and prior events; no conversion | Restricted |
| window_complete | boolean | R | Coverage evidence confirms complete 90 days within approved 24 months | Restricted |
| attribution_method | text(50) | R | Valid mapped source initiator; absent initiator sole owner; otherwise unresolved | Restricted |
| missing_evidence_reason | text(100) | C: Unknown | Joint absent initiator: JOINT_ACCOUNT_INITIATOR_UNRESOLVED; supplied invalid ID is separate identity exception | Restricted |
| recalculation_revision | integer >= 1 | R | Revision starts at 1; corrections create a new version | Restricted |
| rule_version | text(128) | R | FK rule_version.rule_version | Restricted |
| publication_version | text(128) | C: published evidence | FK publication.publication_version | Restricted |
| supersedes_comparison_key | internal key | O: not applicable or not supplied; supplied values must validate | FK rc01_comparison.comparison_key; existing acyclic predecessor | Restricted |


## account_restriction_state

Logical PK: `state_version`. DD-04 source-supported effective state history; unique source-qualified parent/effective start/source version.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| state_version | text(128) | R | Immutable generated version PK | Controlled |
| account_key | bigint | R | FK account.account_key | Controlled |
| effective_from | instant UTC(6) | R | Source-supported effective start | Controlled |
| effective_to | instant UTC(6) | O: not applicable or not supplied; supplied values must validate | Exclusive end; null open-ended | Controlled |
| state_as_of_at | instant UTC(6) | R | Source-supported knowledge instant | Controlled |
| source_version | text(128) | R | Source state version | Controlled |
| publication_version | text(128) | C: published state | FK publication.publication_version | Controlled |
| supersedes_state_version | text(128) | O: not applicable or not supplied; supplied values must validate | FK account_restriction_state.state_version; existing acyclic predecessor | Controlled |
| raw_risk_restriction_status | text(50) | R | Source value retained; invalid domain quarantined with raw evidence | Controlled |
| risk_restriction_status | text(50) | C: valid approved mapping | DD-06 canonical mapping; unmapped causes Unknown, never fabricated negative finding | Controlled |


## fraud_alert_state

Logical PK: `state_version`. DD-04 source-supported effective state history; unique source-qualified parent/effective start/source version.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| state_version | text(128) | R | Immutable generated version PK | Controlled |
| alert_key | bigint | R | FK fraud_alert.alert_key | Controlled |
| effective_from | instant UTC(6) | R | Source-supported effective start | Controlled |
| effective_to | instant UTC(6) | O: not applicable or not supplied; supplied values must validate | Exclusive end; null open-ended | Controlled |
| state_as_of_at | instant UTC(6) | R | Source-supported knowledge instant | Controlled |
| source_version | text(128) | R | Source state version | Controlled |
| publication_version | text(128) | C: published state | FK publication.publication_version | Controlled |
| supersedes_state_version | text(128) | O: not applicable or not supplied; supplied values must validate | FK fraud_alert_state.state_version; existing acyclic predecessor | Controlled |
| raw_case_status | text(50) | R | Source value retained; invalid domain quarantined with raw evidence | Controlled |
| case_status | text(50) | C: valid approved mapping | DD-06 canonical mapping; unmapped causes Unknown, never fabricated negative finding | Controlled |
| raw_severity | text(50) | R | Source value retained; invalid domain quarantined with raw evidence | Controlled |
| severity | text(50) | C: valid approved mapping | DD-06 canonical mapping; unmapped causes Unknown, never fabricated negative finding | Controlled |


## publication

Logical PK: `publication_version`. DD-07 defined version parent; immutable identity, retained corrections.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| publication_version | text(128) | R | Version identifier PK; preserve exact identifier | Audit |
| approval_reference | text(100) | C: approved or successfully published version | Decision/validation reference; not invented for failed candidates | Audit |
| status | text(50) | R | Explicit version lifecycle state; domain details pending source/control contract | Audit |
| supersedes_version | text(128) | O: not applicable or not supplied; supplied values must validate | FK publication.publication_version; existing acyclic predecessor | Audit |
| business_date | date | R | Selected Chicago business date | Audit |
| run_id | text(128) | R | FK pipeline_run.run_id | Audit |
| candidate_id | text(128) | R | FK publication_candidate.candidate_id; successful release matches this candidate | Audit |
| published_at | instant UTC(6) | C: released publication | Actual atomic release instant; never populated for failed attempt | Audit |


## catalog_version

Logical PK: `catalog_version`. DD-07 defined version parent; immutable identity, retained corrections.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| catalog_version | text(128) | R | Version identifier PK; preserve exact identifier | Audit |
| approval_reference | text(100) | C: approved or successfully published version | Decision/validation reference; not invented for failed candidates | Audit |
| status | text(50) | R | Explicit version lifecycle state; domain details pending source/control contract | Audit |
| supersedes_version | text(128) | O: not applicable or not supplied; supplied values must validate | FK catalog_version.catalog_version; existing acyclic predecessor | Audit |
| valid_from | instant UTC(6) | R | Approved applicability start | Audit |
| valid_to | instant UTC(6) | O: open-ended interval | Exclusive interval end; null open-ended, never defaulted current date | Audit |


## rule_version

Logical PK: `rule_version`. DD-07 defined version parent; immutable identity, retained corrections.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| rule_version | text(128) | R | Version identifier PK; preserve exact identifier | Audit |
| approval_reference | text(100) | C: approved or successfully published version | Decision/validation reference; not invented for failed candidates | Audit |
| status | text(50) | R | Explicit version lifecycle state; domain details pending source/control contract | Audit |
| supersedes_version | text(128) | O: not applicable or not supplied; supplied values must validate | FK rule_version.rule_version; existing acyclic predecessor | Audit |
| valid_from | instant UTC(6) | R | Approved applicability start | Audit |
| valid_to | instant UTC(6) | O: open-ended interval | Exclusive interval end; null open-ended, never defaulted current date | Audit |
| condition_id | text(50) | R | RC-01 through RC-05; one individual condition per version | Audit |
| configuration_version | text(128) | R | FK configuration_version.configuration_version | Audit |


## configuration_version

Logical PK: `configuration_version`. DD-07 defined version parent; immutable identity, retained corrections.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| configuration_version | text(128) | R | Version identifier PK; preserve exact identifier | Audit |
| approval_reference | text(100) | C: approved or successfully published version | Decision/validation reference; not invented for failed candidates | Audit |
| status | text(50) | R | Explicit version lifecycle state; domain details pending source/control contract | Audit |
| supersedes_version | text(128) | O: not applicable or not supplied; supplied values must validate | FK configuration_version.configuration_version; existing acyclic predecessor | Audit |
| valid_from | instant UTC(6) | R | Approved applicability start | Audit |
| valid_to | instant UTC(6) | O: open-ended interval | Exclusive interval end; null open-ended, never defaulted current date | Audit |


## mapping_version

Logical PK: `mapping_version`. DD-07 defined version parent; immutable identity, retained corrections.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| mapping_version | text(128) | R | Version identifier PK; preserve exact identifier | Audit |
| approval_reference | text(100) | C: approved or successfully published version | Decision/validation reference; not invented for failed candidates | Audit |
| status | text(50) | R | Explicit version lifecycle state; domain details pending source/control contract | Audit |
| supersedes_version | text(128) | O: not applicable or not supplied; supplied values must validate | FK mapping_version.mapping_version; existing acyclic predecessor | Audit |
| valid_from | instant UTC(6) | R | Approved applicability start | Audit |
| valid_to | instant UTC(6) | O: open-ended interval | Exclusive interval end; null open-ended, never defaulted current date | Audit |


## catalog_rule

Logical PK: `catalog_version + condition_id`. Exactly five unique condition members for evaluated approved catalog.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| catalog_version | text(128) | R | FK catalog_version.catalog_version | Audit |
| condition_id | text(50) | R | RC-01 through RC-05; must agree with referenced rule | Audit |
| rule_version | text(128) | R | FK rule_version.rule_version | Audit |


## mapping_entry

Logical PK: `mapping_version + source_system + domain_code + raw_value`. Versioned source aliases; exact alias content remains source-contract confirmation.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| mapping_version | text(128) | R | FK mapping_version.mapping_version | Audit |
| source_system | text(50) | R | Source namespace | Audit |
| domain_code | text(50) | R | Mapped domain, such as loan status or severity | Audit |
| raw_value | text(50) | R | Source domain value preserved | Audit |
| canonical_value | text(50) | R | Approved target domain value; no forced UNKNOWN default | Audit |


## mapping_eligibility

Logical PK: `mapping_version + source_system + domain_code + raw_value + eligibility_code`. Child eligibility flags; four-field parent FK to mapping_entry.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| mapping_version | text(128) | R | Composite FK to mapping_entry | Audit |
| source_system | text(50) | R | Composite FK to mapping_entry | Audit |
| domain_code | text(50) | R | Composite FK to mapping_entry | Audit |
| raw_value | text(50) | R | Composite FK to mapping_entry | Audit |
| eligibility_code | text(50) | R | Distinct business population such as RC-01 finalized eligibility | Audit |
| is_eligible | boolean | R | Explicit approved eligibility, not inferred from terminal status | Audit |


## applied_mapping

Logical PK: `owner_entity + owner_version_key + mapping_version + usage_code`. Logical typed parent association; owner pair must reference an existing inventory entity/version. Multiple mappings are child rows.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| owner_entity | text(50) | R | Existing parent entity type | Audit |
| mapping_version | text(128) | R | FK mapping_version.mapping_version | Audit |
| usage_code | text(50) | R | Identity, status, eligibility or other approved mapped domain | Audit |
| owner_version_key | typed entity reference | R | Logical FK to the named owner entity PK tuple/version, including composite keys; not serialized text or an invented surrogate | Audit |


## run_extract

Logical PK: `run_id + source_system + entity_name + business_date + revision`. Associates an extract identity with each processing attempt.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| run_id | text(128) | R | FK pipeline_run.run_id | Audit |
| source_system | text(50) | R | Composite FK source_extract | Audit |
| entity_name | text(50) | R | Composite FK source_extract | Audit |
| business_date | date | R | Composite FK source_extract | Audit |
| revision | integer >= 1 | R | Composite FK source_extract | Audit |


## source_reference

Logical PK: `source_reference_key`. DD-01/DD-03 lineage child; one deduplicated owner/source-record/version locator. Owner is a typed existing entity reference.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| source_reference_key | internal key | R | Generated PK | Audit |
| owner_entity | text(50) | R | Existing inventory parent entity | Audit |
| source_system | text(50) | R | Composite FK source_extract | Audit |
| entity_name | text(50) | R | Composite FK source_extract | Audit |
| business_date | date | R | Composite FK source_extract | Audit |
| revision | integer >= 1 | R | Composite FK source_extract | Audit |
| source_record_id | text(128) | C: event/master source row | Preserved source-qualified natural identity | Audit |
| source_version | text(128) | C: source state/version evidence | Distinct from schema_version | Audit |
| source_updated_at | instant UTC(6) | C: supplied by source contract | No ingestion-time substitution | Audit |
| record_operation | text(50) | C: supplied operation | No inferred deletes until contract approved | Audit |
| row_number | int64 >= 0 | R | Raw row locator; convention fixed by source contract | Audit |
| ingested_at | instant UTC(6) | R | Derived receipt instant, not missing business-value default | Audit |
| run_id | text(128) | R | FK pipeline_run.run_id | Audit |
| owner_version_key | typed entity reference | R | Logical FK to the named owner entity PK tuple/version, including composite keys; not serialized text or an invented surrogate | Audit |


## control_population

Logical PK: `population_key`. Structured reconciliation/control population parent; criteria in child rows.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| population_key | internal key | R | Generated PK | Audit |
| entity_name | text(50) | R | Controlled target/source entity | Audit |
| business_date | date | R | Population Chicago date | Audit |
| publication_version | text(128) | C: published target control | FK publication.publication_version | Audit |


## population_member

Logical PK: `population_key + criterion_code + member_value`. One structured population criterion value; no serialized population.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| population_key | internal key | R | FK control_population.population_key | Audit |
| criterion_code | text(50) | R | Source/status/revision or other reviewed population criterion | Audit |
| member_value | text(128) | R | One criterion member; explicit typed domain validation by criterion | Audit |


## source_financial_control

Logical PK: `source_system + entity_name + business_date + revision + amount_field + currency + population_key`. Manifest financial controls, currency-separated.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| source_system | text(50) | R | Composite FK source_extract | Audit |
| entity_name | text(50) | R | Composite FK source_extract | Audit |
| business_date | date | R | Composite FK source_extract | Audit |
| revision | integer >= 1 | R | Composite FK source_extract | Audit |
| amount_field | text(50) | R | Controlled monetary field | Audit |
| currency | char(3) | R | ISO 4217, uppercase | Audit |
| population_key | internal key | R | FK control_population.population_key | Audit |
| control_total | decimal(28,4) | C: available valid control | Signed manifest aggregate, no fabricated zero | Audit |
| unavailable_reason | text(100) | C: unavailable control | Explicit missing/invalid control evidence reason | Audit |


## export_filter

Logical PK: `event_key + filter_code + member_number`. Sanitized typed filter members; never ordinary-export restricted values.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| event_key | bigint | R | FK export_event.event_key | Audit |
| filter_code | text(50) | R | Approved filter identifier | Audit |
| member_number | int64 >= 0 | R | Distinct member within filter | Audit |
| code_value | text(50) | C: code filter | Exactly one matching typed filter value | Audit |
| reference_value | text(100) | C: reference filter | Sanitized permitted reference only | Audit |
| date_value | date | C: date filter | Explicit selected business date | Audit |
| instant_value | instant UTC(6) | C: instant filter | Explicit UTC boundary | Audit |
| numeric_value | decimal(28,8) | C: numeric filter | Explicit numeric selection | Audit |


## recalculation_impact

Logical PK: `impact_key`. DD-06 controlled correction scope and publication lineage.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| impact_key | internal key | R | Generated PK | Audit |
| corrected_event_date | date | R | Corrected occurred_at Chicago business date | Audit |
| through_date | date | R | Corrected event date plus 90 calendar days | Audit |
| old_publication_version | text(128) | R | FK publication.publication_version | Audit |
| new_publication_version | text(128) | C: successful corrected publication | FK publication.publication_version | Audit |
| validation_reference | text(100) | C: corrected publication | Validation evidence reference | Audit |
| reconciliation_reference | text(100) | C: corrected publication | Reconciliation evidence reference | Audit |


## recalculation_customer

Logical PK: `impact_key + customer_key`. Former and corrected affected customers; deduplicated.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| impact_key | internal key | R | FK recalculation_impact.impact_key | Audit |
| customer_key | bigint | R | FK customer.customer_key | Audit |


## date_dimension

Logical PK: `date_key`. Proposed conformed logical calendar attributes from existing analytical model.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| date_key | internal key | R | Generated internal key; calendar_date alternate unique | Audit |
| calendar_date | date | R | Chicago calendar date | Audit |
| month | integer [1,12] | R | Derived calendar month | Audit |
| quarter | integer [1,4] | R | Derived calendar quarter | Audit |
| year | integer | R | Derived calendar year | Audit |

## transaction_publication

Logical PK: `publication_version + source_system + source_transaction_id + business_date`. Selected immutable event version. Natural source identity is unique per publication even if a correction changes the business date.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| publication_version | text(128) | R | FK publication.publication_version | Controlled |
| source_system | text(50) | R | Natural event source namespace | Controlled |
| source_transaction_id | text(128) | R | Natural source event identity; must match selected event version | Controlled |
| business_date | date | R | Chicago event date; must match event version | Controlled |
| transaction_key | bigint | R | FK transaction.transaction_key | Controlled |

## loan_payment_publication

Logical PK: `publication_version + source_system + source_payment_id + business_date`. Selected immutable event version. Natural source identity is unique per publication even if a correction changes the business date.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| publication_version | text(128) | R | FK publication.publication_version | Controlled |
| source_system | text(50) | R | Natural event source namespace | Controlled |
| source_payment_id | text(128) | R | Natural source event identity; must match selected event version | Controlled |
| business_date | date | R | Chicago event date; must match event version | Controlled |
| payment_key | bigint | R | FK loan_payment.payment_key | Controlled |

## DD-08 logical access and governance contracts

Approved by the requesting user on 2026-09-16; names below organize the approved policy, not actual users, grants or source schemas. All DD-07 universal contracts apply. No physical security is implemented.

Entitlement checks use the current instant and selected active role, including historical/corrected publications. A matching deny wins; absent, revoked, expired, unapproved or out-of-scope grants deny. Every scope member is typed and validated; multiple dimension constraints intersect, and members within a dimension select only explicitly authorized values. Enterprise aggregate scope is explicit, never inferred from a null scope. Case detail requires an assigned case and a linked item; customer identity or ownership is not an entitlement. Field/surface permissions cannot exceed the DD-08 role ceiling.

Approval evidence is append-only logical history: administrators cannot alter or discretionarily delete it; only the narrowly approved DD-10 end-of-retention batch process may dispose of eligible evidence. Subject references resolve existing full keys and inherit their sensitivity. Approval child rows capture each required reviewer separately. No self-approval; access requester, Compliance approver and Administrator implementer are distinct. Rule authors cannot be sole approver or publisher; exclusion investigators cannot approve their own exclusions. A waiver requires separate Sponsor and Compliance decisions, a reason, interval and audit reference; none is granted here. Required source and KPI reviews are separate governance_review rows for the applicable owner and Data Owner; risk changes require Risk Manager and Compliance rows. Exceptional export reviews must be tied to the same event, output classification and structured filter scope; requester cannot approve. Every approved identity mapping approval_reference resolves its Approved governance_action with an independent Senior Data Steward decision. Required review rows cannot be replaced by a generic status or unverified reference. DD-09 assigns publication/exclusion authorities in the quality policy; DD-10 approved lifecycle controls apply; physical enforcement remains deferred.

## access_policy

Logical PK: `policy_version`. One immutable access-policy version.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| policy_version | text(128) | R | Version ID | Audit |
| valid_from | instant UTC(6) | R | Effective start | Audit |
| valid_to | instant UTC(6) | O: open-ended | Exclusive end | Audit |
| approval_reference | text(100) | R | Recorded policy approval evidence | Audit |

## access_entitlement

Logical PK: `entitlement_id`. One independently approved, effective-dated principal/role/permission scope. Scope children are mandatory.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| entitlement_id | text(128) | R | Immutable grant/deny identity | Audit |
| user_identity | text(128) | R | Opaque principal ID | Audit |
| active_role | text(50) | R | Single reporting role or explicit governance responsibility | Audit |
| permission_code | text(50) | R | Scoped action including EXPORT_MASKED_DETAIL or restricted inspection; other domain spellings Pending confirmation | Audit |
| effect | text(50) | R | Allow or deny; deny takes precedence | Audit |
| policy_version | text(128) | R | FK access_policy.policy_version | Audit |
| valid_from | instant UTC(6) | R | Approved applicability start | Audit |
| valid_to | instant UTC(6) | O: open-ended except time-bound grants | Exclusive end; mandatory for inspection entitlements | Audit |
| revoked_at | instant UTC(6) | C: revoked | Immediate block from this instant | Audit |
| requester_identity | text(128) | R | Opaque requester principal | Audit |
| implementer_identity | text(128) | C: implemented entitlement | Administrator principal distinct from requester and Compliance approver | Audit |
| approval_reference | text(100) | C: approved entitlement | FK governance_action.action_id; approved access action and independent Compliance decision required | Audit |

## entitlement_scope

Logical PK: `entitlement_id + scope_number`. One typed scope constraint/member; no serialized scope.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| entitlement_id | text(128) | R | FK access_entitlement.entitlement_id | Audit |
| scope_number | int64 >= 0 | R | Distinct member ordinal | Audit |
| scope_type | text(50) | R | Enterprise aggregate, region, branch, HISTORICAL_BRANCH, case, source, field, surface or output class | Audit |
| scope_value | typed scope reference | R | One validated member; case resolves investigation_case.case_key; source domains resolve approved contracts; region/branch/HISTORICAL_BRANCH resolve stable organizational_unit full source-qualified identities; no free narrative | Audit |

## investigation_case

Logical PK: `case_key`. One authorized fraud/customer-risk case; actual assignments Pending confirmation.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| case_key | text(128) | R | Opaque internal case key | Controlled |
| case_type | text(50) | R | Fraud or customer-risk case; not automatic customer-wide access | Controlled |

## case_evidence_link

Logical PK: `case_key + item_number`. One explicitly linked case item; current case entitlement required.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| case_key | text(128) | R | FK investigation_case.case_key | Restricted |
| item_number | int64 >= 0 | R | Distinct evidence member | Restricted |
| owner_entity | text(50) | R | Existing logical entity | Restricted |
| owner_version_key | typed entity reference | R | FK to named entity full PK; raw references stay restricted and hidden from ordinary navigation | Restricted |

## governance_action

Logical PK: `action_id`. One mapping, rule, access, export, exclusion, source/KPI review or waiver action; this is evidence, not approval by existence.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| action_id | text(100) | R | Immutable action identity | Audit |
| action_type | text(50) | R | Controlled action category | Audit |
| requester_identity | text(128) | R | Opaque submitter/requester; author/investigator where applicable | Audit |
| subject_entity | text(50) | R | Existing target entity or controlled source/KPI contract type | Audit |
| subject_reference | typed entity reference | R | Full target key or reviewed contract reference; sensitivity inherited | Audit |
| reason_code | text(100) | R | Sanitized reason; restricted supporting evidence separately referenced | Audit |
| effective_from | instant UTC(6) | C: approved effective action | Required for mapping changes, grants and waivers | Audit |
| effective_to | instant UTC(6) | C: time-bound action | Exclusive end; mandatory waiver end | Audit |
| status | text(50) | R | Proposed/Approved/Rejected; only Approved mapping enters curated joins | Audit |
| history_analysis_reference | text(100) | C: merge, split or retirement | Affected-history analysis evidence | Audit |
| correction_reference | text(100) | C: merge, split or retirement | Correction/recalculation evidence; no invented recalculation result | Audit |
| audit_reference | text(100) | R | Immutable audit evidence locator; no sensitive text | Audit |
| publisher_identity | text(128) | C: published rule change | Opaque publisher; rule author cannot be sole publisher | Audit |

## governance_review

Logical PK: `action_id + review_number`. One independent review decision. Required reviewer responsibilities follow DD-08, not job-title access inheritance.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| action_id | text(100) | R | FK governance_action.action_id | Audit |
| review_number | int64 >= 0 | R | Distinct reviewer evidence | Audit |
| reviewer_identity | text(128) | R | Opaque reviewer principal; no self-approval | Audit |
| reviewer_responsibility | text(50) | R | Senior Data Steward, source owner, Data Owner, business KPI owner, Risk Manager, Compliance, Data Publication Approver or Sponsor as required; Sponsor cannot override CRITICAL | Audit |
| decision | text(50) | R | Approve/reject or consultation; consultation never substitutes for required approval | Audit |
| reviewed_at | instant UTC(6) | R | Actual decision instant | Audit |
| evidence_reference | text(100) | R | Immutable review reference; administrators cannot modify | Audit |

## export_entitlement

Logical PK: `event_key + entitlement_id`. All applicable entitlements evaluated for the attempt, including matching denies; no list serialized in event.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| event_key | bigint | R | FK export_event.event_key | Audit |
| entitlement_id | text(128) | R | FK access_entitlement.entitlement_id | Audit |
| evaluated_at | instant UTC(6) | R | Execution-time reevaluation instant | Audit |

## export_approval

Logical PK: `event_key + action_id`. Per-export exception approval references; standing detail permission stays in export_entitlement.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| event_key | bigint | R | FK export_event.event_key | Audit |
| action_id | text(100) | R | FK governance_action.action_id; subject must be this export and required Compliance plus applicable Data Owner reviews must approve exact scope | Audit |

## rc01_investigation_projection

Logical PK: `case_key + projection_item_key`. Sanitized logical projection only, derived from authorized linked RC-01 evidence. Keys are internal scope controls; no source aliases or raw references are visible.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| case_key | text(128) | R | FK investigation_case.case_key; current assigned Fraud/Risk role only | Controlled |
| projection_item_key | text(128) | R | Opaque internal projection item identity; no raw reference navigation | Controlled |
| current_comparison_amount | decimal(20,4) | C: valid current amount | Sanitized absolute comparison amount | Controlled |
| prior_average | exact numeric ratio | C: available prior evidence | Exact prior sum/history count per DD-07; decimal(28,8) only if exactly representable; no implicit rounding | Controlled |
| multiplier | decimal(28,8) | C: configured comparison | Approved threshold multiplier, 3 under DD-05 | Controlled |
| currency | char(3) | C: valid known currency | ISO 4217 uppercase; no cross-currency comparison | Controlled |
| window_start | instant UTC(6) | R | Current event minus 90 calendar days | Controlled |
| window_end | instant UTC(6) | R | Current event instant; exclusive | Controlled |
| history_count | int64 >= 0 | C: available history | Eligible prior count; missing never defaults to zero | Controlled |
| trigger_state | text(50) | R | Triggered, Not triggered or Unknown from approved evaluation | Controlled |
| missing_evidence_reason | text(100) | C: missing evidence | Sanitized reason code; no identity aliases, raw locators or narratives | Controlled |

## DD-09 publication and control evidence contracts

Approved logical evidence requirements, 2026-09-16. These entities organize the user-approved policy, not executed candidates, grants or physical tables. All DD-07 bounds, exact arithmetic, conditional nulls and typed-reference requirements apply. Audit pointers inherit referenced sensitivity; recipient/principal IDs are opaque, not names/contact details. Administrators cannot alter or discretionarily delete approval evidence; the narrow DD-10 independently approved, engine-scoped disposal exception applies.

Candidate identity is mandatory even if no publication was released. An unavailable control retains status/reason and null measurements, never fabricated zero or PASS. Missing source expectations are candidate_source rows without invented source_extract parents. For delivered malformed/conflicting content that cannot form an accepted source_extract, preserve restricted receipt evidence, supplied metadata and failure state rather than inventing an accepted extract. Every candidate has every expected source/entity, per-source/entity and overall completeness populations, required gate results and decision history. Repeated decisions/notifications are children, not overwritten fields.

Received completeness includes quarantine and quality exclusions. Source-business denominator excludes generated technical IDs/runtime audit fields. Conditional applicability follows the inventory. Each nonempty required source/entity and overall received/curated population must meet >=98%; post-exclusion is supplementary. Unknown/unavailable risk coverage is separately measured, not conflated with source-business completeness. Counts and financial controls reference explicit populations; disjoint row disposition and exact currency residual constraints remain mandatory.

Governance actions for exclusions, corrections, release and explained adjustments retain separate governance_review rows for each required independent reviewer. Exclusion approval is source owner plus independent Data Owner, with Compliance when sensitive access/masking/risk evidence is involved; requester/investigator cannot approve. Correction/release authority follows the quality policy. Data Publication Approver is separate from investigator, rule author and Administrator; Administrator executes only approved operations and never approves. No critical override, including Sponsor waiver. Role responsibility is not a business-detail entitlement.

## gate_ruleset

Logical PK: `gate_ruleset_version`. One immutable approved set of publication gate rules and severity/escalation policy.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| gate_ruleset_version | text(128) | R | Version identity | Audit |
| approval_reference | text(100) | R | Approved policy/review evidence | Audit |
| effective_from | instant UTC(6) | R | Applicability start | Audit |
| effective_to | instant UTC(6) | O: open-ended | Exclusive end; DD-07 interval rules | Audit |

## gate_rule

Logical PK: `gate_ruleset_version + rule_id`. One rule contract in the selected gate ruleset; DD-09 rules and applicable inventory obligations.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| gate_ruleset_version | text(128) | R | FK gate_ruleset.gate_ruleset_version | Audit |
| rule_id | text(50) | R | Rule ID, including DQ-D01 through DQ-D13, RC-D01 through RC-D03 and PUB-D01 | Audit |
| definition_reference | text(100) | R | Versioned validation/severity/escalation definition; no unbounded executable expression | Audit |

## publication_candidate

Logical PK: `candidate_id`. One daily candidate before any successful publication; all terminal and deferred attempts remain auditable.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| candidate_id | text(128) | R | Opaque candidate identity | Audit |
| run_id | text(128) | R | FK pipeline_run.run_id | Audit |
| business_date | date | R | Designated Chicago business date | Audit |
| gate_ruleset_version | text(128) | R | FK gate_ruleset.gate_ruleset_version | Audit |
| created_at | instant UTC(6) | R | Candidate registration instant | Audit |
| gate_at | instant UTC(6) | R | 6:00 a.m. America/Chicago for designated gate date represented in UTC | Audit |
| prior_successful_version | text(128) | C: prior successful publication exists | FK publication.publication_version; retained on block, never an unsuccessful candidate | Audit |
| predecessor_version | text(128) | C: correction/restatement | FK publication.publication_version; version being corrected, distinct from latest prior success | Audit |
| affected_from | date | C: correction/restatement | Earliest affected historical business date | Audit |
| affected_through | date | C: correction/restatement | Inclusive affected range; RC-01 corrected event through following 90 days | Audit |
| unavailable_reason | text(100) | C: missing required candidate evidence | Sanitized reason; do not fabricate configuration or prior publication | Audit |

## candidate_source

Logical PK: `candidate_id + source_system + entity_name`. One expected mandatory source/entity, including absent delivery. Expected entity contracts remain source-specific.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| candidate_id | text(128) | R | FK publication_candidate.candidate_id | Audit |
| source_system | text(50) | R | Expected source namespace; all five mandatory | Audit |
| entity_name | text(50) | R | Expected entity section | Audit |
| business_date | date | R | Expected delivery business date | Audit |
| revision | integer >= 1 | C: revision supplied | Delivered source revision; null when absent | Audit |
| receipt_state | text(50) | R | Present, missing, stale, corrupt or conflicting; no invented valid empty delivery | Audit |
| received_at | instant UTC(6) | C: content received | Actual receipt instant | Audit |
| contract_reference | text(100) | C: approved source contract exists | Evidence for cutoff, allowance and checksum scope; missing contract cannot pass | Audit |
| allowance_deadline_at | instant UTC(6) | C: approved delivery allowance exists | Derived from approved source contract, no invented grace period | Audit |
| checksum | text(128) | C: supplied/computable delivered content | Preserved SHA-256 digest in declared encoding | Audit |
| checksum_algorithm | text(50) | C: checksum evidence available | SHA-256 | Audit |
| checksum_encoding | text(50) | C: checksum evidence available | Agreed digest encoding | Audit |
| content_encoding | text(50) | C: delivered content metadata available | Source-approved encoding | Audit |
| schema_version | text(128) | C: supplied schema version | Preserved delivered schema identity | Audit |
| extract_reference | typed entity reference | C: accepted manifest available | Full source_extract PK; must match source/entity/date/revision | Audit |
| receipt_evidence_reference | text(100) | C: received content | Restricted immutable receipt/quarantine evidence; not a notification payload | Audit |
| unavailable_reason | text(100) | C: missing/invalid delivery or metadata | Explicit reason for each unavailable required control | Audit |

## candidate_control

Logical PK: `control_result_id`. One rule evaluation for a candidate and scoped control population; include successful and unexecuted/unavailable required checks.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| control_result_id | text(128) | R | Control result identity | Audit |
| candidate_id | text(128) | R | FK publication_candidate.candidate_id | Audit |
| gate_ruleset_version | text(128) | R | Composite FK with rule_id to gate_rule; matches candidate ruleset | Audit |
| rule_id | text(50) | R | Composite FK with gate_ruleset_version to gate_rule | Audit |
| population_key | internal key | C: measurable scoped population | FK control_population.population_key | Audit |
| result | text(50) | R | Pass, fail, unavailable or valid not applicable; no fake pass for early failure | Audit |
| base_severity | text(50) | R | CRITICAL, ERROR, WARNING or INFO per rule/result | Audit |
| effective_severity | text(50) | R | Severity after DD-09 escalation; any unresolved CRITICAL blocks | Audit |
| reason_code | text(100) | C: failure, limitation or unavailable check | Sanitized control/escalation reason | Audit |
| evaluated_at | instant UTC(6) | C: evaluation executed | Actual check instant | Audit |
| evidence_reference | text(100) | C: supporting check evidence available | Immutable evidence; unavailable checks retain reason | Audit |

## candidate_population

Logical PK: `candidate_id + population_key + stage`. Measured per-source/entity and overall populations at RECEIVED, CURATED and POST_EXCLUSION stages.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| candidate_id | text(128) | R | FK publication_candidate.candidate_id | Audit |
| population_key | internal key | R | FK control_population.population_key; children identify source/entity or explicit overall scope | Audit |
| stage | text(50) | R | RECEIVED, CURATED or POST_EXCLUSION; post-exclusion uses received population minus approved excluded members | Audit |
| received_rows | int64 >= 0 | C: measured | Received source rows; same baseline when reporting post-exclusion | Audit |
| accepted_rows | int64 >= 0 | C: measured | Accepted final-disposition rows | Audit |
| quarantined_rows | int64 >= 0 | C: measured | Quarantined final-disposition rows | Audit |
| excluded_rows | int64 >= 0 | C: measured | Approved excluded final-disposition rows | Audit |
| required_cells | int64 >= 0 | C: measured applicable population | Required applicable business cells; excludes generated technical IDs/runtime audit | Audit |
| present_cells | int64 >= 0 | C: measured applicable population | Present required cells, <= required_cells; invalid nonblank separately fails validity | Audit |
| completeness_state | text(50) | R | Measured, Unavailable or Not applicable; confirmed valid empty never 100% | Audit |
| unavailable_reason | text(100) | C: unavailable/empty measurement | Explicit reason, not fabricated counts | Audit |

## candidate_coverage

Logical PK: `candidate_id + population_key + result_type`. Unknown/unavailable coverage for customer conditions, classifications or other disclosed report results.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| candidate_id | text(128) | R | FK publication_candidate.candidate_id | Audit |
| population_key | internal key | R | FK control_population.population_key; condition/result scope explicit | Audit |
| result_type | text(50) | R | Condition, classification or documented report result domain | Audit |
| total_count | int64 >= 0 | C: measurable population | Explicit denominator | Audit |
| unknown_count | int64 >= 0 | C: measurable population | Unknown result count | Audit |
| unavailable_count | int64 >= 0 | C: measurable population | Unavailable result count; categories and overlap defined by result_type, do not blindly add | Audit |
| coverage_state | text(50) | R | Measured or unavailable | Audit |
| reason_reference | text(100) | C: unknown/unavailable or limitation | Sanitized reason/coverage disclosure evidence | Audit |

## candidate_evidence

Logical PK: `candidate_id + evidence_number`. Structured links to all applied source mappings, financial/count controls, exceptions, exclusions and corrections; no serialized list.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| candidate_id | text(128) | R | FK publication_candidate.candidate_id | Audit |
| evidence_number | int64 >= 0 | R | Distinct member | Audit |
| evidence_type | text(50) | R | Mapping, reconciliation, exception, exclusion, correction, adjustment, rule/catalog/configuration or validation | Audit |
| owner_entity | text(50) | R | Existing inventory entity | Audit |
| owner_version_key | typed entity reference | R | Full PK of named entity; mapping_version, reconciliation_result, quality_exception or governance_action as applicable | Audit |

## quality_exclusion

Logical PK: `action_id`. One bounded exclusion request/decision linked to independent governance reviews; never a standing permission.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| action_id | text(100) | R | FK governance_action.action_id; exclusion action | Audit |
| candidate_id | text(128) | R | FK publication_candidate.candidate_id | Audit |
| source_system | text(50) | R | Composite source_extract FK | Audit |
| entity_name | text(50) | R | Composite source_extract FK | Audit |
| business_date | date | R | Composite source_extract FK | Audit |
| revision | integer >= 1 | R | Composite source_extract FK; approval scoped to this delivered revision | Audit |
| reason_code | text(100) | R | Sanitized exclusion reason | Audit |
| affected_rows | int64 >= 0 | R | Identified record count; exact members in exclusion_record | Audit |
| required_cells | int64 >= 0 | R | Affected applicable required cells from received population | Audit |
| present_cells | int64 >= 0 | R | Affected present required cells from same received population | Audit |
| sensitive_or_risk_impact | boolean | R | True requires Compliance in addition to source owner and independent Data Owner | Audit |
| evidence_reference | text(100) | R | Noncritical/no-distortion assessment and linked before/after candidate_population evidence | Audit |

## exclusion_record

Logical PK: `action_id + record_number`. Each specifically identified excluded source record; restricted locator inherits access restrictions.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| action_id | text(100) | R | FK quality_exclusion.action_id | Audit |
| record_number | int64 >= 0 | R | Distinct member | Audit |
| source_reference_key | internal key | R | FK source_reference.source_reference_key; source/extract tuple agrees with exclusion | Audit |
| impact_reference | text(100) | R | Restricted field/cell impact evidence; never raw payload in audit text | Audit |

## exclusion_impact

Logical PK: `action_id + impact_number`. Field/KPI and currency-separated monetary impact, with explicit no-impact or unavailable state.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| action_id | text(100) | R | FK quality_exclusion.action_id | Audit |
| impact_number | int64 >= 0 | R | Distinct impact | Audit |
| field_or_kpi | text(100) | R | Inventory field or KPI identifier; no invented business domain | Audit |
| currency | char(3) | C: monetary impact | ISO 4217; no netting | Audit |
| signed_amount | decimal(28,4) | C: measurable monetary impact | Signed affected total, not absolute conversion | Audit |
| impact_state | text(50) | R | Measured, no impact or unavailable; required unavailable financial control remains CRITICAL | Audit |
| evidence_reference | text(100) | R | Impact/approval evidence | Audit |

## publication_decision

Logical PK: `decision_id`. One append-only released, blocked, deferred, failed or corrected candidate decision.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| decision_id | text(128) | R | Decision identity | Audit |
| candidate_id | text(128) | R | FK publication_candidate.candidate_id | Audit |
| decision | text(50) | R | Released, blocked, deferred, failed or corrected; corrected release requires all gates | Audit |
| reason_code | text(100) | R | Sanitized decision reason | Audit |
| decided_at | instant UTC(6) | R | Actual decision instant | Audit |
| publication_version | text(128) | C: a publication version exists | FK publication.publication_version; released/corrected references successful version, never fabricated on early failure | Audit |
| release_action_id | text(100) | C: release approved | FK governance_action.action_id; subject matches candidate and independent release reviews complete | Audit |
| retained_publication_version | text(128) | C: prior success retained | FK publication.publication_version; required on block if prior success exists | Audit |
| prior_state | text(50) | R | Prior successful version retained, superseded by success, or no prior success; no failed candidate served | Audit |
| display_age_seconds | int64 >= 0 | C: retained version served at decision instant | Nonnegative age evidence with displayed business date/version; update display age at viewing time | Audit |
| stale_reason | text(100) | C: prior version served because current candidate blocked | Prominent sanitized reason; no prior success displays Data unavailable | Audit |

## decision_participant

Logical PK: `decision_id + responsibility + member_number`. All required candidate responsibility slots; unassigned/not-performed state is explicit on failed/early attempts.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| decision_id | text(128) | R | FK publication_decision.decision_id | Audit |
| responsibility | text(50) | R | Requester, investigator, rule author, Data Owner, source/business reviewer, Data Publication Approver or executing Administrator | Audit |
| member_number | int64 >= 0 | R | Distinct participant within responsibility | Audit |
| principal_id | text(128) | C: identity known | Opaque principal identity; no names/contact | Audit |
| participation_state | text(50) | R | Assigned, reviewed, approved, executed, not performed or unassigned; no invented approvals | Audit |
| action_id | text(100) | C: governed review/execution action | FK governance_action.action_id; required approved release evidence before execution | Audit |
| acted_at | instant UTC(6) | C: action performed | Actual action instant | Audit |

## publication_notification

Logical PK: `notification_id`. One required notification event for missed gate, restatement or discovered critical failure; delivery state auditable.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| notification_id | text(128) | R | Notification identity | Audit |
| candidate_id | text(128) | R | FK publication_candidate.candidate_id | Audit |
| decision_id | text(128) | C: associated decision exists | FK publication_decision.decision_id | Audit |
| trigger_type | text(50) | R | Missed 6:00 a.m. gate, published-version restatement or critical failure discovered | Audit |
| triggered_at | instant UTC(6) | R | Actual trigger instant; notification required immediately | Audit |
| notified_at | instant UTC(6) | C: sent | Actual notification time; missing send is not success | Audit |
| reason_code | text(100) | R | Sanitized reason; no restricted payload | Audit |
| status | text(50) | R | Pending, sent or failed; actual transport domain to be finalized later | Audit |

## notification_recipient

Logical PK: `notification_id + responsibility + member_number`. Each required Data Owner, Data Publication Approver and affected source/KPI-owner recipient with acknowledgment/status.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| notification_id | text(128) | R | FK publication_notification.notification_id | Audit |
| responsibility | text(50) | R | Data Owner, Data Publication Approver, affected source owner or affected KPI owner | Audit |
| member_number | int64 >= 0 | R | Distinct recipient | Audit |
| principal_id | text(128) | C: assigned recipient exists | Opaque recipient identity; actual addressing kept out of audit text | Audit |
| status | text(50) | R | Unassigned, pending, delivered, failed or acknowledged; no fabricated acknowledgment | Audit |
| acknowledged_at | instant UTC(6) | C: acknowledged | Actual acknowledgment instant | Audit |

## DD-10 logical lifecycle contracts

Approved 2026-09-16 with the user's narrow DD-08 supersession. See [retention policy and complete entity schedule](retention-and-disposal-design.md). These are logical contracts only; no retention engine, purge, backups or security objects exist by this documentation change.

Audit-reference refinement: a live reference resolves the existing full parent PK; an expired-payload reference resolves provenance_envelope.envelope_id with PAYLOAD_EXPIRED. Never invent a parent, silently null a mandatory audit reference, cascade-delete surviving audit or keep Restricted parents indefinitely. For existing source_reference/applied_mapping typed owners, governance_action subjects, candidate_evidence targets, case/entitlement scope, recalculation_customer customer links, source row locators and exclusion_record links, use lifecycle_reference as the explicit surviving audit association. The unchanged historical decision is represented in the minimized envelope; no Administrator edits approval content. Detailed analytical links remain live-FK-only and expire with their parents. A mixed row must be separated into its authorized minimized audit representation before payload deletion; it cannot retain source aliases by merely relabeling them Audit.

Child/composite references are subject to the same rule, including source_extract tuples, customer keys and publication membership. Replacing a payload-bearing audit association with the approved envelope form is an explicit DD-10 logical contract refinement of DD-07, not nulling an unresolved FK. Audit envelopes and deletion evidence remain resolved until their dependent retention/hold obligations end. Publication/candidate/run and disposal/envelope groups require reviewed dependency-group disposal; no uncontrolled cascades.

All approval references below resolve governance_action plus independent governance_review rows with required responsibility/evidence. Compliance plus independent Data Owner approve exact disposal/hold scopes; add designated Legal for actual legal obligation. Requester cannot solely approve/release own hold. Scope is immutable after approval; change requires a new approved batch/action, never Administrator expansion. Engine evaluates expiry, holds and dependencies; Administrator may only operate the approved job. Every failed eligibility, scope mismatch or active hold prevents that item's deletion and records failure. Job evidence is system-recorded, protected from executor alteration.

## retention_schedule

Logical PK: `schedule_version + category_code`. One approved category rule version; exact rules in DD-10 entity schedule.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| schedule_version | text(128) | R | Approved lifecycle ruleset identity | Audit |
| category_code | text(50) | R | Category identifier from approved schedule | Audit |
| anchor_type | text(50) | R | Business/event/snapshot/assessment date, UTC audit/decision timestamp, effective end or specified temporary-output event | Audit |
| period_rule | text(100) | R | Bounded rule code for 24 months, seven years, active/dependency, 24 hours, 7 days or 35 days; not free-form executable logic | Audit |
| approval_action_id | text(100) | R | FK governance_action.action_id; policy approval evidence | Audit |
| valid_from | instant UTC(6) | R | Ruleset applicability start | Audit |
| valid_to | instant UTC(6) | O: open-ended | Exclusive end; prior records retain governing schedule evidence | Audit |

## retention_item

Logical PK: `item_id`. One governed logical record or copy; technical identity never resets original business anchor.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| item_id | text(128) | R | Opaque lifecycle item identity | Audit |
| schedule_version | text(128) | R | Composite FK with category_code to retention_schedule | Audit |
| category_code | text(50) | R | Composite FK with schedule_version to retention_schedule | Audit |
| envelope_id | text(128) | R | FK provenance_envelope.envelope_id; enduring minimized identity | Audit |
| anchor_date | date | C: date-based rule | Original Chicago business/event/snapshot/assessment or effective-end date | Audit |
| anchor_at | instant UTC(6) | C: instant-based rule | Original UTC audit/decision/output timestamp; date and instant semantics follow schedule | Audit |
| anchor_state | text(50) | R | Known, current open-ended or unavailable; unavailable cannot become eligible | Audit |
| anniversary_at | instant UTC(6) | C: computable anniversary | Through-anniversary boundary derived under approved calendar contract, never ingestion reset | Audit |
| live_expiry_at | instant UTC(6) | C: approved expiry computable | Live-store expiry used for bounded backup lag; no discretionary anchor edits | Audit |
| purge_eligible_at | instant UTC(6) | C: eligibility date computable | Next monthly cycle after anniversary, or short-term deadline; holds/dependencies rechecked | Audit |
| last_dependent_decision_at | instant UTC(6) | C: configuration/audit dependency | Last dependent audit decision timestamp; seven years measured from decision, not from its later purge | Audit |
| lifecycle_state | text(50) | R | Active, archive, eligible, held or disposed; reporting state distinct from possession | Audit |

## provenance_envelope

Logical PK: `envelope_id`. Minimized immutable provenance plus append-only expiry/disposal history; no names, contact, aliases or raw payload.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| envelope_id | text(128) | R | Opaque envelope identity | Audit |
| record_token | text(128) | R | Opaque record token; not an unkeyed identity hash | Audit |
| source_namespace | text(50) | C: source-derived record | Source namespace only, never customer alias | Audit |
| entity_name | text(50) | R | Logical entity/category | Audit |
| business_date | date | C: business payload | Original applicable business date | Audit |
| revision | integer >= 1 | C: revisioned payload | Original revision | Audit |
| version_id | text(128) | C: versioned record | Original version | Audit |
| digest | text(128) | C: valid content digest available | Approved content digest, never an identity hash presented as anonymization | Audit |
| disposition | text(50) | R | Retained or PAYLOAD_EXPIRED with preserved decision/control context | Audit |
| expiry_at | instant UTC(6) | C: expired payload | Actual governed expiry instant | Audit |
| deletion_evidence_id | text(128) | C: disposed payload | FK disposal_item.result_id; preserves deletion outcome evidence | Audit |

## lifecycle_reference

Logical PK: `reference_id`. Explicit retained audit relationship to a minimized envelope, replacing a direct payload dependency only under DD-10.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| reference_id | text(128) | R | Relationship identity | Audit |
| owner_envelope_id | text(128) | R | FK provenance_envelope.envelope_id; audit owner | Audit |
| target_envelope_id | text(128) | R | FK provenance_envelope.envelope_id; referenced record | Audit |
| relationship_code | text(50) | R | Source locator, typed owner, correction customer, scope or other named original field/association | Audit |
| payload_state | text(50) | R | AVAILABLE or PAYLOAD_EXPIRED; agrees with target lifecycle | Audit |
| live_target | typed entity reference | C: payload AVAILABLE | Full existing inventory PK; absent only under explicit expired-envelope alternative, not silent null | Audit |
| transition_at | instant UTC(6) | C: payload expiry transition | Append-only lifecycle event; original approval content unchanged | Audit |

## restricted_token_mapping

Logical PK: `mapping_id`. Separate Restricted reversible mapping; not part of seven-year sanitized audit payload.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| mapping_id | text(128) | R | Opaque mapping identity | Restricted |
| record_token | text(128) | R | Token matching envelope record_token | Restricted |
| restricted_reference | typed entity reference | R | Restricted store subject; actual mapping representation deferred | Restricted |
| dependency_reference | text(100) | R | Valid analytical/audit/hold dependency required throughout lifetime | Restricted |
| retention_item_id | text(128) | R | FK retention_item.item_id; remove when no valid dependency remains | Restricted |

## retention_hold

Logical PK: `hold_id`. Approved scoped disposal suspension; no access grant or CRITICAL-publication override.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| hold_id | text(128) | R | Hold identity | Audit |
| requester_id | text(128) | R | Opaque requester | Audit |
| reason_code | text(100) | R | Sanitized reason | Audit |
| approval_action_id | text(100) | C: approved hold | FK governance_action.action_id; independent Compliance/Data Owner and designated Legal if actual obligation | Audit |
| legal_required | boolean | R | Actual obligation only; no invented legal requirement | Audit |
| effective_at | instant UTC(6) | C: approved effective hold | Approved start | Audit |
| next_review_at | instant UTC(6) | C: active hold | Quarterly review due instant; overdue review escalated | Audit |
| state | text(50) | R | Requested, active or released; release never resets retention anchor | Audit |
| release_action_id | text(100) | C: released hold | FK governance_action.action_id; independent Compliance/Data Owner reason/time | Audit |
| released_at | instant UTC(6) | C: released hold | Actual authorized release time | Audit |

## hold_scope

Logical PK: `hold_id + member_number`. Exact record/category/date/system/dependency and backup scope; no blanket backup extension.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| hold_id | text(128) | R | FK retention_hold.hold_id | Audit |
| member_number | int64 >= 0 | R | Distinct scope member | Audit |
| scope_type | text(50) | R | Record, category, date range, system, dependency or backup | Audit |
| scope_reference | typed scope reference | R | Validated approved member; item/backup/envelope when applicable; no sensitive text | Audit |
| from_date | date | C: date-range scope | Inclusive approved date start | Audit |
| through_date | date | C: date-range scope | Inclusive approved date end | Audit |
| evidence_reference | text(100) | R | Exact scope approval evidence | Audit |

## hold_review

Logical PK: `hold_id + review_number`. Quarterly review/escalation/release evidence, independently approved and append-only.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| hold_id | text(128) | R | FK retention_hold.hold_id | Audit |
| review_number | int64 >= 0 | R | Distinct review | Audit |
| action_id | text(100) | R | FK governance_action.action_id; reviewer identities and decisions in governance_review | Audit |
| reviewed_at | instant UTC(6) | R | Actual review time | Audit |
| outcome | text(50) | R | Continue, release request or overdue escalation | Audit |
| evidence_reference | text(100) | R | Sanitized review/escalation evidence | Audit |

## disposal_batch

Logical PK: `batch_id`. Exact independently approved disposal scope; cannot be expanded by executor.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| batch_id | text(128) | R | Approved-scope batch identity | Audit |
| approval_action_id | text(100) | C: approved batch | FK governance_action.action_id; Compliance and independent Data Owner define/approve exact scope | Audit |
| decision_at | instant UTC(6) | C: disposal decision recorded | Starts this disposal evidence seven-year clock | Audit |
| schedule_version | text(128) | R | Approved retention ruleset version; referenced schedule rows must exist | Audit |
| scope_digest | text(128) | C: scope fixed | Digest of exact approved member set; no adding records after approval | Audit |
| status | text(50) | R | Proposed, approved, executing, completed or failed; no authority by existence | Audit |

## disposal_scope

Logical PK: `batch_id + item_id`. Exact approved item membership; category counts and scope verified before each execution.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| batch_id | text(128) | R | FK disposal_batch.batch_id | Audit |
| item_id | text(128) | R | FK retention_item.item_id | Audit |
| category_code | text(50) | R | Matches item category | Audit |
| approval_evidence_reference | text(100) | R | Approval binds this member; no independent Administrator selection | Audit |

## disposal_job

Logical PK: `job_id`. One approved batch execution attempt; evidence cannot be edited by Administrator.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| job_id | text(128) | R | Job attempt identity | Audit |
| batch_id | text(128) | R | FK disposal_batch.batch_id; approved before execution | Audit |
| executor_id | text(128) | R | Operating Administrator, never batch approver | Audit |
| ruleset_version | text(128) | R | Matches approved batch retention ruleset | Audit |
| started_at | instant UTC(6) | R | Actual start | Audit |
| ended_at | instant UTC(6) | C: terminal job | Actual end | Audit |
| eligible_count | int64 >= 0 | C: measured | Engine-eligible subset; not additive with final outcomes | Audit |
| deleted_count | int64 >= 0 | C: measured | Successful terminal deletions | Audit |
| skipped_count | int64 >= 0 | C: measured | Explicit nondeleted terminal skips | Audit |
| failed_count | int64 >= 0 | C: measured | Failures including eligibility/scope/hold failures | Audit |
| verification_state | text(50) | R | Pending, pass or fail; no invented pass | Audit |
| verification_reference | text(100) | C: verification performed | Surviving references/counts/holds/tokens/backups verification | Audit |

## disposal_item

Logical PK: `result_id`. Per-item engine check and final outcome; failed checks prevent deletion.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| result_id | text(128) | R | Result identity | Audit |
| job_id | text(128) | R | FK disposal_job.job_id | Audit |
| item_id | text(128) | R | FK retention_item.item_id; must be in approved batch scope | Audit |
| checked_at | instant UTC(6) | R | Execution-time eligibility/scope/hold/dependency recheck | Audit |
| expired | boolean | R | Engine result under approved anchor/schedule | Audit |
| unheld | boolean | R | Current scoped hold evaluation | Audit |
| dependency_cleared | boolean | R | Reviewed dependency result | Audit |
| scope_matches | boolean | R | Exact batch match; false stops deletion | Audit |
| outcome | text(50) | R | Deleted, skipped or failed; any failed eligibility/scope/active hold is failed, no deletion | Audit |
| reason_code | text(100) | C: skip/failure or exclusion | Sanitized hold/dependency/eligibility/scope reason | Audit |
| deleted_at | instant UTC(6) | C: deleted | Actual deletion time | Audit |
| backup_deadline_at | instant UTC(6) | C: backup obligation | At most 35 days after live-store expiry, not reset by recopy | Audit |
| verification_reference | text(100) | C: verified | Item-level surviving references and deletion evidence | Audit |

## disposal_category_total

Logical PK: `job_id + category_code`. Required category totals; outcomes reconcile with item results.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| job_id | text(128) | R | FK disposal_job.job_id | Audit |
| category_code | text(50) | R | Item category | Audit |
| eligible_count | int64 >= 0 | R | Measured eligible subset | Audit |
| deleted_count | int64 >= 0 | R | Measured deleted outcomes | Audit |
| skipped_count | int64 >= 0 | R | Measured skipped outcomes | Audit |
| failed_count | int64 >= 0 | R | Measured failed outcomes | Audit |
| hold_exclusions | int64 >= 0 | R | Hold-blocked subset, not an extra disjoint outcome | Audit |
| dependency_exclusions | int64 >= 0 | R | Dependency-blocked subset, may overlap hold subset | Audit |

## backup_copy

Logical PK: `backup_id`. Logical encrypted daily backup/copy metadata; no configured service implied.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| backup_id | text(128) | R | Opaque copy identity | Audit |
| copy_type | text(50) | R | Backup, replica, snapshot or transaction log | Audit |
| created_at | instant UTC(6) | R | Original copy instant; recopy cannot reset expired-data deadline | Audit |
| encrypted | boolean | R | Must be true under approved policy | Audit |
| expires_at | instant UTC(6) | R | Rolling 35-day expiry, bounded by member live-expiry deadlines | Audit |
| scope_reference | text(100) | R | Protected inventory of contained items and holds | Audit |
| disposal_evidence_reference | text(100) | C: expired copy disposed | Sanitized disposal verification | Audit |

## restore_validation

Logical PK: `restore_id`. Isolated recovery attempt; no accessible service before deletion/revocation/hold validation.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| restore_id | text(128) | R | Restore attempt identity | Audit |
| backup_id | text(128) | R | FK backup_copy.backup_id | Audit |
| started_at | instant UTC(6) | R | Isolated restore start | Audit |
| validated_at | instant UTC(6) | C: validation performed | Actual validation time | Audit |
| deletion_reapplied | boolean | C: checked | Disposed/expired records removed before service | Audit |
| revocations_reapplied | boolean | C: checked | Current entitlement revocations applied | Audit |
| holds_reapplied | boolean | C: checked | Current active scoped holds applied | Audit |
| result | text(50) | R | Pending, passed or failed; only passed permits accessible service | Audit |
| evidence_reference | text(100) | C: validation performed | Reports/APIs/exports exclude expired records | Audit |
| temporary_copy_deadline | instant UTC(6) | C: validated restore | Within 7 days after restore validation; failed/abandoned handling requires documented operational contract | Audit |
| copy_disposal_reference | text(100) | C: recovery copies removed | Evidence of temporary recovery copy disposal | Audit |

## access_attempt

Logical PK: `attempt_id`. Sanitized denied access/query/navigation attempt, distinct from existing export_event.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| attempt_id | text(128) | R | Opaque attempt identity | Audit |
| actor_id | text(128) | C: known actor | Opaque principal; unavailable identity never fabricated | Audit |
| active_role | text(50) | C: supplied selected role | One role, never union | Audit |
| surface | text(50) | R | Query, navigation, API or other access surface | Audit |
| decided_at | instant UTC(6) | R | UTC denial/event anchor for seven-year audit | Audit |
| decision | text(50) | R | Denied or other recorded access outcome | Audit |
| reason_code | text(100) | R | Sanitized reason; no sensitive requested values | Audit |
| policy_version | text(128) | C: evaluable policy | FK access_policy.policy_version; missing policy denies | Audit |

## DD-11 loan schedule, payment and relationship contracts

Approved logical design 2026-09-16. [Policy](loan-payment-and-schedule-policy.md) defines business semantics. Proposed source-section names organize required Loan Servicing contracts; they are not verified source aliases or availability. Existing source_reference/applied_mapping and DD-09 controls apply to each version. Monetary types retain DD-07 exact precision/minor-unit checks. Raw signed values remain in restricted raw/quarantine lineage, never silently coerced into accepted positive payments.

Each natural source identity is unique within the selected publication; retained correction versions do not duplicate active facts. Exact source identity/version uniqueness contracts must be verified. All predecessor references are existing and acyclic. Composite/typed publication members resolve full keys and agree with target source identity and effective/event date. Corrected selected parent/child versions must remain coherent. Corrected data history never becomes a business REVERSAL/REFUND.

Canonical payment status is PENDING/POSTED/FAILED/CANCELLED, with only POSTED financially effective. PRINCIPAL/INTEREST/FEE are allocation components. REVERSAL/REFUND are adjustment kinds. REPORTING is the required loan-account role. Other source domains/aliases remain Pending confirmation. Every obligation/payment/allocation/unapplied/adjustment currency matches loan.contractual_currency. No currency conversion or allocation waterfall is inferred. Obligations, allocations and unapplied monetary sign domains must be confirmed from valid source contracts; they cannot conceal a violated positive payment rule or financial equation.

For every selected POSTED payment: payment.amount = active allocation amount total + separate unapplied amount. Active means source-supported applicability under the selected publication/as-of instant, not a fabricated status. For adjustments: cumulative selected REVERSAL/REFUND magnitudes <= original POSTED payment amount; source-supplied adjustment/allocation/unapplied effects and effective timing must reconcile without overwriting original payment or changing the approved equation. Missing required source semantics/control evidence blocks release under DD-09.

At every relevant loan/as-of date exactly one effective REPORTING loan_account must resolve a maskable account. Gap/ambiguity suppresses drill-through as Unavailable and is CRITICAL under DD-09. No inference by customer, branch, amount or suffix. Optional payment_transaction_link requires supplied evidence or independent review; no monetary join multiplication.

## loan_schedule

Logical PK: `schedule_version`. One immutable version of a source-qualified schedule for a loan. Natural identity: source_system + source_schedule_id; selected version/effective interval determines applicability. Required proposed SRC-02 schedule contract.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| schedule_version | text(128) | R | Immutable internal schedule version | Controlled |
| source_system | text(50) | R | Loan Servicing source namespace | Controlled |
| source_schedule_id | text(128) | R | Required stable source schedule ID; actual alias pending | Controlled |
| loan_key | bigint | R | FK loan.loan_key | Controlled |
| currency | char(3) | R | Loan contractual currency | Controlled |
| effective_from | instant UTC(6) | R | Source-supported schedule applicability start | Controlled |
| effective_to | instant UTC(6) | O: open-ended | Exclusive end; no conflicting selected schedule interval for same source schedule identity | Controlled |
| original_effective_date | date | R | Original Chicago effective anchor retained through correction/rescheduling | Controlled |
| supersedes_schedule_version | text(128) | O: first version | FK loan_schedule.schedule_version; required for corrected/rescheduled existing schedule | Controlled |
| source_version | text(128) | R | Source-supported immutable version identity; exact convention requires verified contract | Controlled |
| batch_revision | integer >= 1 | R | Qualified source_extract revision through source_reference | Controlled |
| correction_reference | text(100) | C: corrected version | Approved data-correction evidence; prior version preserved | Controlled |

## loan_obligation

Logical PK: `obligation_version`. One immutable scheduled obligation/installment version. Natural identity: source_system + source_obligation_id; one schedule has many obligations. Required proposed SRC-02 obligation contract.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| obligation_version | text(128) | R | Immutable internal version | Controlled |
| source_system | text(50) | R | Source namespace | Controlled |
| source_obligation_id | text(128) | R | Stable obligation identity across rescheduling or approved predecessor mapping | Controlled |
| schedule_version | text(128) | R | FK loan_schedule.schedule_version; selected coherent schedule | Controlled |
| loan_key | bigint | R | FK loan.loan_key; must equal schedule loan | Controlled |
| due_date | date | R | Contractual due date belongs here, never canonical payment | Controlled |
| original_obligation_date | date | R | Original obligation retention anchor; rescheduling cannot reset it | Controlled |
| scheduled_amount | decimal(20,4) | R | Source-supplied contractual obligation amount; component/sign domain contract required | Controlled |
| currency | char(3) | R | Same as loan contractual currency | Controlled |
| effective_from | instant UTC(6) | R | Source-supported applicability start | Controlled |
| effective_to | instant UTC(6) | O: open-ended | Exclusive end | Controlled |
| supersedes_obligation_version | text(128) | O: first version | FK loan_obligation.obligation_version; prior immutable obligation retained | Controlled |
| source_version | text(128) | R | Source-supported immutable version identity; exact convention requires verified contract | Controlled |
| batch_revision | integer >= 1 | R | Qualified source_extract revision through source_reference | Controlled |
| correction_reference | text(100) | C: corrected version | Approved data-correction evidence; prior version preserved | Controlled |

## payment_allocation

Logical PK: `allocation_version`. One immutable source allocation/component version linking one payment to one obligation. Natural identity source_system + source_allocation_id + component. Many-to-many payment/obligation via distinct allocations.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| allocation_version | text(128) | R | Immutable internal allocation version | Controlled |
| source_system | text(50) | R | Source namespace | Controlled |
| source_allocation_id | text(128) | R | Source allocation ID; not generated allocation business fact | Controlled |
| payment_key | bigint | R | FK loan_payment.payment_key; financially active allocation requires POSTED selected payment | Controlled |
| obligation_version | text(128) | R | FK loan_obligation.obligation_version; obligation and payment have same loan | Controlled |
| component | text(50) | R | PRINCIPAL, INTEREST or FEE from reviewed source mapping | Controlled |
| amount | decimal(20,4) | R | Source-supplied component allocation; no invented waterfall | Controlled |
| currency | char(3) | R | Matches payment/obligation/loan currency | Controlled |
| effective_from | instant UTC(6) | R | Source-supported active start | Controlled |
| effective_to | instant UTC(6) | O: open-ended | Exclusive active end; preserve withdrawn/superseded allocation evidence | Controlled |
| original_effective_date | date | R | Original applicability retention anchor, not revised publication date | Controlled |
| supersedes_allocation_version | text(128) | O: first version | FK payment_allocation.allocation_version; correction version, not a business adjustment | Controlled |
| source_version | text(128) | R | Source-supported immutable version identity; exact convention requires verified contract | Controlled |
| batch_revision | integer >= 1 | R | Qualified source_extract revision through source_reference | Controlled |
| correction_reference | text(100) | C: corrected version | Approved data-correction evidence; prior version preserved | Controlled |

## payment_unapplied

Logical PK: `unapplied_version`. One immutable effective unapplied-amount state per payment. Logical natural identity: source-qualified payment plus effective start; source state/version identity required. Exactly one applicable state for each POSTED payment, including explicit source-confirmed zero.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| unapplied_version | text(128) | R | Immutable internal state version | Controlled |
| payment_key | bigint | R | FK loan_payment.payment_key | Controlled |
| amount | decimal(20,4) | R | Separate source-supported unapplied amount; missing never defaults zero | Controlled |
| currency | char(3) | R | Same payment/loan contractual currency | Controlled |
| effective_from | instant UTC(6) | R | State applicability start | Controlled |
| effective_to | instant UTC(6) | O: open-ended | Exclusive end; selected effective states cannot overlap | Controlled |
| original_effective_date | date | R | Original state retention anchor | Controlled |
| supersedes_unapplied_version | text(128) | O: first version | FK payment_unapplied.unapplied_version | Controlled |
| source_version | text(128) | R | Source-supported immutable version identity; exact convention requires verified contract | Controlled |
| batch_revision | integer >= 1 | R | Qualified source_extract revision through source_reference | Controlled |
| correction_reference | text(100) | C: corrected version | Approved data-correction evidence; prior version preserved | Controlled |

## payment_adjustment

Logical PK: `adjustment_key`. One immutable source-qualified business REVERSAL/REFUND event version referencing the original POSTED payment. Natural identity source_system + source_adjustment_id; corrections preserve original natural event.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| adjustment_key | bigint | R | Generated immutable event-version key | Controlled |
| source_system | text(50) | R | Source namespace | Controlled |
| source_adjustment_id | text(128) | R | Required source adjustment identifier | Controlled |
| original_payment_key | bigint | R | FK loan_payment.payment_key; original POSTED event, not deleted/reduced | Controlled |
| adjustment_type | text(50) | R | REVERSAL or REFUND | Controlled |
| amount | decimal(20,4) | R | Positive canonical adjustment magnitude; approved mapping preserves original signed raw value; cumulative cap applies | Controlled |
| currency | char(3) | R | Same original payment/loan currency | Controlled |
| occurred_at | instant UTC(6) | R | Actual adjustment event timestamp | Controlled |
| business_date | date | R | Original Chicago adjustment event date; does not reset payment clock | Controlled |
| application_reference | text(100) | R | Source-supported adjustment/allocation/unapplied impact evidence; reviewed semantics required, no inferred waterfall | Controlled |
| supersedes_event_key | bigint | O: first version | FK payment_adjustment.adjustment_key; data correction only | Controlled |
| source_version | text(128) | R | Source-supported immutable version identity; exact convention requires verified contract | Controlled |
| batch_revision | integer >= 1 | R | Qualified source_extract revision through source_reference | Controlled |
| correction_reference | text(100) | C: corrected version | Approved data-correction evidence; prior version preserved | Controlled |

## loan_account

Logical PK: `loan_account_version`. One immutable effective loan/account/role relationship version; one required effective REPORTING account per loan/as-of date. Natural identity source-qualified relationship ID; no direct loan.account_key authority.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| loan_account_version | text(128) | R | Immutable relationship version | Controlled |
| source_system | text(50) | R | Relationship source namespace | Controlled |
| source_relationship_id | text(128) | R | Required source-supported or approved relationship identity | Controlled |
| loan_key | bigint | R | FK loan.loan_key | Controlled |
| account_key | bigint | R | FK account.account_key; source-qualified account resolved, never suffix match | Controlled |
| relationship_role | text(50) | R | REPORTING required; other roles not invented | Controlled |
| valid_from | instant UTC(6) | R | Source-supported relationship applicability start | Controlled |
| valid_to | instant UTC(6) | O: open-ended | Exclusive end; REPORTING coverage exactly one at required as-of instant | Controlled |
| original_effective_date | date | R | Original effective anchor; DD-10 current/dependency exception applies | Controlled |
| supersedes_relationship_version | text(128) | O: first version | FK loan_account.loan_account_version | Controlled |
| review_reference | text(100) | R | Required reviewed source relationship contract/evidence, not actual review claimed | Controlled |
| source_version | text(128) | R | Source-supported immutable version identity; exact convention requires verified contract | Controlled |
| batch_revision | integer >= 1 | R | Qualified source_extract revision through source_reference | Controlled |
| correction_reference | text(100) | C: corrected version | Approved data-correction evidence; prior version preserved | Controlled |

## payment_transaction_link

Logical PK: `link_version`. One immutable evidenced payment/Core-transaction reference version. Logical natural identity: source-qualified payment and transaction plus original effective start. Optional link existence; supplied links must validate. No invented one-to-one exclusivity.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| link_version | text(128) | R | Immutable internal link version | Controlled |
| payment_key | bigint | R | FK loan_payment.payment_key | Controlled |
| transaction_key | bigint | R | FK transaction.transaction_key; selected versions coherent | Controlled |
| evidence_basis | text(50) | R | Source supplied or independently reviewed; no inferred matching | Controlled |
| evidence_reference | text(100) | R | Source-reference/review evidence supporting exact linked identities | Controlled |
| review_action_id | text(100) | C: independently reviewed linkage | FK governance_action.action_id; independent reviewer evidence | Controlled |
| valid_from | instant UTC(6) | R | Supported effective start | Controlled |
| valid_to | instant UTC(6) | O: open-ended | Exclusive end | Controlled |
| original_effective_date | date | R | Original link retention anchor | Controlled |
| supersedes_link_version | text(128) | O: first version | FK payment_transaction_link.link_version | Controlled |

## loan_contract_publication

Logical PK: `publication_version + entity_name + natural_identity`. One selected immutable DD-11 contract version per natural identity and publication; typed identities are tuples, never serialized payload.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| publication_version | text(128) | R | FK publication.publication_version | Controlled |
| entity_name | text(50) | R | loan_schedule, loan_obligation, payment_allocation, payment_unapplied, payment_adjustment, loan_account or payment_transaction_link | Controlled |
| natural_identity | typed source identity | R | Full source-qualified natural identity declared for selected entity; agrees with target | Controlled |
| selected_version | typed entity reference | R | Full PK of selected existing entity; validates coherent schedule/payment/obligation/link references | Controlled |
| business_date | date | R | Original event/obligation/effective business date; does not replace source manifest date | Controlled |

## Consolidation and dependency register

| Retired or duplicate definition | Authoritative replacement |
| --- | --- |
| Initial dictionary types and base/supplement field rows | This inventory; data-dictionary-and-mappings is now navigation only |
| Snapshot entity/date PK and scalar publication membership | Immutable snapshot_version plus snapshot publication child membership |
| Common scalar mapping_version / eligibility_mapping_version | applied_mapping child rows to mapping_version parents |
| risk_evidence RC-01 amount/window/history fields | rc01_comparison and risk_evidence_item children |
| Serialized risk source_references | source_reference and deduplicated risk_evidence_item |
| complaint.original_created_at | complaint.created_at; only documented source alias permitted |
| rule_config.value | Exactly one typed value plus configuration_version parent |
| reconciliation_result.population / export_event.filter_context | control_population/population_member and export_filter |
| loan.account_key | Effective-dated loan_account; exactly one effective REPORTING link |
| loan_payment.due_date | loan_obligation.due_date; raw due-date alias is not canonical payment semantics |
| Extract identity including run_id | Source/entity/business-date/revision identity; run_extract for repeat attempts |

DD-08 entitlement, DD-09 publication, DD-10 lifecycle and DD-11 payment contracts are approved logical refinements. Fields conditional solely on remaining decisions: DD-12 now approves historical attribution and current scope resolution in historical-branch-attribution-policy.md. Actual source coverage remains unverified; baseline retention durations are unchanged.

Other prerequisites are source-contract facts, not new DD-07 field standards: actual source aliases, valid nonqualifying status memberships, direction/role domains, source timezone/cutoff/version conventions, and source historical coverage. No approval of their unknown values is implied.

Explicitly deferred: sequence/identity implementation, PostgreSQL indexes and physical constraints, partitions, JSON versus normalized physical storage, materialized views, compression, performance tuning, Power BI relationships and physical retention structures. Logical child entities and logical uniqueness remain required independent of storage choice. G3 remains pending; no database, ETL, generated data or implementation results.

## DD-12 authoritative organizational history

These logical contracts are approved; actual aliases/coverage remain unverified. Stable identities never reuse source IDs. Typed version references resolve full keys and selected publication scope. All relationships use half-open intervals. Corrections preserve original end anchors, predecessor, reason, affected interval and review. No inferred attribution or access.

## organizational_unit

Logical PK: `organization_key`. One permanent source-qualified REGION or BRANCH identity; source_system + unit_type + source_id unique, IDs never reused.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| organization_key | text(128) | R | Generated stable identity | Controlled |
| source_system | text(50) | R | SRC-05 namespace | Controlled |
| unit_type | text(50) | R | REGION or BRANCH | Controlled |
| source_id | text(128) | R | region_id or branch_id; stable within corresponding namespace | Controlled |

## region

Logical PK: `region_version`. One effective immutable region version; natural history source_system + region_id + valid_from.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| region_version | text(128) | R | Immutable version | Controlled |
| organization_key | text(128) | R | FK organizational_unit.organization_key; REGION | Controlled |
| source_system | text(50) | R | SRC-05 namespace | Controlled |
| region_id | text(128) | R | Stable source region ID | Controlled |
| region_name | text(200) | R | Source display name | Controlled |
| valid_from | instant UTC(6) | R | Source-supported applicability start | Controlled |
| valid_to | instant UTC(6) | O: open-ended | Exclusive end; null open-ended | Controlled |
| original_effective_end | instant UTC(6) | C: ended interval | Original end retention anchor retained through corrections | Controlled |
| source_version | text(128) | R | Required reviewed source version identity | Controlled |
| supersedes_version | text(128) | C: correction | FK region.region_version; predecessor on correction | Controlled |
| correction_reason | text(200) | C: correction | Sanitized reason | Controlled |
| affected_from | instant UTC(6) | C: correction | Correction affected interval start | Controlled |
| affected_to | instant UTC(6) | O: open-ended or not correction | Exclusive affected end | Controlled |
| approval_action_id | text(128) | R | FK governance_action.action_id; independent source/Data Owner evidence | Controlled |

## organizational_successor

Logical PK: `successor_version`. One effective predecessor/successor relationship; same unit type; no cycles or automatic grants. Natural pair + valid_from.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| successor_version | text(128) | R | Immutable version | Controlled |
| predecessor_key | text(128) | R | FK organizational_unit.organization_key | Controlled |
| successor_key | text(128) | R | FK organizational_unit.organization_key; distinct unit | Controlled |
| source_system | text(50) | R | SRC-05 relationship authority | Controlled |
| valid_from | instant UTC(6) | R | Source-supported applicability start | Controlled |
| valid_to | instant UTC(6) | O: open-ended | Exclusive end; null open-ended | Controlled |
| original_effective_end | instant UTC(6) | C: ended interval | Original end retention anchor retained through corrections | Controlled |
| source_version | text(128) | R | Required reviewed source version identity | Controlled |
| supersedes_version | text(128) | C: correction | FK organizational_successor.successor_version; predecessor on correction | Controlled |
| correction_reason | text(200) | C: correction | Sanitized reason | Controlled |
| affected_from | instant UTC(6) | C: correction | Correction affected interval start | Controlled |
| affected_to | instant UTC(6) | O: open-ended or not correction | Exclusive affected end | Controlled |
| approval_action_id | text(128) | R | FK governance_action.action_id; independent source/Data Owner evidence | Controlled |

## account_branch_assignment

Logical PK: `assignment_version`. One immutable effective subject/role assignment version. Natural source_system + source_assignment_id; exactly one required role at reporting instant, non-additive secondary roles.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| assignment_version | text(128) | R | Immutable version | Controlled |
| source_system | text(50) | R | SRC-01 source namespace | Controlled |
| source_assignment_id | text(128) | R | Required reviewed identity; actual alias pending | Controlled |
| account_key | bigint | R | FK account.account_key | Controlled |
| branch_key | bigint | R | FK branch.branch_key; effective referenced version | Controlled |
| assignment_role | text(50) | R | SERVICING or ORIGINATION | Controlled |
| valid_from | instant UTC(6) | R | Source-supported applicability start | Controlled |
| valid_to | instant UTC(6) | O: open-ended | Exclusive end; null open-ended | Controlled |
| original_effective_end | instant UTC(6) | C: ended interval | Original end retention anchor retained through corrections | Controlled |
| source_version | text(128) | R | Required reviewed source version identity | Controlled |
| supersedes_version | text(128) | C: correction | FK account_branch_assignment.assignment_version; predecessor on correction | Controlled |
| correction_reason | text(200) | C: correction | Sanitized reason | Controlled |
| affected_from | instant UTC(6) | C: correction | Correction affected interval start | Controlled |
| affected_to | instant UTC(6) | O: open-ended or not correction | Exclusive affected end | Controlled |
| approval_action_id | text(128) | R | FK governance_action.action_id; independent source/Data Owner evidence | Controlled |

## loan_branch_assignment

Logical PK: `assignment_version`. One immutable effective subject/role assignment version. Natural source_system + source_assignment_id; exactly one required role at reporting instant, non-additive secondary roles.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| assignment_version | text(128) | R | Immutable version | Controlled |
| source_system | text(50) | R | SRC-02 source namespace | Controlled |
| source_assignment_id | text(128) | R | Required reviewed identity; actual alias pending | Controlled |
| loan_key | bigint | R | FK loan.loan_key | Controlled |
| branch_key | bigint | R | FK branch.branch_key; effective referenced version | Controlled |
| assignment_role | text(50) | R | SERVICING or ORIGINATION | Controlled |
| valid_from | instant UTC(6) | R | Source-supported applicability start | Controlled |
| valid_to | instant UTC(6) | O: open-ended | Exclusive end; null open-ended | Controlled |
| original_effective_end | instant UTC(6) | C: ended interval | Original end retention anchor retained through corrections | Controlled |
| source_version | text(128) | R | Required reviewed source version identity | Controlled |
| supersedes_version | text(128) | C: correction | FK loan_branch_assignment.assignment_version; predecessor on correction | Controlled |
| correction_reason | text(200) | C: correction | Sanitized reason | Controlled |
| affected_from | instant UTC(6) | C: correction | Correction affected interval start | Controlled |
| affected_to | instant UTC(6) | O: open-ended or not correction | Exclusive affected end | Controlled |
| approval_action_id | text(128) | R | FK governance_action.action_id; independent source/Data Owner evidence | Controlled |

## complaint_branch_assignment

Logical PK: `assignment_version`. One immutable effective subject/role assignment version. Natural source_system + source_assignment_id; exactly one required role at reporting instant, non-additive secondary roles.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| assignment_version | text(128) | R | Immutable version | Controlled |
| source_system | text(50) | R | SRC-04 source namespace | Controlled |
| source_assignment_id | text(128) | R | Required reviewed identity; actual alias pending | Controlled |
| complaint_key | bigint | R | FK complaint.complaint_key | Controlled |
| branch_key | bigint | R | FK branch.branch_key; effective referenced version | Controlled |
| assignment_role | text(50) | R | RESPONSIBLE | Controlled |
| valid_from | instant UTC(6) | R | Source-supported applicability start | Controlled |
| valid_to | instant UTC(6) | O: open-ended | Exclusive end; null open-ended | Controlled |
| original_effective_end | instant UTC(6) | C: ended interval | Original end retention anchor retained through corrections | Controlled |
| source_version | text(128) | R | Required reviewed source version identity | Controlled |
| supersedes_version | text(128) | C: correction | FK complaint_branch_assignment.assignment_version; predecessor on correction | Controlled |
| correction_reason | text(200) | C: correction | Sanitized reason | Controlled |
| affected_from | instant UTC(6) | C: correction | Correction affected interval start | Controlled |
| affected_to | instant UTC(6) | O: open-ended or not correction | Exclusive affected end | Controlled |
| approval_action_id | text(128) | R | FK governance_action.action_id; independent source/Data Owner evidence | Controlled |

## branch_attribution

Logical PK: `attribution_key`. One selected fact/analysis-purpose/observation/publication result; natural typed fact + purpose + observation + publication. No fanout into monetary facts.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| attribution_key | text(128) | R | Generated identity | Controlled |
| owner_entity | text(50) | R | Validated inventory entity | Controlled |
| owner_version_key | typed full-key reference | R | Full immutable owner key; selected version required | Controlled |
| purpose | text(50) | R | Approved DD-12 purpose; cash-flow and obligation separate | Controlled |
| observation_id | text(128) | R | Explicit item identity; SINGLE for indivisible fact | Controlled |
| publication_version | text(128) | R | FK publication.publication_version | Controlled |
| attribution_at | instant UTC(6) | R | Approved event instant or reviewed date cutoff; never guessed | Controlled |
| branch_key | bigint | C: Available | FK branch.branch_key; effective at attribution_at | Controlled |
| region_version | text(128) | C: Available | FK region.region_version; historical branch region | Controlled |
| basis | text(50) | R | SUPPLIED_VALIDATED, ASSIGNMENT, LINKED_TRANSACTION, HOME_CLASSIFICATION or UNAVAILABLE | Controlled |
| assignment_entity | text(50) | C: assignment/home basis or validation | Approved assignment entity or customer_version | Controlled |
| assignment_version | typed full-key reference | C: assignment/home basis or validation | Full assignment/customer version; applicable at attribution_at | Controlled |
| source_reference_key | internal key | C: supplied branch | FK source_reference.source_reference_key; supplied role/time evidence | Controlled |
| basis_attribution_key | text(128) | C: inherited attribution | FK branch_attribution.attribution_key; explicit linked/original attribution | Controlled |
| availability | text(50) | R | Available or Unavailable | Controlled |
| missing_reason | text(100) | C: Unavailable | Explicit missing/conflicting evidence; not fabricated branch | Controlled |
| supplied_branch_key | bigint | C: supplied branch | FK branch.branch_key; retained supplied branch, not silently replaced on mismatch | Controlled |
| supplied_role | text(50) | C: supplied branch | Reviewed source business role for event/snapshot/alert branch | Controlled |
| supplied_effective_at | instant UTC(6) | C: supplied branch | Source-supported effective instant; validate against required attribution instant | Controlled |
| validation_state | text(50) | R | Matched, Derived, Reviewed_alert, Unavailable or Conflict; Conflict cannot become accepted by silent precedence | Controlled |
| review_action_id | text(128) | C: reviewed mismatch or supplied alert approval | FK governance_action.action_id; source/Data Owner review evidence, not waiver of critical controls | Controlled |


## organization_publication

Logical PK: `publication_version + entity_name + natural_identity`. One selected organizational/assignment immutable version per natural history identity and publication. Natural identity includes effective start so multiple nonoverlapping intervals survive.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| publication_version | text(128) | R | FK publication.publication_version | Controlled |
| entity_name | text(50) | R | region, branch, organizational_successor, account_branch_assignment, loan_branch_assignment, complaint_branch_assignment or customer_version | Controlled |
| natural_identity | typed full-key reference | R | Complete source identity and interval start | Controlled |
| selected_version | typed full-key reference | R | Existing full immutable version PK; no conflicting selected intervals | Controlled |

## successor_scope_mapping

Logical PK: `scope_mapping_version`. One explicitly approved effective successor-to-predecessor branch access mapping; never implied by organizational succession.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| scope_mapping_version | text(128) | R | Immutable version | Controlled |
| current_branch_key | text(128) | R | FK organizational_unit.organization_key; BRANCH current grant target | Controlled |
| historical_branch_key | text(128) | R | FK organizational_unit.organization_key; BRANCH historical target | Controlled |
| valid_from | instant UTC(6) | R | Approved access start | Controlled |
| valid_to | instant UTC(6) | O: open-ended | Exclusive end | Controlled |
| revoked_at | instant UTC(6) | C: revoked | Immediate denial | Controlled |
| approval_action_id | text(128) | R | FK governance_action.action_id; requester/Compliance/Administrator separation | Controlled |
| supersedes_version | text(128) | C: corrected mapping | FK successor_scope_mapping.scope_mapping_version | Controlled |

## scope_resolution

Logical PK: `resolution_key`. One sanitized authorization decision/resolved stable branch member; Unavailable/deny can retain no member. Current hierarchy selection independent of historical report publication.

| Field | Logical type / maximum | Requiredness | Definition, source, derivation and validation | Classification |
| --- | --- | --- | --- | --- |
| resolution_key | text(128) | R | Generated evidence identity | Audit |
| access_attempt_id | text(128) | C: query | FK access_attempt.attempt_id; query authorization decision | Audit |
| export_event_key | internal key | C: export | FK export_event.event_key; export execution decision | Audit |
| entitlement_id | text(128) | C: applicable entitlement | FK access_entitlement.entitlement_id | Audit |
| checked_at | instant UTC(6) | R | Current evaluation instant | Audit |
| branch_identity | text(128) | C: resolved member | FK organizational_unit.organization_key; BRANCH resolved member | Audit |
| current_branch_version | bigint | C: region expansion | FK branch.branch_key; current region expansion evidence | Audit |
| scope_mapping_version | text(128) | C: successor scope | FK successor_scope_mapping.scope_mapping_version | Audit |
| decision | text(50) | R | Allow or deny; role/deny/scope controls remain | Audit |
| reason | text(100) | R | Sanitized decision reason | Audit |
