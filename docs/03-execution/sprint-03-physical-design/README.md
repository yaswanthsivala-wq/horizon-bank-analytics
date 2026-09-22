# Sprint 3 physical design - WP-PD01

## Data Engineering start - 2026-09-21

The user authorized Sprint 3 Data Engineering and selected offline pipeline work first. [The intake increment](data-engineering-intake.md) implements and tests limited section presence and byte-level validation. Status: Draft — not approved. PD02 database execution remains Pending confirmation.

The [proposed offline manifest contract](offline-manifest-contract.md) records the physical package shape, schema-version rules and unresolved source mappings. The intake validator now accepts reviewed section field contracts and fails closed when one is missing.

The [contract reconciliation](contract-reconciliation.md) and [27-section field inventory](source-field-inventory.md) distinguish approved G3 logical fields from proposed physical aliases and illustrative tests. Sprint 3 remains a working draft.

The [PD-01 through PD-07 decision package](physical-design-decision-package.md) now records all seven as **Approved — Design Rule** by the requesting user on 2026-09-21. Their literal physical annexes remain **Pending confirmation**; see the [approval/control record](../../04-monitoring-and-control/sprint-03-pd01-pd07-design-rule-approval.md). Sprint 3 is started but not approved; PD02 database work is unauthorized. No missing annex may be assumed to pass intake.

### Physical Contract Annex Increment 1 — 2026-09-22

Project Owner reviewed Increment 1 on 2026-09-22; see [approval record](../../04-monitoring-and-control/sprint-03-physical-contract-annex-1-approval.md). [PD-01 header annex](pd01-physical-header-annex.md): **Approved structure — Physical header values pending confirmation** for all 27 sections; unresolved headers fail closed. [PD-02 version annex](pd02-schema-version-annex.md): **Approved convention — Activation pending approved physical header contract**; 27 initial candidate IDs remain inactive. [PD-03 manifest specification](pd03-manifest-json-specification.md): **Approved — Physical manifest contract**, with [one-row](pd03-manifest-normal-example.md) and [zero-row](pd03-manifest-zero-row-example.md) approved structural examples only. [Cross-contract dependency model](pd01-pd03-cross-contract-validation.md) is approved; static evidence and limits remain. PD-04 through PD-07 annex values remain separate pending work; no Python, SQL or dataset implementation occurred. Sprint 3 remains in progress and not approved; PD02 database work remains unauthorized.

### Physical Contract Annex Increment 2 — PD-04

The [conditional applicability annex](pd04-conditional-applicability-annex.md) is **Approved framework — Physical predicates pending confirmation** after Project Owner review on 2026-09-22. It defines predicate governance and cell/completeness semantics, with 51 logical C-field candidates across 22 sections. No physical predicate is active because PD-01 received headers remain unresolved; dependent required validation fails closed. [Approval/control record](../../04-monitoring-and-control/sprint-03-pd04-annex-control.md). At that review, PD-05 through PD-07 annexes had not started; Sprint 3 was not approved and PD02/PostgreSQL was unauthorized.

### Physical Contract Annex Increment 3 — PD-05 through PD-07

[PD-05 financial controls](pd05-financial-control-annex.md): **Approved framework — Physical financial controls pending confirmation**. [PD-06 mappings](pd06-status-mapping-annex.md): **Approved framework — Physical mapping rows and mapping-version IDs pending confirmation**. [PD-07 Chicago runtime](pd07-chicago-time-runtime-annex.md): **Approved specification — Runtime/tzdb verification and executable boundary evidence pending confirmation**. The [cross-contract review](pd05-pd07-cross-contract-validation.md) is an **Approved documentary consistency model — Runtime dependencies remain fail closed**; the 13-row [master pending register](physical-contract-pending-register.md) is an **Approved control register — Open items remain unresolved**. [Project Owner review record](../../04-monitoring-and-control/sprint-03-physical-contract-annex-3-control.md). Seven financial candidates, 23 mapping groups and 15 future executable temporal cases are documented; zero physical control/mapping/predicate rows or timezone runtimes are active. Sprint 3 remains not approved and PD02/PostgreSQL unauthorized.

### Executable Implementation Package 1 — 2026-09-22

The offline contract engine and synthetic banking data foundation are implemented and validated locally under local authorization; see [implementation record](executable-implementation-package-01.md) and [control record](../../04-monitoring-and-control/sprint-03-executable-package-01-control.md). Status: **Sprint 3 Executable Implementation Package 1 — Implemented locally — Pending Project Owner Review**. Implements the contract state model, PD-03 manifest validation, PD-01 header registry, PD-02 schema registry, PD-04 applicability engine, PD-06 status mapping engine, PD-07 Chicago temporal engine with tzdb proof interface, PD-05 exact-decimal financial control engine, and standard-library synthetic banking data generator. All 27 production physical headers, 27 production schemas, 51 candidate predicates, 7 candidate financial controls, 23 domain mapping groups, and runtime tzdb 2026a verification remain PENDING and fail closed; 85 unit tests pass (including 11 original intake baseline tests and 15 PD-07 temporal cases); baseline inventory remains 27 sections / 333 logical target field rows. Sprint 3 remains in progress and not approved; PD02/PostgreSQL remains unauthorized.

Authorized by requesting user 2026-09-17: physical-design documentation and foundation SQL for static review only. G3 remains approved. PD02 and all executable work require separate authorization. Status: PD01 authored, static validation recorded separately; no database inspection/execution, dependencies installed, fixtures or runtime results.

## Artifact inventory

- [Executable Implementation Package 1 Record](executable-implementation-package-01.md)
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
