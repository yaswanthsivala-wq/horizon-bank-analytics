# PD-05 through PD-07 cross-contract validation — Increment 3

Status: **Approved documentary consistency model — Runtime dependencies remain fail closed** (Project Owner reviewed 2026-09-22). Approval covers the PD-01 through PD-07 dependency chain and failure behavior below; it is documentary consistency review only. No received payload, financial reconciliation, mapping or DST test was executed. The [G3 baseline](../../04-monitoring-and-control/g3-data-design-approval.md), [decision package](physical-design-decision-package.md), [PD-01](pd01-physical-header-annex.md), [PD-02](pd02-schema-version-annex.md), [PD-03](pd03-manifest-json-specification.md) and [PD-04](pd04-conditional-applicability-annex.md) remain controlling.

| Chain link | Static result | Runtime/approval gate |
| --- | --- | --- |
| PD-01 received header → PD-02 schema | Structural relationship consistent; all 27 headers unresolved and candidate schema IDs inactive | Unknown/unapproved header or schema fails closed |
| PD-02 schema → PD-03 manifest | Manifest references exact source/section/version; its mapping/control arrays are evidence references only | Missing active schema or required referenced evidence fails closed |
| PD-03 package → PD-04 applicability | Manifest selects physical contract before any row predicate | Zero active physical predicates; unknown required predicate or invalid evidence fails dependent gate |
| PD-04 ↔ [PD-05](pd05-financial-control-annex.md) | Disjoint received/accepted/quarantined/approved-excluded financial populations cannot silently omit unresolved applicable records | No financial row active until applicability/population evidence is approved |
| [PD-06](pd06-status-mapping-annex.md) ↔ PD-04 | Status-dependent predicate requires approved raw-to-canonical version/eligibility | Unknown/retired mapping blocks predicate; no `OTHER`/`UNKNOWN` default |
| PD-06 ↔ PD-05 | Status-dependent monetary population uses exact applied mapping version | Missing mapping blocks control rather than excluding amount |
| [PD-07](pd07-chicago-time-runtime-annex.md) ↔ PD-04 | Temporal predicate needs approved Chicago instant/calendar interpretation | Missing tzdb/runtime proof blocks dependent predicate |
| PD-07 ↔ PD-05 | Control business date, cutoff and stock/flow periods use the same Chicago boundary semantics | Unknown cutoff/version blocks comparison; no fixed 24-hour day |
| PD-07 ↔ PD-06 | Historical replay retains applied mapping and temporal version evidence | Later mapping/tzdb change cannot silently rewrite accepted interpretation |

Static outcome: **consistent as a proposed dependency chain; no conflict identified** with the approved Sprint 2/G3 rules. This is not acceptance evidence: PD-01 headers, PD-02 activation, PD-04 predicate bindings, PD-05 matrix, PD-06 mapping rows and PD-07 runtime proof are pending. Every unknown required dependency fails closed. See the [master pending register](physical-contract-pending-register.md) and [control record](../../04-monitoring-and-control/sprint-03-physical-contract-annex-3-control.md).
