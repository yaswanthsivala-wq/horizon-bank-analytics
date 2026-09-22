# Sprint 3 physical design - WP-PD01

## Data Engineering start - 2026-09-21

The user authorized Sprint 3 Data Engineering and selected offline pipeline work first. [The intake increment](data-engineering-intake.md) implements and tests limited section presence and byte-level validation. Status: Draft — not approved. PD02 database execution remains Pending confirmation.

The [proposed offline manifest contract](offline-manifest-contract.md) records the physical package shape, schema-version rules and unresolved source mappings. The intake validator now accepts reviewed section field contracts and fails closed when one is missing.

The [contract reconciliation](contract-reconciliation.md) and [27-section field inventory](source-field-inventory.md) distinguish approved G3 logical fields from proposed physical aliases and illustrative tests. Sprint 3 remains a working draft.

The [PD-01 through PD-07 decision package](physical-design-decision-package.md) now records all seven as **Approved — Design Rule** by the requesting user on 2026-09-21. Their literal physical annexes remain **Pending confirmation**; see the [approval/control record](../../04-monitoring-and-control/sprint-03-pd01-pd07-design-rule-approval.md). Sprint 3 is started but not approved; PD02 database work is unauthorized. No missing annex may be assumed to pass intake.

Authorized by requesting user 2026-09-17: physical-design documentation and foundation SQL for static review only. G3 remains approved. PD02 and all executable work require separate authorization. Status: PD01 authored, static validation recorded separately; no database inspection/execution, dependencies installed, fixtures or runtime results.

## Artifact inventory

- [Architecture](physical-architecture.md)
- [109-entity/982-field mapping](logical-to-physical-map.md)
- [Constraints and typed references](constraint-matrix.md)
- [Versions and publication](versioning-and-publication.md)
- [Indexes and partitions](indexing-and-partitioning.md)
- [Security enforcement](security-enforcement.md)
- [Lifecycle execution](lifecycle-execution.md)
- [Safe cleanup](development-cleanup.md)
- [Foundation SQL](../../../sql/migrations/0001_foundation.sql)
- [Static validation](static-validation.md)

Approved input: [G3 decision](../../04-monitoring-and-control/g3-data-design-approval.md), [authoritative inventory](../sprint-02-data-design/field-level-dictionary.md), [synthetic contract](../sprint-02-data-design/synthetic-source-contract.md) and all DD-01 through DD-12. No logical decisions reopened or changed. Physical helpers are proposed representations, not new logical banking entities.

## PD02 prerequisites

Separate explicit user authorization must specify permitted local environment inspection, database target/bootstrap credential mechanism, dependency/extension installation if needed, SQL execution, disposable test scope and cleanup. Inspect installed PostgreSQL version only then; proposed target is PostgreSQL 18, not confirmed installed. Review role/schema name collisions and required bootstrap privileges. Pin driver/test/timezone dependencies and decide exact authorized next migration scope. Complete target-specific typed binding schemas and semantic triggers before loading their referencing records. Foundation SQL alone does not implement business integrity, RLS or publication.

Next lifecycle gate remains G4 Analytics Validation; neither PD01 nor a successful migration approves it.
