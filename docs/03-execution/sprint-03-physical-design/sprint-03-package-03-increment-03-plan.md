# Sprint 3 Package 3 Increment 3 Implementation Plan — Core Banking KPIs & Analytical Marts

Status: **Approved by Project Owner** (2026-09-25) via `/approve sprint-3-package-3-increment-3-plan`. Technical implementation completed and validated locally.

## 1. Executive Summary & Scope Boundaries

### 1.1 Objectives
1. Implement deterministic, offline computation of the 10 approved core banking KPIs (K01 through K10) in exact scale-4 Decimal currency arithmetic and scale-8 ratio precision.
2. Design and implement four dimensional analytical marts (`mart_transaction_kpis`, `mart_loan_delinquency_kpis`, `mart_customer_risk_kpis`, `mart_complaint_kpis`) adhering to conformed dimensions (`dim_date`, `dim_branch`, `dim_customer`, `dim_account`).
3. Connect curated pipeline outputs from Package 2 and risk assessments from Package 3 Increments 1–2 into deterministic JSON mart artifacts.

### 1.2 Strict Scope Boundaries & Prohibitions
- **NO Database Execution (PD02 Unauthorized):** All marts and KPI engines are implemented in standard-library Python in-memory structures and deterministic JSON serialization. No PostgreSQL connection, migrations, or database inspection.
- **NO Composite Risk Scoring:** Adheres strictly to DD-04/DD-05/DD-06. No machine-learning, probabilistic scoring, or automated lending/fraud decisioning.
- **Fail-Closed Production Boundaries:** All 27 production headers, schemas, candidate predicates, and status mapping tables remain `PENDING` and fail closed in `ExecutionMode.PRODUCTION`. Deterministic calculations execute exclusively against verified `ExecutionMode.FIXTURE` contracts.
- **Non-Additive Exposure (DD-02):** Customer-level shared balances and multi-owner relationship exposures remain strictly non-additive across customers; bank and branch totals are computed directly from natural entity facts (accounts/loans), never summed across customer bridge views.

---

## 2. Review of Approved KPI Definitions & DD-06 Policy Alignment

| ID | Metric Name | Approved Formula / Population Filter | Denominator & Gating Rules | Output Scale |
|---|---|---|---|---|
| **K01** | **Transaction Volume** | Count of all terminal processed transactions: `SUCCESSFUL`, `POSTED`, `FAILED`, `DECLINED`, `CANCELLED`, `VOIDED`, `REVERSED`. | Excludes `PENDING`. Temporal filter: `occurred_at` within half-open interval `[start, end)` (closed start, open end) in `America/Chicago`. | Integer count |
| **K02** | **Transaction Success Rate** | `(SUCCESSFUL + POSTED) / Denominator * 100` | Denominator = `SUCCESSFUL + POSTED + FAILED + DECLINED`. If denominator = 0, displays `Unavailable` (`None`). | Decimal(28, 8) % |
| **K03** | **Transaction Failure Rate** | `(FAILED + DECLINED) / Denominator * 100` | Same denominator as K02 (`SUCCESSFUL + POSTED + FAILED + DECLINED`). Note: `CANCELLED`, `VOIDED`, `REVERSED` are excluded from the rate denominator. | Decimal(28, 8) % |
| **K04** | **Fraud-Alert Rate** | `Distinct eligible transactions with >= 1 linked fraud alert / Denominator * 100` | Same 4-status denominator as K02/K03 (`SUCCESSFUL + POSTED + FAILED + DECLINED`). **Linked transactions must belong to this same eligible 4-status population; non-eligible statuses (`CANCELLED`, `VOIDED`, `REVERSED`, `PENDING`) are excluded from numerator and denominator.** Multiple alerts on one transaction count once. Unlinked fraud alerts cannot enter numerator. | Decimal(28, 8) % |
| **K05** | **Loan Delinquency Rate** | `Count(Active Loans with DPD > 30) / Count(Active Loans) * 100` | Active loans = `ACTIVE`, `DELINQUENT_ACTIVE`, `FORBEARANCE_ACTIVE` as of snapshot date. `PAID_OFF`, `CLOSED`, `CHARGED_OFF`, and `UNKNOWN` are excluded. | Decimal(28, 8) % |
| **K06** | **Outstanding Delinquent Balance** | `Sum(outstanding_principal)` for all loans with `DPD > 30` | **Exact preservation of Planning formula:** Evaluated across **all** loan statuses (not restricted to active). No `outstanding_principal > 0` filter. Currencies kept strictly separate. **DD-09 Gating:** Any loan with `DPD > 30` having missing principal (`PRINCIPAL_MISSING`) or negative principal (`PRINCIPAL_NEGATIVE`) blocks candidate publication for that currency/business-date. | Decimal(28, 4) currency-separated |
| **K07** | **High-Risk Customer Count** | `Count(Distinct Customers)` classified as `RiskClassification.PROVISIONAL_HIGH_RISK` ($t \ge 2$) | Evaluated against immutable customer assessment records from Increment 2. **Incomplete evidence (`INCOMPLETE_EVIDENCE`) and unresolvable assessments (`UNAVAILABLE`) are tracked as separate unknown/unavailable populations and NEVER treated as confirmed not-high-risk customers.** Home branch attributed as of assessment date. | Integer count |
| **K08** | **Average Complaint Resolution Time** | `Mean(final_closed_at - created_at)` in elapsed calendar hours | Evaluated on complaints finally closed within period. Elapsed hours, continuous 24/7 clock, no business-hours pauses. Negative or invalid timestamps quarantined. | Decimal(28, 4) hours |
| **K09** | **Open Complaints** | `Count(Complaints)` with no current closure timestamp AND status != `CLOSED` | Evaluated at snapshot date. `REOPENED` counts as open (retaining original `created_at` clock). Contradictory states quarantined. | Integer count |
| **K10** | **SLA Breach Rate** | `Count(Eligible Complaints with Elapsed Hours > SLA) / Count(Eligible Complaints) * 100` | Priority at creation determines SLA: `Critical` (4h), `High` (24h), `Medium` (72h), `Low` (120h). Open complaints measured `created_at` to snapshot as-of; closed complaints measured `created_at` to `final_closed_at`; reopened complaints measured `created_at` to as-of without clock reset. Strict `>` inequality. | Decimal(28, 8) % |

---

## 3. Detailed Policy Reconciliations

### 3.1 K06 Missing and Negative Principal Handling (DD-06 & DD-09)
1. **Record-Level Disposition:** In loan position records with `days_past_due > 30`:
   - Missing principal (`outstanding_principal is None`) is recorded as `PRINCIPAL_MISSING` (incomplete evidence finding).
   - Negative principal (`outstanding_principal < 0`) is recorded as `PRINCIPAL_NEGATIVE` (quality finding) and quarantined.
2. **Candidate Publication Gating (DD-09 lines 78–80):**
   - For any `DPD > 30` loan with negative or missing principal, K06 cannot be presented as complete: the candidate publication for that currency and business-date is **BLOCKED** until corrected or valid evidence is supplied.
   - Missing principal is *never* treated as zero and cannot produce a fabricated reconciled total.
   - Negative principal remains visible in raw/quarantine signed totals, not erased or converted to absolute values.
3. **Mart Output Representation:** If a currency cohort contains any `DPD > 30` loan with missing or negative principal, K06 outputs `BLOCKED_CANDIDATE` / `Unavailable` with the blocking reason code.

### 3.2 K07 Classification Enum & Population Segregation (DD-04 & Code)
1. **Classification Enum Members ([risk_classification.py](../../../src/horizon_pipeline/analytics/risk_classification.py)):**
   - `RiskClassification.PROVISIONAL_HIGH_RISK = "Provisional high risk"` (Priority 2: $t \ge 2$)
   - `RiskClassification.INCOMPLETE_EVIDENCE = "Incomplete evidence - classification unavailable"` (Priority 3: $t < 2, t + u \ge 2$)
   - `RiskClassification.NOT_HIGH_RISK = "Not high risk under current rule"` (Priority 4: $t < 2, t + u < 2$)
   - `RiskClassification.UNAVAILABLE = "Classification unavailable"` (Priority 1: missing catalog/rule version or invalid condition count)
2. **Strict Population Segregation:**
   - K07 counts only `RiskClassification.PROVISIONAL_HIGH_RISK`.
   - `RiskClassification.INCOMPLETE_EVIDENCE` and `RiskClassification.UNAVAILABLE` represent indeterminate risk states (an unknown condition could trigger and push $t \ge 2$). **They must be reported as distinct unknown/unavailable populations and NEVER grouped with, or counted as, confirmed not-high-risk customers.**
   - `not_high_risk_customer_count` strictly counts customers with complete/evaluated evidence where $t < 2$ and $t + u < 2$.

### 3.3 K04 Cohort Consistency with K02/K03 Denominator (DD-06)
1. **Eligible Transaction Population:** K02, K03, and K04 share the exact same eligible 4-status cohort: `SUCCESSFUL`, `POSTED`, `FAILED`, `DECLINED`.
2. **Fraud-Alert Link Filtering:** A transaction linked to a fraud alert is counted in the K04 numerator **if and only if** its transaction status belongs to the eligible 4-status population.
3. **Non-Eligible Statuses:** Transactions in statuses `CANCELLED`, `VOIDED`, `REVERSED`, or `PENDING` (or unmapped) that happen to be linked to a fraud alert are **excluded from both the numerator and the denominator** of K04.
4. **Alert Deduplication:** Multiple alerts linked to the same eligible transaction count as exactly one alert-linked transaction. Unlinked alerts cannot enter the numerator.

### 3.4 K10 Complaint SLA Clock Continuity (DD-06)
1. **Continuous Calendar Hours:** Clocks run 24 hours a day, 7 days a week, without deductions for non-business hours, weekends, or holidays.
2. **Strict Breach:** Breach requires `elapsed_hours > threshold` (e.g. 24.0000h is not breached; 24.0001h is breached).
3. **Reopened Complaints:** A complaint transitioned to `REOPENED` returns to the open evaluation population. Its elapsed hours are measured from original `created_at` to the snapshot as-of time $T$ **continuously without reset**, including the duration spent in prior closed status.
4. **Invalid Evidence:** Complaints with `final_closed_at < created_at` or missing `created_at` are quarantined and excluded from K10 numerator and denominator.

---

## 4. Register of Unresolved Physical Decisions (Preserved)

All eight unresolved physical decisions remain **Pending confirmation** and enforce fail-closed behavior:

| Decision ID | Item Name | Status | Fail-Closed Enforcement in Increment 3 |
|---|---|---|---|
| **PD-01** | Received CSV Column Headers | Pending confirmation across all 27 sections | `ExecutionMode.PRODUCTION` raises `PendingContractError` |
| **PD-02** | Per-Section Physical Schema IDs | Candidate IDs remain inactive | `ExecutionMode.PRODUCTION` raises `PendingContractError` |
| **PD-04** | Conditional Applicability Predicates | 51 candidate predicates nonactive | Missing predicate evidence fails closed without active filters |
| **PD-05** | Production Financial Tolerances | Candidate controls remain pending | `ExecutionMode.PRODUCTION` raises `PendingContractError` |
| **PD-06** | Physical Status Mappings | 23 mapping groups remain pending | `ExecutionMode.PRODUCTION` raises `PendingContractError` |
| **PD-07** | Chicago tzdb 2026a Proof | Runtime host verification pending | Explicit check required; unverified host fails closed |
| **PD02** | PostgreSQL Migration & DDL | Database execution is **unauthorized** | Pure offline Python in-memory and JSON serialization only |
| **DD-06 / DD-09** | K06 Reason Code Spellings | `PRINCIPAL_NEGATIVE`, `PRINCIPAL_MISSING` draft | Modeled as typed constants; documented as draft spellings |

---

## 5. Dimensional Analytical Marts Design

### 5.1 Mart 1: `mart_transaction_kpis`
- **Grain:** `[aggregation_period_start, aggregation_period_end, branch_id, channel, currency]`
- **Dimensions:** `period_start`, `period_end`, `branch_id`, `channel`, `currency`
- **Measures:**
  - `total_transaction_count` (K01)
  - `successful_transaction_count`, `posted_transaction_count`
  - `failed_transaction_count`, `declined_transaction_count`
  - `cancelled_count`, `voided_count`, `reversed_count`
  - `rate_eligible_transaction_count` (Denominator for K02, K03, K04)
  - `success_rate_pct` (K02)
  - `failure_rate_pct` (K03)
  - `eligible_transactions_with_fraud_alert_count` (K04 Numerator)
  - `fraud_alert_rate_pct` (K04)
  - `total_transaction_amount` (Decimal(28, 4))

### 5.2 Mart 2: `mart_loan_delinquency_kpis`
- **Grain:** `[business_date, branch_id, currency, loan_type]`
- **Dimensions:** `business_date`, `branch_id`, `currency`, `loan_type`
- **Measures:**
  - `active_loan_count` (K05 Denominator)
  - `delinquent_active_loan_count` (K05 Numerator: DPD > 30 and Active)
  - `loan_delinquency_rate_pct` (K05)
  - `total_loans_evaluated`
  - `delinquent_loan_count_all_statuses` (DPD > 30 regardless of status)
  - `delinquent_outstanding_principal` (K06: Decimal(28, 4) or `None` if blocked)
  - `k06_publication_status` (`PUBLISHED`, `BLOCKED_CANDIDATE`, `UNAVAILABLE`)
  - `quarantined_negative_principal_count` (DD-09 audit control)
  - `missing_principal_count` (DD-09 audit control)

### 5.3 Mart 3: `mart_customer_risk_kpis`
- **Grain:** `[as_of_date, home_branch_id]`
- **Dimensions:** `as_of_date`, `home_branch_id`
- **Measures:**
  - `total_assessed_customer_count`
  - `provisional_high_risk_customer_count` (K07: $t \ge 2$)
  - `incomplete_evidence_customer_count` ($t < 2, t + u \ge 2$; separate unknown population)
  - `unavailable_assessment_customer_count` (missing catalog/rule version or invalid evidence)
  - `not_high_risk_customer_count` ($t < 2, t + u < 2$; confirmed not-high-risk)
  - `rc01_triggered_count` through `rc05_triggered_count`
  - `relationship_exposure_non_additive: true` (DD-02 mandatory metadata flag)

### 5.4 Mart 4: `mart_complaint_kpis`
- **Grain:** `[reporting_period_start, reporting_period_end, branch_id, channel, priority]`
- **Dimensions:** `period_start`, `period_end`, `branch_id`, `channel`, `priority`
- **Measures:**
  - `closed_complaint_count`
  - `total_resolution_hours` (Decimal(28, 4))
  - `avg_resolution_hours` (K08)
  - `open_complaint_count` (K09)
  - `reopened_complaint_count`
  - `sla_eligible_complaint_count` (K10 Denominator)
  - `sla_breached_complaint_count` (K10 Numerator)
  - `sla_breach_rate_pct` (K10)

---

## 6. Acceptance Criteria & Dedicated Acceptance Tests

### AC-K01-01: Transaction Volume
- **Given** transactions in `[start, end)` America/Chicago with mixed statuses,
- **When** evaluating K01,
- **Then** all terminal statuses are counted and `PENDING` is strictly excluded.

### AC-K02-01 & AC-K03-01: Success & Failure Rates
- **Given** terminal transactions in period,
- **When** the eligible 4-status population is > 0,
- **Then** K02 = `(SUCCESSFUL + POSTED) / Denominator * 100` and K03 = `(FAILED + DECLINED) / Denominator * 100`, satisfying `K02 + K03 == 100.00000000%`.
- **When** the eligible population is 0,
- **Then** K02 and K03 return `Unavailable` (`None`).

### AC-K04-01: Fraud-Alert Deduplication on Eligible Transactions
- **Given** eligible transaction TX1 with status `SUCCESSFUL` and three linked fraud alerts,
- **When** evaluating K04,
- **Then** TX1 contributes exactly 1 to the K04 numerator.

### AC-K04-02: K04 Eligible Status Filter & Denominator Consistency
- **Given** transaction TX1 with status `SUCCESSFUL` and linked fraud alert A1,
- **And** transaction TX2 with status `CANCELLED` and linked fraud alert A2,
- **And** transaction TX3 with status `POSTED` without a fraud alert,
- **When** evaluating K04,
- **Then** TX2 is excluded from both the K04 numerator and the K04 denominator because `CANCELLED` does not belong to the eligible 4-status set (`SUCCESSFUL`, `POSTED`, `FAILED`, `DECLINED`),
- **And** the eligible denominator is 2 (TX1, TX3),
- **And** the numerator is 1 (TX1), yielding K04 = `50.00000000%`.

### AC-K05-01: Loan Delinquency Rate
- **Given** loan snapshots on `business_date`,
- **When** evaluating K05,
- **Then** only active loans (`ACTIVE`, `DELINQUENT_ACTIVE`, `FORBEARANCE_ACTIVE`) are included, and numerator requires `DPD > 30` (DPD = 30 is strictly not delinquent).

### AC-K06-01: Missing Principal Gating
- **Given** a loan snapshot containing at least one loan with `DPD > 30` and `outstanding_principal is None`,
- **When** evaluating K06,
- **Then** K06 candidate publication for that currency is marked `BLOCKED_CANDIDATE` with reason `PRINCIPAL_MISSING`, and no partial sum is published.

### AC-K06-02: Negative Principal Quarantine & Gating
- **Given** a loan snapshot with `DPD > 30` and `outstanding_principal < 0`,
- **When** evaluating K06,
- **Then** the record is quarantined as `PRINCIPAL_NEGATIVE`, K06 candidate publication is blocked under DD-09, and the signed negative amount is preserved in quarantine reconciliation controls.

### AC-K07-01: Provisional High Risk Aggregation
- **Given** customer risk assessments generated from Increment 2,
- **When** aggregating K07,
- **Then** only assessments with `RiskClassification.PROVISIONAL_HIGH_RISK` ($t \ge 2$) contribute to `provisional_high_risk_customer_count`.

### AC-K07-02: Segregation of Incomplete Evidence & Unavailable from Not-High-Risk
- **Given** Customer C1 with $t=1, u=1$ (`RiskClassification.INCOMPLETE_EVIDENCE`),
- **And** Customer C2 with missing catalog version (`RiskClassification.UNAVAILABLE`),
- **And** Customer C3 with $t=0, u=0$ (`RiskClassification.NOT_HIGH_RISK`),
- **And** Customer C4 with $t=2, u=0$ (`RiskClassification.PROVISIONAL_HIGH_RISK`),
- **When** aggregating `mart_customer_risk_kpis`,
- **Then** K07 (`provisional_high_risk_customer_count`) is 1 (C4),
- **And** `incomplete_evidence_customer_count` is 1 (C1),
- **And** `unavailable_assessment_customer_count` is 1 (C2),
- **And** `not_high_risk_customer_count` is 1 (C3),
- **And** C1 and C2 are **strictly excluded** from `not_high_risk_customer_count`, ensuring unknown evidence is never conflated with confirmed not-high-risk status.

### AC-K08-01: Complaint Resolution Time
- **Given** finally closed complaints in period,
- **When** evaluating K08,
- **Then** elapsed hours from `created_at` to `final_closed_at` are averaged across the cohort using continuous 24/7 calendar hours.

### AC-K09-01: Open Complaints Count
- **Given** complaint snapshots at business date,
- **When** evaluating K09,
- **Then** complaints without a closure timestamp and status != `CLOSED` (including `REOPENED`) are counted.

### AC-K10-01: Continuous Clock & Strict Greater Than Breach
- **Given** an open complaint with priority `High` (24h SLA) created 24.0000 hours prior to snapshot $T$,
- **When** evaluating K10,
- **Then** elapsed hours (24.0000) does not exceed 24.0000, so it is evaluated as **Not Breached**.
- **When** elapsed hours is 24.0001,
- **Then** it is evaluated as **Breached**.

### AC-K10-02: Reopened Complaint Continuity
- **Given** a complaint that was closed and subsequently `REOPENED`,
- **When** evaluating K10,
- **Then** elapsed hours is measured from original `created_at` to snapshot $T$ without clock reset or deduction for intermediate closed duration.

### AC-MODE-01: Strict Production Fail-Closed
- **Given** invocation with `ExecutionMode.PRODUCTION`,
- **When** any physical header, schema, status mapping, or financial tolerance is `PENDING`,
- **Then** execution immediately raises `PendingContractError` and publishes zero unverified data.

---

## 7. QA & Test Strategy

1. **Preserve Baseline Regression:** Maintain 100% pass rate across the existing 187 tests (`python -m pytest -q tests`).
2. **Dedicated Test Modules (~35–40 new unit tests):**
   - `tests/test_kpi_transactions.py`: K01–K04 formulas, zero-denominator `Unavailable`, fraud alert deduplication, K04 eligible-status filtering, half-open interval boundaries.
   - `tests/test_kpi_loans.py`: K05 active-only filter, K06 all-status filter, DPD 30 vs 31 boundary, `PRINCIPAL_MISSING` publication blocking, `PRINCIPAL_NEGATIVE` quarantine, currency separation.
   - `tests/test_kpi_customer_risk.py`: K07 `PROVISIONAL_HIGH_RISK` aggregation, `INCOMPLETE_EVIDENCE` reporting, non-additive exposure metadata, home branch attribution.
   - `tests/test_kpi_complaints.py`: K08 calendar hours, K09 open/reopened logic, K10 strict `>` SLA thresholds, reopened clock continuity.
   - `tests/test_analytical_marts.py`: Star schema record integrity, grain uniqueness, dimension conformity, deterministic JSON serialization.
   - `tests/test_kpi_mode_isolation.py`: Fail-closed verification under `ExecutionMode.PRODUCTION`.
3. **Source Reconciliation Invariance:** Confirm `python scripts/reconcile_source_fields.py` remains exactly 27 sections and 333 logical target field rows.

---

## 8. Approval Gate

Project Owner approval was received on 2026-09-25 via:

```text
/approve sprint-3-package-3-increment-3-plan
```

Technical implementation was completed under offline fixture mode across K01–K10 and four dimensional analytical marts, with 223 total passing tests (187 baseline + 36 Increment 3 tests) and source field reconciliation invariant at 27 sections / 333 rows.
