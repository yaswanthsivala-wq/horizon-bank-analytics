# DD-11 approved loan-payment and schedule policy

Approved by the requesting user on 2026-09-16. Evidence: the explicit "Approve DD-11" instruction and its 20 controlling decisions, following the read-only design review. No additional unsupplied policy, source schema or source availability is assumed. Logical documentation only; G3 and implementation remain **Draft — not approved**.

## Compatibility and authority

No conflict found with Planning, Sprint 1 or DD-01 through DD-10; reported before edits. Planning includes scheduled and actual payments; US-04 requires masked account, DPD, principal and payment history. DD-11 supplies logical contracts for those needs. DD-02 non-additive ownership exposure is preserved: payment-to-obligation allocation is not allocation of shared ownership balances. DD-03 daily positions, DD-06 K05/K06, DD-04 RC-03 and DPD > 30 remain unchanged. DD-07 immutable versions, DD-08 scoped access, DD-09 exact controls and DD-10 original-anchor lifecycle remain in force.

Loan Operations Manager is the applicable Loan Servicing source/loan KPI owner; source and KPI mappings require the Data Owner review evidence specified by DD-08. Source-data corrections and independent release validation follow DD-09. Names, actual contracts, samples, approvals and verified coverage remain Pending confirmation. This is not approval of a source delivery, actual exclusion, release or implementation.

## Approved entities and version selection

The [authoritative inventory](field-level-dictionary.md) is the sole field contract. Add immutable versioned loan_schedule and loan_obligation. A schedule has source-qualified identity and effective interval; obligations identify contractual installments in that schedule. Contractual due_date belongs to loan_obligation, not the canonical loan_payment. Remove loan_payment.due_date; raw source due-date aliases remain lineage and cannot masquerade as an obligation without verified linkage.

loan_payment remains one immutable actual-payment event version, linked to one loan. Add source-supplied payment_allocation versions relating payments and obligations by PRINCIPAL, INTEREST or FEE component; one payment can cover many obligations and one obligation can receive many payments. Multiple source allocations are retained distinctly; never allocate by an invented waterfall. payment_unapplied records the separate source-supported unapplied amount and effective version. A source-confirmed zero is valid unapplied evidence; absence is not zero.

payment_adjustment is a separate immutable REVERSAL or REFUND event referencing the original POSTED payment. Partial and multiple adjustments are supported; cumulative adjustments cannot exceed that original payment. Original events are never deleted or overwritten. Data correction uses supersedes_event_key/version predecessors, independently of the business original-payment reference. A correction is not a refund/reversal and does not itself add a second financial event.

loan_account replaces loan.account_key as the authoritative relationship. It is effective-dated with relationship_role REPORTING for masked drill-through. Require exactly one effective REPORTING account for each loan/as-of date; never infer from shared customers, branches, amounts or account suffix. Missing/ambiguous linkage yields Unavailable drill-through and the DD-09 critical control. Masking uses account.masked_account; no full-number reporting access.

payment_transaction_link is optional and may exist only for source-supplied or independently reviewed references. A link is not inferred from matching amounts/dates/accounts and does not duplicate monetary facts. Multiple explicit references, if supplied, require reviewed cardinality/scope; no one-to-one banking assumption is invented. Loan/account role aliases other than REPORTING remain Pending confirmation.

Versioned source identities and applied mappings remain source-qualified. Identical revision replay creates no new facts; conflicting duplicate/revision blocks under DD-09. Corrected versions preserve predecessors, reason/evidence and original retention anchors. loan_contract_publication selects immutable schedule, obligation, allocation, unapplied, adjustment, account-link and transaction-link versions consistently with loan_payment_publication and loan_snapshot_publication. Exactly one selected version per natural identity in a publication; effective intervals determine as-of applicability. No mixed-version join or payment/obligation fanout may multiply totals.

## Currency, signs and financial effectiveness

Add loan.contractual_currency. Every obligation, payment, allocation, unapplied amount and adjustment must use that loan currency; compare loan positions consistently in their disclosed currency and flag inconsistent source evidence for review. Release 1 has no currency conversion. Contractual currency is source-supported; source corrections preserve original/corrected evidence and never silently change historical currency.

Accepted canonical payment amounts must be positive. Zero or negative payments are invalid and quarantined while raw signed values and lineage are preserved. Canonical statuses are PENDING, POSTED, FAILED and CANCELLED; only POSTED is financially effective. Preserve raw status and versioned source mapping. Status transitions are source-supported new versions, not silent updates. Do not reuse Core transaction status groups as payment mappings.

Obligation/component sign domains and source adjustment-sign representation must be explicitly validated with the source contract; no negative-source value is silently converted by abs(). Adjustment amount is the positive magnitude of the separate reversal/refund for cumulative-cap validation; the signed source value remains Restricted raw/control evidence. Any source-to-canonical representation must have approved mapping/evidence. Fees/interest/principal are supported as source-supplied allocation components, not as authorization to compute interest, originate charges or prescribe a servicing waterfall.

## Exact reconciliation

For each selected POSTED payment in loan contractual currency:

posted payment amount = sum(active source-supplied allocations) + unapplied amount.

Select only the effective allocation/unapplied versions for the same payment/as-of/publication; count every allocation once at its source allocation/component grain. Non-POSTED payment versions cannot enter financially effective totals. Any active financial allocation claiming a non-POSTED selected payment is invalid evidence; do not silently mark it effective.

For each original POSTED payment:

sum(selected business REVERSAL and REFUND adjustment amounts) <= original posted payment amount.

Deduplicate immutable adjustment natural events and exclude superseded correction versions from that sum. The original POSTED reference remains preserved even if a later data correction is delivered; changes affecting the cap require reviewed consistent selection and reconciliation before publication. Do not replace the approved posted-payment equation with a net equation or reduce original payment.amount to hide adjustments.

The source must supply/review the relationship between business adjustments, allocation changes and unapplied changes, including their effective timing and gross/net presentation. This prerequisite does not authorize an invented adjustment waterfall or an unsupported release. Preserve the two approved equations above and separate original-payment versus adjustment controls; block publication if source evidence cannot reconcile them or a result would be misleading.

Apply DD-09 exact counts and signed source-to-target controls separately by source, entity, business date, revision, monetary field, currency and comparable status population for schedules/obligations, payments, allocations, unapplied amounts and adjustments. No cross-currency netting or nonzero tolerance. Invalid signed payload remains visible in quarantine controls. Required missing/unparseable controls are CRITICAL. Schedule totals, when supplied as required source controls, reconcile to their explicit obligation/component populations; no invented schedule sum or allocation priority.

## Loan-position authority and reporting

Daily loan_snapshot remains authoritative for days_past_due, outstanding_principal and loan status. Payment history cannot independently reconstruct delinquency or replace daily position inputs. Preserve K05 active-loan denominator and DPD > 30 numerator, K06 principal sum for DPD > 30 without active-only/positive-only filters, and RC-03 at least one related active loan with DPD > 30. Negative/missing DPD > 30 principal retains the DD-09 publication block. Payment allocation/component values do not recalculate these KPIs.

US-04 payment history can show posted/nonposted event status, source-supplied schedule/obligation context, allocation components, separate unapplied amounts and separate reversal/refund history under DD-08 Loan Operations scope. Source detail availability is not asserted. Exactly one effective REPORTING account is selected at the relevant as-of date and final-four masked; account history is not deduced from customer relationships. DD-12 branch attribution remains pending and is not resolved by loan_account.

## DD-10 lifecycle

Apply approved 24-month analytical schedules to original obligation/effective dates and payment/adjustment event dates, with current/dependency exceptions where applicable. Schedule/obligation correction, rescheduling, reversal, refund, reingestion and republication do not restart the original analytical clock. Preserve an original_obligation_date separately from a revised contractual due_date; source rescheduling must retain predecessor lineage rather than disguise an old obligation as an unrelated new one. Each adjustment is its own event with its own original event anchor; it does not restart the referenced payment's clock.

Allocation/unapplied/account-link versions retain original effective-date lineage; publication memberships inherit target anchors, not publication time. Necessary retained-child dependencies use DD-10 current/dependency handling and minimized envelopes after permitted payload expiry, never silent dangling FKs or indefinite raw retention. Seven-year audit preserves corrections, mappings, controls and approvals without raw identity payload. DD-12 branch-history application remains conditional on its final semantics.

## Mandatory source prerequisites and remaining limits

Loan Servicing must provide verified logical coverage for contractual currency, schedule/obligation identities and versions, obligation due dates, actual positive payments/status mappings, allocations/component IDs and effective states, unapplied evidence, adjustments/original-payment references and effective REPORTING account linkage. Actual aliases, extraction sections, new-entity delivery modes, cutoffs/version conventions, adjustment-allocation timing and supplied monetary domains require source owner plus Data Owner review. Optional transaction links require source evidence or recorded independent review. No source availability is inferred from the logical inventory.

Missing verified coverage remains a prerequisite before implementation/publication. DD-11 policy is approved; these source-contract facts and physical choices are not invented approvals. DD-12 remains pending. Future verification covers positive/zero/negative payments, all four statuses, many-to-many allocations, exact posted equation, unapplied zero versus missing, partial/multiple adjustments and cap, correction versus adjustment separation, REPORTING interval gaps/overlaps, no inferred links, currency mismatch, duplicate replay, position-authoritative DPD and original-anchor retention. Tests and acceptance remain unexecuted.
