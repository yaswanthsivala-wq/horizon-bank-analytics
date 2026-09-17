# DD-08 approved access, ownership and export design

Current portfolio interpretation (2026-09-16): [G3 prerequisite register](g3-prerequisite-register.md) replaces real-source verification with finalized [synthetic contracts](synthetic-source-contract.md). Logical fields/policies remain approved; physical aliases are proposed until fixture implementation. Review roles are personas, not actual independent organizational approvals. Prior source-evidence prerequisites now mean synthetic contract/specification at G3 and executed fixture validation before publication. G3 remains unapproved.

Approved by the requesting user on 2026-09-16. Evidence: the user's supplied DD-08 policy, following pre-edit compatibility review. Logical entitlements and responsibilities only; G3 and physical Power BI/database security remain **Draft — not approved**. No real users, access grants or security implementation have been created.

## Compatibility and authority

No conflict found with Planning FR-11/FR-12/FR-14, Sprint 1 US-01/US-02/US-03/US-06/US-07/US-08 or DD-01 through DD-07. Exceptional restricted-export approval does not override final-four masking in reporting outputs, executive aggregate-only access, explicit denies or other baseline restrictions. It is not blanket permission to export full account numbers. Joint Risk Manager/Compliance approval refines change authorization; US-06's configurable-threshold behavior remains intact. Sanitized RC-01 projection supports US-03 without granting raw evidence access or reclassifying Restricted raw fields.

The requester approves design policy here. Named organizational reviewers, actual assignments and actual approval evidence remain Pending confirmation. Governance/source responsibility alone grants no business-detail access. Role simulation remains the Release 1 approach; API rules express access boundaries, not authorization to build an API or connect an identity provider.

## General authorization

- Default deny for roles, rows, fields, drill-through, tooltips, downloads, APIs and exports.
- Each session/report has exactly one explicitly selected active role. Assigned roles are never automatically unioned. A role switch requires reevaluation of scope and entitlements.
- Explicit deny overrides allow. Entitlements are effective-dated, scoped and independently approved; use DD-07 half-open UTC intervals and Chicago business dates.
- Expired/revoked entitlements immediately block new queries and exports. Historical/corrected publications use current entitlement, never historical ownership.
- Administrative, governance and source ownership responsibilities grant no automatic business-detail permission. Ownership/co-borrower relationships are not access entitlements; DD-02 non-additive exposure and DD-05 initiation stay distinct.

## Approved reporting and export roles

| Active role | Approved reporting scope | Ordinary export scope |
| --- | --- | --- |
| Executive | Enterprise/regional aggregates only; no customer/account/transaction/loan/complaint/fraud-detail rows | Authorized aggregate CSV/PDF |
| Operations Manager | Aggregates for assigned regions/branches; no individual customer/transaction rows; investigation requires separately assigned and selected role | Authorized aggregate CSV/PDF |
| Fraud Analyst | Assigned fraud cases; linked customer context, final-four account, transaction and alert detail needed for case | Masked assigned-case detail only with explicit standing EXPORT_MASKED_DETAIL entitlement |
| Risk Analyst | Assigned customer-risk cases and conditions; underlying domain detail only when linked to assigned case | Masked assigned-case detail only with explicit standing EXPORT_MASKED_DETAIL entitlement |
| Loan Operations Manager | Assigned-region/branch loan and payment detail; final-four accounts | Masked assigned-scope detail only with EXPORT_MASKED_DETAIL |
| Customer Service Manager | Assigned-region/branch complaint detail; masked related accounts | Masked assigned-scope detail only with EXPORT_MASKED_DETAIL |
| Data Analyst / Business Analyst | Enterprise aggregates and deidentified curated analysis/reconciliation/testing detail; no names, contacts, full numbers, source aliases or raw payloads | Aggregates or deidentified curated data |
| Source Data Owner | Own-source quality, reconciliation, raw and quarantine evidence only; no automatic cross-domain reporting | Raw/quarantine denied by default; no additional ordinary export grant inferred |
| Administrator | Pipeline/configuration operations and sanitized audit only; no automatic business detail, restricted identity or export grant | Sanitized operational audit only when authorized under the general entitlement rules |
| Compliance Officer | Security/masking/entitlement/export audit; Restricted inspection requires recorded time-bound inspection entitlement | No blanket detail/export grant; exceptional route requires the specified approvals |
| Unmapped/unauthorized | No rows, navigation, export or administration | Denied |

Governance titles (Sponsor, Director of Banking Operations, Fraud Manager, Risk Manager, Branch Administration Manager) and steward responsibilities do not independently create a reporting role grant. Source Data Owner and the Data Owner review responsibility are distinct unless an explicit appointment establishes otherwise. Deidentification must remove the listed identity/raw fields; its exact transformation contract and residual reidentification checks require review before release. A stable customer key alone is not proof of deidentification.

## Restricted fields and RC-01 projection

Full account numbers, names/contact information, synthetic master IDs and source customer aliases are excluded from ordinary reporting/exports. Account reporting uses fixed masking plus final four characters; preserve leading zeros. Invalid/shorter-than-four input yields Unavailable and a quality exception. Full numbers are removed at reporting boundaries; masked suffix is not a key. No ordinary reporting role receives unmasked numbers.

Only assigned Fraud/Risk Analysts may view the sanitized RC-01 investigation projection for an authorized linked case. Its visible fields are current comparison amount, prior average, multiplier, currency, window boundaries, history count, trigger state and missing-evidence reason. No source identity aliases or unrestricted source references appear. Internal case/evidence links enforce scope but are not unrestricted navigation paths. DD-07 exact mean/sum-count semantics remain; no new rounding permission. Raw RC-01 evidence/source references remain Restricted.

Restricted/Controlled/Audit field classifications remain in the [authoritative inventory](field-level-dictionary.md). Audit references inherit referenced sensitivity. Narratives remain bounded and excluded from ordinary exports. Restricted inspection access is scoped/time-bound and recorded, not inferred from Compliance job title. Apply these controls to tooltips, downloads, direct access and corrected history as well as visible pages.

## Identity governance

Data Steward Submitter proposes mappings and supplies evidence. Independent Senior Data Steward Approver approves or rejects. The same person cannot submit and approve the same mapping action. Only Approved mappings enter curated joins.

Merge, split and retirement require independent Senior Data Steward approval, reason, effective date, affected-history analysis and correction/recalculation reference. Preserve old/new mapping versions; no silent overwrites or key reuse. Consult Risk/Compliance or relevant source owner for ambiguous high-impact cases; consultation does not replace independent crosswalk approval. Steward responsibility authorizes the scoped review workflow, not unrestricted reporting/export of identity data.

## Governance ownership

| Contract / decision | Required responsible review |
| --- | --- |
| Core Banking source contract | Director of Banking Operations plus Data Owner review evidence |
| Loan Servicing source contract | Loan Operations Manager plus Data Owner review evidence |
| Fraud Monitoring source contract | Fraud Manager plus Data Owner review evidence |
| CRM source contract | Customer Service Manager plus Data Owner review evidence |
| Branch Reference source contract | Branch Administration Manager plus Data Owner review evidence |
| Each source mapping | Its applicable source owner plus Data Owner review evidence |
| KPI mappings | Applicable business KPI owner plus Data Owner review |
| Customer-risk catalog/threshold changes | Joint Risk Manager and Compliance approval |
| Access changes | Separate requester, Compliance approver and Administrator implementer |
| Exceptional restricted export | Per-export Compliance and applicable Data Owner approval; requester cannot approve |

Planning business KPI ownership remains: Director of Banking Operations for operations KPIs; Loan Operations Manager for loan KPIs; Customer Service Manager for complaint KPIs; Fraud Manager for fraud indicators; Risk Manager for risk logic. Data Analyst/Business Analyst may prepare and recommend, but cannot give final business approval. Administrators cannot approve their own entitlements or modify approval evidence. Named appointments/delegates and specific review references must be supplied, not fabricated.

## Export execution and evidence

Recheck selected active role, row/field scope and all applicable entitlements at export execution. Expiry/revocation during preparation causes denial and no sensitive output. Standing EXPORT_MASKED_DETAIL permits only the specified masked assigned scope; it is not a Restricted export authorization. Source raw/quarantine, Restricted identity, full account numbers, names/contact and unrestricted narrative exports are denied by default.

Exceptional Restricted exports require per-export Compliance and applicable Data Owner approval, with a nonapproving requester. Approval must identify the exact permitted scope/output; it cannot bypass explicit deny or approved reporting restrictions. Exceptional scope/destination contracts must be reviewable before such an export; no actual exception is approved by this design.

Record user identity (opaque simulation principal ID, not customer identity or credentials), active role, every applicable entitlement ID in child references, policy version, report, format, requested/completed timestamps, selected publication, structured sanitized filters, row count, allow/deny decision, denial reason, approval references when required and output classification. Log all denied attempts without sensitive output. No names/contact/account numbers/case narrative in filters or audit text. Missing/unmeasured counts remain unavailable, not fabricated zero. A measured denied-output count may be zero. Pending preparation is not a fabricated completed/allowed result.

## Separation of duties

No self-approval for mappings, rule changes, access changes, exceptional exports, exclusions or entitlement grants. Rule authors cannot be the sole approver or publisher. Exception investigators cannot authorize their own exclusions. Administrators cannot alter or manually/discretionarily delete approval evidence. DD-10 permits only engine-eligible, expired, unheld, dependency-cleared items inside an exact independently approved disposal batch; this is a narrow lifecycle refinement, not general deletion permission.

Any exceptional separation-of-duties waiver requires Sponsor and Compliance approval, reason, effective interval and audit record. Waivers are explicit, linked, time-bound exceptions; they do not silently disable denies, masking or baseline restrictions. No waiver has been granted. Quality exclusion and publication authority remain coordinated with DD-09; audit retention mechanics remain DD-10. Analytics 24 months and pipeline/quality/export audit seven years remain the baseline durations.

## Planned security evidence and remaining dependencies

Future checks: active-role isolation; deny precedence; effective scope and revocation; case-linked detail; executive/operations aggregate-only outputs; deidentified analyst detail; own-source raw isolation; time-bound Compliance inspection; steward independence; joint rule approval; three-party access changes; masked export standing entitlement; exceptional dual approval; preparation-time revocation; denied-attempt logging; sanitized RC-01 projection; immutable approval evidence; bounded waivers. ST-01 through ST-07 remain planned, not executed.

DD-09 now assigns publication/exclusion authority and control disposition under the approved coordination below. DD-10 resolves retention with the narrow controlled end-of-retention exception below; discretionary deletion and alteration remain prohibited. DD-11 payment contracts are approved; DD-12 branch-history logical contracts are approved; actual coverage remains pending; neither grants access. Named appointments, entitlement/case assignments, specific approval evidence and physical enforcement await later authorized work. G3 remains pending.

## DD-09 approved governance responsibilities - 2026-09-16

Applicable source owner authorizes source-data corrections; Data Owner independently validates corrected data and reconciliation. Independent Senior Data Steward identity approval and joint Risk Manager/Compliance rule/configuration approval remain required. Quality exclusions require source owner plus independent Data Owner, with Compliance for sensitive access, masking or risk evidence; investigator cannot approve their own exclusion. Scope is exact source/entity/date/revision/records, never indefinite.

Data Publication Approver is a governance responsibility separate from investigator, rule author and Administrator. It grants no automatic business-detail or export access. Only candidates passing every automated gate with complete evidence may be approved. Corrected/restated publications additionally require Data Owner validation and applicable business/source-owner review. Administrator executes approved replay/publication but cannot approve it. No person, role or Sponsor waiver may override unresolved CRITICAL failure.

Notify Data Owner, Data Publication Approver and affected source/KPI owners immediately for gate miss, restatement or discovered critical failure; retain sanitized notification/recipient/acknowledgment evidence. This is a logical requirement; no message is sent by this documentation change. Named appointments and actual approvals remain Pending confirmation. DD-10 logical retention mechanics are approved; physical implementation remains deferred. See [DD-09 policy](data-quality-and-reconciliation.md).

## DD-10 approved lifecycle coordination - 2026-09-16

DD-10 expressly supersedes the DD-08 Administrator deletion prohibition only for expired, unheld, dependency-cleared items in the exact batch defined and approved by Compliance and an independent Data Owner. The retention engine determines eligibility. Administrator only initiates/operates the job, cannot select/add records, expand scope, shorten retention, alter approvals/anchors/holds/evidence or manually delete evidence. Failed eligibility, scope mismatch or hold prevents item deletion and records failure. All other separation and access controls remain unchanged. Holds/disposal have independent approvals; denied access/export events are minimized seven-year audit. Backup restore must reapply current revocations/deletions/holds. See [retention and disposal policy](retention-and-disposal-design.md) and [authoritative inventory](field-level-dictionary.md).

## DD-11 approved coordination

See [approved DD-11 policy](loan-payment-and-schedule-policy.md). US-04 uses snapshot-authoritative DPD/outstanding principal and exactly one effective REPORTING account through loan_account for masked drill-through. Schedules and actual events are distinct; component allocations and unapplied balances reconcile without fanout, and reversals/refunds preserve originals. K05, K06 and RC-03 including DPD > 30 remain unchanged. Existing scoped access and original-date retention apply. Source coverage remains unverified; fixture/runtime validation is planned, not executed.

## DD-12 approved coordination - 2026-09-16

[DD-12 approved policy](historical-branch-attribution-policy.md). Earlier dated dependency notes retain historical status; DD-12 logical policy is now approved, actual source coverage remains unverified.

Current effective unrevoked entitlements always apply, with single active role, deny precedence and role ceilings. Current branch grant reaches retained history for that stable source-qualified branch. Current region grant resolves CURRENT branch membership and reaches retained history for those stable branch identities; historical region labels remain unchanged. Historical ownership/employment grants nothing. Closed/merged/predecessor history outside current scope needs explicit current HISTORICAL_BRANCH scope or independently approved effective successor_scope_mapping plus current base grant; succession alone grants nothing. Access-change requester/Compliance/Administrator separation applies. Unsafe scope denies. Cases remain assigned, Executive aggregate-only, Operations authorized aggregates; exports recheck current authorization. scope_resolution records current hierarchy/mapping/member evidence independently of report publication.
