# Combined integration candidate validation — 2026-09-21

Branch: `integration/r1-cr002-wp-pd01`. Validation date: 2026-09-21. Status: candidate prepared for review; fresh static validation completed; approval pending. No independent review is claimed.

## Source commits and integration method

| Input | Commit |
| --- | --- |
| Approved G3 baseline | `cbd698dbcf7b1895939ea4f3be4d16150a59d904` |
| R1 remediation | `50f4b3796752b49d82d8693dec9af4bd16f61edc` |
| CR-002 decisions / candidate HEAD | `d8bd6d275bd2f4a93cc882004e4e6ee7f804f9f6` |
| Preserved WP-PD01 source | `6fed2d70906b91418e6d4f710c43d15c8697baa5` |

Working-tree content integration: copied the WP-PD01 delta relative to G3 into the CR-002-based worktree, with explicit reconciliation of README, PROJECT_STATUS, CHANGELOG and Monitoring and Control README. The non-overlapping WP-PD01 files are byte-identical to the clean preserved worktree and their normalized bytes match the source commit. No Git merge, rebase, cherry-pick, staging or commit was performed. No index conflicts were created. WP-PD01 is a preserved source commit, not an ancestor of current HEAD; content inclusion must not be misrepresented as merge ancestry.

Overlap resolutions: preserve R1 source clarification and all dated delivery/decision entries; add current dispositions distinguishing logical approval from authored/not-executed WP-PD01; keep old statuses as historical; place WP-PD01 September 17 before G3 September 17 and after September 20/21 corrections in newest-first CHANGELOG. Keep the original historical changelog entry texts exactly once.

Location follows the Monitoring and Control quality-reviews convention. Its empty placeholder is removed under AGENTS.md; the other deletion, sql/.gitkeep, is the preserved WP-PD01 deletion. No business/data files are deleted.

## Fresh validation results

Fresh checks executed on 2026-09-21 against the combined working tree. All available checks passed. The external checker's initial aggregate FK assertion accidentally referenced the Git-ref list; that checker defect was corrected and the checks rerun without changing candidate content.

| Required check | Fresh result |
| --- | --- |
| 1. Ancestry | G3 is an ancestor of R1; R1 is an ancestor of CR-002; candidate HEAD equals CR-002. G3 is an ancestor of preserved WP-PD01. WP-PD01 is not an ancestor of candidate HEAD: content integration only. |
| 2. Inventory | 84 base files; 95 candidate files; exactly 5 tracked modifications, 2 placeholder deletions and 13 new files; no staged changes. |
| 3. Deletions | Only sql/.gitkeep and quality-reviews/.gitkeep; both replaced by substantive content. |
| 4-5. R1 and CR-002 | Artifacts retained; all existing change-control records byte-identical. |
| 6-7. WP-PD01 and foundation | All 13 non-overlapping copied files byte-identical to the preserved clean worktree, including execution README and foundation SQL; original physical-design validation retained. |
| 8-9. Protected content | SHA-256 comparison of 77 unaffected pre-existing files passed; Initiation, Planning, Sprint 1, approved Sprint 2 and G3 evidence unchanged. |
| 10. Relationships | Register matches dictionary: 203 explicit FK references, 195 entity pairs and 240 FK field rows. |
| 11-12. Owner decisions | Original H01-H03 confirmations and H05 authority clarification retained byte-identically; September 9 historical G2 date and September 21 clarification remain distinct. |
| 13. Markdown links | 62 Markdown files; 403 local links, including 3 anchor references; zero broken targets/anchors. |
| 14-15. Tables and fences | 292 tables checked for consistent column counts; zero errors; no unmatched code fences. |
| 16. Mermaid | 15 blocks structurally checked; no block-header or relationship-edge errors. Original ERD covers 41 entities; dependency diagrams cover 68 additional entities, sizes 19/20/18/3/8; all 109 covered. Mermaid module/CLI unavailable, so no parser-based syntax certification. |
| 17. Whitespace | git diff --check passed. |
| 18. SQL static | 70 statements; 8 schemas; 12 NOLOGIN/NOSUPERUSER/NOBYPASSRLS roles; btree_gist declaration; only audit.schema_migration table; transaction wrapper and quote/parenthesis balance passed; no out-of-scope statement starts. No SQL parser installed; no SQL executed. |
| 19. Sensitive/runtime content | Added-content scans found no private keys, token patterns, AWS access-key patterns, email addresses or SSN-shaped values. Inventory contains only expected Markdown and preserved SQL additions; no generated/runtime data. Pattern checks are not an exhaustive secret audit. |
| 20. Lifecycle | Current dispositions distinguish logical approval, documentation corrections, owner confirmations and authored/not-executed physical design. All 22 CR-002-base changelog entries and the WP-PD01 entry preserved exactly once; 24 entries including this candidate entry, newest-first. |
| 21-22. Authorization | No PD02 artifacts/work or new gate approval; no G4, independent persona approval or runtime claims introduced. |

Fresh semantic counts: 109 logical entities; 982 distinct entity/field rows; retention covers all 109 exactly once with no missing/extra entities; field traceability covers all 982 with no missing/extra fields. Sprint 1: 8 stories, 32 acceptance criteria, 14 functional requirements, 9 nonfunctional requirements, 17 business rules and 35 scenarios.

Foundation SQL SHA-256: `0b0e8d97ffddeae421e77db12b259f2dac777669655535908408d61326d5afae` (working-tree bytes).

Protected refs were rechecked: main, origin/main and origin/checkpoint/sprint-02-g3-approved remain at the G3 SHA above; local/remote R1 and CR-002 branches remain at their source SHAs; local WP-PD01 remains at its preservation SHA. All three source worktrees remain clean. No stage, commit or push occurred.

## Limits and approval boundary

Static documentation and foundation SQL review only. No database connection, version inspection, SQL execution, dependency installation, fixture generation, ETL, deployment or runtime/security/performance test. Mermaid syntax will only be reported as machine-validated if an available parser actually runs; structural checks alone are not syntax certification.

Historical WP-PD01 333-link results, historical branch-at-validation text, pre-PD01 hashes and all Sprint 2/G3 records are preserved, not reused as evidence of the combined tree. The new results above apply to this candidate's current files only.

PD02 is not started and not authorized. No new gate approval, G4, business-policy change or independent persona approval. Main is not yet updated. The integration candidate remains unstaged/uncommitted/unpushed and awaits explicit approval. Original R1, CR-002 and WP-PD01 commits and branches remain unchanged.
