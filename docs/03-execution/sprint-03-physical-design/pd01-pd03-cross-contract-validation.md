# PD-01–PD-03 cross-contract validation — Increment 1

Status: **Dependency model approved; static evidence retained** (Project Owner review 2026-09-22). This is static documentation evidence, not implementation, approved received headers, executed intake, financial reconciliation or publication readiness. The [header annex](pd01-physical-header-annex.md) has approved structure but pending values; the [schema-version annex](pd02-schema-version-annex.md) has an approved convention but inactive candidate IDs; the [manifest specification](pd03-manifest-json-specification.md) is approved subject to unresolved downstream annex dependencies.

| Cross-contract assertion | Static result | Limitation / fail-closed disposition |
| --- | --- | --- |
| Mandatory section coverage | 27 PD-01 rows and 27 distinct PD-02 proposed IDs correspond to the 27 G3 sections | All 27 exact received headers remain Pending confirmation; none can be accepted |
| PD-01 header → exactly one PD-02 schema ID | Each section row references its one proposed `v001` ID | No actual header bytes approved, so semantic/header uniqueness cannot be certified; fail closed |
| PD-02 ID → PD-03 manifest | The draft `schema_version` field and both excerpts reference a listed proposed ID | Reserved IDs are not active; unknown/unapproved IDs fail closed |
| PD-03 selects PD-01/PD-02 | Candidate lookup key is source + section + schema version | Missing approved header annex blocks intake, even with a syntactically valid manifest |
| Changed header | PD-02 rule requires a new immutable per-section ID | No changed-header fixture or approved transition exists yet |
| Changed payload at same revision | PD-03 rule classifies changed exact bytes as conflict | No persistent replay registry or runtime conflict test is claimed |
| Controlled correction | Must increment batch revision and retain prior extract; schema ID changes only for contract changes | No correction payload generated; no predecessor fabricated |
| Zero-row versus missing | Example has header-only bytes, row_count 0 and matching SHA-256; missing entry/path is a different failure | Example is one section, not a complete 27-section package |
| PD-04/PD-05/PD-06/PD-07 dependencies | Explicit placeholders/references remain unresolved | Empty arrays, proposed aliases and timestamp strings cannot satisfy later gates |

## Validation execution and boundaries

Local static checks on 2026-09-22: existing Python unit discovery passed **11/11**; `scripts/reconcile_source_fields.py` produced **27 mandatory sections / 333 logical field rows**; the PD-01 and PD-02 tables each contain **27 rows**, their `(source, section, proposed schema ID)` triples match, and all **27 IDs are unique**. PD-01 section identities exactly match the existing mandatory `REQUIRED_SECTIONS` set. Both structural JSON excerpts parse; their declared row counts are 1 and 0 respectively, and recomputed SHA-256 values match the shown exact illustrative CSV bytes. **95 local Markdown links** in affected files resolved and no trailing whitespace was found. `git diff --check` passed. Git name checks found no modified Sprint 1/Sprint 2 approved baseline files; `git status` showed only the eleven intended documentation files, no Python/SQL/data change. Branch and HEAD remained `checkpoint/sprint-03-offline-contract-reconciliation` at `37b2dba85822893f5f80912985796b42b7e28e77`; local `main` remained `537380db03286be70b5910b76409a8e99a6af6a9`. A parsed excerpt is not a full package or approved received header. A section with no approved header or schema contract remains unavailable and cannot be accepted merely because a draft example parses.
