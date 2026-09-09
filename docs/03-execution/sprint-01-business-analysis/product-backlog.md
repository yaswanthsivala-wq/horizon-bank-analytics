# Product Backlog and Acceptance Criteria

**Project:** Banking Operations & Customer Risk Analytics  
**Release:** 1  
**Backlog version:** 1.0

## Priority Definitions

- **Must:** Required for Release 1 acceptance.
- **Should:** Important but may be deferred if it threatens mandatory scope.
- **Could:** Optional enhancement.

## US-01 — Executive KPI Summary

**Priority:** Must  
**Persona:** Executive

As an executive, I want a summarized view of banking operations and customer-risk KPIs so that I can evaluate performance without accessing sensitive customer details.

### Acceptance Criteria

1. **Given** an authenticated executive user, **when** the Executive Summary opens, **then** it displays the ten approved Release 1 KPIs using aggregated data only.
2. **Given** a selected date range, **when** the executive changes the period, **then** the page recalculates the KPIs and displays the comparable preceding-period change.
3. **Given** an executive user, **when** the user navigates or exports data, **then** customer names, contact information, full account numbers, and transaction-level customer details are unavailable.
4. **Given** validated daily data, **when** the dashboard is opened, **then** the displayed last-refresh timestamp is visible.

## US-02 — Branch Performance Analysis

**Priority:** Must  
**Persona:** Banking Operations Manager

As an operations manager, I want to compare transaction performance across regions and branches so that I can identify operational problems requiring investigation.

### Acceptance Criteria

1. **Given** an operations manager with an assigned region, **when** the Branch Performance page opens, **then** only authorized regional and branch information is displayed.
2. **Given** the user selects a region, **when** the user drills down, **then** transaction volume, success rate, failure rate, and status distribution appear by branch.
3. **Given** cancelled or reversed transactions exist, **when** success and failure rates are calculated, **then** those transactions are shown separately and excluded from both denominators.
4. **Given** branch filters are active, **when** the user clears the filters, **then** authorized regional totals are restored.

## US-03 — Fraud Investigation

**Priority:** Must  
**Persona:** Fraud Analyst

As a fraud analyst, I want to review fraud alerts and unusual-transaction indicators so that I can prioritize cases for investigation.

### Acceptance Criteria

1. **Given** an authorized fraud analyst, **when** the Fraud Analysis page opens, **then** alerts can be filtered by date, severity, status, region, branch, and alert reason.
2. **Given** a transaction amount is at least three times the customer's average transaction amount during the preceding 90 days, **when** risk indicators are calculated, **then** the transaction is flagged as unusual activity.
3. **Given** an unusual-activity flag, **when** the analyst opens its detail, **then** the current amount, preceding 90-day average, multiplier, alert history, and masked account number are displayed.
4. **Given** a transaction has an unusual-activity flag, **when** results are displayed, **then** the system labels it as an analytical indicator and not confirmed fraud.

## US-04 — Loan Delinquency Monitoring

**Priority:** Must  
**Persona:** Loan Operations Manager

As a loan operations manager, I want to monitor delinquent loans and outstanding balances so that I can prioritize accounts for follow-up.

### Acceptance Criteria

1. **Given** active loan records, **when** the Loan Operations page opens, **then** it displays the delinquency rate and outstanding delinquent balance using approved formulas.
2. **Given** a loan is more than 30 days past due, **when** delinquency logic executes, **then** the loan is classified as delinquent.
3. **Given** authorized access, **when** the manager filters by branch, loan type, or aging band, **then** all loan KPIs and visualizations respond consistently.
4. **Given** a delinquent-loan record, **when** the user drills through, **then** the page shows masked account details, days past due, outstanding principal, and payment history.

## US-05 — Complaint and SLA Monitoring

**Priority:** Must  
**Persona:** Customer Service Manager

As a customer service manager, I want to monitor open complaints and SLA breaches so that overdue and high-priority cases can be addressed before weekly reviews.

### Acceptance Criteria

1. **Given** complaint data, **when** the Complaint Operations page opens, **then** it displays open complaints, average resolution hours, and SLA breach rate.
2. **Given** a complaint priority, **when** SLA status is calculated, **then** the thresholds are Critical 4 hours, High 24 hours, Medium 72 hours, and Low 120 hours.
3. **Given** a complaint has no closed date and its status is not Closed, **when** open complaints are calculated, **then** it is counted as open.
4. **Given** an authorized manager, **when** the user filters by priority, channel, region, branch, or status, **then** the page updates and retains the same KPI definitions.

## US-06 — Explainable Customer-Risk View

**Priority:** Must  
**Persona:** Risk Analyst

As a risk analyst, I want to see each customer's triggered risk conditions so that I can understand and review the reason for the provisional classification.

### Acceptance Criteria

1. **Given** the approved provisional rule, **when** a customer meets at least two configured risk conditions, **then** the customer is classified as high risk.
2. **Given** a high-risk classification, **when** the analyst opens customer detail, **then** every triggered condition, calculation date, source, and threshold is shown.
3. **Given** Risk or Compliance changes a threshold, **when** configuration is updated and the process reruns, **then** the classification uses the new value without changing program source code where practical.
4. **Given** a classification is displayed, **when** the user reviews it, **then** the dashboard states that it supports human review and does not make an automatic fraud or lending decision.

## US-07 — Role-Based Security and Masking

**Priority:** Must  
**Persona:** Compliance Officer

As a compliance officer, I want role-appropriate access, masking, and export behavior so that sensitive information is protected and access is auditable.

### Acceptance Criteria

1. **Given** an executive user, **when** any report is viewed or exported, **then** only aggregated information is available.
2. **Given** an account number is displayed in reporting, **when** the report renders, **then** only its final four digits are visible.
3. **Given** an unauthorized user attempts customer-level navigation, **when** access rules are evaluated, **then** access is denied and no sensitive row is returned.
4. **Given** a simulated export occurs, **when** it completes, **then** user role, report, timestamp, format, and filter context are recorded in the audit dataset.

## US-08 — Daily Refresh and Data Quality

**Priority:** Must  
**Persona:** Data Owner

As a data owner, I want daily pipeline, reconciliation, and quality results so that I can confirm the dashboard is complete and trustworthy before publication.

### Acceptance Criteria

1. **Given** five expected daily extracts, **when** the pipeline begins, **then** it verifies that every required source is present and stops publication if a critical source is missing.
2. **Given** source records, **when** validation runs, **then** duplicates, missing required values, invalid dates, invalid statuses, and orphan relationships are recorded with a reason code.
3. **Given** a completed load, **when** reconciliation runs, **then** source and target counts and financial control totals are compared and unexplained differences fail the run.
4. **Given** a successful validated run, **when** publication completes, **then** the status, start/end timestamps, row counts, rejection counts, completeness rate, and readiness time are recorded.

## Definition of Ready

A story is ready when its business owner, source data, requirement links, assumptions, acceptance criteria, and test approach are identified.

## Definition of Done

A story is complete when implementation is tested, acceptance criteria pass, traceability is updated, documentation matches actual behavior, no critical defect remains open, and no sensitive secret is committed.

