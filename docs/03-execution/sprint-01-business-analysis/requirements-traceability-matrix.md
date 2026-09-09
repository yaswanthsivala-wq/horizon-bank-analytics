# Requirements Traceability Matrix

**Version:** 1.0  
**Purpose:** Ensure every approved requirement is designed, implemented, and tested.

## Functional Traceability

| Requirement | Business objective | User story | Planned component | Verification | Status |
|---|---|---|---|---|---|
| FR-01 Daily five-source load | BO-01, BO-02 | US-08 | Python ingestion layer | Integration test IT-01 | Planned |
| FR-02 24-month history | BO-04 | US-01, US-02 | Raw and curated PostgreSQL tables | Data-range test DQ-01 | Planned |
| FR-03 Identifier standardization | BO-01, BO-04 | US-08 | Customer/account crosswalk | Match and exception test DQ-02 | Planned |
| FR-04 Data-quality controls | BO-02, BO-03 | US-08 | Validation and quarantine modules | Data-quality suite DQ-03 | Planned |
| FR-05 Approved KPI formulas | BO-03 | US-01–US-06 | SQL analytics views and Power BI measures | KPI reconciliation RC-01 | Planned |
| FR-06 Previous-period comparison | BO-03 | US-01, US-02 | Date dimension and measures | Functional test FT-01 | Planned |
| FR-07 Configurable customer risk | BO-04 | US-06 | Rules configuration and risk view | Rule tests UT-01–UT-06 | Planned |
| FR-08 3× preceding 90-day indicator | BO-04 | US-03, US-06 | SQL window calculation | Boundary test UT-07 | Planned |
| FR-09 Six report views | BO-03–BO-05 | US-01–US-08 | Power BI report | UAT scenarios UAT-01–08 | Planned |
| FR-10 Filters and drill-down | BO-04 | US-01–US-06 | Report navigation and filters | Functional test FT-02 | Planned |
| FR-11 Account masking | BO-05 | US-07 | Masked account field | Security test ST-01 | Planned |
| FR-12 Role restrictions | BO-05 | US-01, US-02, US-07 | Power BI roles and secured views | Security tests ST-02–ST-05 | Planned |
| FR-13 Pipeline and quality summaries | BO-01–BO-03 | US-08 | Audit schema and quality report | Integration test IT-02 | Planned |
| FR-14 Controlled CSV/PDF exports | BO-05 | US-07 | Report export configuration | Security test ST-06 | Planned |

## Nonfunctional Traceability

| Requirement | Target | Verification | Status |
|---|---|---|---|
| NFR-01 Daily readiness | By 6:00 a.m. CT in at least 95% of simulated runs | Timed scheduled-run test PT-01 | Planned |
| NFR-02 Completeness | At least 98% required-field completeness | Quality calculation DQ-04 | Planned |
| NFR-03 Accuracy | Zero unexplained KPI variance | SQL-to-dashboard reconciliation RC-01 | Planned |
| NFR-04 Dashboard response | Summary ≤5 sec; drill-down ≤10 sec | Power BI Performance Analyzer PT-02 | Planned |
| NFR-05 Export response | ≤30 sec | Export timing PT-03 | Planned |
| NFR-06 Capacity design | 100 concurrent-user assumption documented | Architecture review AR-01 | Planned |
| NFR-07 Auditability | Runs, exceptions, and exports traceable | Audit completeness test ST-07 | Planned |
| NFR-08 Retention | 24-month analytics; 7-year audit design | Data lifecycle review AR-02 | Planned |
| NFR-09 Maintainability | Configurable rules and mappings | Configuration-change test MT-01 | Planned |

## Business Objective IDs

| ID | Objective |
|---|---|
| BO-01 | Reduce manual reporting and consolidation effort |
| BO-02 | Make validated data available daily by 6:00 a.m. CT |
| BO-03 | Establish consistent KPI definitions and calculations |
| BO-04 | Provide unified operational and customer-risk analysis |
| BO-05 | Protect sensitive information through controlled reporting |
| BO-06 | Enable timely management action and investigation |

## Traceability Control Rules

1. No Must requirement may be removed without approved change control.
2. Every implemented requirement must link to at least one test.
3. A requirement remains open until its tests pass and evidence is recorded.
4. Changes to formulas must update the KPI dictionary, SQL logic, Power BI measures, and reconciliation tests.
5. Changes to security must be reviewed by Compliance before release.

