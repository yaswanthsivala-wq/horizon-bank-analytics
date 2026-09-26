# Proposed offline manifest packaging contract - 2026-09-21

Status: **Draft — not approved**. This is a proposed physical representation of the approved Sprint 2/G3 [synthetic source contract](../sprint-02-data-design/synthetic-source-contract.md) and [source_extract inventory](../sprint-02-data-design/field-level-dictionary.md). It does not establish new business rules or assert a reviewed source schema.

The [reconciliation register](contract-reconciliation.md) and [section/field inventory](source-field-inventory.md) are the current authority classification for this proposal. Test-only headers and `reviewed-v1` are illustrative implementation details.

## Package shape

One logical delivery for business date `D` contains one manifest document and one CSV byte stream per source/entity section. A proposed portable directory layout is `manifest.json` plus `sections/SRC-01/<entity>.csv` through `sections/SRC-05/<entity>.csv`. Paths, archive format, transport, ordering, and naming are **Pending confirmation**; the validator currently accepts caller-supplied manifest objects and bytes and performs no filesystem discovery. A zero-row section still has a manifest entry and a header-only CSV. Missing sections are not zero-row sections.

The manifest contains an entry for each required section listed in `intake.REQUIRED_SECTIONS`. Each entry identifies `source_system`, `entity_name`, `business_date`, `revision`, `delivery_mode`, `schema_version`, `cutoff_at`, `extracted_at`, `checksum`, `row_count`, `checksum_algorithm`, `checksum_encoding`, `content_encoding`, and `checksum_scope_reference`, as required by `source_extract`. `extract_id` is the required batch identity. The physical JSON key layout, identifier generation and exact value vocabulary for delivery mode/encoding/scope are **Pending confirmation**. Financial-control entries remain required where the approved contract calls for them; their physical JSON shape and full reconciliation are **Pending confirmation**. No missing control is interpreted as zero.

CSV bytes follow the approved proposed UTF-8 without BOM, comma/RFC-4180-style quoting, LF and final LF contract. SHA-256 is over the exact section bytes including header and final LF and is represented as lowercase hexadecimal. Each manifest entry refers to one section identity `(source_system, entity_name, business_date, revision)`. A new correction increments revision; identical replay and conflicting bytes require persistent revision evidence in a later increment.

## Schema versions and fields

`schema_version` is a required nonblank text value of at most 128 characters for each section, distinct from source-state `source_version` and mapping version. The intake validator compares it for exact equality with the reviewed contract registered for that source/entity. A missing registry entry or mismatch fails validation. The literal version identifier and source-approved header list for every section are **Pending confirmation**; the `v1` label on the synthetic logical contract is documentary and is not silently promoted into a physical schema version.

The approved [field inventory](../sprint-02-data-design/field-level-dictionary.md) governs logical types, requiredness, limits and classifications. The synthetic contract proposes source section aliases and says field aliases equal inventory names unless specified, but it leaves physical aliases unconfirmed. A reviewed section registry must map received headers to those authoritative fields, specify types and required business cells, and document conditional applicability. The current validator accepts such an injected registry; it deliberately ships with no invented production registry. Tests use a small illustrative registry solely to prove the validator's behavior.

Supported checks for registered fields: exact header set, duplicate/missing/unexpected headers, nonblank required cells, text length, ISO calendar date, integer/revision/int64, exact decimal precision/scale, offset-qualified timestamp syntax, uppercase three-letter currency code, and optional row fields `source_system`, `entity_name`, `business_date`, and `revision` against the manifest. A passing result is limited to these syntactic checks. It does not establish currency membership, timezone/Chicago offset correctness, conditional requiredness, reference integrity, source-state version, complete DD-07 type coverage, financial reconciliation, freshness, replay, or publication eligibility.

## Pending confirmations before fixture acceptance

- Physical package path/transport and machine-readable manifest serialization.
- Per-section schema-version identifiers and reviewed source header-to-inventory mappings for all five sources, including conditional fields and aliases.
- Exact delivery-mode, checksum-encoding, content-encoding and checksum-scope vocabulary; cutoff and extraction instant checks.
- Financial-control serialization and exact comparison populations; persistent revision/replay evidence.

No PostgreSQL connection, PD02 action, fixture generation, credential, remote service or publication is part of this increment.
