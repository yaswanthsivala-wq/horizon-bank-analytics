# DD-12 approved historical branch attribution and security - 2026-09-16

Current portfolio interpretation (2026-09-16): [G3 prerequisite register](g3-prerequisite-register.md) replaces real-source verification with finalized [synthetic contracts](synthetic-source-contract.md). Logical fields/policies remain approved; physical aliases are proposed until fixture implementation. Review roles are personas, not actual independent organizational approvals. Prior source-evidence prerequisites now mean synthetic contract/specification at G3 and executed fixture validation before publication. G3 remains unapproved.

Approval evidence: requesting user's explicit Approve DD-12 instruction and 25 controlling decisions. Logical design only. No source availability, actual owner review, G3 or implementation approval is claimed.

## Compatibility and authority

No conflict with Planning, Sprint 1 or DD-01 through DD-11 was found and this was reported before editing. Region/branch drill-down and historical reporting refine existing requirements. DD-08 current-entitlement and role ceilings, DD-09 exact atomic controls, DD-10 original-anchor lifecycle and existing payment/snapshot/KPI financial rules remain intact. DD-12 introduces posted_at for attribution without replacing paid_at event evidence. Date-only due dates and business dates require reviewed source cutoff conventions; no midnight convention is invented.

## Organization and assignment history

Stable identities are source_system + region_id and source_system + branch_id; identifiers cannot be reused for different units. Release 1 hierarchy is Region -> Branch. region is effective-dated; branch remains the authoritative effective branch-version entity keyed by branch_key, linked to a region version. organizational_unit registers stable identities independently of effective versions. Region reassignment creates a new branch version; closure ends its interval without deleting identity/history. Explicit effective organizational_successor versions model mergers. A successor never replaces predecessor identity or automatically inherits access.

account_branch_assignment and loan_branch_assignment have SERVICING and ORIGINATION roles. Exactly one effective SERVICING assignment is required at each reporting instant. Secondary relationships are non-additive; they cannot duplicate facts or balances. Scalar account.branch_key and loan.branch_key are selected-current convenience projections only. complaint_branch_assignment preserves responsible branch intervals. customer_version retains separate effective home branch/segment history. A hierarchy change can require an interval split to keep referenced branch/region versions applicable.

Intervals are half-open [valid_from, valid_to). Same-instant transfers end old and begin new assignment. Overlap checks use stable subject + role within selected correction scope, not interval start. Exactly-one SERVICING and RESPONSIBLE coverage is checked at requested attribution instants. No inferred assignment from customer home branch, shared ownership, masked suffix, reporting-account relationships, amount or another domain; never bridge gaps or ambiguous matches by fallback. Historical branch and region labels always reflect the fact's attribution time, unaffected by later transfer, closure, merger or region reassignment.

## Attribution contract

branch_attribution records each fact/analysis-purpose/observation and selected publication separately: typed immutable fact reference, branch and region versions, attribution instant, basis, assignment-version reference, supplied evidence and availability reason. Source-supplied branches are accepted only with defined business role/effective time and validation against applicable assignment history. Mismatch requires review, never silent precedence. When no authoritative event branch exists, derive only from approved effective assignment history. RC-02's explicitly approved alert/transaction paths are the stated exception to a direct assignment reference, not invented fallback. If attribution is unavailable, retain explicit missing evidence with no fabricated branch. Required controls still apply.

| Population/purpose | Attribution instant and authority |
| --- | --- |
| K01-K04 transactions | Account SERVICING at occurred_at |
| Loan snapshots/K05/K06 | Loan SERVICING on snapshot business date, using reviewed snapshot cutoff |
| Complaint creation | Responsible complaint branch at created_at |
| K08 | Responsible complaint branch at final_closed_at |
| K09 | Complaint snapshot branch on selected business date |
| K10 | Responsible branch at selected as-of instant for open cases; final_closed_at for closed cases |
| Schedule | Loan SERVICING at schedule effective_from |
| Obligation | Loan SERVICING at contractual due_date; reviewed date-to-instant convention required |
| POSTED payment | Loan SERVICING at posted_at; never silently substitute paid_at |
| Nonposted payment | Loan SERVICING at payment-event timestamp paid_at |
| Adjustment | Loan SERVICING at adjustment occurred_at |
| Allocation cash flow / unapplied | Payment-event attribution; allocation separately retains obligation attribution |
| Adjustment original-payment context | Retain original-payment attribution separately from adjustment-time branch |
| RC-01 | Transaction attribution |
| RC-02 | Approved source-supplied alert branch; otherwise valid linked-transaction branch; otherwise Unavailable |
| RC-03 | Qualifying loan-snapshot attribution |
| RC-04 | Qualifying complaint as-of attribution |
| RC-05 | Restricted account SERVICING at assessment time |
| K07 | Home branch at assessment date for branch/region analysis; enterprise counts each high-risk customer once |

Allocation cash-flow and obligation branches need not match after a transfer. Evidence spanning branches retains every observation's attribution without multiplying condition counts. Missing home attribution never removes a high-risk customer from enterprise K07; disclose branch coverage and apply required gates separately. No other KPI population/formula changes. Risk case access and sanitized projections are not widened by attribution fields.

## Current authorization over historical labels

Current effective, unrevoked DD-08 entitlements apply at query/export execution. Historical ownership/employment never grants access. A current branch grant may access retained history attributed to that stable branch identity. A current region grant expands to branches currently assigned to that region, then can access retained history for those stable IDs; historical report labels remain unchanged. Thus historical R1 labels can appear in a currently authorized R2 user's scope after an approved branch transfer; labels are not the security predicate.

Closed/merged/predecessor history outside current scope requires explicit current HISTORICAL_BRANCH scope or an approved effective successor_scope_mapping. Organizational succession alone grants nothing. Successor mappings require separated access-change approval under DD-08: requester, Compliance approver and Administrator implementer; mapping evidence and current base entitlement must both resolve. Default deny if resolution is unsafe. Single active role, explicit deny precedence, scope-dimension intersection and role ceilings remain. Fraud/Risk remain assigned-case based; Executive aggregate-only; Operations aggregate within authorized scope. Exports recheck current authorization. Record hierarchy/scope mapping versions and resolved stable branch members in scope_resolution evidence without sensitive payload.

## Corrections and quality

Hierarchy/assignment corrections are immutable with predecessor, reason, affected interval, source version and approval evidence. The selected publication chooses exact versions via organization_publication. Corrections restate only retained facts whose attribution timestamps lie in the corrected interval; related cash-flow/obligation purposes are evaluated independently. Recalculate affected branch/region KPIs, risk-evidence projections, scope evaluations and publication membership. Preserve original publication, issue a new version through DD-09; current scope must always use current approved effective hierarchy, not the queried historical publication's hierarchy selection.

Source owner authorizes source correction; independent Data Owner validates reconciliation, applicable business/source reviewers and Data Publication Approver govern restated release. Access changes retain DD-08 independent Compliance approval. No actual review is claimed. Missing/conflicting assignments never use fallback. DQ-D03/D04 quarantine and DD-09 escalation apply; DQ-D05 overlap/invalid intervals, RC-D03 multiplication and required attribution coverage below 98% are CRITICAL. Required coverage is measured per applicable population and overall with visible unavailable counts; passing 98% permits neither guessing nor security exposure. Source mismatch remains unresolved until reviewed; block when required controls fail or reporting is misleading. Exact row/currency reconciliation and atomic publication apply; no critical override. Last successful publication and notifications follow DD-09.

## Lifecycle and source prerequisites

Keep effective organization/assignment versions while active or required; after original effective end, retain 24 months or until no retained analytical child depends, whichever later. Corrections do not restart clocks. Attribution/membership follows underlying analytical original dates, not republication. Minimized corrections, approval and scope-decision evidence is seven-year audit under DD-10; approved configuration remains while active and through its dependent audit retention. Holds, bounded backups, approved disposal and PAYLOAD_EXPIRED envelopes apply; no dangling analytical FK or indefinite raw retention.

Required logical source coverage: SRC-05 effective region/branch/successor history; SRC-01 account assignments and customer home history; SRC-02 loan assignments and posted_at; SRC-04 responsible complaint history/as-of branch; supplied authoritative event branches with role/time; SRC-03 approved alert branch when supplied. RC-02 explicitly allows linked-transaction attribution or Unavailable if neither path exists. These are contracts, not verified availability. Actual aliases, transitions, date cutoffs, historical sample reconciliation and source-owner plus Data Owner review remain prerequisites before implementation/publication. No additional unresolved logical DD decision is asserted; source-contract facts, named appointments, physical design and G3 remain pending.
