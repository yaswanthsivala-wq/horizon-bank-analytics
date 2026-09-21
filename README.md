# Horizon Community Bank

Current Sprint 2 decision status (2026-09-17): DD-01 through DD-12 and G3 logical Data Design approved. Physical design, generation and implementation require separate authorization.

## Banking Operations & Customer Risk Analytics

This repository is the permanent source of truth for a fictional, synthetic-data portfolio project covering the full Data Analyst and Business Analyst lifecycle. It documents requirements, process analysis, data design, engineering, SQL analysis, Power BI reporting, testing, monitoring, and closure without using real bank or customer data.

## Current status

Initiation is approved. Planning was approved by the user September 9, 2026. Sprint 1 Business Analysis was approved by the user; required synchronization was verified September 14, 2026. Sprint 2 logical Data Design and Gate G3 were approved by the user September 17, 2026 under the synthetic-project scope. Technical implementation has not started.

- [Project status](PROJECT_STATUS.md)
- [Planning baseline](docs/02-planning/Horizon_Community_Bank_Project_Planning_Baseline.md)
- [Sprint 01 business analysis](docs/03-execution/sprint-01-business-analysis/README.md)
- [Sprint 02 data design](docs/03-execution/sprint-02-data-design/README.md)
- [Changelog](CHANGELOG.md)

## Project lifecycle

| Phase | Location | Status |
| --- | --- | --- |
| Initiation | [01-initiation](docs/01-initiation/README.md) | Approved; baseline documentation corrected |
| Planning | [02-planning](docs/02-planning/README.md) | Approved September 9, 2026; baseline published |
| Execution | [03-execution](docs/03-execution/README.md) | Sprint 1 BA approved; synchronization verified September 14, 2026; Sprint 2 logical design and G3 approved September 17, 2026; technical implementation not started |
| Monitoring and Control | [04-monitoring-and-control](docs/04-monitoring-and-control/README.md) | Sprint 1 evidence preserved; Sprint 2 controls recorded |
| Closure | [05-closure](docs/05-closure/README.md) | Not started |

## Approved business context

Build a realistic, portfolio-grade analytics solution for a fictional community bank to improve banking operations, customer-risk visibility, and management decision-making. The approved objectives include reducing monthly reporting from three business days to under four hours, validated daily data by 6:00 a.m. Central Time, one trusted KPI view, and controlled branch-to-customer drill-down. These are targets, not achieved results. See the [project charter](docs/01-initiation/project-charter.md) for the full baseline.

## Release 1 direction

Release 1 will integrate daily extracts from five simulated systems: Core Banking (customers, accounts, holders and transactions), Loan Servicing (loans, borrowers, daily positions and payments), Fraud Monitoring (fraud alerts), CRM (complaints), and Branch Reference (effective branch/region hierarchy), as defined in the [source-system definitions](docs/03-execution/sprint-02-data-design/source-system-definitions.md). The planned solution uses Python, PostgreSQL, SQL, and Power BI with data-quality controls, reconciliation, explainable risk indicators, masking, role-based reporting, and 24 months of synthetic history.

## Repository safeguards

- GitHub `main` and the local folder `C:\Users\yaswa\OneDrive\Desktop\horizon-bank-analytics` are the permanent source of truth.
- Preserve the approved Initiation business baseline; the authorized documentation correction records that baseline and reconciles lifecycle status.
- Real customer information, credentials, environment files, and generated data must not be committed.
- Risk indicators support human review and do not represent confirmed fraud or automated lending decisions.
- Sprint 1 approval and historical synchronization are recorded; the current user authorized Sprint 2 design documentation. G3 approval and further authorization are required before implementation. Request permission before any Git metadata write.

Read [AGENTS.md](AGENTS.md) before making changes.

## DD-11 documentation update - 2026-09-16

DD-01 through DD-12 approved; synthetic documentary prerequisites closed; G3 pending. DD-11 adds logical schedules, obligations, allocations, unapplied amounts, adjustment events and effective loan-account links while preserving snapshot/KPI authority. Required source availability and reviewed mappings remain unverified prerequisites; G3 and implementation remain unapproved. Earlier dated entries retain historical status.

## DD-12 documentation update - 2026-09-16

DD-01 through DD-12 approved; synthetic documentary prerequisites closed; G3 pending. Historical hierarchy/assignment and attribution policy separates historical report labels from current effective authorization. Required source contracts remain unverified; no implementation or G3 approval. Earlier dated records retain historical status.

## Synthetic G3 prerequisite closure - 2026-09-16

User-authorized fictional-project scope clarification replaces real-source verification with synthetic logical contracts, proposed aliases, deterministic temporal conventions and unexecuted scenario expectations. Documentary prerequisites are finalized; full consolidated Sprint 2 G3 approval remains pending. Physical confirmation, generation and all runtime/security/publication evidence remain post-G3 and require authorization. No real independent personnel or approvals are claimed.

## G3 logical design approval - 2026-09-17

The requesting user approved the complete consolidated Sprint 2 logical package. See [gate decision](docs/04-monitoring-and-control/g3-data-design-approval.md). This updates lifecycle status only: no real-source verification, production readiness, physical implementation, generated fixtures, executed reconciliation, implemented RLS/security, KPI achievement, UAT or publication readiness is claimed. All post-G3 work requires separate authorization; material design changes require change control. Dated prior statuses remain historical.

## Historical status (superseded)

Release 1 will integrate five simulated daily source extracts covering customers/accounts, transactions, loans/payments, fraud alerts, complaints, and branch reference data. The planned solution uses Python, PostgreSQL, SQL, and Power BI with data-quality controls, reconciliation, explainable risk indicators, masking, role-based reporting, and 24 months of synthetic history.
