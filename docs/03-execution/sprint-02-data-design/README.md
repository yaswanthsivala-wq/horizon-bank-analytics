# Sprint 02 — Data Design

[Execution](../README.md) > [Sprint 01: Business Analysis](../sprint-01-business-analysis/README.md) < **Sprint 02: Data Design** | Next: [Sprint 03: Physical Design](../sprint-03-physical-design/README.md) >>

---

## Purpose & Lifecycle Status

**Purpose:** Establish the logical data architecture, normalized entity-relationship models, authoritative field-level data dictionary, source-to-target mappings, customer identity rules, data quality controls, security/masking designs, and customer risk catalog across all five banking domains.

**Current Lifecycle Status (2026-09-25):** **Approved September 17, 2026 (Gate G3); permanent logical baseline.**<br/>
The complete consolidated logical data design package was formally reviewed and approved by the Project Owner at Gate G3 on September 17, 2026 ([Gate G3 Approval Record](../../04-monitoring-and-control/g3-data-design-approval.md)). It serves as the authoritative logical contract for physical design, database schemas, and offline processing pipelines. Downstream Sprint 3 (Physical Design & Offline Implementation) has since been formally executed and closed.

---

## Authoritative Artifact Inventory

### Logical Architecture & Data Modeling
- [Logical data model](logical-data-model.md): Comprehensive enterprise ERD and entity definitions covering 109 logical entities and 982 fields across five banking domains.
- [Data model and ERD](data-model.md): Grains, natural identity keys, temporal history, and analytical projections.
- [Relationship register](relationship-register.md): Dictionary-derived foreign key references and entity dependency graphs.

### Authoritative Dictionary & Source Mappings
- [Field-level dictionary and mappings](field-level-dictionary.md): Authoritative DD-07 field repository defining data types, nullability, requiredness, lineage, and cross-field constraints.
- [Data dictionary and source mappings](data-dictionary-and-mappings.md): Conceptual navigation mapping simulated source files to logical target entities.
- [Source-system definitions](source-system-definitions.md): Daily extract specifications, grain definitions, and provenance across SRC-01 through SRC-05.

### Domain Rules, Quality & Governance
- [Customer-identity rules](customer-identity-reconciliation.md): Deterministic identity crosswalk, conflict resolution, and human review ledgers.
- [Customer-risk catalog](customer-risk-catalog.md): Five explainable risk conditions (RC-01..05), threshold-aware unknown handling, and customer risk classification ($t/u$).
- [KPI-to-data mappings](kpi-to-data-mappings.md): Precise calculation logic, time windows, filter semantics, and denominator definitions for K01–K10.
- [Security and masking design](security-and-masking-design.md): Role-based access control (RBAC), last-four PII masking, export governance, and retention constraints.
- [Data-quality and reconciliation design](data-quality-and-reconciliation.md): 17-rule severity catalog (DQ-D01..DQ-D13), quarantine ledger, rerun policies, and dual exact reconciliation.
- [Retention and disposal design](retention-and-disposal-design.md): 24-month raw data retention, 7-year audit retention, legal hold mechanics, and batch disposal rules.
- [Historical branch attribution policy](historical-branch-attribution-policy.md): Effective-dated branch assignment versioning and historical reporting rules (DD-12).
- [Loan payment and schedule policy](loan-payment-and-schedule-policy.md): Contractual obligations, amortization schedules, unapplied funds, and adjustment events (DD-11).

### Validation & Gate Closure
- [Synthetic-data specification](synthetic-data-specification.md): Scenario specifications, volume parameters, and generation distributions.
- [Synthetic contract traceability](synthetic-contract-traceability.md): Complete mapping between synthetic extract fields and logical targets.
- [Design traceability and review](design-traceability-and-review.md): Full requirement coverage verification against Sprint 1 BA backlog.
- [Gate G3 prerequisite register](g3-prerequisite-register.md) and [G3 closure validation](g3-closure-validation.md): Formal verification evidence for Gate G3 closure.

---

## Chronological Design Decision Journey (DD-01 through DD-12)

During Sprint 2, twelve foundational data design decisions were formulated, reviewed, and approved:
1. **DD-01 (Delivery Modes & Manifests):** Entity-specific delivery modes (full, delta, snapshot) and mandatory batch manifest files.
2. **DD-02 (Relationship Exposure):** Retention of joint holders and co-borrowers; shared balances labeled *Relationship Exposure* and modeled as strictly non-additive.
3. **DD-03 (Historical Snapshots):** Daily position snapshots at `loan + business_date` and `complaint + business_date` grains; no backfilling or forward-peeking.
4. **DD-04 (Customer Risk Catalog):** Definition of RC-01 through RC-05, threshold $t \ge 2$, and explicit segregation of unknown evidence populations.
5. **DD-05 (RC-01 Attribution Hierarchy):** Transaction initiator and primary account owner attribution hierarchy.
6. **DD-06 (KPI Policy):** Standardized formulas, eligible status denominators, and continuous 24/7 calendar clocks for K01–K10.
7. **DD-07 (Authoritative Field Dictionary):** Consolidation of all 109 logical entities and 982 fields into a single authoritative dictionary.
8. **DD-08 (Security & Masking):** Role entitlement scopes, last-four tax identifier masking, and restricted export policies.
9. **DD-09 (Quality & Publication):** 17-rule quality severity catalog, mandatory source gates, and dual exact reconciliation (`RC-D01` and `RC-D02`).
10. **DD-10 (Lifecycle & Retention):** Exact-batch disposal exceptions, 24-month raw analytical retention, and 7-year audit retention.
11. **DD-11 (Loan Payment Semantics):** Separate contractual loan obligations, payment allocations, unapplied balances, and adjustment events.
12. **DD-12 (Historical Branch Hierarchy):** Separate effective organizational hierarchy from historical transactional branch attribution.

---

## Historical Status & Boundary Clarification

> [!NOTE]
> Historical status statements in Sprint 2 documentation noting that *"No source schemas, DDL, generated data, ETL, Power BI model or test results exist"* describe the project boundary upon completion of the logical design phase on September 17, 2026. Downstream Sprint 3 successfully authored the foundation DDL (`sql/migrations/0001_foundation.sql`), implemented the offline contract engine, created synthetic generators, and executed the offline pipeline across 236 passing tests. Production database execution (PD02/PostgreSQL) remains unauthorized pending future authorization.

---

[Execution](../README.md) > [Sprint 01: Business Analysis](../sprint-01-business-analysis/README.md) < **Sprint 02: Data Design** | Next: [Sprint 03: Physical Design](../sprint-03-physical-design/README.md) >>
