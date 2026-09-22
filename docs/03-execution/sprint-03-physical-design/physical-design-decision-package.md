# Sprint 3 Physical Design Decision Package — PD-01 through PD-07

Prepared 2026-09-21. Current status: **PD-01 through PD-07 Approved — Design Rule; physical annexes Pending confirmation**. The requesting user's 2026-09-21 instruction approved the seven rules recorded below, without approving literal headers, identifiers, mappings, examples, runtime mechanisms or database work. This package originated as a draft framing seven open physical decisions from the [contract reconciliation](contract-reconciliation.md); the detailed questions and unresolved-evidence sections remain useful review history. `PD-02` here is a **decision ID** about schema versions, not authorization for the separately named PD02 database work package. Sprint 3, database execution, fixture generation and publication remain unapproved. See the [decision approval/control record](../../04-monitoring-and-control/sprint-03-pd01-pd07-design-rule-approval.md).

Design-rule approver: the requesting user, by explicit 2026-09-21 instruction. Exact source-annex review owners and evidence remain **Pending confirmation**. Source-owner and Data Owner titles in the G3 documents are simulated review personas, not evidence of completed review. A choice that changes approved grain, formulas, security, retention or source semantics requires the G3 change-control process, not a physical implementation shortcut.

## Approved design rules — scope of this decision only

| ID | Approved — Design Rule | Still Pending confirmation |
| --- | --- | --- |
| PD-01 | Explicit ordered, case-sensitive received-header mappings per `(source, section, schema_version)`; never infer physical CSV headers from every logical field. | Exact 27-section header annexes |
| PD-02 | Independent immutable schema IDs per section; changed header, mapped meaning, type or applicability requires a new ID. Schema version, batch revision, mapping version and source-state version remain separate. | Literal IDs and transition/compatibility records |
| PD-03 | UTF-8 `manifest.json` package with relative `sections/<SRC-ID>/<section>.csv` payloads and exact-byte SHA-256 binding. | Final JSON schema/vocabulary and zero-row/one-row examples |
| PD-04 | Versioned per-field received/generated/resolved/derived disposition and explicit always/optional/conditional applicability; unresolved applicability fails the applicable gate. | Complete predicates and denominator/applicability rules |
| PD-05 | Explicit versioned source/field/currency/status/population financial-control matrix; signed decimal(28,4) totals or explicit unavailable reasons, with exact reconciliation. | Complete matrix and worked examples |
| PD-06 | Explicit versioned raw-to-canonical tables with eligibility flags; preserve raw values and exact applied mapping-version lineage. | Final mapping rows and literal mapping-version IDs |
| PD-07 | Verifiable IANA 2026a evidence for America/Chicago; DST-aware calendar boundaries, supplied-offset checks and microsecond-precision processing. | Runtime/dependency verification mechanism |

The approved design rules are implementation constraints, not an accepted physical source contract. Required reviewed annexes remain absent, so intake must fail closed when a needed annex is unavailable. No Sprint 3 approval, PD02 authorization or G4 approval follows from these rules.

## Decision register

| ID | Decision | Status | Dependent implementation |
| --- | --- | --- | --- |
| PD-01 | Final physical CSV headers and aliases | Approved — Design Rule; annex pending | Populate reviewed source-field registry for all 27 sections |
| PD-02 | Physical schema-version identifiers and versioning convention | Approved — Design Rule; IDs pending | Bind manifests to reviewed schemas and manage corrections |
| PD-03 | Manifest serialization, package paths and encoding vocabulary | Approved — Design Rule; schema/vocabulary pending | Read and validate delivered packages |
| PD-04 | Conditional source-cell applicability rules | Approved — Design Rule; predicates pending | Apply complete required-cell and completeness checks |
| PD-05 | Financial-control representation and applicable populations | Approved — Design Rule; matrix pending | Execute exact signed reconciliation |
| PD-06 | Final status mappings and dictionary-version bindings | Approved — Design Rule; rows/IDs pending | Validate source codes before KPI/risk derivation |
| PD-07 | Timezone implementation and Chicago offset/DST verification | Approved — Design Rule; runtime mechanism pending | Verify instants, business days and temporal joins |

## PD-01 — Final physical CSV headers and aliases

**Exact unresolved question.** For each of the [27 mandatory sections](source-field-inventory.md), what is the ordered, case-sensitive physical CSV header; which supplied column maps to each approved logical source field; and which logical fields are generated, resolved or derived instead of received?

**Approved baseline requirements.** The [synthetic source contract](../sprint-02-data-design/synthetic-source-contract.md) names the five sources and section aliases, proposes field aliases equal to inventory names unless explicitly overridden, and distinguishes received from generated/resolved/derived fields. The [DD-07 field dictionary](../sprint-02-data-design/field-level-dictionary.md) alone defines logical types, requiredness, keys and meaning. [Synthetic field trace](../sprint-02-data-design/synthetic-contract-traceability.md) covers every logical field. G3 approves those logical contracts, not verified received headers.

**Implementation constraints.** Preserve source-qualified natural IDs, leading zeros, source lineage and separate generated keys. Do not require every logical `R` field in raw CSV: some are generated, resolved or control evidence. Reject duplicate/unreviewed received fields once the physical contract is selected. Header changes require a corresponding reviewed schema version.

**Derived implementation details.** `SectionContract` permits an exact header registry; the current test header (`source_system,entity_name,business_date,revision,source_id,amount`) is illustrative only. The proposed package path in [offline manifest contract](offline-manifest-contract.md) does not settle headers.

**Unresolved / decision evidence needed.** A section-by-section signed mapping with ordered headers, aliases, type/format, received-versus-derived disposition, key fields and example header bytes. Applicable synthetic source-owner and independent Data Owner review evidence: **Pending confirmation**. No production registry may be installed before selection.

## PD-02 — Physical schema-version identifiers and versioning convention

**Exact unresolved question.** What literal version ID identifies each of the 27 section schemas, what changes require a new ID, and how are accepted revisions and replay tied to that schema ID?

**Approved baseline requirements.** The [dictionary `source_extract` contract](../sprint-02-data-design/field-level-dictionary.md) requires `schema_version` as text(128) per source/entity/business-date/revision; `source_reference.source_version` is distinct source-state evidence. [DD-01 source definitions](../sprint-02-data-design/source-system-definitions.md) require manifest schema versions; the [synthetic contract](../sprint-02-data-design/synthetic-source-contract.md) distinguishes identical replay, conflicting same-revision bytes and corrected incremented revision. [DD-09](../sprint-02-data-design/data-quality-and-reconciliation.md) blocks conflicting content and unavailable required contract evidence.

**Implementation constraints.** Compare the manifest version to the exact reviewed schema for that section. Keep schema version, source-state version, mapping version and batch revision separate. Do not infer a schema version from a date, `v1` documentary title or the test-only `reviewed-v1` value. Preserve earlier accepted schema/revision evidence.

**Derived implementation details.** Exact-string registry matching and fail-closed unknown versions are current offline mechanisms. A version naming pattern or compatibility matrix has not been chosen.

**Unresolved / decision evidence needed.** A literal version ID per section, version-change rules (headers, type, requiredness, semantics), effective dates, compatibility/migration behavior and reviewer evidence: **Pending confirmation**. A single global version versus per-section versions also needs a selected policy.

## PD-03 — Manifest serialization, package paths and encoding vocabulary

**Exact unresolved question.** What exact bytes and directory/archive layout represent one daily manifest and its section payloads, and what values populate the required encoding, checksum-scope and delivery-mode fields?

**Approved baseline requirements.** [DD-01](../sprint-02-data-design/source-system-definitions.md) requires a manifest per source/entity/date/revision with modes, versions, counts, checksum and controls. The [synthetic contract](../sprint-02-data-design/synthetic-source-contract.md) specifies one logical manifest plus sections, UTF-8 without BOM, LF, comma/RFC-4180-style CSV, one header, empty cell for null, exact-byte SHA-256 including header/final LF and lowercase hex. The [dictionary](../sprint-02-data-design/field-level-dictionary.md) requires `extract_id`, cutoff/extraction instants, checksum algorithm/encoding, content encoding and checksum-scope reference. [DD-09](../sprint-02-data-design/data-quality-and-reconciliation.md) treats missing/corrupt/stale delivery as critical.

**Implementation constraints.** A zero-row section has an explicit manifest entry and header-only CSV. A missing section is never inferred empty. Package identity must bind exact payload bytes and all required manifest fields. No filesystem convention may change checksum coverage or source/entity/date/revision identity.

**Derived implementation details.** `manifest.json` plus `sections/SRC-xx/<entity>.csv` is a Sprint 3 proposal only. `intake.py` currently accepts caller-supplied objects/bytes and performs no package parsing.

**Unresolved / decision evidence needed.** Canonical manifest serialization/schema, ordering and duplicate-key behavior, path/transport/archive rules, exact vocabulary for `delivery_mode`, `checksum_encoding`, `content_encoding` and `checksum_scope_reference`, and cutoff/extraction timestamp representation: **Pending confirmation**. Approval should include a minimal zero-row and one-row package example with no customer data.

## PD-04 — Conditional source-cell applicability rules

**Exact unresolved question.** For each physical section, which cells are mandatory on every row, which are conditional on a stated status/operation, and which logical fields are never supplied because they are generated or resolved?

**Approved baseline requirements.** The [DD-07 dictionary](../sprint-02-data-design/field-level-dictionary.md) marks logical fields `R`, `O` or `C` with the applicable condition. The [synthetic contract](../sprint-02-data-design/synthetic-source-contract.md) requires optional fields to be null unless applicable and conditional fields to be populated exactly when applicable; it defines `record_operation`, source revision/history behavior and payment `posted_at` rules. [DD-09 DQ-D03/D10](../sprint-02-data-design/data-quality-and-reconciliation.md) requires valid required values and separate received/curated applicable-cell completeness, without treating unknown applicability as inapplicable.

**Implementation constraints.** Keep raw missing/blank, invalid nonblank, generated and inapplicable distinct. Evaluate condition predicates only from valid evidence. Preserve `POSTED`-only `posted_at` with `posted_at >= paid_at`; do not supply an invented posting instant. Unknown applicability cannot become a passing completeness denominator.

**Derived implementation details.** `FieldContract.required` handles unconditional test fields only. It does not represent DD-07 conditional predicates or distinguish received from generated fields; extending it awaits the selected per-section mapping.

**Unresolved / decision evidence needed.** A per-section, per-field applicability table with source field, predicate, null/empty behavior, source-versus-derived disposition and negative examples. Review of cross-field predicates and completeness denominators: **Pending confirmation**.

## PD-05 — Financial-control representation and applicable populations

**Exact unresolved question.** How are required signed financial control rows encoded in the physical manifest, and which monetary field, currency, status and population combinations must be present for each source/entity/date/revision?

**Approved baseline requirements.** [DD-09 RC-D01/D02](../sprint-02-data-design/data-quality-and-reconciliation.md) requires exact row and currency-separated signed financial reconciliation, with no unexplained residual or fabricated zero; received equals accepted plus quarantined plus approved excluded. The [dictionary `source_financial_control`](../sprint-02-data-design/field-level-dictionary.md) keys controls by source/entity/date/revision/amount field/currency/population and specifies decimal(28,4) control totals. The [synthetic contract](../sprint-02-data-design/synthetic-source-contract.md) specifies signed scale-4 decimal strings per field/currency/comparable status. [DD-11 policy](../sprint-02-data-design/loan-payment-and-schedule-policy.md) keeps gross payment/allocation/unapplied and adjustments distinct; [KPI mappings](../sprint-02-data-design/kpi-to-data-mappings.md) preserve stock versus flow grains.

**Implementation constraints.** No floating-point comparison, cross-currency netting, arbitrary tolerance, missing-as-zero or daily stock summation. Keep payment gross and adjustment/net controls separate. Nonmonetary sections still need exact row counts; whether a financial control is inapplicable must be explicit.

**Derived implementation details.** The [field inventory](source-field-inventory.md) lists logical decimal targets by section, but this does not establish a required raw manifest control for every displayed decimal. The current intake does not parse or reconcile financial controls.

**Unresolved / decision evidence needed.** Exact manifest control schema, complete applicable population matrix, treatment of explicit zero versus unavailable control, signed adjustment representation, status mapping used for comparability and worked exact-reconciliation examples: **Pending confirmation**.

## PD-06 — Final status mappings and dictionary-version bindings

**Exact unresolved question.** Which received raw codes map to each approved canonical status/reference domain, which mapping version applies to a section/date/revision, and how are unknown/unmapped values recorded?

**Approved baseline requirements.** The [synthetic contract](../sprint-02-data-design/synthetic-source-contract.md) proposes fictional raw domains and `IDENTITY_SYN_V1`, reserving `X_UNMAPPED` for negative fixtures. [DD-06 policy](../sprint-02-data-design/kpi-policy-dd06.md) fixes KPI/status populations, significant HIGH/CRITICAL severity, restricted states and complaint SLA treatment. The [risk catalog](../sprint-02-data-design/customer-risk-catalog.md) requires approved mappings before RC-02 through RC-05 can be evaluated. The [dictionary mapping_version/mapping_entry contracts](../sprint-02-data-design/field-level-dictionary.md) require versioned mapping evidence; [DD-09 DQ-D06](../sprint-02-data-design/data-quality-and-reconciliation.md) governs invalid/unavailable required mappings.

**Implementation constraints.** Preserve raw values and applied mapping version; never silently map unknown to a passing category. Keep `Unknown` risk evidence distinct from critical missing configuration. A mapping update cannot rewrite historical published interpretation without controlled correction/publication.

**Derived implementation details.** The synthetic identity map and proposed domain spellings are documentary fixture proposals, not verified physical source code lists or completed mapping reviews. The current intake only checks syntactic field formats when a registry is supplied.

**Unresolved / decision evidence needed.** Per-source/domain raw-to-canonical tables, literal mapping version IDs, eligibility flags, effective/retirement dates, invalid-code treatment and required simulated source-owner/Data Owner review evidence: **Pending confirmation**. Any semantic change to approved KPI/risk populations requires change control.

## PD-07 — Timezone implementation and America/Chicago offset/DST verification

**Exact unresolved question.** Which runtime timezone data and parser will implement the approved Chicago local-day/UTC(6) rules, and what verification evidence proves offset, fold, gap, midnight and cutoff behavior?

**Approved baseline requirements.** The [synthetic source contract](../sprint-02-data-design/synthetic-source-contract.md) specifies America/Chicago, IANA tzdb 2026a as the specification version, offset-qualified event instants, rejection of ambiguous/nonexistent local times, offset agreement with the zone, local-midnight business days, exclusive snapshot cutoffs and cutoff-minus-one-microsecond matching. [DD-03](../sprint-02-data-design/logical-data-model.md), [DD-11](../sprint-02-data-design/loan-payment-and-schedule-policy.md) and [DD-12](../sprint-02-data-design/historical-branch-attribution-policy.md) govern snapshot, due-date and attribution instants. [G3 prerequisite register](../sprint-02-data-design/g3-prerequisite-register.md) defers timezone dependency/version/boundary execution evidence.

**Implementation constraints.** Do not add a fixed 24 hours to derive Chicago next midnight; local days can be 23/25 hours. Do not accept a supplied offset inconsistent with Chicago at the instant, shift nonexistent times, guess an ambiguous fold, carry current state backward or round UTC microseconds. Due dates remain dates until the approved local-midnight lookup.

**Derived implementation details.** The current `instant` format parser checks offset-qualified syntax only and does not claim Chicago offset/fold or tzdb 2026a verification. A runtime library, pinned tzdb package and version-recording method have not been selected.

**Unresolved / decision evidence needed.** Chosen runtime/parser and pinned tzdb data source/version, upgrade policy, rules for supplied offset/fold evidence, and executable examples covering spring gap, fall fold, 23/25-hour days, due-date midnight, exclusive snapshot cutoff and microsecond boundary: **Pending confirmation**. Offline dependency inspection/testing needs separate scoped authorization if it installs software; PD02 database execution remains unauthorized.

## Approval record template

The seven design-rule selections and approval evidence are recorded above and in the dedicated control record. For each still-pending annex, record the exact selected values, date, requesting-user approval evidence, rationale, impact on G3 semantics, reviewer personas and evidence if simulated, affected section/schema versions, tests required, and superseded proposal text. Until that annex record exists, its values remain **Pending confirmation**. Design-rule approval does not approve Sprint 3, PD02 or G4.
