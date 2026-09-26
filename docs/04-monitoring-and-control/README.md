# Phase 04: Monitoring and Control

[Project Root](../../README.md) > [Phase 03: Execution](../03-execution/README.md) < **Phase 04: Monitoring & Control** | Next: [Phase 05: Closure](../05-closure/README.md) >>

---

## Purpose & Lifecycle Status

**Purpose:** Provide continuous governance, change control, decision logs, risk management, quality reviews, and formal gate approval records across all project lifecycle phases.

**Current Lifecycle Status (2026-09-25):** **Active governance maintained.**<br/>
This directory maintains the immutable audit trail for all project decisions and milestones from Initiation through Sprint 3. The offline implementation scope of Sprint 3 was formally approved and closed on September 25, 2026 ([Sprint 3 Closure Approval Record](sprint-03-closure-approval.md)) based on the published [Sprint 3 Retrospective](sprint-03-retrospective.md).

---

## Chronological Register of Approvals & Controls

The governance trail progresses forward in time across project sprints:

### 1. Phase 02 Planning Controls (September 2026)
- **2026-09-09 — Gate G2 Planning Approval:** Approved master project planning baseline, scope boundaries, delivery schedule, and risk management plan. See [Planning Baseline](../02-planning/Horizon_Community_Bank_Project_Planning_Baseline.md).

### 2. Sprint 01 Business Analysis Controls (September 2026)
- **2026-09-14 — Sprint 1 BA Approval & Synchronization:** Formal Project Owner approval of user stories, acceptance criteria, process flows, and requirements traceability matrix. See [Sprint 1 Approval Record](sprint-01-approval-record.md).

### 3. Sprint 02 Data Design Controls & Gate G3 (September 2026)
- **2026-09-15 — Sprint 2 Control Record:** Documented design authorization, initial risks, issues, and delivery tracking. See [Sprint 2 Control Record](sprint-02-control-record.md).
- **2026-09-17 — Gate G3 Logical Data Design Approval:** Formal Project Owner approval of the consolidated 109-entity/982-field logical data design package, authoritative dictionary, customer risk catalog, and DD-01 through DD-12 decisions. See [Gate G3 Approval Record](g3-data-design-approval.md).
- **2026-09-17 — WP-PD01 Control Record:** Documented authorization and static delivery of physical architecture and foundation SQL (`sql/migrations/0001_foundation.sql`). See [WP-PD01 Control Record](wp-pd01-control-record.md).

### 4. Change Control & Remediation (September 2026)
- **2026-09-20 — CR-001 (KPI and Risk Refinements):** Retrospective change control documenting KPI formulas and customer risk catalog refinements. See [CR-001 Record](change-control/CR-001-kpi-and-risk-refinements.md).
- **2026-09-20 — CR-002 (Baseline Lifecycle Corrections):** Change control reconciling baseline document versions and lifecycle statuses. See [CR-002 Record](change-control/CR-002-baseline-lifecycle-corrections.md).
- **2026-09-21 — CR-002 Project-Owner Decisions:** Formal Project Owner decision record confirming documentary reconciliation and authority clarifications. See [CR-002 Decisions Record](change-control/CR-002-project-owner-decisions-2026-09-21.md).
- **2026-09-21 — Integration Validation Review:** Validation review confirming static tree consistency across R1, CR-002, and WP-PD01. See [Quality Review](quality-reviews/integration-r1-cr002-wp-pd01-validation-2026-09-21.md).

### 5. Sprint 03 Physical Design & Contract Controls (September 2026)
- **2026-09-21 — Contract Reconciliation Control:** Authority comparison distinguishing approved G3 logical fields from candidate physical aliases. See [Contract Reconciliation Control](sprint-03-contract-reconciliation-control.md).
- **2026-09-21 — PD-01 through PD-07 Design Rule Approval:** Formal approval of seven physical design rules with literal physical annexes pending confirmation. See [PD-01..07 Approval Record](sprint-03-pd01-pd07-design-rule-approval.md).
- **2026-09-22 — Physical Contract Annex Increment 1 Approval:** Approval of PD-01 header structures, PD-02 versioning conventions, and PD-03 manifest specifications. See [Annex 1 Approval Record](sprint-03-physical-contract-annex-1-approval.md).
- **2026-09-22 — PD-04 Conditional Applicability Annex Control:** Control record defining predicate governance across 51 candidate conditional fields. See [PD-04 Control Record](sprint-03-pd04-annex-control.md).
- **2026-09-22 — Physical Contract Annex Increment 3 Control:** Control record documenting PD-05 financial frameworks, PD-06 mappings, PD-07 Chicago runtime specifications, and the master pending register. See [Annex 3 Control Record](sprint-03-physical-contract-annex-3-control.md).

### 6. Sprint 03 Executable Package Controls & Offline Closure (September 2026)
- **2026-09-22 — Executable Package 1 Control Record:** Control record for offline contract engine and synthetic banking data foundation (90 passed tests). See [Package 1 Control Record](sprint-03-executable-package-01-control.md).
- **2026-09-22 — Executable Package 2 Approval & Control Record:** Formal approval of curated processing pipeline, masking, quality rules (DQ-D01..D13), and dual exact reconciliation (135 passed tests). See [Package 2 Control Record](sprint-03-executable-package-02-control.md).
- **2026-09-24 — Package 3 Completion Review Control Record:** Control record for risk condition evaluation (RC-01..05), customer risk classification ($t/u$), and risk hardening. See [Package 3 Completion Review Control](sprint-03-package-03-completion-review-control.md).
- **2026-09-25 — Package 3 Increment 3 Control Record:** Control record for Core Banking KPIs (K01–K10) and four dimensional analytical marts (223 passed tests). See [Increment 3 Control Record](sprint-03-package-03-increment-03-control.md).
- **2026-09-25 — Package 3 Increment 4 Control Record:** Control record for consolidated pipeline orchestration runner, companion `manifest.json.sha256`, and diagnostic-only quarantine scoping (236 passed tests). See [Increment 4 Control Record](sprint-03-package-03-increment-04-control.md).
- **2026-09-25 — Package 3 Consolidated Control Record:** Master control record consolidating delivery across Package 3 Increments 1 through 4. See [Consolidated Control Record](sprint-03-package-03-consolidated-control.md).
- **2026-09-25 — Package 3 Offline Closure Approval Record:** Formal Project Owner acceptance and approval of Package 3 offline scope. See [Package 3 Closure Approval Record](sprint-03-package-03-offline-closure-approval.md).
- **2026-09-25 — Sprint 3 Retrospective:** Comprehensive synthesis of Sprint 3 achievements, quality invariants, lessons learned, and Sprint 4 entry criteria. See [Sprint 3 Retrospective](sprint-03-retrospective.md).
- **2026-09-25 — Sprint 3 Overall Closure Approval Record:** Formal Project Owner acceptance, governance record, and offline scope closure for Sprint 3. See [Sprint 3 Closure Approval Record](sprint-03-closure-approval.md).

---

## Governance Register Map

| Register Directory | Description & Current Contents |
| :--- | :--- |
| **`change-control/`** | Contains [CR-001](change-control/CR-001-kpi-and-risk-refinements.md), [CR-002](change-control/CR-002-baseline-lifecycle-corrections.md), and [CR-002 Project-Owner Decisions](change-control/CR-002-project-owner-decisions-2026-09-21.md). |
| **`quality-reviews/`** | Contains [Integration R1 / CR-002 / WP-PD01 Validation](quality-reviews/integration-r1-cr002-wp-pd01-validation-2026-09-21.md). Additional validation evidence is maintained within the DD-07 through DD-12 validation records. |
| **`decision-log/`** | Retains `.gitkeep`. Formal decisions are documented in the [Sprint 2 Control Record](sprint-02-control-record.md), [Design Traceability Review](../03-execution/sprint-02-data-design/design-traceability-and-review.md), and dated approval records. |
| **`risks-and-issues/`** | Retains `.gitkeep`. Risk registers are actively maintained in [Planning Baseline §15](../02-planning/Horizon_Community_Bank_Project_Planning_Baseline.md#15-risk-register) and individual sprint control records. |
| **`status-reports/`** | Retains `.gitkeep`. Overall progress is tracked in root [PROJECT_STATUS.md](../../PROJECT_STATUS.md) and individual sprint retrospectives. |

---

[Project Root](../../README.md) > [Phase 03: Execution](../03-execution/README.md) < **Phase 04: Monitoring & Control** | Next: [Phase 05: Closure](../05-closure/README.md) >>
