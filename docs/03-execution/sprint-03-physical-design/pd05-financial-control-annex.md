# PD-05 financial-control annex — Increment 3

Status: **Approved framework — Physical financial controls pending confirmation** (Project Owner reviewed 2026-09-22). PD-05 is **Approved — Design Rule** in the [decision package](physical-design-decision-package.md). Approval covers the exact-decimal, currency-separated, disjoint-population and residual framework, unavailable/not-applicable distinction, fail-closed dependencies, `decimal(28,4)` control arithmetic and synthetic worked-example structure. It does not approve or activate any of the seven candidate physical control rows, section-specific population, source field, reference, sign convention or tolerance. No complete physical control row is active.

## Authority and classification

| Classification | Evidence and consequence |
| --- | --- |
| Approved baseline | [DD-09 RC-D01/D02](../sprint-02-data-design/data-quality-and-reconciliation.md) requires exact, disjoint row and currency-separated signed financial reconciliation; received equals accepted plus quarantined plus approved excluded, with no unexplained residual or fabricated zero. [DD-07 `source_financial_control`](../sprint-02-data-design/field-level-dictionary.md) keys a control by source, entity, business date, revision, amount field, currency and population, using `decimal(28,4)` control totals or an unavailable reason. [G3 synthetic contract](../sprint-02-data-design/synthetic-source-contract.md) specifies signed scale-4 strings per field/currency/comparable status. [DD-11](../sprint-02-data-design/loan-payment-and-schedule-policy.md) separates payment, allocation, unapplied and adjustment grains. |
| Derived physical implementation detail | The candidate ledger and equations below translate the approved logical controls into a reviewable physical representation. Use exact decimal arithmetic; binary floating point is forbidden. The [PD-03 manifest](pd03-manifest-json-specification.md) has `financial_control_references` but does not define the referenced object schema. |
| Pending confirmation | Exact manifest reference object, physical monetary fields, source totals, status/currency populations, sign handling per section, control applicability, approved exclusion evidence, and any section-specific tolerance or unavailable reason vocabulary. A logical decimal target in the [inventory](source-field-inventory.md) does not prove a received control. |
| Conflict | None identified. Any disagreement with DD-09, DD-11 or G3 must enter change control. |

## Candidate control record and population equation

Each future approved record must identify control ID/version, source, section, active PD-02 schema, date/revision, physical amount and currency fields, comparable status set and PD-06 mapping version, PD-04 applicability version, source control field/reference, signed `decimal(28,4)` total, explicit control state (`available`, `unavailable`, `not applicable`), controlled unavailable reason, sign/precision rule, reconciliation equation, tolerance, evidence and approval state. An unavailable control is **not** numeric zero; `not applicable` requires approved population evidence. A structurally present PD-03 reference is not proof that its control is available.

For one approved source/section/date/revision/amount field/currency/status population, partition all received rows exactly once into accepted, quarantined and approved-excluded sets. Candidate equation, only after the full population and source total are approved:

`source_control_total = accepted_total + quarantined_total + approved_excluded_total`

`residual = source_control_total - (accepted_total + quarantined_total + approved_excluded_total)`

All terms are signed exact decimals at scale 4 and same currency/meaning; do not sum unlike stock and flow grains, gross payments with adjustments, or currencies. Exact zero residual is required where DD-09 exact reconciliation applies; no arbitrary financial tolerance is added. If the source total, comparable status rule, sign rule or any component is missing/invalid, the result is **unavailable**, with controlled reason and failed required gate, not zero or pass. Counts reconcile separately even for nonmonetary sections. PD-04 unresolved applicability cannot silently remove rows. Preserve received and excluded evidence rather than reconciling accepted rows alone.

## Candidate physical-control population matrix

All seven rows are **Pending confirmation**, not activated controls. `PENDING` means the exact physical field/control/reference, status population, sign convention and PD-03 object are not established. `decimal(28,4)` is the approved control total type; received source money is `decimal(20,4)` where DD-07 specifies it. Every row depends on an approved PD-01 header, active PD-02 schema and PD-03 control reference; status-dependent rows also need PD-06, and time/applicability-dependent rows need PD-07/PD-04. No numerical tolerance is inferred.

The matrix's candidate ID is a review locator, **not** an active control ID. For **each** row, the PD-02 schema version, exact physical monetary and currency fields, PD-03 source-total field/reference, `decimal(28,4)` signed control representation, source sign convention, PD-04 applicability binding, PD-06 mapping-version binding where statuses apply, PD-07 cutoff/date binding, unavailable-reason code and approval evidence are **Pending confirmation**. Its candidate equation is the disjoint same-currency signed relationship above, conditional on a reviewed comparable population; exact residual `0.0000` is required when that approved comparison is available. A different tolerance is not authorized. An unavailable required control fails closed rather than becoming zero. These per-row pending dependencies are not abbreviated into approval by the table's logical evidence.

| Candidate ID | Source / section | Logical monetary evidence | Candidate population and equation | Blocking physical evidence | State |
| --- | --- | --- | --- | --- | --- |
| FC-C01 | SRC-01 / `transactions` | `transaction.amount`; signed debit/credit; RC-01 uses absolute comparison separately | Same currency, approved comparable status and transaction flow; source total = disjoint disposition totals | Physical amount/currency/control field, debit/credit sign, status mapping, source total, schema | Pending confirmation |
| FC-C02 | SRC-02 / `positions` | `loan_snapshot.outstanding_principal` | Selected as-of stock per loan/date/currency; never sum daily snapshots as flow | Selected version/cutoff, physical amount/currency/control field, source total, schema | Pending confirmation |
| FC-C03 | SRC-02 / `payments` | `loan_payment.amount`; only POSTED financially effective under DD-11 | Gross payment flow by contractual currency and mapped status | Physical gross amount/control, status mapping, sign and posted evidence, source total, schema | Pending confirmation |
| FC-C04 | SRC-02 / `loan_obligation` | `loan_obligation.scheduled_amount` | Due obligation grain by contractual currency and approved date/status | Physical amount/control, due-date population, sign, source total, schema | Pending confirmation |
| FC-C05 | SRC-02 / `payment_allocation` | `payment_allocation.amount` | Component allocation by contractual currency; preserve PRINCIPAL/INTEREST/FEE | Physical amount/control, component population, sign, source total, schema | Pending confirmation |
| FC-C06 | SRC-02 / `payment_unapplied` | `payment_unapplied.amount` | Unapplied payment remainder by contractual currency, separate from allocation | Physical amount/control, sign/state population, source total, schema | Pending confirmation |
| FC-C07 | SRC-02 / `payment_adjustment` | `payment_adjustment.amount` | REVERSAL/REFUND adjustment grain, separate signed control from gross payment | Physical amount/control, kind/status mapping, sign, source total, schema | Pending confirmation |

The other 20 mandatory sections retain exact row-count controls; the inventory does not establish a monetary target/control for them. That is **not** approval to mark a financial control `not applicable`: a reviewed source/section population decision is still needed. USD/EUR synthetic examples in G3 do not authorize aggregating currencies; no FX conversion is proposed. PD-06 status mapping and PD-07 business-date/cutoff evidence must be bound to every affected control version.

## Structural arithmetic example — synthetic, not an approved source control

For one fictional `SRC-01/transactions`, `USD`, business date `2026-01-15`, assume a reviewed signed source total `125.0000`, accepted `100.0000`, quarantined `20.0000` and approved-excluded `5.0000`. Exact decimal calculation gives `125.0000 - (100.0000 + 20.0000 + 5.0000) = 0.0000`. This illustrates disjoint reconciliation only. Its physical header, status set, exclusion approval and source-total evidence are **not** approved; it must not become an active FC-C01 test or manifest control.
