# DD-11 documentation validation - 2026-09-16

Scope: requesting user approved the 20 controlling DD-11 decisions. Logical documentation only; G3, physical design and implementation remain unapproved.

## Pre-edit compatibility review

No conflict found with Planning, Sprint 1 or DD-01 through DD-10; reported before edits. Scheduled/actual payments and masked US-04 drill-through are existing needs. DD-11 distinguishes contractual obligations from payment events without changing DD-02 ownership exposure, DD-03 snapshot authority, DD-04 RC-03 or DD-06 K05/K06. DPD > 30, DD-08 access and separation, DD-09 atomic exact controls and DD-10 original-anchor retention remain intact. Nine protected baseline files match the captured pre-edit SHA-256 hashes and the DD-07 record.

## Policy and inventory review

Reviewed all 20 controlling decisions against the policy, authoritative inventory and coordinated documents. The sole inventory now has 99 entities and 853 field rows. Added eight logical entities for schedules, obligations, allocations, unapplied states, adjustments, effective account links, optional transaction links and publication membership. Removed the authoritative scalar loan account reference and canonical payment due date; added contractual currency and payment statuses. Required logical coverage is explicitly distinguished from verified source availability.

Checked immutable source-qualified versions, acyclic correction predecessors, same-loan/currency relationships, many-to-many allocation grain, positive payment amounts, POSTED-only financial effect, the exact allocation equation, cumulative adjustment cap, no inferred links and exactly one effective masked REPORTING account. Checked original retention anchors and full entity-schedule coverage. Source-supported adjustment/allocation/unapplied timing and sign/domain mappings remain mandatory reviewed source facts; no waterfall or undocumented net equation is invented. K05/K06/RC-03 formulas remain unchanged.

## Documentation checks

- 265 local Markdown links resolve.
- 99 entity names and 853 entity/field pairs are unique; declared primary-key fields are required, explicit scalar FK targets resolve and text/decimal declarations are bounded. Typed/composite references retain full-key resolution rules; no real data was checked.
- All 99 entities occur exactly once in the retention entity schedule.
- All 32 acceptance-criterion traceability rows, 14 FR identifiers and 9 NFR identifiers remain covered; the 17-rule DD-09 catalog remains intact.
- Sprint 2/control-record Markdown table widths, fence pairing and trailing whitespace pass; git diff --check passes.
- Nine protected Initiation/Planning/Sprint 1 files retain their hashes. Reserved data/technical directories contain only placeholders.
- Read-only Git inspection: main; existing origin fetch/push URL https://github.com/yaswanthsivala-wq/horizon-bank-analytics.git; index empty. No staging, commit, push, remote contact or Git metadata writes.

## Limits

These are documentation checks, not executed financial, security, retention, performance or acceptance tests. Mermaid diagrams were not visually rendered. No source discovery, actual owner reviews, source coverage, allocations, publication or runtime result is claimed. DD-12, verified source schemas and mappings, reviewed adjustment application timing, delivery conventions and G3 remain pending. No technical implementation began. Earlier validation records retain their historical scope and counts.
