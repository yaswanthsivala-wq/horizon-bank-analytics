# PD-07 America/Chicago time and DST runtime annex — Increment 3

Status: **Approved specification — Runtime/tzdb verification and executable boundary evidence pending confirmation** (Project Owner reviewed 2026-09-22). PD-07 is **Approved — Design Rule**. The Chicago/UTC(6), offset, calendar, cutoff, fold/gap, replay and change-control specification and all 15 future executable cases are approved as test requirements. No runtime timezone package, parser, tzdb 2026a version or executable boundary test has been verified or activated.

## Authority and classification

| Classification | Evidence and consequence |
| --- | --- |
| Approved baseline | [G3 synthetic contract](../sprint-02-data-design/synthetic-source-contract.md) specifies `America/Chicago`, IANA tzdb **2026a** as design version, offset-qualified events, supplied-offset agreement, invalid gap/unresolved fold, UTC(6), Chicago business days, exclusive D+1 midnight snapshot cutoff and cutoff-minus-one-microsecond matching. [DD-07 dictionary](../sprint-02-data-design/field-level-dictionary.md), [DD-03 logical model](../sprint-02-data-design/logical-data-model.md), [DD-11](../sprint-02-data-design/loan-payment-and-schedule-policy.md), [DD-12](../sprint-02-data-design/historical-branch-attribution-policy.md) and [KPI policy](../sprint-02-data-design/kpi-policy-dd06.md) govern typed time, due dates, SLA and history. |
| Derived physical implementation detail | The future verification ledger and case matrix below are test-design proposals. They do not select a library or prove its data version. |
| Pending confirmation | Runtime parser/dependency, proof of bundled tzdb 2026a, supplied fold resolution mechanism, boundary-test execution, upgrade policy artifact and exact source cutoff fields/values where PD-01 has no approved header. |
| Conflict | None identified in the documentary design. Runtime behavior remains unverified. |

## Candidate runtime contract

1. Record the literal zone ID `America/Chicago`, runtime/library identity, IANA tzdb data source and verified version `2026a` with each relevant run/publication. Do not infer version from operating-system timezone, current offset or a library name alone. A future implementation must use a verifiable pinned data artifact or equivalent exact-version proof; the selection and proof method are **Pending confirmation**. Missing/mismatched proof blocks dependent validation.
2. Parse offset-qualified source timestamps as exact instants. Reject missing offset unless an approved source contract explicitly declares a timezone. Check fractional precision before conversion; greater than six digits is not silently rounded or truncated. Preserve original text/offset and normalized UTC instant at microsecond precision.
3. Verify that the supplied offset agrees with `America/Chicago` at that instant where the selected source contract requires Chicago-local evidence. An offset alone identifies an instant, but an invalid Chicago offset is a controlled error. Do not infer a fold for ambiguous local wall time without approved offset/fold evidence; reject nonexistent local wall times rather than shifting them.
4. Derive business date and calendar boundaries using Chicago local dates. Compute next **local midnight**, then convert to UTC; never add a fixed 24 hours to the prior UTC boundary. Treat due dates as calendar dates until the approved Chicago-midnight lookup. Snapshot cutoff is exclusive; the point immediately before it is cutoff minus one microsecond. Half-open effective intervals `[start,end)` preserve DD-12 as-of semantics.
5. Preserve the applied temporal contract/tzdb version and source-state, schema, revision and PD-06 mapping-version evidence in historical interpretation and replay. A later tzdb/runtime upgrade needs change review, compatibility/boundary reruns and a new recorded interpretation version when results can change; accepted history cannot be silently rewritten.

The G3 synthetic delivery convention sets business date D to `[D 00:00, D+1 00:00)` Chicago, initial delivery at 04:30 Chicago D+1, approved late allowance to 05:30, and 06:00 publication gate. These are fictional design rules, not observed operating results. PD-03 manifest `cutoff_at`/`extracted_at` uses UTC with six fractional digits and `Z`; PD-07 must verify the corresponding local cutoff semantics after an approved physical contract is selected.

## Candidate DST and boundary validation specification

Every case below is **specified, not executed**. Expected UTC results shown for the two G3 documented day pairs are baseline examples; remaining exact fixture instants and executable assertions require reviewed runtime evidence. All comparisons retain microseconds.

| Case | Candidate assertion | Evidence state |
| --- | --- | --- |
| T01 standard-time ordinary date | Correct Chicago offset and UTC(6) round-trip in winter | Not executed |
| T02 daylight-time ordinary date | Correct Chicago offset and UTC(6) round-trip in summer | Not executed |
| T03 spring transition | Offset changes at the 2025-03-09 boundary; no skipped instant | Not executed |
| T04 spring gap | Reject nonexistent Chicago local wall time; never auto-shift | Not executed |
| T05 fall transition | Offset changes at the 2025-11-02 boundary without duplicating an instant | Not executed |
| T06 fall fold | Reject ambiguous offset-free local time absent approved fold evidence; accept only correctly qualified instant | Not executed |
| T07 23-hour local day | G3: 2025-03-09 00:00 Chicago = 06:00Z; 2025-03-10 00:00 = 05:00Z; elapsed 23 hours | Not executed |
| T08 25-hour local day | G3: 2025-11-02 00:00 Chicago = 05:00Z; 2025-11-03 00:00 = 06:00Z; elapsed 25 hours | Not executed |
| T09 local midnight | Business-date D maps to the correct Chicago midnight and UTC instant | Not executed |
| T10 due/calendar date | Due date remains a date; resolve through Chicago calendar, not an arbitrary UTC midnight | Not executed |
| T11 cutoff-minus-one-microsecond | Point match immediately before exclusive D+1 midnight remains eligible | Not executed |
| T12 cutoff exact boundary | Event at exclusive cutoff belongs to the next period, not D | Not executed |
| T13 effective intervals | `[start,end)` selects the version valid at the queried instant; no future/current-state backfill | Not executed |
| T14 supplied-offset mismatch | Reject an offset that disagrees with Chicago zone at the parsed instant | Not executed |
| T15 excess precision and replay | Reject silent >6-digit truncation; replay retains original and applied tzdb/version evidence | Not executed |

**15 cases specified; 0 executed; runtime tzdb 2026a verification Pending confirmation.** Do not install a dependency, change machine timezone or treat OS zone configuration as proof. PD-04 temporal predicates and PD-05 financial cutoff populations remain inactive where this evidence is required.
