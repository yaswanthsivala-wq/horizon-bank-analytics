# Sprint 01 — Business Analysis

[Execution](../README.md) > **Sprint 01: Business Analysis** | Next: [Sprint 02: Data Design](../sprint-02-data-design/README.md) >>

---

## Purpose & Lifecycle Status

**Purpose:** Establish the approved Release 1 business-analysis baseline, functional and non-functional requirements traceability, user stories, acceptance criteria, and business process models before technical design or implementation begins.

**Current Lifecycle Status (2026-09-25):** **Approved September 14, 2026; permanent baseline.**<br/>
Sprint 1 artifacts were formally reviewed and approved by the Project Owner on September 14, 2026. They serve as the immutable requirements contract for all downstream data modeling, processing logic, and analytical marts. Subsequent delivery sprints—including Sprint 2 (Data Design - Gate G3) and Sprint 3 (Physical Design & Offline Implementation)—have been formally executed and closed.

---

## Artifact Inventory

- [Product backlog and acceptance criteria](product-backlog.md): Eight prioritized user stories (US-01 through US-08) and 32 Given–When–Then acceptance criteria.
- [AS-IS, TO-BE, role-access, and customer-risk process flows](process-flows.md): Detailed swimlane and procedural flows for month-end reporting, daily intake, role-based reporting, and risk review.
- [Requirements traceability matrix](requirements-traceability-matrix.md): Complete forward and backward traceability mapping business requirements to acceptance criteria and downstream components.
- [Approved Planning baseline](../../02-planning/Horizon_Community_Bank_Project_Planning_Baseline.md): Authoritative upstream project baseline.

---

## Scope & Core Deliverables

1. **User Stories & Acceptance Criteria:**
   - Operational reporting across transaction volumes, failure rates, and branch attribution.
   - Loan portfolio delinquency tracking and outstanding principal aggregation.
   - Multi-condition customer risk indicators and drill-down review.
   - Customer complaint SLA breach tracking and escalation flows.
2. **Process Analysis:**
   - **AS-IS Reporting Process:** 3-day manual aggregation bottleneck with high operational risk.
   - **TO-BE Reporting Process:** Automated daily ingestion and reconciliation delivering trusted marts by 6:00 a.m. Central Time.
   - **Role-Based Navigation Flow:** Branch Manager, Loan Operations, Fraud Analyst, Executive, and Risk Manager role personas.
   - **Customer Risk Evaluation Flow:** Standardized, deterministic rule-based evaluation avoiding black-box scoring.
3. **Traceability:**
   - Strict bidirectional mapping connecting Business Objectives $\leftrightarrow$ Functional Requirements $\leftrightarrow$ User Stories $\leftrightarrow$ Test Scenarios.

---

## Historical Sign-off Record

> [!NOTE]
> Historical notes in Sprint 1 documents stating that *"Technical implementation: not started"* or *"Sprint 2 has not started"* describe the project boundary at the conclusion of Sprint 1 sign-off on September 14, 2026. See the formal [Sprint 1 Approval Record](../../04-monitoring-and-control/sprint-01-approval-record.md). Downstream Sprints 2 and 3 offline scopes have since completed.

---

[Execution](../README.md) > **Sprint 01: Business Analysis** | Next: [Sprint 02: Data Design](../sprint-02-data-design/README.md) >>
