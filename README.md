# Horizon Community Bank

## Banking Operations & Customer Risk Analytics

This repository is the permanent source of truth for a fictional, synthetic-data portfolio project covering the full Data Analyst and Business Analyst lifecycle. It documents requirements, process analysis, data design, engineering, SQL analysis, Power BI reporting, testing, monitoring, and closure without using real bank or customer data.

## Current status

Initiation and Planning are approved. Execution Sprint 1 business-analysis artifacts have been published and await synchronization and verification in the permanent local VS Code repository. Sprint 2 has not started.

- [Project status](PROJECT_STATUS.md)
- [Planning baseline](docs/02-planning/Horizon_Community_Bank_Project_Planning_Baseline.md)
- [Sprint 01 business analysis](docs/03-execution/sprint-01-business-analysis/README.md)
- [Changelog](CHANGELOG.md)

## Project lifecycle

| Phase | Location | Status |
| --- | --- | --- |
| Initiation | [01-initiation](docs/01-initiation/README.md) | Approved; existing files preserved |
| Planning | [02-planning](docs/02-planning/README.md) | Approved; baseline published |
| Execution | [03-execution](docs/03-execution/README.md) | Sprint 1 BA published; local verification pending |
| Monitoring and Control | [04-monitoring-and-control](docs/04-monitoring-and-control/README.md) | Tracking structure prepared |
| Closure | [05-closure](docs/05-closure/README.md) | Not started |

## Release 1 direction

Release 1 will integrate five simulated daily source extracts covering customers/accounts, transactions, loans/payments, fraud alerts, complaints, and branch reference data. The planned solution uses Python, PostgreSQL, SQL, and Power BI with data-quality controls, reconciliation, explainable risk indicators, masking, role-based reporting, and 24 months of synthetic history.

## Repository safeguards

- GitHub `main` and the local folder `C:\Users\yaswa\OneDrive\Desktop\horizon-bank-analytics` are the permanent source of truth.
- Existing Initiation documentation must be preserved.
- Real customer information, credentials, environment files, and generated data must not be committed.
- Risk indicators support human review and do not represent confirmed fraud or automated lending decisions.
- Sprint 2 must not begin until Sprint 1 is committed, pushed, pulled locally, and verified.

Read [AGENTS.md](AGENTS.md) before making changes.
