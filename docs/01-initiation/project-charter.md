# Project charter

Project: **Horizon Community Bank — Banking Operations & Customer Risk Analytics**

Updated: 2026-09-14

Status: **Initiation approved**

## Confirmed project purpose

Build a realistic, portfolio-grade analytics solution for a fictional community bank to improve banking operations, customer-risk visibility, and management decision-making.

## Confirmed core business problems

- Siloed operational data and separate reports across Core Banking, Loan Operations, Fraud Operations, Customer Service/CRM, and Branch Administration.
- Conflicting KPI definitions and inconsistent monthly reports.
- Customer identity-reconciliation problems.
- No trusted unified operational and customer-risk view.
- Limited drill-down from branch to segment to customer.
- Manual, slow, error-prone reporting.
- Weak data lineage, ownership, and access controls.

## Confirmed business objectives

- Establish one trusted source of truth for operational and customer-risk KPIs.
- Reduce monthly reporting time from three business days to under four hours.
- Make validated daily data available by 6:00 a.m. Central Time.
- Standardize Release 1 KPI definitions and data lineage.
- Enable branch, segment, and customer-level drill-down.
- Create a unified view of customer, account, loan, fraud, complaint, and branch activity.
- Enable controlled investigations by authorized users.
- Protect sensitive fields through role-based visibility, masking, and export controls.

These are approved objectives and targets for the fictional scenario, not achieved outcomes or measured technical results.

## Confirmed Release 1 scope

- Synthetic Core Banking, Loan Servicing, Fraud Monitoring, CRM, and Branch Reference sources.
- Twenty-four months of historical data.
- Daily batch ingestion.
- PostgreSQL analytical database.
- Python ETL.
- Customer identity standardization.
- Reconciliation and data-quality exception reporting.
- Approved KPIs and prior-period comparisons.
- Configurable provisional customer-risk rules.
- Power BI reports with role-based pages, filters, and drill-downs.
- Restricted CSV and PDF exports.
- Documentation, testing evidence, recommendations, and GitHub portfolio materials.

## Confirmed exclusions

- Production banking connections or real customer data.
- Streaming or real-time processing.
- Hourly fraud-system integration.
- Predictive machine-learning fraud decisions.
- Automatic account blocking, loan decisions, or fraud decisions.
- Permanently approved enterprise-risk definitions.
- Quantified fraud-loss or delinquency-reduction commitments.
- Mobile application development.

## Approved assumptions

- One daily extract per source.
- Source-owner approval is represented through project governance.

These are confirmed elements of the approved delivery basis; no completed source-owner approvals or actual extracts are claimed.

## Approved constraints

- Use synthetic data only.
- Local Power BI Desktop, PostgreSQL, Python, Git, and GitHub.
- One-person portfolio delivery team.
- Six-week target schedule.
- No paid enterprise infrastructure.
- Demonstrate security through data design and Power BI role simulation.
- Validate the 6:00 a.m. target using simulated scheduled runs.
- Do not invent real stakeholder names. Use stakeholder roles and mark specific names as not applicable or pending.

## Approval evidence and lifecycle

| Record | Date | Evidence |
| --- | --- | --- |
| Approved Initiation baseline | 2026-09-09 | User supplied the approved purpose, problems, objectives, scope, exclusions, assumptions, and constraints recorded above. |
| Historical checkpoint | 2026-09-09 | Baseline corrections were preserved in local checkpoint commit `16fab131dabdf17d0b891919c1ce667f698cf46c`. |
| Planning approval | 2026-09-09 | Planning approved by the user; see the [Planning baseline](../02-planning/Horizon_Community_Bank_Project_Planning_Baseline.md). |
| Lifecycle confirmation | 2026-09-10 | Sprint 1 Business Analysis published and awaiting user approval; Sprint 2 Data Design and technical implementation not started, as confirmed by the user. |

## Documented definitions and pending decisions

The approved Planning baseline documents role definitions, requirements, KPI formulas, provisional risk conditions, masking and export requirements, the six-sprint schedule, testing expectations, and governance. Those definitions are confirmed baseline content, not absent information or achieved results.

Real-person assignments, actual source-owner review evidence, detailed design decisions not specified in Planning, executed validation evidence, and release acceptance remain **Pending confirmation**. Confirmed fictional role definitions do not establish real-person assignments or prove consultation. See the [stakeholder register](stakeholder-register.md).

## Progress and evidence limits

Planning was approved by the user September 9, 2026. Sprint 1 Business Analysis was approved by the user; required synchronization was verified September 14, 2026. Sprint 2 Data Design and technical implementation have not started. This approval covers BA documentation only; no implementation, test, KPI-achievement, UAT, or release-acceptance results are claimed.

Sprint 1 BA approval is recorded. Explicit authorization to start Sprint 2 remains pending. See [project status](../../PROJECT_STATUS.md).
