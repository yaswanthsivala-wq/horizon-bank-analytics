# Business Process Flows

## AS-IS: Current Manual Reporting Process

```mermaid
flowchart TD
    A["Departments export separate reports"] --> B["Files sent to Operations"]
    B --> C["Analyst manually combines spreadsheets"]
    C --> D{"Identifiers and totals match?"}
    D -- No --> E["Contact departments and reconcile"]
    E --> C
    D -- Yes --> F["Recalculate departmental KPIs"]
    F --> G["Prepare monthly management report"]
    G --> H["Managers review delayed results"]
```

### Current-State Problems

- Separate reports arrive on different schedules.
- Customer and account identifiers are inconsistent.
- Manual spreadsheet consolidation is error-prone.
- KPI formulas differ across departments.
- Reconciliation delays monthly reporting by approximately three business days.
- Managers cannot easily drill from summary results to the responsible branch or account.
- There is no combined customer-risk view.

## TO-BE: Release 1 Daily Analytics Process

```mermaid
flowchart TD
    A["Five daily synthetic extracts"] --> B["Automated ingestion"]
    B --> C["Validation and standardization"]
    C --> D{"Critical controls pass?"}
    D -- No --> E["Quarantine exceptions and stop publication"]
    E --> F["Data owner reviews quality report"]
    D -- Yes --> G["Load curated analytical model"]
    G --> H["Calculate KPIs and risk indicators"]
    H --> I["Reconcile counts and financial totals"]
    I --> J{"Reconciliation passes?"}
    J -- No --> E
    J -- Yes --> K["Publish role-based Power BI dataset"]
    K --> L["Users review and investigate"]
```

## Role-Based Navigation

```mermaid
flowchart TD
    A["Authenticated user"] --> B{"Authorized role"}
    B -- Executive --> C["Aggregated bank and region summary"]
    B -- Operations Manager --> D["Authorized region and branch detail"]
    B -- Analyst --> E["Customer and masked-account investigation"]
    B -- Administrator --> F["Pipeline and quality administration"]
```

## Risk-Assessment Flow

```mermaid
flowchart TD
    A["Validated customer activity"] --> B["Evaluate five configured conditions"]
    B --> C["Record condition evidence"]
    C --> D{"At least two conditions?"}
    D -- Yes --> E["Provisional high-risk flag"]
    D -- No --> F["Not high risk under current rule"]
    E --> G["Human analyst review"]
    F --> G
    G --> H["Document investigation outcome"]
```

The unusual-transaction rule compares a transaction with the customer's preceding 90-day average. It is one risk indicator and never confirms fraud automatically.

## Process Improvement Expected

| Area | AS-IS | TO-BE |
|---|---|---|
| Frequency | Monthly consolidated report | Validated daily dataset |
| Preparation | Manual spreadsheet work | Automated, controlled pipeline |
| KPI definitions | Department-specific | Central approved dictionary |
| Data quality | Discovered during reporting | Validated before publication |
| Investigation | Separate reports | Controlled drill-down |
| Customer risk | Fragmented | Explainable combined indicators |
| Security | File-dependent | Role-specific views and masking |

