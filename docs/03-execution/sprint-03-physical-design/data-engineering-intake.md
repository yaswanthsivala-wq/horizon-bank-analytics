# Sprint 3 offline intake increment - 2026-09-21

Status: Draft — not approved. The requesting user authorized starting Sprint 3 Data Engineering and selected offline pipeline work first. This increment does not authorize PD02 database work.

## Implemented

- `src/horizon_pipeline/intake.py` accepts a caller-supplied section manifest and exact CSV bytes. Manifest packaging and physical paths remain Pending confirmation.
- For one business date, it checks presence of all required sections across SRC-01 through SRC-05, manifest identity/date/revision/count, lowercase SHA-256 over exact bytes, UTF-8 without BOM, LF with final LF, one nonempty unique header, CSV row widths and row count. A manifest-confirmed zero-row section is present, not missing.
- It returns findings without storing source rows, accessing a database, or publishing data. The mandatory section list follows the approved synthetic source contract; optional payment-transaction and alert-branch evidence is not required here.

## Validation and limits

Four standard-library unit tests passed for valid zero-row sections, missing mandatory section, changed content and BOM/CRLF. `git diff --check` passed. This proves only the tested offline intake controls. Header names/types, required business cells, financial controls, freshness, replay history, corrections, reconciliation, security, lineage and atomic publication are not implemented or tested. No generated data, database object, dependency, credential or remote service was used.

## Controlled continuation - 2026-09-21

Added the [proposed package contract](offline-manifest-contract.md), a required per-section schema-version comparison, and injected field-contract validation for headers, supported types/formats, required cells and row/manifest identity. No production header registry is installed because physical aliases and version identifiers remain Pending confirmation under G3. Illustrative test contracts are test-only; they are not source approval. Eleven unit tests now cover valid/invalid scenarios. Historical four-test result above describes the first increment.

Next: obtain reviewed source/header/version mappings, then register all required sections and add controlled revision/replay evidence. PD02 still needs its separately specified disposable target, bootstrap method and action scope.

## Contract reconciliation - 2026-09-21

[Reconciliation](contract-reconciliation.md) inspected the approved G3 source, dictionary, model, KPI, risk, quality and traceability artifacts. [The field inventory](source-field-inventory.md) covers all 27 mandatory sections and 333 logical target field rows without treating them as verified CSV cells. The illustrative test registry remains test-only; no source-field registry was installed. No implementation change was justified by confirmed physical mappings in this increment.
