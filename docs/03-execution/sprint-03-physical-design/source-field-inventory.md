# SRC-01 through SRC-05 source-field reconciliation inventory

Status: **Draft — not approved**. Derived from the approved G3 logical [field inventory](../sprint-02-data-design/field-level-dictionary.md), [synthetic source contract](../sprint-02-data-design/synthetic-source-contract.md), [source definitions](../sprint-02-data-design/source-system-definitions.md), and [contract trace](../sprint-02-data-design/synthetic-contract-traceability.md). These are logical target fields, not verified received CSV headers. `R`, `O`, and `C` below are **logical** required, optional and conditional states. Generated keys, derived values and review evidence must not be demanded from source rows merely because their target field is `R`. Field meaning/type text is preserved from the authoritative dictionary; consult that dictionary for complete cross-field rules.

Every section has a source/entity/business-date/revision manifest identity, exact row count, checksum and required schema-version field under DD-01/DD-09. Actual schema-version **values**, physical header mapping, serialization and financial-control layout are **Pending confirmation** for all 27 sections. The synthetic contract fixes Chicago business-day/cutoff and correction/replay semantics; individual event dates, due dates, effective intervals and snapshot dates below retain their different meanings. Currency-separated signed scale-4 controls are required where applicable; exact control populations/physical fields remain Pending confirmation.

| Source | Section | Logical target(s) | Documented business identity or grain | Requirement/KPI/risk trace |
| --- | --- | --- | --- | --- |
| SRC-01 | `customers` | customer, customer_identity, customer_version | source_system + source_customer_id; governed identity/version keys are resolved | FR-01/02/03/05; US-01/02/08; RC-01/RC-05 |
| SRC-01 | `accounts` | account | source_system + source_account_id | FR-01/02/03/05; K01-K04; RC-01/RC-05 |
| SRC-01 | `holders` | account_customer | account + customer + role + effective start | DD-02; FR-03; RC-01/RC-05 |
| SRC-01 | `transactions` | transaction | source_system + source_transaction_id; version selected per publication | K01-K04; RC-01; DD-05/06 |
| SRC-01 | `account_restriction_state` | account_restriction_state | source-qualified account + effective state version | RC-05; DD-04/06 |
| SRC-01 | `account_branch_assignment` | account_branch_assignment | source_system + source_assignment_id; effective version | DD-12; K01-K04 |
| SRC-02 | `loans` | loan | source_system + source_loan_id | US-04; K05/K06; RC-03 |
| SRC-02 | `borrowers` | loan_customer | loan + customer + role + effective start | DD-02; US-04; RC-03 |
| SRC-02 | `positions` | loan_snapshot | loan + business date + selected snapshot version | DD-03; K05/K06; RC-03 |
| SRC-02 | `payments` | loan_payment | source_system + source_payment_id; immutable event version | DD-11; US-04; K05/K06 |
| SRC-02 | `loan_schedule` | loan_schedule | source_system + source_schedule_id; version/effective interval | DD-11; US-04 |
| SRC-02 | `loan_obligation` | loan_obligation | source_system + source_obligation_id; version | DD-11; US-04 |
| SRC-02 | `payment_allocation` | payment_allocation | source_system + source_allocation_id + component; version | DD-11; US-04 |
| SRC-02 | `payment_unapplied` | payment_unapplied | source-qualified payment + unapplied version | DD-11; US-04 |
| SRC-02 | `payment_adjustment` | payment_adjustment | source_system + source_adjustment_id; version | DD-11; US-04 |
| SRC-02 | `loan_account` | loan_account | source-qualified relationship ID; effective loan/account/role version | DD-11; US-04 |
| SRC-02 | `loan_branch_assignment` | loan_branch_assignment | source_system + source_assignment_id; effective version | DD-12; K05/K06 |
| SRC-03 | `alerts` | fraud_alert | source_system + source_alert_id | RC-02; FR-07/08 |
| SRC-03 | `fraud_alert_state` | fraud_alert_state | source-qualified alert + effective state version | RC-02; DD-04/06 |
| SRC-04 | `complaints` | complaint | source_system + source_complaint_id | K08-K10; RC-04 |
| SRC-04 | `complaint_snapshot` | complaint_snapshot | complaint + business date + selected snapshot version | DD-03; K08-K10; RC-04 |
| SRC-04 | `complaint_history_event` | complaint_history_event | source-qualified complaint + history event version | DD-03/06; K08-K10 |
| SRC-04 | `complaint_branch_assignment` | complaint_branch_assignment | source_system + source_assignment_id; effective version | DD-12; K08-K10 |
| SRC-05 | `organizational_unit` | organizational_unit | source_system + unit_type + source_id | DD-12; FR-09/10 |
| SRC-05 | `region` | region | source_system + region_id + valid_from | DD-12; FR-09/10 |
| SRC-05 | `branches` | branch | source_system + branch_id + valid_from | DD-12; K01-K10 |
| SRC-05 | `organizational_successor` | organizational_successor | predecessor + successor + valid_from | DD-12; FR-09/10 |

## Cross-section contract dimensions

The following dictionary/reference entries are approved synthetic logical domains and policies, not confirmed raw-code/header mappings. The approved status-mapping version must be applied before KPI/risk use; unrecognized values are not silently accepted.

| Source | Section | Applicable approved dictionary/reference policy | Logical monetary fields requiring field/currency/status-separated controls where applicable |
| --- | --- | --- | --- |
| SRC-01 | `customers` | segment RETAIL/SMALL_BUSINESS; identity crosswalk governed separately | No decimal logical target field; count controls still apply |
| SRC-01 | `accounts` | account_type CHECKING/SAVINGS | No decimal logical target field; count controls still apply |
| SRC-01 | `holders` | relationship_role PRIMARY/JOINT | No decimal logical target field; count controls still apply |
| SRC-01 | `transactions` | transaction_type TRANSFER/PAYMENT/WITHDRAWAL/DEPOSIT; canonical status via DD-06 mapping; debit/credit direction | `transaction.amount`, `transaction.absolute_comparison_amount` |
| SRC-01 | `account_restriction_state` | NONE/RESTRICTED/FROZEN/BLOCKED; RC-05 restricted mapping DD-06 | No decimal logical target field; count controls still apply |
| SRC-01 | `account_branch_assignment` | SERVICING/ORIGINATION | No decimal logical target field; count controls still apply |
| SRC-02 | `loans` | loan_type PERSONAL/AUTO/MORTGAGE; canonical active/status mapping DD-06 | No decimal logical target field; count controls still apply |
| SRC-02 | `borrowers` | relationship_role PRIMARY/CO_BORROWER | No decimal logical target field; count controls still apply |
| SRC-02 | `positions` | canonical loan status DD-06; DPD 0..36500 | `loan_snapshot.outstanding_principal` |
| SRC-02 | `payments` | PENDING/POSTED/FAILED/CANCELLED; POSTED posted_at policy DD-11 | `loan_payment.amount` |
| SRC-02 | `loan_schedule` | DD-11 schedule/effective version and currency contract | No decimal logical target field; count controls still apply |
| SRC-02 | `loan_obligation` | DD-11 component/currency and due_date contract | `loan_obligation.scheduled_amount` |
| SRC-02 | `payment_allocation` | PRINCIPAL/INTEREST/FEE components under DD-11 | `payment_allocation.amount` |
| SRC-02 | `payment_unapplied` | DD-11 source-confirmed unapplied amount state | `payment_unapplied.amount` |
| SRC-02 | `payment_adjustment` | REVERSAL/REFUND under DD-11 | `payment_adjustment.amount` |
| SRC-02 | `loan_account` | REPORTING relationship under DD-11 | No decimal logical target field; count controls still apply |
| SRC-02 | `loan_branch_assignment` | SERVICING/ORIGINATION | No decimal logical target field; count controls still apply |
| SRC-03 | `alerts` | fraud case OPEN/CLOSED; severity LOW/MEDIUM/HIGH/CRITICAL; RC-02 mapping DD-06 | No decimal logical target field; count controls still apply |
| SRC-03 | `fraud_alert_state` | fraud open/severity mapping DD-06 | No decimal logical target field; count controls still apply |
| SRC-04 | `complaints` | OPEN/IN_PROGRESS/REOPENED/CLOSED; Critical/High/Medium/Low; PHONE/WEB/BRANCH | No decimal logical target field; count controls still apply |
| SRC-04 | `complaint_snapshot` | complaint status/priority DD-06; as-of DD-03 | No decimal logical target field; count controls still apply |
| SRC-04 | `complaint_history_event` | closure/reopening event DD-06 | No decimal logical target field; count controls still apply |
| SRC-04 | `complaint_branch_assignment` | RESPONSIBLE | No decimal logical target field; count controls still apply |
| SRC-05 | `organizational_unit` | REGION/BRANCH | No decimal logical target field; count controls still apply |
| SRC-05 | `region` | DD-12 effective region history | No decimal logical target field; count controls still apply |
| SRC-05 | `branches` | DD-12 effective branch/region history | No decimal logical target field; count controls still apply |
| SRC-05 | `organizational_successor` | DD-12 same-unit-type successor; no automatic access grant | No decimal logical target field; count controls still apply |

## SRC-01 / customers

Logical target(s): `customer, customer_identity, customer_version`. Source business identity/grain: source_system + source_customer_id; governed identity/version keys are resolved. Relevant trace: FR-01/02/03/05; US-01/02/08; RC-01/RC-05. Physical source key/header aliases: **Pending confirmation** where the G3 proposal has not been fixture-confirmed.

| Logical target | Field | Logical type/format | Logical requiredness | Approved meaning/derivation |
| --- | --- | --- | --- | --- |
| `customer` | `customer_key` | bigint | R | generated |
| `customer` | `display_name` | text(200) | R | display_name |
| `customer` | `synthetic_master_id` | text(128) | R | synthetic_master_id |
| `customer` | `contact` | text(254) | O: not applicable or not supplied; supplied values must validate | contact |
| `customer` | `source_system` | text(50) | R | Source namespace; natural source ID must be qualified by this value |
| `customer` | `source_customer_id` | text(128) | R | SRC-01.customer_id; preserve source identifier, distinct from synthetic_master_id |
| `customer_identity` | `identity_key` | bigint | R | generated |
| `customer_identity` | `customer_key` | bigint | R | resolved customer; FK customer.customer_key |
| `customer_identity` | `source_system` | text(50) | R | source namespace |
| `customer_identity` | `source_customer_id` | text(128) | R | source customer_id |
| `customer_identity` | `valid_from` | instant UTC(6) | R | reviewed effective start |
| `customer_identity` | `valid_to` | instant UTC(6) | O: open-ended interval | Exclusive interval end; null open-ended, never defaulted current date |
| `customer_identity` | `match_method` | text(50) | R | deterministic method |
| `customer_identity` | `review_state` | text(50) | R | review outcome |
| `customer_identity` | `approval_reference` | text(100) | C: approved identity mapping | Review evidence reference required before Approved |
| `customer_version` | `customer_version_key` | bigint | R | generated |
| `customer_version` | `customer_key` | bigint | R | customer_id resolved; FK customer.customer_key |
| `customer_version` | `segment` | text(50) | R | segment |
| `customer_version` | `branch_key` | bigint | R | home_branch_id resolved; FK branch.branch_key |
| `customer_version` | `valid_from` | instant UTC(6) | R | effective change boundary |
| `customer_version` | `valid_to` | instant UTC(6) | O: open-ended interval | Exclusive interval end; null open-ended, never defaulted current date |

## SRC-01 / accounts

Logical target(s): `account`. Source business identity/grain: source_system + source_account_id. Relevant trace: FR-01/02/03/05; K01-K04; RC-01/RC-05. Physical source key/header aliases: **Pending confirmation** where the G3 proposal has not been fixture-confirmed.

| Logical target | Field | Logical type/format | Logical requiredness | Approved meaning/derivation |
| --- | --- | --- | --- | --- |
| `account` | `account_key` | bigint | R | generated |
| `account` | `source_account_id` | text(128) | R | account_id |
| `account` | `account_number` | text(128) | R | account_number |
| `account` | `masked_account` | text(128) | R | Fixed mask plus final four source account characters; not a relational key |
| `account` | `branch_key` | bigint | R | Selected-current convenience projection only; historical authority is account_branch_assignment; FK branch.branch_key |
| `account` | `account_type` | text(50) | R | account_type |
| `account` | `opened_date` | date | R | opened_date |
| `account` | `closed_date` | date | C: closed account | Source closure date; absent for an open account |
| `account` | `source_system` | text(50) | R | Source namespace; natural source ID must be qualified by this value |

## SRC-01 / holders

Logical target(s): `account_customer`. Source business identity/grain: account + customer + role + effective start. Relevant trace: DD-02; FR-03; RC-01/RC-05. Physical source key/header aliases: **Pending confirmation** where the G3 proposal has not been fixture-confirmed.

| Logical target | Field | Logical type/format | Logical requiredness | Approved meaning/derivation |
| --- | --- | --- | --- | --- |
| `account_customer` | `account_key` | bigint | R | account_id resolved; FK account.account_key |
| `account_customer` | `customer_key` | bigint | R | customer_id resolved; FK customer.customer_key |
| `account_customer` | `relationship_role` | text(50) | R | source ownership role; source code mapping Pending confirmation |
| `account_customer` | `valid_from` | instant UTC(6) | R | ownership_start |
| `account_customer` | `valid_to` | instant UTC(6) | O: open-ended interval | Exclusive interval end; null open-ended, never defaulted current date |

## SRC-01 / transactions

Logical target(s): `transaction`. Source business identity/grain: source_system + source_transaction_id; version selected per publication. Relevant trace: K01-K04; RC-01; DD-05/06. Physical source key/header aliases: **Pending confirmation** where the G3 proposal has not been fixture-confirmed.

| Logical target | Field | Logical type/format | Logical requiredness | Approved meaning/derivation |
| --- | --- | --- | --- | --- |
| `transaction` | `transaction_key` | bigint | R | generated |
| `transaction` | `source_transaction_id` | text(128) | R | transaction_id |
| `transaction` | `account_key` | bigint | R | account_id resolved; FK account.account_key |
| `transaction` | `branch_key` | bigint | R | account branch at occurred_at; FK branch.branch_key |
| `transaction` | `occurred_at` | instant UTC(6) | R | occurred_at |
| `transaction` | `amount` | decimal(20,4) | R | amount |
| `transaction` | `currency` | char(3) | R | currency |
| `transaction` | `transaction_type` | text(50) | R | transaction_type |
| `transaction` | `raw_status` | text(50) | R | status |
| `transaction` | `status` | text(50) | R | versioned status mapping |
| `transaction` | `source_system` | text(50) | R | Source namespace; natural source ID must be qualified by this value |
| `transaction` | `source_initiating_customer_id` | text(128) | O: not applicable or not supplied; supplied values must validate | SRC-01 initiating-customer identifier when supplied; invalid supplied ID gives Unknown and identity exception, no fallback |
| `transaction` | `debit_credit_direction` | text(50) | R | Source debit/credit direction retained; source alias mapping required |
| `transaction` | `absolute_comparison_amount` | decimal(20,4) | C: eligible RC-01 comparison | abs(amount), nonzero; signed amount retained |
| `transaction` | `business_date` | date | R | Derived Chicago event business date; source manifest date retained separately |
| `transaction` | `source_version` | text(128) | R | Immutable source event version; source contract must supply or reliably identify it |
| `transaction` | `batch_revision` | integer >= 1 | R | Delivered source_extract revision through source_reference |
| `transaction` | `supersedes_event_key` | bigint | O | FK transaction.transaction_key; existing acyclic predecessor; correction retains original fields |

## SRC-01 / account_restriction_state

Logical target(s): `account_restriction_state`. Source business identity/grain: source-qualified account + effective state version. Relevant trace: RC-05; DD-04/06. Physical source key/header aliases: **Pending confirmation** where the G3 proposal has not been fixture-confirmed.

| Logical target | Field | Logical type/format | Logical requiredness | Approved meaning/derivation |
| --- | --- | --- | --- | --- |
| `account_restriction_state` | `state_version` | text(128) | R | Immutable generated version PK |
| `account_restriction_state` | `account_key` | bigint | R | FK account.account_key |
| `account_restriction_state` | `effective_from` | instant UTC(6) | R | Source-supported effective start |
| `account_restriction_state` | `effective_to` | instant UTC(6) | O: not applicable or not supplied; supplied values must validate | Exclusive end; null open-ended |
| `account_restriction_state` | `state_as_of_at` | instant UTC(6) | R | Source-supported knowledge instant |
| `account_restriction_state` | `source_version` | text(128) | R | Source state version |
| `account_restriction_state` | `publication_version` | text(128) | C: published state | FK publication.publication_version |
| `account_restriction_state` | `supersedes_state_version` | text(128) | O: not applicable or not supplied; supplied values must validate | FK account_restriction_state.state_version; existing acyclic predecessor |
| `account_restriction_state` | `raw_risk_restriction_status` | text(50) | R | Source value retained; invalid domain quarantined with raw evidence |
| `account_restriction_state` | `risk_restriction_status` | text(50) | C: valid approved mapping | DD-06 canonical mapping; unmapped causes Unknown, never fabricated negative finding |

## SRC-01 / account_branch_assignment

Logical target(s): `account_branch_assignment`. Source business identity/grain: source_system + source_assignment_id; effective version. Relevant trace: DD-12; K01-K04. Physical source key/header aliases: **Pending confirmation** where the G3 proposal has not been fixture-confirmed.

| Logical target | Field | Logical type/format | Logical requiredness | Approved meaning/derivation |
| --- | --- | --- | --- | --- |
| `account_branch_assignment` | `assignment_version` | text(128) | R | Immutable version |
| `account_branch_assignment` | `source_system` | text(50) | R | SRC-01 source namespace |
| `account_branch_assignment` | `source_assignment_id` | text(128) | R | Required reviewed identity; actual alias pending |
| `account_branch_assignment` | `account_key` | bigint | R | FK account.account_key |
| `account_branch_assignment` | `branch_key` | bigint | R | FK branch.branch_key; effective referenced version |
| `account_branch_assignment` | `assignment_role` | text(50) | R | SERVICING or ORIGINATION |
| `account_branch_assignment` | `valid_from` | instant UTC(6) | R | Source-supported applicability start |
| `account_branch_assignment` | `valid_to` | instant UTC(6) | O: open-ended | Exclusive end; null open-ended |
| `account_branch_assignment` | `original_effective_end` | instant UTC(6) | C: ended interval | Original end retention anchor retained through corrections |
| `account_branch_assignment` | `source_version` | text(128) | R | Required reviewed source version identity |
| `account_branch_assignment` | `supersedes_version` | text(128) | C: correction | FK account_branch_assignment.assignment_version; predecessor on correction |
| `account_branch_assignment` | `correction_reason` | text(200) | C: correction | Sanitized reason |
| `account_branch_assignment` | `affected_from` | instant UTC(6) | C: correction | Correction affected interval start |
| `account_branch_assignment` | `affected_to` | instant UTC(6) | O: open-ended or not correction | Exclusive affected end |
| `account_branch_assignment` | `approval_action_id` | text(128) | R | FK governance_action.action_id; independent source/Data Owner evidence |

## SRC-02 / loans

Logical target(s): `loan`. Source business identity/grain: source_system + source_loan_id. Relevant trace: US-04; K05/K06; RC-03. Physical source key/header aliases: **Pending confirmation** where the G3 proposal has not been fixture-confirmed.

| Logical target | Field | Logical type/format | Logical requiredness | Approved meaning/derivation |
| --- | --- | --- | --- | --- |
| `loan` | `loan_key` | bigint | R | generated |
| `loan` | `source_loan_id` | text(128) | R | loan_id |
| `loan` | `branch_key` | bigint | R | Selected-current convenience projection only; historical authority is loan_branch_assignment; FK branch.branch_key |
| `loan` | `loan_type` | text(50) | R | loan_type |
| `loan` | `originated_date` | date | R | originated_date |
| `loan` | `source_system` | text(50) | R | Source namespace; natural source ID must be qualified by this value |
| `loan` | `contractual_currency` | char(3) | R | Source loan contractual currency; all DD-11 obligations/payments/allocations/unapplied/adjustments must agree; no conversion |

## SRC-02 / borrowers

Logical target(s): `loan_customer`. Source business identity/grain: loan + customer + role + effective start. Relevant trace: DD-02; US-04; RC-03. Physical source key/header aliases: **Pending confirmation** where the G3 proposal has not been fixture-confirmed.

| Logical target | Field | Logical type/format | Logical requiredness | Approved meaning/derivation |
| --- | --- | --- | --- | --- |
| `loan_customer` | `loan_key` | bigint | R | loan_id resolved; FK loan.loan_key |
| `loan_customer` | `customer_key` | bigint | R | borrower_customer_id resolved through crosswalk; FK customer.customer_key |
| `loan_customer` | `relationship_role` | text(50) | R | source borrower/co-borrower role; domain Pending confirmation |
| `loan_customer` | `valid_from` | instant UTC(6) | R | relationship_start |
| `loan_customer` | `valid_to` | instant UTC(6) | O: open-ended interval | Exclusive interval end; null open-ended, never defaulted current date |

## SRC-02 / positions

Logical target(s): `loan_snapshot`. Source business identity/grain: loan + business date + selected snapshot version. Relevant trace: DD-03; K05/K06; RC-03. Physical source key/header aliases: **Pending confirmation** where the G3 proposal has not been fixture-confirmed.

| Logical target | Field | Logical type/format | Logical requiredness | Approved meaning/derivation |
| --- | --- | --- | --- | --- |
| `loan_snapshot` | `loan_key` | bigint | R | loan_id resolved; FK loan.loan_key |
| `loan_snapshot` | `business_date` | date | R | business_date |
| `loan_snapshot` | `currency` | char(3) | R | currency |
| `loan_snapshot` | `days_past_due` | integer [0,36500] | R | days_past_due |
| `loan_snapshot` | `status` | text(50) | R | versioned status mapping |
| `loan_snapshot` | `as_of_cutoff_at` | instant UTC(6) | R | source-supported knowledge cutoff for business_date; exact cutoff remains a source-contract detail |
| `loan_snapshot` | `batch_revision` | integer >= 1 | R | source_extract.revision; exact delivered batch revision |
| `loan_snapshot` | `source_version` | text(128) | R | source record/state version reference; if absent, source contract must define a reliable version identity |
| `loan_snapshot` | `snapshot_version` | text(128) | R | proposed immutable version identifier linking preserved values to publication/correction history |
| `loan_snapshot` | `reconstruction_reference` | text(100) | C: reliably reconstructed snapshot | required evidence/method/version for reconstructed state |
| `loan_snapshot` | `state_availability` | text(50) | R | supplied or reliably_reconstructed for accepted snapshot; unavailable expectations go in historical_coverage |
| `loan_snapshot` | `supersedes_snapshot_version` | text(128) | O: not applicable or not supplied; supplied values must validate | FK loan_snapshot.snapshot_version; existing predecessor; acyclic correction chain |
| `loan_snapshot` | `correction_reference` | text(100) | C: corrected version | Correction approval/evidence reference; predecessor required for correction of existing version |
| `loan_snapshot` | `outstanding_principal` | decimal(20,4) | R | SRC-02 outstanding_principal; zero valid; negative quarantined; missing incomplete DD-09; no absolute conversion or positive-only population filter |

## SRC-02 / payments

Logical target(s): `loan_payment`. Source business identity/grain: source_system + source_payment_id; immutable event version. Relevant trace: DD-11; US-04; K05/K06. Physical source key/header aliases: **Pending confirmation** where the G3 proposal has not been fixture-confirmed.

| Logical target | Field | Logical type/format | Logical requiredness | Approved meaning/derivation |
| --- | --- | --- | --- | --- |
| `loan_payment` | `payment_key` | bigint | R | generated |
| `loan_payment` | `source_payment_id` | text(128) | R | payment_id |
| `loan_payment` | `loan_key` | bigint | R | loan_id resolved; FK loan.loan_key |
| `loan_payment` | `paid_at` | instant UTC(6) | R | paid_at |
| `loan_payment` | `amount` | decimal(20,4) | R | Positive canonical actual-payment amount; zero/negative invalid, preserve raw signed quarantine evidence |
| `loan_payment` | `currency` | char(3) | R | Must equal referenced loan.contractual_currency; no conversion |
| `loan_payment` | `source_system` | text(50) | R | Source namespace; natural source ID must be qualified by this value |
| `loan_payment` | `business_date` | date | R | Derived Chicago event business date; source manifest date retained separately |
| `loan_payment` | `source_version` | text(128) | R | Immutable source event version; source contract must supply or reliably identify it |
| `loan_payment` | `batch_revision` | integer >= 1 | R | Delivered source_extract revision through source_reference |
| `loan_payment` | `supersedes_event_key` | bigint | O | FK loan_payment.payment_key; existing acyclic predecessor; correction retains original fields |
| `loan_payment` | `raw_status` | text(50) | R | Source payment status; approved mapping required |
| `loan_payment` | `status` | text(50) | R | PENDING, POSTED, FAILED or CANCELLED; only POSTED financially effective |
| `loan_payment` | `correction_reference` | text(100) | C: corrected event version | Independent correction evidence; supersedes_event_key is data correction, not business adjustment |
| `loan_payment` | `posted_at` | instant UTC(6) | C: POSTED | Synthetic SRC-02 posted_at: required for POSTED, null otherwise, >= paid_at; offset-qualified instant normalized UTC; paid_at remains event evidence |

## SRC-02 / loan_schedule

Logical target(s): `loan_schedule`. Source business identity/grain: source_system + source_schedule_id; version/effective interval. Relevant trace: DD-11; US-04. Physical source key/header aliases: **Pending confirmation** where the G3 proposal has not been fixture-confirmed.

| Logical target | Field | Logical type/format | Logical requiredness | Approved meaning/derivation |
| --- | --- | --- | --- | --- |
| `loan_schedule` | `schedule_version` | text(128) | R | Immutable internal schedule version |
| `loan_schedule` | `source_system` | text(50) | R | Loan Servicing source namespace |
| `loan_schedule` | `source_schedule_id` | text(128) | R | Required stable source schedule ID; actual alias pending |
| `loan_schedule` | `loan_key` | bigint | R | FK loan.loan_key |
| `loan_schedule` | `currency` | char(3) | R | Loan contractual currency |
| `loan_schedule` | `effective_from` | instant UTC(6) | R | Source-supported schedule applicability start |
| `loan_schedule` | `effective_to` | instant UTC(6) | O: open-ended | Exclusive end; no conflicting selected schedule interval for same source schedule identity |
| `loan_schedule` | `original_effective_date` | date | R | Original Chicago effective anchor retained through correction/rescheduling |
| `loan_schedule` | `supersedes_schedule_version` | text(128) | O: first version | FK loan_schedule.schedule_version; required for corrected/rescheduled existing schedule |
| `loan_schedule` | `source_version` | text(128) | R | Source-supported immutable version identity; exact convention requires verified contract |
| `loan_schedule` | `batch_revision` | integer >= 1 | R | Qualified source_extract revision through source_reference |
| `loan_schedule` | `correction_reference` | text(100) | C: corrected version | Approved data-correction evidence; prior version preserved |

## SRC-02 / loan_obligation

Logical target(s): `loan_obligation`. Source business identity/grain: source_system + source_obligation_id; version. Relevant trace: DD-11; US-04. Physical source key/header aliases: **Pending confirmation** where the G3 proposal has not been fixture-confirmed.

| Logical target | Field | Logical type/format | Logical requiredness | Approved meaning/derivation |
| --- | --- | --- | --- | --- |
| `loan_obligation` | `obligation_version` | text(128) | R | Immutable internal version |
| `loan_obligation` | `source_system` | text(50) | R | Source namespace |
| `loan_obligation` | `source_obligation_id` | text(128) | R | Stable obligation identity across rescheduling or approved predecessor mapping |
| `loan_obligation` | `schedule_version` | text(128) | R | FK loan_schedule.schedule_version; selected coherent schedule |
| `loan_obligation` | `loan_key` | bigint | R | FK loan.loan_key; must equal schedule loan |
| `loan_obligation` | `due_date` | date | R | Contractual due date belongs here, never canonical payment |
| `loan_obligation` | `original_obligation_date` | date | R | Original obligation retention anchor; rescheduling cannot reset it |
| `loan_obligation` | `scheduled_amount` | decimal(20,4) | R | Source-supplied contractual obligation amount; component/sign domain contract required |
| `loan_obligation` | `currency` | char(3) | R | Same as loan contractual currency |
| `loan_obligation` | `effective_from` | instant UTC(6) | R | Source-supported applicability start |
| `loan_obligation` | `effective_to` | instant UTC(6) | O: open-ended | Exclusive end |
| `loan_obligation` | `supersedes_obligation_version` | text(128) | O: first version | FK loan_obligation.obligation_version; prior immutable obligation retained |
| `loan_obligation` | `source_version` | text(128) | R | Source-supported immutable version identity; exact convention requires verified contract |
| `loan_obligation` | `batch_revision` | integer >= 1 | R | Qualified source_extract revision through source_reference |
| `loan_obligation` | `correction_reference` | text(100) | C: corrected version | Approved data-correction evidence; prior version preserved |

## SRC-02 / payment_allocation

Logical target(s): `payment_allocation`. Source business identity/grain: source_system + source_allocation_id + component; version. Relevant trace: DD-11; US-04. Physical source key/header aliases: **Pending confirmation** where the G3 proposal has not been fixture-confirmed.

| Logical target | Field | Logical type/format | Logical requiredness | Approved meaning/derivation |
| --- | --- | --- | --- | --- |
| `payment_allocation` | `allocation_version` | text(128) | R | Immutable internal allocation version |
| `payment_allocation` | `source_system` | text(50) | R | Source namespace |
| `payment_allocation` | `source_allocation_id` | text(128) | R | Source allocation ID; not generated allocation business fact |
| `payment_allocation` | `payment_key` | bigint | R | FK loan_payment.payment_key; financially active allocation requires POSTED selected payment |
| `payment_allocation` | `obligation_version` | text(128) | R | FK loan_obligation.obligation_version; obligation and payment have same loan |
| `payment_allocation` | `component` | text(50) | R | PRINCIPAL, INTEREST or FEE from reviewed source mapping |
| `payment_allocation` | `amount` | decimal(20,4) | R | Source-supplied component allocation; no invented waterfall |
| `payment_allocation` | `currency` | char(3) | R | Matches payment/obligation/loan currency |
| `payment_allocation` | `effective_from` | instant UTC(6) | R | Source-supported active start |
| `payment_allocation` | `effective_to` | instant UTC(6) | O: open-ended | Exclusive active end; preserve withdrawn/superseded allocation evidence |
| `payment_allocation` | `original_effective_date` | date | R | Original applicability retention anchor, not revised publication date |
| `payment_allocation` | `supersedes_allocation_version` | text(128) | O: first version | FK payment_allocation.allocation_version; correction version, not a business adjustment |
| `payment_allocation` | `source_version` | text(128) | R | Source-supported immutable version identity; exact convention requires verified contract |
| `payment_allocation` | `batch_revision` | integer >= 1 | R | Qualified source_extract revision through source_reference |
| `payment_allocation` | `correction_reference` | text(100) | C: corrected version | Approved data-correction evidence; prior version preserved |

## SRC-02 / payment_unapplied

Logical target(s): `payment_unapplied`. Source business identity/grain: source-qualified payment + unapplied version. Relevant trace: DD-11; US-04. Physical source key/header aliases: **Pending confirmation** where the G3 proposal has not been fixture-confirmed.

| Logical target | Field | Logical type/format | Logical requiredness | Approved meaning/derivation |
| --- | --- | --- | --- | --- |
| `payment_unapplied` | `unapplied_version` | text(128) | R | Immutable internal state version |
| `payment_unapplied` | `payment_key` | bigint | R | FK loan_payment.payment_key |
| `payment_unapplied` | `amount` | decimal(20,4) | R | Separate source-supported unapplied amount; missing never defaults zero |
| `payment_unapplied` | `currency` | char(3) | R | Same payment/loan contractual currency |
| `payment_unapplied` | `effective_from` | instant UTC(6) | R | State applicability start |
| `payment_unapplied` | `effective_to` | instant UTC(6) | O: open-ended | Exclusive end; selected effective states cannot overlap |
| `payment_unapplied` | `original_effective_date` | date | R | Original state retention anchor |
| `payment_unapplied` | `supersedes_unapplied_version` | text(128) | O: first version | FK payment_unapplied.unapplied_version |
| `payment_unapplied` | `source_version` | text(128) | R | Source-supported immutable version identity; exact convention requires verified contract |
| `payment_unapplied` | `batch_revision` | integer >= 1 | R | Qualified source_extract revision through source_reference |
| `payment_unapplied` | `correction_reference` | text(100) | C: corrected version | Approved data-correction evidence; prior version preserved |

## SRC-02 / payment_adjustment

Logical target(s): `payment_adjustment`. Source business identity/grain: source_system + source_adjustment_id; version. Relevant trace: DD-11; US-04. Physical source key/header aliases: **Pending confirmation** where the G3 proposal has not been fixture-confirmed.

| Logical target | Field | Logical type/format | Logical requiredness | Approved meaning/derivation |
| --- | --- | --- | --- | --- |
| `payment_adjustment` | `adjustment_key` | bigint | R | Generated immutable event-version key |
| `payment_adjustment` | `source_system` | text(50) | R | Source namespace |
| `payment_adjustment` | `source_adjustment_id` | text(128) | R | Required source adjustment identifier |
| `payment_adjustment` | `original_payment_key` | bigint | R | FK loan_payment.payment_key; original POSTED event, not deleted/reduced |
| `payment_adjustment` | `adjustment_type` | text(50) | R | REVERSAL or REFUND |
| `payment_adjustment` | `amount` | decimal(20,4) | R | Positive canonical adjustment magnitude; approved mapping preserves original signed raw value; cumulative cap applies |
| `payment_adjustment` | `currency` | char(3) | R | Same original payment/loan currency |
| `payment_adjustment` | `occurred_at` | instant UTC(6) | R | Actual adjustment event timestamp |
| `payment_adjustment` | `business_date` | date | R | Original Chicago adjustment event date; does not reset payment clock |
| `payment_adjustment` | `application_reference` | text(100) | R | Source-supported adjustment/allocation/unapplied impact evidence; reviewed semantics required, no inferred waterfall |
| `payment_adjustment` | `supersedes_event_key` | bigint | O: first version | FK payment_adjustment.adjustment_key; data correction only |
| `payment_adjustment` | `source_version` | text(128) | R | Source-supported immutable version identity; exact convention requires verified contract |
| `payment_adjustment` | `batch_revision` | integer >= 1 | R | Qualified source_extract revision through source_reference |
| `payment_adjustment` | `correction_reference` | text(100) | C: corrected version | Approved data-correction evidence; prior version preserved |

## SRC-02 / loan_account

Logical target(s): `loan_account`. Source business identity/grain: source-qualified relationship ID; effective loan/account/role version. Relevant trace: DD-11; US-04. Physical source key/header aliases: **Pending confirmation** where the G3 proposal has not been fixture-confirmed.

| Logical target | Field | Logical type/format | Logical requiredness | Approved meaning/derivation |
| --- | --- | --- | --- | --- |
| `loan_account` | `loan_account_version` | text(128) | R | Immutable relationship version |
| `loan_account` | `source_system` | text(50) | R | Relationship source namespace |
| `loan_account` | `source_relationship_id` | text(128) | R | Required source-supported or approved relationship identity |
| `loan_account` | `loan_key` | bigint | R | FK loan.loan_key |
| `loan_account` | `account_key` | bigint | R | FK account.account_key; source-qualified account resolved, never suffix match |
| `loan_account` | `relationship_role` | text(50) | R | REPORTING required; other roles not invented |
| `loan_account` | `valid_from` | instant UTC(6) | R | Source-supported relationship applicability start |
| `loan_account` | `valid_to` | instant UTC(6) | O: open-ended | Exclusive end; REPORTING coverage exactly one at required as-of instant |
| `loan_account` | `original_effective_date` | date | R | Original effective anchor; DD-10 current/dependency exception applies |
| `loan_account` | `supersedes_relationship_version` | text(128) | O: first version | FK loan_account.loan_account_version |
| `loan_account` | `review_reference` | text(100) | R | Required reviewed source relationship contract/evidence, not actual review claimed |
| `loan_account` | `source_version` | text(128) | R | Source-supported immutable version identity; exact convention requires verified contract |
| `loan_account` | `batch_revision` | integer >= 1 | R | Qualified source_extract revision through source_reference |
| `loan_account` | `correction_reference` | text(100) | C: corrected version | Approved data-correction evidence; prior version preserved |

## SRC-02 / loan_branch_assignment

Logical target(s): `loan_branch_assignment`. Source business identity/grain: source_system + source_assignment_id; effective version. Relevant trace: DD-12; K05/K06. Physical source key/header aliases: **Pending confirmation** where the G3 proposal has not been fixture-confirmed.

| Logical target | Field | Logical type/format | Logical requiredness | Approved meaning/derivation |
| --- | --- | --- | --- | --- |
| `loan_branch_assignment` | `assignment_version` | text(128) | R | Immutable version |
| `loan_branch_assignment` | `source_system` | text(50) | R | SRC-02 source namespace |
| `loan_branch_assignment` | `source_assignment_id` | text(128) | R | Required reviewed identity; actual alias pending |
| `loan_branch_assignment` | `loan_key` | bigint | R | FK loan.loan_key |
| `loan_branch_assignment` | `branch_key` | bigint | R | FK branch.branch_key; effective referenced version |
| `loan_branch_assignment` | `assignment_role` | text(50) | R | SERVICING or ORIGINATION |
| `loan_branch_assignment` | `valid_from` | instant UTC(6) | R | Source-supported applicability start |
| `loan_branch_assignment` | `valid_to` | instant UTC(6) | O: open-ended | Exclusive end; null open-ended |
| `loan_branch_assignment` | `original_effective_end` | instant UTC(6) | C: ended interval | Original end retention anchor retained through corrections |
| `loan_branch_assignment` | `source_version` | text(128) | R | Required reviewed source version identity |
| `loan_branch_assignment` | `supersedes_version` | text(128) | C: correction | FK loan_branch_assignment.assignment_version; predecessor on correction |
| `loan_branch_assignment` | `correction_reason` | text(200) | C: correction | Sanitized reason |
| `loan_branch_assignment` | `affected_from` | instant UTC(6) | C: correction | Correction affected interval start |
| `loan_branch_assignment` | `affected_to` | instant UTC(6) | O: open-ended or not correction | Exclusive affected end |
| `loan_branch_assignment` | `approval_action_id` | text(128) | R | FK governance_action.action_id; independent source/Data Owner evidence |

## SRC-03 / alerts

Logical target(s): `fraud_alert`. Source business identity/grain: source_system + source_alert_id. Relevant trace: RC-02; FR-07/08. Physical source key/header aliases: **Pending confirmation** where the G3 proposal has not been fixture-confirmed.

| Logical target | Field | Logical type/format | Logical requiredness | Approved meaning/derivation |
| --- | --- | --- | --- | --- |
| `fraud_alert` | `alert_key` | bigint | R | generated |
| `fraud_alert` | `source_alert_id` | text(128) | R | alert_id |
| `fraud_alert` | `customer_key` | bigint | R | customer_id resolved; FK customer.customer_key |
| `fraud_alert` | `transaction_key` | bigint | O: alert linked to transaction | FK transaction.transaction_key when supplied; unlinked alerts excluded from K04 numerator |
| `fraud_alert` | `alert_time` | instant UTC(6) | R | alert_time |
| `fraud_alert` | `severity` | text(50) | R | severity |
| `fraud_alert` | `case_status` | text(50) | R | case_status |
| `fraud_alert` | `reason` | text(1000) | R | reason; excluded from ordinary exports |
| `fraud_alert` | `source_system` | text(50) | R | Source namespace; natural source ID must be qualified by this value |

## SRC-03 / fraud_alert_state

Logical target(s): `fraud_alert_state`. Source business identity/grain: source-qualified alert + effective state version. Relevant trace: RC-02; DD-04/06. Physical source key/header aliases: **Pending confirmation** where the G3 proposal has not been fixture-confirmed.

| Logical target | Field | Logical type/format | Logical requiredness | Approved meaning/derivation |
| --- | --- | --- | --- | --- |
| `fraud_alert_state` | `state_version` | text(128) | R | Immutable generated version PK |
| `fraud_alert_state` | `alert_key` | bigint | R | FK fraud_alert.alert_key |
| `fraud_alert_state` | `effective_from` | instant UTC(6) | R | Source-supported effective start |
| `fraud_alert_state` | `effective_to` | instant UTC(6) | O: not applicable or not supplied; supplied values must validate | Exclusive end; null open-ended |
| `fraud_alert_state` | `state_as_of_at` | instant UTC(6) | R | Source-supported knowledge instant |
| `fraud_alert_state` | `source_version` | text(128) | R | Source state version |
| `fraud_alert_state` | `publication_version` | text(128) | C: published state | FK publication.publication_version |
| `fraud_alert_state` | `supersedes_state_version` | text(128) | O: not applicable or not supplied; supplied values must validate | FK fraud_alert_state.state_version; existing acyclic predecessor |
| `fraud_alert_state` | `raw_case_status` | text(50) | R | Source value retained; invalid domain quarantined with raw evidence |
| `fraud_alert_state` | `case_status` | text(50) | C: valid approved mapping | DD-06 canonical mapping; unmapped causes Unknown, never fabricated negative finding |
| `fraud_alert_state` | `raw_severity` | text(50) | R | Source value retained; invalid domain quarantined with raw evidence |
| `fraud_alert_state` | `severity` | text(50) | C: valid approved mapping | DD-06 canonical mapping; unmapped causes Unknown, never fabricated negative finding |

## SRC-04 / complaints

Logical target(s): `complaint`. Source business identity/grain: source_system + source_complaint_id. Relevant trace: K08-K10; RC-04. Physical source key/header aliases: **Pending confirmation** where the G3 proposal has not been fixture-confirmed.

| Logical target | Field | Logical type/format | Logical requiredness | Approved meaning/derivation |
| --- | --- | --- | --- | --- |
| `complaint` | `complaint_key` | bigint | R | generated |
| `complaint` | `source_complaint_id` | text(128) | R | complaint_id |
| `complaint` | `customer_key` | bigint | R | customer_id resolved; FK customer.customer_key |
| `complaint` | `branch_key` | bigint | R | branch_id resolved; FK branch.branch_key |
| `complaint` | `priority` | text(50) | R | priority |
| `complaint` | `channel` | text(50) | R | channel |
| `complaint` | `status` | text(50) | R | status |
| `complaint` | `source_system` | text(50) | R | Source namespace; natural source ID must be qualified by this value |
| `complaint` | `created_at` | instant UTC(6) | R | Immutable original SRC-04 creation instant; original_created_at may only be a documented source alias |
| `complaint` | `priority_at_creation` | text(50) | C: SLA evaluation | Immutable creation priority, source or reliable historical reconstruction; Critical/High/Medium/Low |
| `complaint` | `closed_at` | instant UTC(6) | C: closed selected state | SRC-04 closure known in selected as-of/publication; null for open/REOPENED; contradictory status/closure quarantined |
| `complaint` | `final_closed_at` | instant UTC(6) | C: finally closed in selected publication | Derived original-creation-to-final-closure history; never use future closure evidence |

## SRC-04 / complaint_snapshot

Logical target(s): `complaint_snapshot`. Source business identity/grain: complaint + business date + selected snapshot version. Relevant trace: DD-03; K08-K10; RC-04. Physical source key/header aliases: **Pending confirmation** where the G3 proposal has not been fixture-confirmed.

| Logical target | Field | Logical type/format | Logical requiredness | Approved meaning/derivation |
| --- | --- | --- | --- | --- |
| `complaint_snapshot` | `complaint_key` | bigint | R | complaint_id resolved; FK complaint.complaint_key |
| `complaint_snapshot` | `business_date` | date | R | manifest business_date |
| `complaint_snapshot` | `branch_key` | bigint | R | branch_id resolved at date; FK branch.branch_key |
| `complaint_snapshot` | `priority` | text(50) | R | priority at cutoff |
| `complaint_snapshot` | `channel` | text(50) | R | channel at cutoff |
| `complaint_snapshot` | `status` | text(50) | R | status at cutoff |
| `complaint_snapshot` | `as_of_cutoff_at` | instant UTC(6) | R | source-supported knowledge cutoff for business_date; exact cutoff remains a source-contract detail |
| `complaint_snapshot` | `batch_revision` | integer >= 1 | R | source_extract.revision; exact delivered batch revision |
| `complaint_snapshot` | `source_version` | text(128) | R | source record/state version reference; if absent, source contract must define a reliable version identity |
| `complaint_snapshot` | `snapshot_version` | text(128) | R | proposed immutable version identifier linking preserved values to publication/correction history |
| `complaint_snapshot` | `reconstruction_reference` | text(100) | C: reliably reconstructed snapshot | required evidence/method/version for reconstructed state |
| `complaint_snapshot` | `created_at` | instant UTC(6) | R | Immutable original SRC-04 creation instant; original_created_at may only be a documented source alias |
| `complaint_snapshot` | `priority_at_creation` | text(50) | C: SLA evaluation | Immutable creation priority, source or reliable historical reconstruction; Critical/High/Medium/Low |
| `complaint_snapshot` | `closed_at` | instant UTC(6) | C: closed selected state | SRC-04 closure known in selected as-of/publication; null for open/REOPENED; contradictory status/closure quarantined |
| `complaint_snapshot` | `state_availability` | text(50) | R | supplied or reliably_reconstructed for accepted snapshot; unavailable expectations go in historical_coverage |
| `complaint_snapshot` | `supersedes_snapshot_version` | text(128) | O: not applicable or not supplied; supplied values must validate | FK complaint_snapshot.snapshot_version; existing predecessor; acyclic correction chain |
| `complaint_snapshot` | `correction_reference` | text(100) | C: corrected version | Correction approval/evidence reference; predecessor required for correction of existing version |

## SRC-04 / complaint_history_event

Logical target(s): `complaint_history_event`. Source business identity/grain: source-qualified complaint + history event version. Relevant trace: DD-03/06; K08-K10. Physical source key/header aliases: **Pending confirmation** where the G3 proposal has not been fixture-confirmed.

| Logical target | Field | Logical type/format | Logical requiredness | Approved meaning/derivation |
| --- | --- | --- | --- | --- |
| `complaint_history_event` | `history_event_key` | internal key | R | Generated PK |
| `complaint_history_event` | `complaint_key` | bigint | R | FK complaint.complaint_key |
| `complaint_history_event` | `event_type` | text(50) | R | Source-mapped closure or reopening event; source aliases pending |
| `complaint_history_event` | `event_at` | instant UTC(6) | R | SRC-04 event instant known for selected publication |
| `complaint_history_event` | `source_version` | text(128) | R | Source state/version identity |
| `complaint_history_event` | `publication_version` | text(128) | C: published history | FK publication.publication_version |

## SRC-04 / complaint_branch_assignment

Logical target(s): `complaint_branch_assignment`. Source business identity/grain: source_system + source_assignment_id; effective version. Relevant trace: DD-12; K08-K10. Physical source key/header aliases: **Pending confirmation** where the G3 proposal has not been fixture-confirmed.

| Logical target | Field | Logical type/format | Logical requiredness | Approved meaning/derivation |
| --- | --- | --- | --- | --- |
| `complaint_branch_assignment` | `assignment_version` | text(128) | R | Immutable version |
| `complaint_branch_assignment` | `source_system` | text(50) | R | SRC-04 source namespace |
| `complaint_branch_assignment` | `source_assignment_id` | text(128) | R | Required reviewed identity; actual alias pending |
| `complaint_branch_assignment` | `complaint_key` | bigint | R | FK complaint.complaint_key |
| `complaint_branch_assignment` | `branch_key` | bigint | R | FK branch.branch_key; effective referenced version |
| `complaint_branch_assignment` | `assignment_role` | text(50) | R | RESPONSIBLE |
| `complaint_branch_assignment` | `valid_from` | instant UTC(6) | R | Source-supported applicability start |
| `complaint_branch_assignment` | `valid_to` | instant UTC(6) | O: open-ended | Exclusive end; null open-ended |
| `complaint_branch_assignment` | `original_effective_end` | instant UTC(6) | C: ended interval | Original end retention anchor retained through corrections |
| `complaint_branch_assignment` | `source_version` | text(128) | R | Required reviewed source version identity |
| `complaint_branch_assignment` | `supersedes_version` | text(128) | C: correction | FK complaint_branch_assignment.assignment_version; predecessor on correction |
| `complaint_branch_assignment` | `correction_reason` | text(200) | C: correction | Sanitized reason |
| `complaint_branch_assignment` | `affected_from` | instant UTC(6) | C: correction | Correction affected interval start |
| `complaint_branch_assignment` | `affected_to` | instant UTC(6) | O: open-ended or not correction | Exclusive affected end |
| `complaint_branch_assignment` | `approval_action_id` | text(128) | R | FK governance_action.action_id; independent source/Data Owner evidence |

## SRC-05 / organizational_unit

Logical target(s): `organizational_unit`. Source business identity/grain: source_system + unit_type + source_id. Relevant trace: DD-12; FR-09/10. Physical source key/header aliases: **Pending confirmation** where the G3 proposal has not been fixture-confirmed.

| Logical target | Field | Logical type/format | Logical requiredness | Approved meaning/derivation |
| --- | --- | --- | --- | --- |
| `organizational_unit` | `organization_key` | text(128) | R | Generated stable identity |
| `organizational_unit` | `source_system` | text(50) | R | SRC-05 namespace |
| `organizational_unit` | `unit_type` | text(50) | R | REGION or BRANCH |
| `organizational_unit` | `source_id` | text(128) | R | region_id or branch_id; stable within corresponding namespace |

## SRC-05 / region

Logical target(s): `region`. Source business identity/grain: source_system + region_id + valid_from. Relevant trace: DD-12; FR-09/10. Physical source key/header aliases: **Pending confirmation** where the G3 proposal has not been fixture-confirmed.

| Logical target | Field | Logical type/format | Logical requiredness | Approved meaning/derivation |
| --- | --- | --- | --- | --- |
| `region` | `region_version` | text(128) | R | Immutable version |
| `region` | `organization_key` | text(128) | R | FK organizational_unit.organization_key; REGION |
| `region` | `source_system` | text(50) | R | SRC-05 namespace |
| `region` | `region_id` | text(128) | R | Stable source region ID |
| `region` | `region_name` | text(200) | R | Source display name |
| `region` | `valid_from` | instant UTC(6) | R | Source-supported applicability start |
| `region` | `valid_to` | instant UTC(6) | O: open-ended | Exclusive end; null open-ended |
| `region` | `original_effective_end` | instant UTC(6) | C: ended interval | Original end retention anchor retained through corrections |
| `region` | `source_version` | text(128) | R | Required reviewed source version identity |
| `region` | `supersedes_version` | text(128) | C: correction | FK region.region_version; predecessor on correction |
| `region` | `correction_reason` | text(200) | C: correction | Sanitized reason |
| `region` | `affected_from` | instant UTC(6) | C: correction | Correction affected interval start |
| `region` | `affected_to` | instant UTC(6) | O: open-ended or not correction | Exclusive affected end |
| `region` | `approval_action_id` | text(128) | R | FK governance_action.action_id; independent source/Data Owner evidence |

## SRC-05 / branches

Logical target(s): `branch`. Source business identity/grain: source_system + branch_id + valid_from. Relevant trace: DD-12; K01-K10. Physical source key/header aliases: **Pending confirmation** where the G3 proposal has not been fixture-confirmed.

| Logical target | Field | Logical type/format | Logical requiredness | Approved meaning/derivation |
| --- | --- | --- | --- | --- |
| `branch` | `branch_key` | bigint | R | generated |
| `branch` | `branch_id` | text(128) | R | branch_id |
| `branch` | `branch_name` | text(200) | R | branch_name |
| `branch` | `region_id` | text(128) | R | region_id |
| `branch` | `valid_from` | instant UTC(6) | R | valid_from |
| `branch` | `valid_to` | instant UTC(6) | O: open-ended interval | Exclusive interval end; null open-ended, never defaulted current date |
| `branch` | `source_system` | text(50) | R | Source namespace; natural source ID must be qualified by this value |
| `branch` | `region_version` | text(128) | R | FK region.region_version; applicable at branch interval; region_id remains source identity |
| `branch` | `organization_key` | text(128) | R | FK organizational_unit.organization_key; BRANCH stable identity |
| `branch` | `source_version` | text(128) | R | Reviewed source version |
| `branch` | `supersedes_branch_key` | bigint | C: correction | FK branch.branch_key; immutable correction predecessor |
| `branch` | `correction_action_id` | text(128) | C: correction | FK governance_action.action_id; reason, affected interval and independent review |
| `branch` | `affected_from` | instant UTC(6) | C: correction | Corrected interval start |
| `branch` | `affected_to` | instant UTC(6) | O: open-ended or not correction | Exclusive corrected interval end; null open-ended |
| `branch` | `correction_reason` | text(200) | C: correction | Sanitized correction reason |
| `branch` | `original_effective_end` | instant UTC(6) | C: ended interval | Original effective-end retention anchor; corrections do not restart clock |

## SRC-05 / organizational_successor

Logical target(s): `organizational_successor`. Source business identity/grain: predecessor + successor + valid_from. Relevant trace: DD-12; FR-09/10. Physical source key/header aliases: **Pending confirmation** where the G3 proposal has not been fixture-confirmed.

| Logical target | Field | Logical type/format | Logical requiredness | Approved meaning/derivation |
| --- | --- | --- | --- | --- |
| `organizational_successor` | `successor_version` | text(128) | R | Immutable version |
| `organizational_successor` | `predecessor_key` | text(128) | R | FK organizational_unit.organization_key |
| `organizational_successor` | `successor_key` | text(128) | R | FK organizational_unit.organization_key; distinct unit |
| `organizational_successor` | `source_system` | text(50) | R | SRC-05 relationship authority |
| `organizational_successor` | `valid_from` | instant UTC(6) | R | Source-supported applicability start |
| `organizational_successor` | `valid_to` | instant UTC(6) | O: open-ended | Exclusive end; null open-ended |
| `organizational_successor` | `original_effective_end` | instant UTC(6) | C: ended interval | Original end retention anchor retained through corrections |
| `organizational_successor` | `source_version` | text(128) | R | Required reviewed source version identity |
| `organizational_successor` | `supersedes_version` | text(128) | C: correction | FK organizational_successor.successor_version; predecessor on correction |
| `organizational_successor` | `correction_reason` | text(200) | C: correction | Sanitized reason |
| `organizational_successor` | `affected_from` | instant UTC(6) | C: correction | Correction affected interval start |
| `organizational_successor` | `affected_to` | instant UTC(6) | O: open-ended or not correction | Exclusive affected end |
| `organizational_successor` | `approval_action_id` | text(128) | R | FK governance_action.action_id; independent source/Data Owner evidence |
