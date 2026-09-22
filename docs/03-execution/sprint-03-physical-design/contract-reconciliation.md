# Sprint 3 offline source-contract reconciliation - 2026-09-21

Status: **Draft — not approved**. The user authorized this reconciliation only; Sprint 3 and PD02 remain unapproved. No Sprint 1 or Sprint 2 approved artifact was edited.

## Authority inspected

- [G3 gate decision](../../04-monitoring-and-control/g3-data-design-approval.md) and [G3 closure validation](../sprint-02-data-design/g3-closure-validation.md): complete logical package approved; physical aliases and runtime evidence remain later work.
- [Synthetic source contract](../sprint-02-data-design/synthetic-source-contract.md), [source definitions](../sprint-02-data-design/source-system-definitions.md), [synthetic contract trace](../sprint-02-data-design/synthetic-contract-traceability.md), and [synthetic data specification](../sprint-02-data-design/synthetic-data-specification.md): mandatory sections, proposed alias/format, manifests, dates, revisions, domains and expected scenarios.
- [Authoritative field dictionary](../sprint-02-data-design/field-level-dictionary.md), [dictionary/mapping navigation](../sprint-02-data-design/data-dictionary-and-mappings.md), [logical model](../sprint-02-data-design/logical-data-model.md), and [data model](../sprint-02-data-design/data-model.md): logical source/staging/curated target grain, keys, fields, types, requiredness and derivations. No separate staging-layer, curated-layer, glossary or technical-assumption files exist; these topics are embedded in these artifacts and the G3 prerequisite register.
- [KPI mappings](../sprint-02-data-design/kpi-to-data-mappings.md), [DD-06 KPI/status policy](../sprint-02-data-design/kpi-policy-dd06.md), [risk catalog](../sprint-02-data-design/customer-risk-catalog.md), [quality/reconciliation controls](../sprint-02-data-design/data-quality-and-reconciliation.md), [design traceability](../sprint-02-data-design/design-traceability-and-review.md), [historical branch policy](../sprint-02-data-design/historical-branch-attribution-policy.md), [DD-11 payment policy](../sprint-02-data-design/loan-payment-and-schedule-policy.md), and [G3 prerequisite register](../sprint-02-data-design/g3-prerequisite-register.md): KPI/risk and validation context, control semantics, mapping dependencies and unresolved physical confirmation.

## Complete section/field inventory

[Source-field inventory](source-field-inventory.md) lists **27 mandatory sections** across SRC-01 through SRC-05 and **333 logical target field rows**. Every section has its source ID, section name, documented business identity/grain, relevant requirement/KPI/risk trace, applicable synthetic dictionary/status policy, monetary target fields, and each mapped logical target field's type, logical requiredness and meaning. Common manifest identity, date, revision, schema-version and control semantics are stated there. The inventory is rendered reproducibly by `scripts/reconcile_source_fields.py` from the unchanged authoritative dictionary. These 333 rows are not a claim that 333 cells are required in delivered CSV files.

## Classification register

Counts below are **decision/rule rows**, not the 333 logical field rows. Each row has one classification; no row is counted twice.

| ID | Classification | Reconciled item | Authority / outcome |
| --- | --- | --- | --- |
| A01 | APPROVED BASELINE | 27 required section identities; all five sources | Synthetic source contract, DD-01/DD-09 |
| A02 | APPROVED BASELINE | Manifest source/entity/business-date/revision identity; revision >=1 | Dictionary `source_extract`, DD-01 |
| A03 | APPROVED BASELINE | Exact row counts, zero-row manifests, identical replay versus revision conflict | Synthetic source contract, DD-09 DQ-D01/D02, RC-D01 |
| A04 | APPROVED BASELINE | Exact-byte SHA-256, lowercase hex, UTF-8 without BOM, LF/final LF and CSV framing | Synthetic source contract, DD-09 DQ-D01 |
| A05 | APPROVED BASELINE | Required per-section `schema_version` field, text(128), distinct from source-state version | Dictionary `source_extract`/`source_reference` |
| A06 | APPROVED BASELINE | Logical field types, limits, R/O/C status, meaning and generated/derived distinctions | DD-07 authoritative dictionary |
| A07 | APPROVED BASELINE | Chicago business date, cutoff, daily snapshots and temporal corrections | Synthetic source contract, DD-03/DD-12 |
| A08 | APPROVED BASELINE | Native-grain, currency/status-separated counts and financial controls | DD-09 RC-D01/D02; dictionary `source_financial_control` |
| A09 | APPROVED BASELINE | Status/reference mappings and KPI/risk dependencies | DD-04/05/06/11/12, KPI mappings, risk catalog |
| D01 | DERIVED IMPLEMENTATION DETAIL | Proposed `manifest.json` and `sections/SRC-xx/<entity>.csv` layout | Sprint 3 draft only; not a confirmed G3 path |
| D02 | DERIVED IMPLEMENTATION DETAIL | Python `SectionContract` injection and fail-closed missing-registry behavior | Local mechanism for enforcing reviewed mapping, not itself a source schema |
| D03 | DERIVED IMPLEMENTATION DETAIL | Current parser's subset of types/formats and optional row/manifest equality checks | Partial implementation of DD-07/contract; no complete domain, conditional or temporal validation claim |
| D04 | DERIVED IMPLEMENTATION DETAIL | Test-only `source_id`, `amount`, common header and `reviewed-v1` version | Illustrative fixture; **not approved source mappings or version IDs** |
| P01 | PENDING CONFIRMATION | Final physical headers and source-to-logical aliases for all 27 sections | Synthetic contract calls aliases proposed; G3 does not verify physical header |
| P02 | PENDING CONFIRMATION | Actual per-section schema-version identifiers and version evolution | `schema_version` field required, value not supplied |
| P03 | PENDING CONFIRMATION | Manifest serialization, package paths/transport and encoding/scope vocabulary | Logical manifest categories set; physical representation not designed at G3 |
| P04 | PENDING CONFIRMATION | Source-cell applicability of conditional R/O/C fields and generated/derived fields | Logical requiredness cannot be copied wholesale to raw headers |
| P05 | PENDING CONFIRMATION | Physical financial-control representation and approved comparable populations | Exact controls required, actual serialization/mapping not specified |
| P06 | PENDING CONFIRMATION | Final status/source aliases and mapping-version bindings | Synthetic domains proposed; review/mapping evidence needed for implementation |
| P07 | PENDING CONFIRMATION | Actual timezone-library version and full Chicago offset/fold validation | Contract specifies IANA 2026a and rejection behavior; runtime verification later |

**Count:** APPROVED BASELINE 9; DERIVED IMPLEMENTATION DETAIL 4; PENDING CONFIRMATION 7; CONFLICT 0. No conflict was found in the current test-only registry because it is not installed as a source contract. Installing it as production mappings would conflict with the G3 requirement to verify actual aliases and would be blocked.

## Implemented rule trace

| Validator rule | Baseline trace | Limit |
| --- | --- | --- |
| Required sections and explicit zero rows | DD-01; DD-09 DQ-D01/D10; synthetic source contract source table | No source delivery generated |
| Source/entity/date/revision manifest checks | Dictionary `source_extract`; DD-01; DD-09 DQ-D02 | No persistent replay registry |
| Byte checksum and CSV encoding/framing | Synthetic source contract encoding paragraph; DD-09 DQ-D01 | Caller supplies bytes/manifest; no physical package parser |
| Row count and unique header | DD-09 RC-D01; synthetic CSV contract | Header names require reviewed registry |
| Required `schema_version` and exact registry match | Dictionary `source_extract`; DD-07 versioned contract | Version identifier Pending confirmation |
| Registered field names, required cells and limited formats | DD-07 dictionary; DD-09 DQ-D03/D07/D09 | Registry is not populated from unconfirmed aliases; full conditions/domains not checked |
| Optional row/manifest identity agreement | DD-01 qualified identity; DD-09 DQ-D02 | Applies only when reviewed row schema includes those fields |

## Current implementation disposition

`intake.py` remains an offline validation engine. Its accepted test registry is illustrative only; there is **no production source-field registry**. A missing reviewed contract fails validation. The generic parser checks syntax for configured fields but cannot certify a full DD-07 logical entity, ISO currency membership, IANA Chicago offset/fold, conditional applicability, source lineage, financial reconciliation, or publication readiness. No code change is warranted until approved physical mappings are available; changing those checks now would invent a source schema or pretend incomplete evidence passed.

No PostgreSQL, PD02, credentials, generated full dataset, remote service, commit, push or merge was used. Checkpoint readiness is limited to this clearly marked draft reconciliation and offline engine, subject to review of the pending mapping decisions above.
