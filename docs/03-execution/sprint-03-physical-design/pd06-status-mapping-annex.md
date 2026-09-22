# PD-06 status and reference mapping annex — Increment 3

Status: **Approved framework — Physical mapping rows and mapping-version IDs pending confirmation** (Project Owner reviewed 2026-09-22). PD-06 is **Approved — Design Rule**. Approval covers the keyed mapping-contract structure, raw/canonical separation, exact applied-version lineage, deterministic lookup, unknown/missing/retired-version fail-closed behavior and version separation. The 23 domain groups remain candidate coverage; no literal physical mapping-version ID or raw-to-canonical row is approved or active by this annex.

## Authority and classification

| Classification | Evidence and consequence |
| --- | --- |
| Approved baseline | [DD-07 dictionary](../sprint-02-data-design/field-level-dictionary.md) defines immutable `mapping_version`, four-field `mapping_entry` key (`mapping_version`, `source_system`, `domain_code`, `raw_value`) and child eligibility; [DD-06](../sprint-02-data-design/kpi-policy-dd06.md), [KPI mappings](../sprint-02-data-design/kpi-to-data-mappings.md) and [risk catalog](../sprint-02-data-design/customer-risk-catalog.md) define canonical populations/eligibility. [G3 synthetic contract](../sprint-02-data-design/synthetic-source-contract.md) proposes identity raw codes and `IDENTITY_SYN_V1`, with `X_UNMAPPED` reserved for negative fixtures. [DD-09 DQ-D06](../sprint-02-data-design/data-quality-and-reconciliation.md) controls unknown/unavailable mapping evidence. |
| Derived physical implementation detail | The candidate row model, coverage register and failure state machine below organize review; they do not make G3's illustrative fixture codes active mappings. |
| Pending confirmation | Exact received raw fields/codes, final `(source, domain, version, raw)` rows, literal mapping IDs, effective/retired states, eligibility flags and simulated owner review. PD-03 `mapping_version_references` is a structural placeholder. |
| Conflict | None identified. A semantic change to approved KPI/risk populations requires change control. |

## Candidate row contract and lineage

A future active mapping row is keyed by `(source_system, domain_code, mapping_version, raw_value)` and records the immutable canonical value, KPI and risk eligibility flags by named rule/version, PD-04 predicate eligibility where needed, effective/retired state, source evidence, approval decision and any predecessor. Preserve the exact raw value alongside the canonical result. Store the **mapping version actually applied** on interpreted history/replay; a later mapping cannot silently rewrite an accepted publication. Mapping version is independent of PD-02 schema version, batch revision and source-state version. A mapping-only change does not automatically change a physical schema; a changed header, physical meaning/type or applicability does require PD-02 review.

An unknown raw code, missing row, retired mapping, unsupported version or missing required eligibility evidence is a controlled finding and fails the dependent KPI, risk, PD-04 or PD-05 gate. Do not silently map it to `OTHER`, `UNKNOWN` or a passing status. Legitimate `Unknown` **risk result from incomplete business evidence** remains distinct from missing required configuration. The G3 proposal `IDENTITY_SYN_V1` is candidate synthetic evidence, not an activated physical mapping version. `X_UNMAPPED` remains a negative fixture code, not a canonical value.

## Domain coverage register

The source-domain candidates below are traceable to the [source-field inventory](source-field-inventory.md) and G3 synthetic contract. Listed values are **documented synthetic logical/fixture values**, not final received raw-to-canonical rows. For every row: raw physical field, exact raw code set, mapping-version ID, eligibility flags, owner review and active state are **Pending confirmation**. The table is a coverage checklist, not a mapping table.

| Source / section(s) | Candidate domain and documented values | Rule dependency | Physical mapping state |
| --- | --- | --- | --- |
| SRC-01 / `customers` | segment: RETAIL, SMALL_BUSINESS | customer/KPI grouping | Pending confirmation |
| SRC-01 / `accounts` | account type: CHECKING, SAVINGS | K01–K04 grouping | Pending confirmation |
| SRC-01 / `holders` | holder role: PRIMARY, JOINT | DD-02 relationship | Pending confirmation |
| SRC-01 / `transactions` | transaction type: TRANSFER, PAYMENT, WITHDRAWAL, DEPOSIT | flow/RC-01 grain | Pending confirmation |
| SRC-01 / `transactions` | transaction status: SUCCESSFUL, POSTED, FAILED, DECLINED, CANCELLED, VOIDED, REVERSED, PENDING | DD-06 RC-01 eligible SUCCESSFUL/POSTED | Pending confirmation |
| SRC-01 / `account_restriction_state` | restriction: NONE, RESTRICTED, FROZEN, BLOCKED | RC-05 | Pending confirmation |
| SRC-01 / `account_branch_assignment` | branch role: SERVICING, ORIGINATION | DD-12 attribution | Pending confirmation |
| SRC-02 / `loans` | loan type: PERSONAL, AUTO, MORTGAGE | K05/K06 grouping | Pending confirmation |
| SRC-02 / `borrowers` | borrower role: PRIMARY, CO_BORROWER | DD-02 relationship | Pending confirmation |
| SRC-02 / `positions` | loan status: ACTIVE, DELINQUENT_ACTIVE, FORBEARANCE_ACTIVE, PAID_OFF, CLOSED, CHARGED_OFF | K05/K06, RC-03 | Pending confirmation |
| SRC-02 / `payments` | payment status: PENDING, POSTED, FAILED, CANCELLED | DD-11 financially effective POSTED; PD-04 `posted_at` | Pending confirmation |
| SRC-02 / `payment_allocation` | component: PRINCIPAL, INTEREST, FEE | DD-11 allocation | Pending confirmation |
| SRC-02 / `payment_adjustment` | kind: REVERSAL, REFUND | DD-11 separate adjustment | Pending confirmation |
| SRC-02 / `loan_account` | relationship role: REPORTING | DD-11 reporting link | Pending confirmation |
| SRC-02 / `loan_branch_assignment` | branch role: SERVICING, ORIGINATION | DD-12 attribution | Pending confirmation |
| SRC-03 / `alerts`, `fraud_alert_state` | fraud case status: OPEN, CLOSED | RC-02 | Pending confirmation |
| SRC-03 / `alerts`, `fraud_alert_state` | severity: LOW, MEDIUM, HIGH, CRITICAL | RC-02 HIGH/CRITICAL | Pending confirmation |
| SRC-03 / `alerts` | alert reason: VELOCITY, AMOUNT, RESTRICTION | RC-02 context | Pending confirmation |
| SRC-04 / `complaints`, `complaint_snapshot`, `complaint_history_event` | complaint status: OPEN, IN_PROGRESS, REOPENED, CLOSED | K08–K10, RC-04, PD-04 closure | Pending confirmation |
| SRC-04 / `complaints`, `complaint_snapshot` | priority: Critical, High, Medium, Low | DD-06 SLA | Pending confirmation |
| SRC-04 / `complaints` | channel: PHONE, WEB, BRANCH | complaint grouping | Pending confirmation |
| SRC-04 / `complaint_branch_assignment` | branch role: RESPONSIBLE | DD-12 attribution | Pending confirmation |
| SRC-05 / `organizational_unit` | unit type: REGION, BRANCH | DD-12 hierarchy | Pending confirmation |

**Coverage totals:** 23 domain/source-section candidate groups; 0 final raw-to-canonical rows; 23 groups Pending confirmation; 0 conflicts and 0 active mapping rows. Other status/reference needs may emerge when PD-01 exact headers are approved. A repeated domain across two sections remains one listed candidate group only where the source and proposed vocabulary are shared; final physical binding is still per received field and contract.
