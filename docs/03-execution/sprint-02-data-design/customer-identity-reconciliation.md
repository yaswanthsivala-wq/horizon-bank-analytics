# Customer-identity reconciliation rules

Status: **Draft — not approved**. Supports FR-03, FR-04, US-08 and baseline risk R-02.

| Rule | Proposed ordered behavior | Retained evidence / exception |
| --- | --- | --- |
| ID-01 | Preserve original text and leading zeros; trim boundary whitespace only under a versioned source mapping. Case-folding/punctuation removal requires source confirmation. | Original token, normalized token, mapping version; normalization collision blocks matching |
| ID-02 | Look up (source_system, source_customer_id) at the event/as-of instant in an approved, nonoverlapping crosswalk interval. | Canonical customer_key, effective interval, match method, approval reference |
| ID-03 | For an unseen Core customer, propose a new canonical key only after uniqueness checks and approved master policy. Never reuse retired keys. | New identity proposal; approval state pending |
| ID-04 | For Loan/Fraud/CRM aliases, use an explicitly reviewed synthetic master mapping; equal ID strings in different systems are not proof of identity. | Mapping provenance and reviewer evidence; unknown alias enters exception queue |
| ID-05 | Multiple candidates, overlapping mappings, conflicting master IDs or contradictory supplied account references produce an unresolved match. | ID_AMBIGUOUS or ID_CONFLICT; no automatic merge |
| ID-06 | Names, contact values and account last-four digits never authorize automatic identity matching. | ID_UNMATCHED when no deterministic evidence exists |
| ID-07 | Resolve account and transaction aliases using source-qualified references. Check effective ownership before customer attribution. | ID_ACCOUNT_CONFLICT; DD-02 retains all effective owner/co-borrower roles; no equal or weighted allocation |
| ID-08 | Review merges/splits as versioned corrections with effective dates and approval evidence; re-evaluate affected history explicitly. | Old/new mappings, reason, reviewer reference, impacted runs; no silent overwrite |

Proposed crosswalk states: Pending review, Approved, Rejected, Retired. Only Approved mappings enter curated customer joins. Reviewer authority is approved under DD-08 below; named identities and escalation SLA remain Pending confirmation. A source-local ID is never displayed as a canonical global identity without resolution.

## Unresolved records and reconciliation

Preserve unresolved source rows in restricted quarantine with run/source/row locator and reason; do not invent an unknown real customer or assign a low-risk result. Customer-attributed publication remains blocked when critical identity exceptions exist; exclusions and publication gates follow approved DD-09; no general numerical tolerance is granted. Reconcile distinct source identities into matched, unresolved and explicitly excluded populations, whose union is disjoint and equals all received identities. Reconcile transactional rows separately so one customer with many events does not inflate identity counts.

## Planned review cases (not executed)

Same alias in two systems stays separate without evidence; leading zeros survive; a duplicate alias with conflicting targets fails; an expired mapping does not link a later event; ambiguous joint ownership does not duplicate financial totals; reviewed merge/split corrections remain reproducible by mapping version. Trace to Sprint 1 DQ-02 and DQ-03.

## DD-02 approved relationship policy - 2026-09-15

DD-02 approved by the user on 2026-09-15: retain all owners and co-borrowers with effective-dated relationship roles. Monetary facts remain at their natural account, transaction, payment or loan grain. Customer-level shared balances are labeled "Relationship exposure" and are non-additive across customers; bank totals are computed from distinct natural-grain facts, never by summing customer exposures. Equal or weighted allocation requires a separately approved policy.

## DD-03 historical joins

DD-03 is approved: snapshot joins use customer and relationship evidence valid at the snapshot as-of date. Do not replace historical identity/ownership with current or future relationships. Preserve mapping version in publication lineage; unsupported historical linkage remains an exception/unavailable state under the approved snapshot policy. DD-02 non-additive exposure remains unchanged.

## DD-04 risk attribution

[DD-04](customer-risk-catalog.md) uses effective account owners for RC-05; RC-01 now follows approved DD-05 initiator-first/sole-owner fallback and all effective loan borrowers/co-borrowers for RC-03, without monetary allocation. RC-02/RC-04 use the resolved source customer for the alert/complaint. Unresolved identity or historical relationship evidence cannot prove Not triggered; retain the missing reason. Multiple role paths cannot multiply one condition outcome.

## DD-05 superseding RC-01 hierarchy

[DD-05](customer-risk-catalog.md) supersedes DD-04 for RC-01 only: valid mapped supplied initiator first; absent initiator plus one distinct effective owner permits fallback; absent initiator plus joint owners yields Unknown per individual with `JOINT_ACCOUNT_INITIATOR_UNRESOLVED`. Supplied invalid/unmapped initiator yields Unknown and identity/quality exception, with no fallback even for a sole-owner account. Deduplicate overlapping relationships before owner count and retain conflicts. No inferred initiation by all owners. DD-02 exposure and other condition attribution are preserved.

## DD-06 recalculation context

Corrected-event recalculation covers affected customers from event business date through following 90 days under one selected successful revision. Preserve DD-05 initiator hierarchy and invalid-identifier exceptions; DD-02 relationship exposure is unchanged. Retain old/new identity lineage in controlled corrections.

## DD-07 logical contracts - 2026-09-16

DD-07 preserves source identifiers as bounded text with leading zeros, source-qualified natural keys and internal generated surrogates. Use nonoverlapping half-open effective alias intervals; no fabricated customer FK for unresolved raw evidence. Multiple applied mapping versions use child references. DD-05 initiation and DD-02 ownership exposure remain separate. See the [authoritative inventory](field-level-dictionary.md).

## DD-08 approved identity governance - 2026-09-16

Data Steward Submitter proposes mappings and evidence; an independent Senior Data Steward Approver approves/rejects. No person may submit and approve the same action. Merge, split and retirement require reason, effective date, affected-history analysis and correction/recalculation reference. Only Approved mappings enter curated joins. Risk/Compliance or the relevant source owner is consulted for ambiguous high-impact cases; consultation cannot replace steward approval. Named appointments and escalation SLA remain Pending confirmation. See [DD-08 policy](security-and-masking-design.md) and governance_action/governance_review in the [inventory](field-level-dictionary.md). Historical mapping/ownership determines calculation lineage; current entitlement determines access.

## DD-09 approved coordination - 2026-09-16

DD-09 resolves exclusion/publication severity: DQ-D04 ERROR quarantines unresolved identity without guessing; dependent reconciliation or coverage failure escalates to CRITICAL, as does any misleading published result. DQ-D05 invalid/overlapping intervals and DQ-D02 conflicting duplicates are CRITICAL. An investigator cannot approve exclusions; source owner plus independent Data Owner approval is required, with Compliance for sensitive access/masking/risk evidence. Critical keys cannot be excluded. DD-08 Senior Data Steward approval remains mandatory for identity corrections; Data Owner validates corrected data/reconciliation. Data Publication Approver is separate from investigator, rule author and Administrator. No critical override. Named appointments remain pending. See [approved quality policy](data-quality-and-reconciliation.md) and [authoritative inventory](field-level-dictionary.md).

## DD-10 approved lifecycle coordination - 2026-09-16

Current approved crosswalks and necessary intersecting historical versions follow DD-10 current/dependency rules; no indefinite obsolete aliases/narratives. Rejected identity decisions remain minimized seven-year audit while supplied Restricted payload follows shorter source/analytical schedule. Separate reversible token mappings require valid dependency. Expired audit subjects resolve provenance envelopes rather than guessed identity, dangling FKs or Administrator-edited approvals. See [retention and disposal policy](retention-and-disposal-design.md) and [authoritative inventory](field-level-dictionary.md).
