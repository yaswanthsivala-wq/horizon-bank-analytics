# Horizon Community Bank

## Current status — 2026-09-25

Sprint 3 offline implementation scope formally approved and closed on September 25, 2026 (/approve sprint-3-closure) based on the published Sprint 3 retrospective and overall closure review. Implements offline contract engine, curated processing pipeline, risk conditions RC-01..05, customer risk classification, core banking KPIs K01–K10, four dimensional analytical marts, and offline orchestration runner in pure fixture mode. Full regression passes 236 tests and 36 subtests across 34 test modules; 27 sections / 333 rows invariant; 0 broken links. Physical production contracts PD-01 through PD-07 remain pending fail-closed; PostgreSQL / PD02 remains unauthorized.

- [Sprint 3 closure approval](docs/04-monitoring-and-control/sprint-03-closure-approval.md)
- [Sprint 3 retrospective](docs/04-monitoring-and-control/sprint-03-retrospective.md)
- [Sprint 3 physical design and pipeline](docs/03-execution/sprint-03-physical-design/README.md)
- [CR-002 project-owner decisions](docs/04-monitoring-and-control/change-control/CR-002-project-owner-decisions-2026-09-21.md)
- [Project status](PROJECT_STATUS.md)
- [Planning baseline](docs/02-planning/Horizon_Community_Bank_Project_Planning_Baseline.md)
- [Sprint 01 business analysis](docs/03-execution/sprint-01-business-analysis/README.md)
- [Sprint 02 data design](docs/03-execution/sprint-02-data-design/README.md)
- [Changelog](CHANGELOG.md)

## Banking Operations & Customer Risk Analytics

This repository is the permanent source of truth for a fictional, synthetic-data portfolio project covering the full Data Analyst and Business Analyst lifecycle. It documents requirements, process analysis, data design, engineering, SQL analysis, Power BI reporting, testing, monitoring, and closure without using real bank or customer data.

## Project lifecycle

| Phase | Location | Status |
| --- | --- | --- |
| Initiation | [01-initiation](docs/01-initiation/README.md) | Approved; baseline documentation corrected |
| Planning | [02-planning](docs/02-planning/README.md) | Approved September 9, 2026; baseline published |
| Execution | [03-execution](docs/03-execution/README.md) | Sprint 1 BA approved; synchronization verified September 14, 2026; Sprint 2 logical design and G3 approved September 17, 2026; R1, CR-002 and WP-PD01 reconciled; Sprint 3 offline scope approved and closed September 25, 2026 (WP-PD01, Packages 1–3, 236 passed tests + 36 subtests across 34 test modules); physical contracts PD-01..07 pending fail-closed; PD02 unauthorized |
| Monitoring and Control | [04-monitoring-and-control](docs/04-monitoring-and-control/README.md) | Sprint 1 evidence preserved; Sprint 2 controls recorded; CR-002 decisions recorded; Sprint 3 package controls and closure approval record published |
| Closure | [05-closure](docs/05-closure/README.md) | Not started |

## Approved business context

Build a realistic, portfolio-grade analytics solution for a fictional community bank to improve banking operations, customer-risk visibility, and management decision-making. The approved objectives include reducing monthly reporting from three business days to under four hours, validated daily data by 6:00 a.m. Central Time, one trusted KPI view, and controlled branch-to-customer drill-down. These are targets, not achieved results. See the [project charter](docs/01-initiation/project-charter.md) for the full baseline.

## Release 1 direction

Release 1 will integrate daily extracts from five simulated systems: Core Banking (customers, accounts, holders and transactions), Loan Servicing (loans, borrowers, daily positions and payments), Fraud Monitoring (fraud alerts), CRM (complaints), and Branch Reference (effective branch/region hierarchy), as defined in the [source-system definitions](docs/03-execution/sprint-02-data-design/source-system-definitions.md). The planned solution uses Python, PostgreSQL, SQL, and Power BI with data-quality controls, reconciliation, explainable risk indicators, masking, role-based reporting, and 24 months of synthetic history.

## Repository safeguards

- GitHub main and the local folder C:\Users\yaswa\OneDrive\Desktop\horizon-bank-analytics are the permanent source of truth.
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

## WP-PD01 authorized delivery - 2026-09-17

G3 remains approved. The user authorized only physical-design documentation and foundation SQL authorship/static review. WP-PD01 documents all 109 logical entities/982 fields and proposed enforcement; no database inspection or execution, dependency installation, fixtures or runtime tests. PD02 and all executable work require separate authorization. Earlier statements that no physical design was authorized are historical to G3 approval. No approved business semantics changed.

[WP-PD01 package](docs/03-execution/sprint-03-physical-design/README.md).
