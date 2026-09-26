# PD-04 conditional source-cell applicability — Annex Increment 2

Status: **Approved framework — Physical predicates pending confirmation** (Project Owner reviewed, 2026-09-22). The PD-04 [design rule](physical-design-decision-package.md) is **Approved — Design Rule**. Approval covers the source-cell states, disposition and applicability models, predicate governance, deterministic evaluation requirement, completeness-denominator and unresolved-applicability behavior, PD-01/02/03/04 selection relationship, fail-closed behavior and PD-05/06/07 dependency boundaries below. It does **not** approve any physical predicate, field binding or candidate row. All 27 [PD-01 received headers](pd01-physical-header-annex.md) remain Pending confirmation, so no physical source-cell predicate may be activated and required validation dependent on one fails closed. This annex does not change the approved Sprint 2/G3 logical dictionary.

## Authority and classification

| Evidence | Classification | Consequence |
| --- | --- | --- |
| DD-07 [field dictionary](../sprint-02-data-design/field-level-dictionary.md) R/O/C meanings, no missing-value defaults, conditional fields, typed temporal/monetary contracts | **Approved baseline** | Logical target conditions guide future mappings; they are not automatically received CSV columns |
| DD-01/G3 [synthetic source contract](../sprint-02-data-design/synthetic-source-contract.md) source/date/revision, empty cell for null, `posted_at` POSTED-only and history/correction rules | **Approved baseline** | Preserve conditional source evidence and source identity; do not invent source aliases |
| DD-09 [quality/completeness policy](../sprint-02-data-design/data-quality-and-reconciliation.md), NFR-02 and [Sprint 1 acceptance criteria](../sprint-01-business-analysis/product-backlog.md) | **Approved baseline** | Measure received and curated applicable required business cells, with separate validity and fail-closed missing controls |
| [PD-01](pd01-physical-header-annex.md) / [PD-02](pd02-schema-version-annex.md) / [PD-03](pd03-manifest-json-specification.md) contract selection sequence | **Approved physical structure/convention/manifest** | Select an approved received header and active schema before applying a predicate to payload cells |
| Predicate record shape, cell-state ledger and deterministic evaluation order below | **Derived physical implementation detail — framework approved** | Project Owner approved this structure; no runtime predicate is installed |
| Candidate physical field names/bindings and dispositions, predicate IDs, exact source-cell conditions, per-predicate denominator treatment and downstream mapping/time evidence | **Pending confirmation** | Reject dependent validation until reviewed contract rows supply them |
| Material contradiction with approved G3 rules found in this review | **Conflict: none identified** | Any later contradiction must enter change control, not be silently implemented |

The [source-field inventory](source-field-inventory.md), [contract reconciliation](contract-reconciliation.md), [source definitions](../sprint-02-data-design/source-system-definitions.md), [logical model](../sprint-02-data-design/logical-data-model.md), [source mapping navigation](../sprint-02-data-design/data-dictionary-and-mappings.md), [KPI mappings](../sprint-02-data-design/kpi-to-data-mappings.md), [risk catalog](../sprint-02-data-design/customer-risk-catalog.md), [DD-11 payment policy](../sprint-02-data-design/loan-payment-and-schedule-policy.md), [DD-12 temporal/branch policy](../sprint-02-data-design/historical-branch-attribution-policy.md), [security/classification design](../sprint-02-data-design/security-and-masking-design.md), and [G3 approval](../../04-monitoring-and-control/g3-data-design-approval.md) provide the relevant context. None supplies final physical headers or authorizes inferring a source predicate from a logical C marker alone.

## Physical applicability model — approved framework, no active rows

One future reviewed predicate record must carry all of the following. `source`, `section`, `schema_version` and `physical_field` together locate an **approved PD-01 received field**; generated/resolved/derived target fields may have lineage/target rules but are not source-cell predicates. A stable predicate ID is assigned only when the complete reviewed record is approved; this annex assigns **zero active predicate IDs**.

| Attribute | Deterministic contract requirement |
| --- | --- |
| Identity | Stable `predicate_id`, version/effective contract association, `(source, section, schema_version, physical_field)`, mapped logical target and approval evidence |
| Disposition | Exactly one of `received`, `generated`, `resolved`, `derived`; only `received` is a CSV cell. Others identify target-side provenance outside the received header |
| Applicability | Exactly one of `always`, `optional`, `conditional`, `inapplicable`; `inapplicable` is a result of an approved rule, never a default for missing evidence |
| Predicate | Approved evidence/input field(s), operator, typed expected value/set/range, explicit true and false results, and a defined unresolved result. No free-text runtime interpretation or analyst judgment |
| Cell contract | Required or permitted-null result when applicable; prohibited/inapplicable result when false; explicit absent, blank, recognized null and invalid-evidence behavior |
| Completeness | Whether the source business cell contributes to received/curated applicable-required denominators; numerator evidence and quality disposition are separate |
| Trace and governance | G3 source evidence, mapping/version dependency, source-owner/Data Owner simulated review evidence where required, approval state and replacement/supersession record |

For `always`, a reviewed received business field is applicable to every row in the section. For `optional`, presence is not a completeness requirement solely because the column exists; if supplied, format/domain checks still apply. For `conditional`, evaluate the reviewed predicate from **valid** evidence and apply its true/false contract. For `inapplicable`, the field is outside a particular row's business meaning only after a reviewed rule proves that result. A schema/header or predicate change affecting applicability requires a new PD-02 section schema ID; a mapping-only change remains separately governed by PD-06 and must not rewrite accepted historical interpretation.

No bank threshold is introduced. As a logical example only, G3 says `loan_payment.posted_at` is required for POSTED source payment versions, null for PENDING/FAILED/CANCELLED and >= `paid_at`; [DD-06/PD-06](../sprint-02-data-design/kpi-policy-dd06.md) mapping evidence is needed to know canonical status. Because the physical `payments` header and final mapping rows are unresolved, **no PD-04 physical `posted_at` predicate is created or executable**. The same caution applies to complaint closure, correction references, effective ends and derived/publication fields.

## Source-cell evidence states

| State | Meaning | Validation/completeness effect |
| --- | --- | --- |
| **Absent** | An approved physical column is absent from the header, or a row lacks its expected cell position | Header/row-framing error; never inferred null, blank or inapplicable; required validation fails |
| **Blank** | A cell is physically present as whitespace-only or a literal empty-text representation rather than an approved null representation | Missing business value for an applicable required field; not proof of inapplicability. Preserve lexical evidence where CSV quoting matters |
| **Null** | A physically present cell uses an explicitly approved null representation | G3 proposes an empty CSV cell for null. A different token (for example the letters `NULL`) is **not** approved by this annex. Null may be allowed only by the selected field contract; required applicable values remain missing |
| **Invalid** | Nonblank supplied value fails its approved type, domain, temporal, reference or cross-field rule | Keep raw evidence, issue a quality finding; do not coerce to a valid value or make dependent fields inapplicable |
| **Inapplicable** | Approved predicate, using valid evidence, determines the field does not apply to this record | Exclude only this legitimately inapplicable cell from its applicable-required denominator; record predicate/version evidence |
| **Applicability unresolved** | Predicate, contract or required input evidence is missing, invalid, unmapped or unapproved | Record controlled finding and unavailable denominator/gate as needed; never classify as inapplicable or silently subtract a cell |

CSV lexical details matter: G3 says an **empty cell** represents null and literal empty required text is invalid. A future parser must preserve enough raw framing to distinguish an explicitly allowed null representation from whitespace/quoted empty-text evidence if the approved physical contract makes that distinction. No new null token or trimming/coercion rule is approved here. `blank != inapplicable`; `invalid evidence != permission to classify a dependent field as inapplicable`.

## Completeness denominators and gate behavior

For each required source/entity and overall, DD-09 measures received and curated applicable **required business cells** separately. Generated technical IDs and runtime audit fields are excluded; quarantined and excluded records remain visible in received completeness. The unrounded ratio is `present applicable required cells / applicable required cells`; each nonempty population must meet >=98%, with other critical gates independent of this tolerance. A confirmed valid empty population is `Not applicable/Unavailable`, not 100%; a missing section is critical absence, never valid empty.

| Applicability/value outcome | Required-cell denominator | Present-cell numerator | Other result |
| --- | --- | --- | --- |
| Applicable, valid nonblank value | +1 | +1 | Continue remaining field/quality checks |
| Applicable, blank or permitted-encoding null | +1 | +0 | Missing required-cell finding; no default value |
| Applicable, invalid nonblank value | +1 | Presence counted per DD-09's nonblank rule; validity fails separately | Quarantine/escalate under the applicable quality rule; never a completeness-only pass |
| Validly inapplicable under approved predicate | +0 | +0 | Preserve predicate evidence; not a missing value |
| Optional field with no approved conditional requirement | +0 for required-cell gate | +0 | Supplied value still validated; optionality is not blanket acceptance |
| Applicability unresolved | **Do not fabricate a numeric denominator or remove the cell as inapplicable** | **Unavailable**, not an invented zero/pass | Controlled DQ finding; block the dependent gate whenever required contract/evidence is unavailable |

For measured populations retain field-level supporting counts and source/section/date/revision, stage, predicate/schema/mapping versions, row locator and quality disposition. Overall completeness aggregates comparable applicable cell counts, not an unweighted average. A nonblank invalid value may count as physically present yet fail DQ-D03/D06/D07 or another validity gate. No 2% margin permits broken keys, financial imbalance, misleading KPI/risk output or missing required configuration. When condition evidence is invalid/missing, neither the numerator nor denominator may be silently adjusted into a passing ratio; record `Unavailable` where the required count cannot be established and fail the applicable gate.

## Selection sequence and later dependencies

1. PD-03 verifies the manifest, exact bytes, source/section/date/revision and section schema reference.
2. PD-02 resolves that reference to one **active approved** physical schema. Unknown/inactive schema fails closed.
3. PD-01 checks the exact approved received header and row framing. All 27 headers are currently pending, so payload acceptance stops here.
4. Only then may PD-04 select an approved predicate version for that source/section/schema/field. Unknown/unapproved predicate or unresolved evidence fails dependent validation; it never becomes inapplicable.
5. PD-05 financial-control populations may depend on these applicability results, but its matrix/worked examples remain a separate pending annex. PD-06 mapping rows/version IDs may supply canonical predicate evidence, but remain pending. PD-07 Chicago-time normalization/version verification may supply temporal predicate evidence, but remains pending. None is implemented or approved by PD-04.

## Coverage of candidate logical conditional fields

The table below covers all **51** `C:` logical target-field rows mapped to the 27 mandatory sections in the [source-field inventory](source-field-inventory.md). A logical C condition is **approved target meaning**, not evidence that its field is received. Every physical column, received/generated/resolved/derived disposition, active predicate ID, input binding, typed operator/result, exact source-cell requirement and denominator effect is **Pending confirmation** until the PD-01 header and necessary PD-06/PD-07 evidence are approved. No row below is an active predicate. `PD-01` blocks every row; family-specific dependencies are additional. Approval state for every row is **Pending confirmation**.

| Source / section | Logical target field | Approved logical condition | Physical field/disposition | Predicate/evidence status | Additional blocking dependency | Approval |
| --- | --- | --- | --- | --- | --- | --- |
| SRC-01 / customers | `customer_identity`.`approval_reference` | C: approved identity mapping | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | source/governance evidence | Pending confirmation |
| SRC-01 / accounts | `account`.`closed_date` | C: closed account | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | source/target provenance review | Pending confirmation |
| SRC-01 / transactions | `transaction`.`absolute_comparison_amount` | C: eligible RC-01 comparison | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | derived/selected target; not assumed received | Pending confirmation |
| SRC-01 / account_restriction_state | `account_restriction_state`.`publication_version` | C: published state | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | derived/selected target; not assumed received | Pending confirmation |
| SRC-01 / account_restriction_state | `account_restriction_state`.`risk_restriction_status` | C: valid approved mapping | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | PD-06 mapping/status | Pending confirmation |
| SRC-01 / account_branch_assignment | `account_branch_assignment`.`original_effective_end` | C: ended interval | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | PD-07 time/history | Pending confirmation |
| SRC-01 / account_branch_assignment | `account_branch_assignment`.`supersedes_version` | C: correction | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | source/governance evidence | Pending confirmation |
| SRC-01 / account_branch_assignment | `account_branch_assignment`.`correction_reason` | C: correction | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | source/governance evidence | Pending confirmation |
| SRC-01 / account_branch_assignment | `account_branch_assignment`.`affected_from` | C: correction | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | PD-07 time/history | Pending confirmation |
| SRC-02 / positions | `loan_snapshot`.`reconstruction_reference` | C: reliably reconstructed snapshot | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | PD-07 time/history | Pending confirmation |
| SRC-02 / positions | `loan_snapshot`.`correction_reference` | C: corrected version | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | source/governance evidence | Pending confirmation |
| SRC-02 / payments | `loan_payment`.`correction_reference` | C: corrected event version | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | source/governance evidence | Pending confirmation |
| SRC-02 / payments | `loan_payment`.`posted_at` | C: POSTED | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | PD-06 mapping/status; PD-07 time/history | Pending confirmation |
| SRC-02 / loan_schedule | `loan_schedule`.`correction_reference` | C: corrected version | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | source/governance evidence | Pending confirmation |
| SRC-02 / loan_obligation | `loan_obligation`.`correction_reference` | C: corrected version | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | source/governance evidence | Pending confirmation |
| SRC-02 / payment_allocation | `payment_allocation`.`correction_reference` | C: corrected version | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | source/governance evidence | Pending confirmation |
| SRC-02 / payment_unapplied | `payment_unapplied`.`correction_reference` | C: corrected version | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | source/governance evidence | Pending confirmation |
| SRC-02 / payment_adjustment | `payment_adjustment`.`correction_reference` | C: corrected version | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | source/governance evidence | Pending confirmation |
| SRC-02 / loan_account | `loan_account`.`correction_reference` | C: corrected version | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | source/governance evidence | Pending confirmation |
| SRC-02 / loan_branch_assignment | `loan_branch_assignment`.`original_effective_end` | C: ended interval | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | PD-07 time/history | Pending confirmation |
| SRC-02 / loan_branch_assignment | `loan_branch_assignment`.`supersedes_version` | C: correction | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | source/governance evidence | Pending confirmation |
| SRC-02 / loan_branch_assignment | `loan_branch_assignment`.`correction_reason` | C: correction | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | source/governance evidence | Pending confirmation |
| SRC-02 / loan_branch_assignment | `loan_branch_assignment`.`affected_from` | C: correction | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | PD-07 time/history | Pending confirmation |
| SRC-03 / fraud_alert_state | `fraud_alert_state`.`publication_version` | C: published state | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | derived/selected target; not assumed received | Pending confirmation |
| SRC-03 / fraud_alert_state | `fraud_alert_state`.`case_status` | C: valid approved mapping | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | PD-06 mapping/status | Pending confirmation |
| SRC-03 / fraud_alert_state | `fraud_alert_state`.`severity` | C: valid approved mapping | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | PD-06 mapping/status | Pending confirmation |
| SRC-04 / complaints | `complaint`.`priority_at_creation` | C: SLA evaluation | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | source/target provenance review | Pending confirmation |
| SRC-04 / complaints | `complaint`.`closed_at` | C: closed selected state | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | PD-06 mapping/status; PD-07 time/history | Pending confirmation |
| SRC-04 / complaints | `complaint`.`final_closed_at` | C: finally closed in selected publication | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | PD-06 mapping/status; PD-07 time/history; derived/selected target; not assumed received | Pending confirmation |
| SRC-04 / complaint_snapshot | `complaint_snapshot`.`reconstruction_reference` | C: reliably reconstructed snapshot | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | PD-07 time/history | Pending confirmation |
| SRC-04 / complaint_snapshot | `complaint_snapshot`.`priority_at_creation` | C: SLA evaluation | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | source/target provenance review | Pending confirmation |
| SRC-04 / complaint_snapshot | `complaint_snapshot`.`closed_at` | C: closed selected state | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | PD-06 mapping/status; PD-07 time/history | Pending confirmation |
| SRC-04 / complaint_snapshot | `complaint_snapshot`.`correction_reference` | C: corrected version | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | source/governance evidence | Pending confirmation |
| SRC-04 / complaint_history_event | `complaint_history_event`.`publication_version` | C: published history | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | derived/selected target; not assumed received | Pending confirmation |
| SRC-04 / complaint_branch_assignment | `complaint_branch_assignment`.`original_effective_end` | C: ended interval | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | PD-07 time/history | Pending confirmation |
| SRC-04 / complaint_branch_assignment | `complaint_branch_assignment`.`supersedes_version` | C: correction | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | source/governance evidence | Pending confirmation |
| SRC-04 / complaint_branch_assignment | `complaint_branch_assignment`.`correction_reason` | C: correction | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | source/governance evidence | Pending confirmation |
| SRC-04 / complaint_branch_assignment | `complaint_branch_assignment`.`affected_from` | C: correction | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | PD-07 time/history | Pending confirmation |
| SRC-05 / region | `region`.`original_effective_end` | C: ended interval | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | PD-07 time/history | Pending confirmation |
| SRC-05 / region | `region`.`supersedes_version` | C: correction | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | source/governance evidence | Pending confirmation |
| SRC-05 / region | `region`.`correction_reason` | C: correction | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | source/governance evidence | Pending confirmation |
| SRC-05 / region | `region`.`affected_from` | C: correction | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | PD-07 time/history | Pending confirmation |
| SRC-05 / branches | `branch`.`supersedes_branch_key` | C: correction | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | source/governance evidence | Pending confirmation |
| SRC-05 / branches | `branch`.`correction_action_id` | C: correction | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | source/governance evidence | Pending confirmation |
| SRC-05 / branches | `branch`.`affected_from` | C: correction | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | PD-07 time/history | Pending confirmation |
| SRC-05 / branches | `branch`.`correction_reason` | C: correction | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | source/governance evidence | Pending confirmation |
| SRC-05 / branches | `branch`.`original_effective_end` | C: ended interval | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | PD-07 time/history | Pending confirmation |
| SRC-05 / organizational_successor | `organizational_successor`.`original_effective_end` | C: ended interval | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | PD-07 time/history | Pending confirmation |
| SRC-05 / organizational_successor | `organizational_successor`.`supersedes_version` | C: correction | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | source/governance evidence | Pending confirmation |
| SRC-05 / organizational_successor | `organizational_successor`.`correction_reason` | C: correction | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | source/governance evidence | Pending confirmation |
| SRC-05 / organizational_successor | `organizational_successor`.`affected_from` | C: correction | Pending confirmation | Approved logical C; physical evidence/predicate ID pending | PD-07 time/history | Pending confirmation |

Other logical `O:` fields (such as `customer.contact`, `transaction.source_initiating_customer_id`, open-ended `valid_to`, and supplied correction predecessors) remain optional/conditional according to their individual dictionary wording. They are **not** upgraded to required physical source cells here; a future reviewed PD-01/PD-04 map must address any source-cell condition that actually applies. There is no conflict identified with G3 at this documentation stage. Sprint 3 remains in progress and not approved; PD02/PostgreSQL work remains unauthorized.
