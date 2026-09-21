# CR-001 — KPI and risk refinements

Recorded retroactively: 2026-09-20. Documentation remediation only; no formula is changed by this record. No new approval is requested or asserted here. Record owner: Pending confirmation.

## Reason

Planning section 17 requires a change record for refinements. The approved Sprint 2 policies refine Planning section 8 populations and temporal semantics and the FR-08 risk comparison. This records their existing evidence without editing the protected baselines.

## Impact

| Item | Planning baseline | Approved Sprint 2 refinement | Approval evidence |
| --- | --- | --- | --- |
| K04 Fraud-Alert Rate | Distinct transactions with ≥1 alert ÷ total transactions (§8) | ÷ eligible transactions (SUCCESSFUL, POSTED, FAILED, DECLINED), same population as K02/K03; multiple alerts count once | DD-06, approved by the requesting user 2026-09-16; [KPI policy](../../03-execution/sprint-02-data-design/kpi-policy-dd06.md) |
| K01 Transaction Volume | Count of processed transactions | Processed = terminal outcome; PENDING excluded | DD-06, approved by the requesting user 2026-09-16; [KPI policy](../../03-execution/sprint-02-data-design/kpi-policy-dd06.md) |
| RC-01 / FR-08 | ≥3× preceding 90-day average | Full 90-day window, ≥5 eligible priors, same currency, initiator-first attribution; missing/unresolved evidence remains Unknown under the approved policy | DD-05, approved by the requesting user 2026-09-15; [risk catalog](../../03-execution/sprint-02-data-design/customer-risk-catalog.md) |
| K08 / K10 | Creation→closure hours; SLA breach among eligible | K08 original creation to final closure with reopen handling; K10 eligible open and closed cases, open cases measured to as-of | DD-06, approved by the requesting user 2026-09-16; [KPI policy](../../03-execution/sprint-02-data-design/kpi-policy-dd06.md) |

Scope: documentary traceability of already approved refinements. Data/quality impact: populations, attribution and historical complaint states must follow the cited policies during separately authorized implementation and validation. Security impact: no changed access rule or classification. Schedule impact: Pending confirmation; no measured effort or delay claimed. No implementation or tests are performed by this record.

## Recommendation

Retain the existing approved DD-05/DD-06 semantics and use this record to clarify the cross-reference in KPI mappings. No baseline formula, threshold, grain, or field is altered.

## Approval evidence

The cited policy documents record requesting-user approval on the dates above. They are evidence of existing design decisions, not new approval of this retrospective record. Independent sponsor review of this record: Pending confirmation.

Risk Manager / Compliance / KPI-owner reviews: Pending confirmation — persona roles only; no independent review is claimed.

## Documents updated

- This retrospective CR-001 record.
- [KPI-to-data mappings](../../03-execution/sprint-02-data-design/kpi-to-data-mappings.md): current status and clarification that DD-05/DD-06 refine Planning.
- [Monitoring and Control inventory](../README.md): register location.

[Planning baseline](../../02-planning/Horizon_Community_Bank_Project_Planning_Baseline.md), the two cited approved policies, Sprint 1 requirements and tests remain unchanged.
