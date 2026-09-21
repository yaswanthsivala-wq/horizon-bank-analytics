# CR-002 — Baseline lifecycle corrections

Recorded retroactively: 2026-09-20. Documentation-only disclosure; protected baseline files are not edited or reverted. Record owner and sponsor confirmation: Pending confirmation. No approval status changes.

## Reason and evidence

The earlier "unchanged blob IDs" statement applied to commit `ad33a92` and is superseded by this record for the later baseline. It must not be read as byte-preservation through `cbd698d`.

Reviewed commands:

```text
git diff 5de8b06 cbd698d -- docs/01-initiation
git diff ad33a92 cbd698d -- docs/02-planning/Horizon_Community_Bank_Project_Planning_Baseline.md
git log --oneline 5de8b06..cbd698d -- docs/01-initiation docs/02-planning
```

The relevant correction commits are `b44fc5b` (baseline/lifecycle reconciliation) and `dff1cf1` (Sprint 1 BA approval). Both touch the three Initiation Markdown files and the Planning baseline listed below. The log also returns `f77c208` and `456a69e` for Planning/Sprint 1 integration, and `cbd698d` for the Planning README's G3/lifecycle update. These additional log entries are disclosed; the hunk audit below uses precisely the two requested comparison ranges. The Planning README is outside those two diff targets and remains protected.

## Hunk classification

S = lifecycle/status wording; C = business content (including mixed business-content/status hunks); ? = unclear. Each row is one default-context Git diff hunk, identified by its old/new line coordinates, not an inferred individual edit.

| Hunk | File | Old/new range | Class | Evidence and rationale |
| --- | --- | --- | --- | --- |
| H01 | `docs/01-initiation/README.md` | `-1,25 +1,27` | C | Replaces pending business context with problems, targets, delivery scope and constraints as well as lifecycle wording. |
| H02 | `docs/01-initiation/project-charter.md` | `-2,55 +2,98` | C | Adds purpose, business problems/objectives, Release 1 scope/exclusions, assumptions, constraints and approval evidence; also updates lifecycle wording. |
| H03 | `docs/01-initiation/stakeholder-register.md` | `-2,41 +2,36` | C | Adds nine fictional role responsibilities and approval authorities, assignment limits and governance content; also updates lifecycle wording. |
| H04 | `docs/02-planning/Horizon_Community_Bank_Project_Planning_Baseline.md` | `-14,6 +14,8` | S | Adds dated Planning/Sprint 1 lifecycle status. |
| H05 | `docs/02-planning/Horizon_Community_Bank_Project_Planning_Baseline.md` | `-314,7 +316,7` | S | Changes G2 evidence from Sponsor approval of this plan to Approved by the user September 9, 2026. |
| H06 | `docs/02-planning/Horizon_Community_Bank_Project_Planning_Baseline.md` | `-322,7 +324,9` | S | Reframes Execution entry criteria as retained original criteria and records G2 status; criteria themselves unchanged. |
| H07 | `docs/02-planning/Horizon_Community_Bank_Project_Planning_Baseline.md` | `-330,7 +334,9` | S | Renames §21 Original Planned Execution Queue and adds BA artifact/status links; queue items unchanged. |
| H08 | `docs/02-planning/Horizon_Community_Bank_Project_Planning_Baseline.md` | `-341,5 +347,7` | S | Replaces pending Planning footer with recorded Planning/Sprint 1 approval and synchronization status. |

Summary: **5 S / 3 C / 0 ? hunks**. Classification describes textual changes, not whether business content is substantively incorrect or newly approved.

## Impact and recommendation

The Initiation comparisons contain substantive additions relative to the earlier placeholder-like baseline, so they cannot all be labelled status-only. The Planning baseline comparison changes lifecycle/gate/status framing while preserving the shown business criteria and queue items. Retain existing content and request sponsor confirmation of the three C hunks; do not revert or silently recertify historical approvals. Schedule, security and downstream implementation impact: Pending confirmation.

## Pending sponsor confirmation

- H01: Initiation README business context, targets, scope and constraints.
- H02: Project charter business purpose, objectives, scope, exclusions, assumptions and constraints.
- H03: Stakeholder register role responsibilities and approval authorities.

The later documents attribute content to user-supplied approved material, but this retrospective diff review does not independently establish the original approval evidence for every added business statement. Sponsor confirmation of these content hunks remains Pending confirmation.

## Approval evidence and documents updated

The Git history establishes when these textual changes entered the repository. Dated approval statements remain in their original documents; no new sponsor, Risk or Compliance approval is asserted.

Only this CR-002 record and its [Monitoring and Control inventory](../README.md) reference are added for this finding. Initiation, Planning and Sprint 1 files remain byte-identical to the R1 preflight.

## Project-owner disposition — 2026-09-21

The requesting user confirmed Option A for H01, H02 and H03 as intended reconciled documentation and clarified H05's historical G2 authority. See [project-owner decisions and Planning supplement traceability](CR-002-project-owner-decisions-2026-09-21.md). The G2 approval date remains 2026-09-09; this authority clarification is dated 2026-09-21. The original body, pending-confirmation statements and hunk classification above remain unchanged as historical evidence. No independent bank/persona approval, new gate approval or implementation authorization is asserted.
