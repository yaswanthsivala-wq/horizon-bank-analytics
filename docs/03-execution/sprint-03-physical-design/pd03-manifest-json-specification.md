# PD-03 physical manifest JSON contract — v001

Status: **Approved — Physical manifest contract** (Project Owner review 2026-09-22). The Project Owner approved this Increment 1 JSON/package structure, vocabulary, exact-byte binding and structural examples. This approval does **not** approve PD-01 exact headers, activate the PD-02 candidate IDs, or resolve the separate PD-04 applicability, PD-05 financial-control populations, PD-06 mapping rows/IDs or PD-07 runtime mechanism. No example described here is a complete daily package or publication-ready. See the [Increment 1 approval record](../../04-monitoring-and-control/sprint-03-physical-contract-annex-1-approval.md).

## Package and JSON shape

One directory package for one Chicago business date contains exactly `manifest.json` and exactly one CSV at `sections/<SRC-ID>/<section>.csv` for each of the [27 mandatory sections](source-field-inventory.md). Both JSON and CSV are UTF-8 without BOM. The manifest is one JSON object; duplicate JSON keys, repeated extract identities or repeated paths are invalid. No archive or remote transport is selected by this local-package proposal. JSON object member order and insignificant JSON whitespace do not affect the section checksum; the manifest itself has no approved checksum contract. No additional payload file may silently join the package.

Approved top-level shape (types shown, not literal example values):

```json
{
  "manifest_version": "HCB.SYN.MANIFEST.v001",
  "business_date": "YYYY-MM-DD",
  "sections": [
    {
      "extract_id": "nonempty text <=128",
      "source_system": "SRC-01",
      "entity_name": "section alias",
      "business_date": "YYYY-MM-DD",
      "revision": 1,
      "delivery_mode": "FULL_STATE",
      "schema_version": "HCB.SYN.SRC-01.customers.v001",
      "cutoff_at": "YYYY-MM-DDTHH:MM:SS.ffffffZ",
      "extracted_at": "YYYY-MM-DDTHH:MM:SS.ffffffZ",
      "payload_path": "sections/SRC-01/customers.csv",
      "row_count": 0,
      "checksum_algorithm": "SHA-256",
      "checksum_encoding": "LOWERCASE_HEX",
      "checksum": "64 lowercase hexadecimal characters",
      "content_encoding": "UTF-8",
      "checksum_scope_reference": "CSV_EXACT_BYTES_V1",
      "mapping_version_references": [],
      "financial_control_references": []
    }
  ]
}
```

`sections` must contain exactly one entry for each `(source_system, entity_name)` in the mandatory inventory and no unexpected entry. Every entry's `business_date` equals the top-level date. The extract identity is `(source_system, entity_name, business_date, revision)`; `extract_id` is an opaque supplied batch identity, not a replacement key. `revision` is a JSON integer >=1 (Boolean is not an integer). `row_count` is a JSON integer in 0..2^63-1. Text bounds follow the [DD-07 dictionary](../sprint-02-data-design/field-level-dictionary.md): source/entity/mode <=50, schema/extract IDs <=128, checksum/scope metadata <= their inventory bounds. `schema_version` must select exactly one **approved**, exact `(source, section, version)` header annex; a reserved draft ID is rejected for acceptance. `cutoff_at`/`extracted_at` are UTC instants with exactly six fractional digits and `Z`; the approved Chicago date/cutoff rules still apply, while their runtime verification is PD-07.

## Approved manifest vocabulary and dependent placeholders

| Field | Approved manifest values / dependent rule | Authority and limit |
| --- | --- | --- |
| `manifest_version` | `HCB.SYN.MANIFEST.v001` | Approved physical JSON format ID, **not** a section schema or mapping version |
| `source_system` | `SRC-01`, `SRC-02`, `SRC-03`, `SRC-04`, `SRC-05` | G3 five-source contract |
| `entity_name` | Exact mandatory section alias under the named source | G3 synthetic contract; 27-section inventory |
| `delivery_mode` | `FULL_STATE`, `EFFECTIVE_HISTORY`, `DAILY_STATE`, `IMMUTABLE_EVENT` | Approved physical spelling for G3 mode categories; per-section assignment Pending confirmation |
| `checksum_algorithm` | `SHA-256` | DD-09/G3 |
| `checksum_encoding` | `LOWERCASE_HEX` | Approved literal spelling for G3 lowercase hexadecimal digest |
| `content_encoding` | `UTF-8` | G3 CSV convention; BOM forbidden |
| `checksum_scope_reference` | `CSV_EXACT_BYTES_V1` | Approved literal ID for exact delivered CSV bytes including header and final LF |
| `mapping_version_references` | Array of distinct nonempty version-reference strings; may be empty only as *unresolved evidence*, never proof mapping is inapplicable | PD-06 final bindings Pending confirmation |
| `financial_control_references` | Array of distinct nonempty control-reference strings; may be empty only as *unresolved evidence*, never proof controls are inapplicable | PD-05 matrix/representation Pending confirmation |

Unknown fields or vocabulary values fail structural validation. In particular, empty mapping/control arrays cannot produce a passing downstream mapping or reconciliation gate when that evidence is required. Their final referenced object schemas, applicability and authority remain PD-05/PD-06 work; this approved manifest contract records explicit placeholders only. Even structurally consistent examples are not accepted deliveries until all required source header/schema and downstream annex evidence is approved.

## Payload, path and checksum rules

- `payload_path` is exactly `sections/<entry.source_system>/<entry.entity_name>.csv`, with `/` separators. It is relative to the package root; reject absolute paths, drive/UNC paths, `.` or `..` segments, encoded separators, symlink escapes, duplicate paths, case-fold collisions and paths outside the package. File name aliases cannot be silently changed.
- Each CSV uses comma and RFC-4180-style quoting, UTF-8 without BOM, LF only, one nonempty unique header and a final LF. Empty cell means null; blank required business cells remain invalid under PD-04. A valid zero-row section still contains the approved header line plus final LF and has `row_count: 0`. Missing payload/manifest entry is not zero rows.
- SHA-256 covers **exact payload bytes**, including header, every line terminator and final LF. `checksum` is exactly 64 lowercase hex characters. Compare bytes before parsing or newline conversion. `row_count` counts data records, excluding the header, using strict CSV framing; a quoted embedded newline is not a new record.
- The manifest must bind each entry's source/section/date/revision, schema version and payload path to one exact byte stream. A prior accepted identity plus identical bytes is replay; changed bytes at the same identity/revision are a conflict even if an attacker supplies a matching new checksum. A controlled correction increments revision and preserves predecessor bytes, metadata and evidence. A new schema version is needed only for PD-02-defined contract changes, not every data correction. A manifest with missing, corrupt, stale or conflicting required evidence fails closed under DD-09.

## Structural examples and acceptance limit

[One-row example](pd03-manifest-normal-example.md) and [valid zero-row example](pd03-manifest-zero-row-example.md) are **approved structural examples** with byte-matched section-entry excerpts. Each uses an unapproved `alerts` header and inactive candidate schema ID and omits the other 26 mandatory entries; neither is a valid complete daily package. They demonstrate JSON/CSV/checksum and missing-versus-zero behavior only. Neither approves the PD-01 header, activates the PD-02 ID, resolves PD-05/PD-06 applicability, or authorizes publication or data generation.
