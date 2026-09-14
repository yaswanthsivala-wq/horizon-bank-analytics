# Horizon Community Bank

## Banking Operations & Customer Risk Analytics

This repository is the permanent source of truth for a fictional, synthetic-data portfolio project covering the full Data Analyst and Business Analyst lifecycle. It documents requirements, process analysis, data design, engineering, SQL analysis, Power BI reporting, testing, monitoring, and closure without using real bank or customer data.

## Current status

Initiation is approved. Planning was approved by the user September 9, 2026. Sprint 1 Business Analysis was approved by the user; required synchronization was verified September 14, 2026. Sprint 2 Data Design and technical implementation have not started.

- [Project status](PROJECT_STATUS.md)
- [Planning baseline](docs/02-planning/Horizon_Community_Bank_Project_Planning_Baseline.md)
- [Sprint 01 business analysis](docs/03-execution/sprint-01-business-analysis/README.md)
- [Changelog](CHANGELOG.md)

## Project lifecycle

| Phase | Location | Status |
| --- | --- | --- |
| Initiation | [01-initiation](docs/01-initiation/README.md) | Approved; baseline documentation corrected |
| Planning | [02-planning](docs/02-planning/README.md) | Approved September 9, 2026; baseline published |
| Execution | [03-execution](docs/03-execution/README.md) | Sprint 1 BA approved; synchronization verified September 14, 2026; Sprint 2 Data Design and technical implementation not started |
| Monitoring and Control | [04-monitoring-and-control](docs/04-monitoring-and-control/README.md) | Sprint 1 BA approval and synchronization evidence recorded |
| Closure | [05-closure](docs/05-closure/README.md) | Not started |

## Approved business context

Build a realistic, portfolio-grade analytics solution for a fictional community bank to improve banking operations, customer-risk visibility, and management decision-making. The approved objectives include reducing monthly reporting from three business days to under four hours, validated daily data by 6:00 a.m. Central Time, one trusted KPI view, and controlled branch-to-customer drill-down. These are targets, not achieved results. See the [project charter](docs/01-initiation/project-charter.md) for the full baseline.

## Release 1 direction

Release 1 will integrate five simulated daily source extracts covering customers/accounts, transactions, loans/payments, fraud alerts, complaints, and branch reference data. The planned solution uses Python, PostgreSQL, SQL, and Power BI with data-quality controls, reconciliation, explainable risk indicators, masking, role-based reporting, and 24 months of synthetic history.

## Repository safeguards

- GitHub `main` and the local folder `C:\Users\yaswa\OneDrive\Desktop\horizon-bank-analytics` are the permanent source of truth.
- Preserve the approved Initiation business baseline; the authorized documentation correction records that baseline and reconciles lifecycle status.
- Real customer information, credentials, environment files, and generated data must not be committed.
- Risk indicators support human review and do not represent confirmed fraud or automated lending decisions.
- Sprint 2 must not begin until Sprint 1 is committed, pushed, pulled locally, verified, and approved by the user.

Read [AGENTS.md](AGENTS.md) before making changes.
