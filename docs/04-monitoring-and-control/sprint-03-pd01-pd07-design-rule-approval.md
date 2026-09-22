# Sprint 3 PD-01 through PD-07 design-rule approval/control record — 2026-09-21

Decision authority: requesting user. Direct evidence: the user's instruction to record the specified PD-01 through PD-07 rules as `Approved — Design Rule`, explicitly excluding missing physical annex values and PostgreSQL/PD02 work. The complete [decision package](../03-execution/sprint-03-physical-design/physical-design-decision-package.md) states each question, approved G3 authority, implementation boundary, derived detail and still-pending evidence. Rationale: establish fail-closed physical-contract design rules while preserving G3 logical semantics and deferring unverified values. No simulated source-owner or Data Owner review is claimed.

| ID | Decision status | Scope of approved design rule | Excluded evidence |
| --- | --- | --- | --- |
| PD-01 | Approved — Design Rule | Explicit ordered, case-sensitive received headers keyed by source/section/schema version | Exact 27-section header annexes |
| PD-02 | Approved — Design Rule | Immutable per-section schema IDs and separate revision/mapping/source-state versions | Literal IDs; transition/compatibility records |
| PD-03 | Approved — Design Rule | UTF-8 `manifest.json`, relative section CSV paths, exact-byte SHA-256 binding | Final JSON schema/vocabulary; zero-row/one-row examples |
| PD-04 | Approved — Design Rule | Versioned field disposition and always/optional/conditional applicability; unresolved fails gate | Complete predicates; denominator/applicability rules |
| PD-05 | Approved — Design Rule | Versioned explicit financial matrix, signed decimal(28,4) or unavailable reason, exact reconciliation | Complete matrix; worked examples |
| PD-06 | Approved — Design Rule | Versioned raw-to-canonical mappings/eligibility; raw and applied-version lineage | Final rows; literal mapping-version IDs |
| PD-07 | Approved — Design Rule | Verifiable IANA 2026a Chicago/DST/offset/microsecond handling | Runtime/dependency verification mechanism |

All excluded evidence remains **Pending confirmation**. An absent required reviewed annex fails closed; this approval does not turn illustrative test headers, `reviewed-v1`, proposed raw codes or document labels into approved physical values. `PD-02` above is a decision ID; it does not authorize the separate PD02 database work package. Sprint 3 is started but **not approved**; PD02, PostgreSQL, dataset generation, publication and G4 remain unauthorized/unapproved.

The user authorized documentation, local validation and one controlled checkpoint commit on the existing Sprint 3 branch. No push or merge is authorized in this turn. No approved Sprint 1/Sprint 2 baseline, pipeline code or test file is changed by this decision record.
