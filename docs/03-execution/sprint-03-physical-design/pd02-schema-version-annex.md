# PD-02 physical schema-version annex — Increment 1

Status: **Approved convention — Activation pending approved physical header contract** (Project Owner review 2026-09-22). The immutable per-section schema-ID model and deterministic naming convention are approved. The 27 literal `v001` strings below are initial **candidate identifiers** for first physical contracts, not active runtime contracts while their [PD-01 headers](pd01-physical-header-annex.md) remain unresolved. These are not batch revisions, raw-to-canonical mapping versions, source-state versions or the separate PD02 database work package.

## Deterministic naming and transition rule

Format: `HCB.SYN.<SRC-ID>.<section>.vNNN`, where `<SRC-ID>` is exactly `SRC-01`…`SRC-05`, `<section>` is the exact mandatory section alias, and `NNN` is a three-digit positive per-section ordinal. The first proposed ID is `v001`; no historical predecessor is fabricated. The full string is within the DD-07 `text(128)` bound. IDs are immutable and never recycled. A change in **ordered header bytes, physical-to-logical meaning, source-cell type/format, or applicability/requiredness** requires a new per-section ID. Data correction uses a new batch revision, not a schema ID. Raw mapping changes use a separate PD-06 mapping version. Source-state corrections retain their own version lineage. An older approved ID remains available for accepted historical/replay evidence until applicable lifecycle disposal.

Compatibility is **not assumed**: a new ID needs explicit predecessor, change reason, compatibility assessment, effective date, validation and approval evidence. An unknown or unapproved ID fails closed. An initial `v001` has `predecessor = none (first proposal)`; it is not an invented history. No `v001` may be activated before its exact PD-01 header and any needed PD-04/PD-06 evidence are approved.

## Reserved section IDs

Every row has reason `initial candidate physical section contract`, effective design state `Convention approved; inactive`, compatibility status `not evaluated / not active`, predecessor `none`, and approval state `Activation pending approved physical header contract`. The associated header contract is the exact section row in [PD-01](pd01-physical-header-annex.md), whose received header remains pending. The shorter approval cells in the table describe the candidate IDs' **activation**, not the now-approved convention.

| Source | Section | Proposed literal immutable schema ID | Associated PD-01 header | Effective design state | Compatibility | Predecessor | Approval |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SRC-01 | `customers` | `HCB.SYN.SRC-01.customers.v001` | Pending confirmation | Convention approved; inactive | Not evaluated | None | Activation pending approved header |
| SRC-01 | `accounts` | `HCB.SYN.SRC-01.accounts.v001` | Pending confirmation | Convention approved; inactive | Not evaluated | None | Activation pending approved header |
| SRC-01 | `holders` | `HCB.SYN.SRC-01.holders.v001` | Pending confirmation | Convention approved; inactive | Not evaluated | None | Activation pending approved header |
| SRC-01 | `transactions` | `HCB.SYN.SRC-01.transactions.v001` | Pending confirmation | Convention approved; inactive | Not evaluated | None | Activation pending approved header |
| SRC-01 | `account_restriction_state` | `HCB.SYN.SRC-01.account_restriction_state.v001` | Pending confirmation | Convention approved; inactive | Not evaluated | None | Activation pending approved header |
| SRC-01 | `account_branch_assignment` | `HCB.SYN.SRC-01.account_branch_assignment.v001` | Pending confirmation | Convention approved; inactive | Not evaluated | None | Activation pending approved header |
| SRC-02 | `loans` | `HCB.SYN.SRC-02.loans.v001` | Pending confirmation | Convention approved; inactive | Not evaluated | None | Activation pending approved header |
| SRC-02 | `borrowers` | `HCB.SYN.SRC-02.borrowers.v001` | Pending confirmation | Convention approved; inactive | Not evaluated | None | Activation pending approved header |
| SRC-02 | `positions` | `HCB.SYN.SRC-02.positions.v001` | Pending confirmation | Convention approved; inactive | Not evaluated | None | Activation pending approved header |
| SRC-02 | `payments` | `HCB.SYN.SRC-02.payments.v001` | Pending confirmation | Convention approved; inactive | Not evaluated | None | Activation pending approved header |
| SRC-02 | `loan_schedule` | `HCB.SYN.SRC-02.loan_schedule.v001` | Pending confirmation | Convention approved; inactive | Not evaluated | None | Activation pending approved header |
| SRC-02 | `loan_obligation` | `HCB.SYN.SRC-02.loan_obligation.v001` | Pending confirmation | Convention approved; inactive | Not evaluated | None | Activation pending approved header |
| SRC-02 | `payment_allocation` | `HCB.SYN.SRC-02.payment_allocation.v001` | Pending confirmation | Convention approved; inactive | Not evaluated | None | Activation pending approved header |
| SRC-02 | `payment_unapplied` | `HCB.SYN.SRC-02.payment_unapplied.v001` | Pending confirmation | Convention approved; inactive | Not evaluated | None | Activation pending approved header |
| SRC-02 | `payment_adjustment` | `HCB.SYN.SRC-02.payment_adjustment.v001` | Pending confirmation | Convention approved; inactive | Not evaluated | None | Activation pending approved header |
| SRC-02 | `loan_account` | `HCB.SYN.SRC-02.loan_account.v001` | Pending confirmation | Convention approved; inactive | Not evaluated | None | Activation pending approved header |
| SRC-02 | `loan_branch_assignment` | `HCB.SYN.SRC-02.loan_branch_assignment.v001` | Pending confirmation | Convention approved; inactive | Not evaluated | None | Activation pending approved header |
| SRC-03 | `alerts` | `HCB.SYN.SRC-03.alerts.v001` | Pending confirmation | Convention approved; inactive | Not evaluated | None | Activation pending approved header |
| SRC-03 | `fraud_alert_state` | `HCB.SYN.SRC-03.fraud_alert_state.v001` | Pending confirmation | Convention approved; inactive | Not evaluated | None | Activation pending approved header |
| SRC-04 | `complaints` | `HCB.SYN.SRC-04.complaints.v001` | Pending confirmation | Convention approved; inactive | Not evaluated | None | Activation pending approved header |
| SRC-04 | `complaint_snapshot` | `HCB.SYN.SRC-04.complaint_snapshot.v001` | Pending confirmation | Convention approved; inactive | Not evaluated | None | Activation pending approved header |
| SRC-04 | `complaint_history_event` | `HCB.SYN.SRC-04.complaint_history_event.v001` | Pending confirmation | Convention approved; inactive | Not evaluated | None | Activation pending approved header |
| SRC-04 | `complaint_branch_assignment` | `HCB.SYN.SRC-04.complaint_branch_assignment.v001` | Pending confirmation | Convention approved; inactive | Not evaluated | None | Activation pending approved header |
| SRC-05 | `organizational_unit` | `HCB.SYN.SRC-05.organizational_unit.v001` | Pending confirmation | Convention approved; inactive | Not evaluated | None | Activation pending approved header |
| SRC-05 | `region` | `HCB.SYN.SRC-05.region.v001` | Pending confirmation | Convention approved; inactive | Not evaluated | None | Activation pending approved header |
| SRC-05 | `branches` | `HCB.SYN.SRC-05.branches.v001` | Pending confirmation | Convention approved; inactive | Not evaluated | None | Activation pending approved header |
| SRC-05 | `organizational_successor` | `HCB.SYN.SRC-05.organizational_successor.v001` | Pending confirmation | Convention approved; inactive | Not evaluated | None | Activation pending approved header |

## Separation and fail-closed binding

For a manifest entry, lookup key is `(source_system, entity_name, schema_version)` and must select exactly one approved header contract. `revision` is the positive integer delivered batch revision for `(source, entity, business_date)`; it never forms part of the schema ID. `mapping_version` identifies separately approved raw-to-canonical rules; `source_version` identifies supplied state/correction evidence. A manifest citing an **inactive** `v001` fails closed. The manifest JSON example can show the candidate literal ID but is not an accepted delivery. Future transition/compatibility records remain Pending confirmation; no historical predecessor is fabricated.
