# Sprint 3 Package 3 Increment 4 Implementation Plan — Offline Pipeline Orchestration & Consolidated Packaging

Status: **Approved by Project Owner** (2026-09-25) via `/approve sprint-3-package-3-increment-4-plan`. Technical implementation authorized in controlled offline fixture increments.

---

## 1. Executive Summary & Scope Boundaries

### 1.1 Objectives
1. Implement a unified, deterministic pipeline runner (`ConsolidatedPipelineRunner`) and consolidated artifact packager (`ConsolidatedArtifactWriter`) that orchestrates the entire offline data flow:
   - Intake and contract validation (Package 1: `pipeline.py`).
   - Deduplication, data quality evaluation (DQ-D01..DQ-D13), quarantine, curated transformation, and exact reconciliation (Package 2: `processing/`).
   - Customer risk assessment correlation and classification across RC-01 through RC-05 (Package 3: `analytics/risk_orchestrator.py`).
   - Four dimensional analytical marts calculation for K01 through K10 (Package 3: `analytics/marts.py`).
   - End-to-end publication gating (`PUB-D01`) and deterministic JSON artifact writing with companion SHA-256 digests.
2. Bridge curated domain entities into customer risk assessments via a dedicated coordinator (`CustomerRiskOrchestrator`).
3. Enforce approved Project Owner decisions:
   - Quarantined package artifacts: diagnostic artifacts only (`quarantine/`, `lineage/`, `dq_summary.json`, `reconciliation_summary.json`, `manifest.json`, `manifest.json.sha256`); strictly omit `accepted/`, `risk/`, and `marts/`.
   - Manifest checksum companion: emit companion `manifest.json.sha256` for every written manifest.
   - Self-referential hash cycle prevention: `manifest.json` is strictly excluded from its own `artifact_checksums` map.

### 1.2 Strict Scope Boundaries & Governance Preservations
- **NO Database Execution (PD02 Unauthorized):** All orchestration, transformations, risk evaluations, and mart builds execute strictly in standard-library Python in-memory data structures and deterministic JSON file output. Zero PostgreSQL connection, migrations, or database queries.
- **Fail-Closed Production Boundaries:** All 27 physical headers, schemas, candidate predicates, financial controls, and mapping tables remain `PENDING`. When invoked with `ExecutionMode.PRODUCTION`, the orchestrated runner fails closed immediately, returning a quarantined result with zero output artifacts and zero downstream execution. Direct component-level invocations strictly raise `PendingContractError`.
- **Preservation of Untracked Baseline Artifact:** `package2-test-results.txt` remains untouched and untracked.
- **Preservation of Baseline Tests & Invariant:** All 223 existing passing tests (including 36 subtests) and the 27-section / 333-field reconciliation invariant must be 100% preserved.

---

## 2. Reconciled Architectural Blueprint & Policy Alignments

### 2.1 Reconciled Production Fail-Closed Behavior
To guarantee complete alignment between package-level orchestration and individual component safety guards:
1. **Package-Level Orchestration (`ConsolidatedPipelineRunner.run_package`):**
   - In `ExecutionMode.PRODUCTION`, the runner delegates intake to `OfflineProcessingEngine.process_package(..., execution_mode=ExecutionMode.PRODUCTION)`.
   - `OfflineProcessingEngine` evaluates contracts against `MasterProductionRegistry`. Because all 27 physical headers and schemas are `PENDING`, the engine generates fatal contract findings (`HDR-PENDING`, `SCH-PENDING`) and returns a `ProcessingResult` with `disposition = RecordDisposition.QUARANTINED`, `passed = False`, and empty `curated_entities`.
   - Upon detecting `passed is False` and `execution_mode == ExecutionMode.PRODUCTION`, the runner **immediately halts**:
     - **No downstream execution:** `CustomerRiskOrchestrator`, `KPIEngine`, and `AnalyticalMartsBuilder` are **never called**.
     - **Zero output artifacts:** No files or directories are created or written to disk under `output_dir`.
     - **Return Value:** Returns a `ConsolidatedRunResult` with `disposition=RecordDisposition.QUARANTINED`, `passed=False`, `risk_assessments=()`, `marts_result=None`, `artifact_checksums={}`, `manifest_path=None`, and `findings` populated with the pending contract findings.
2. **Component-Level Direct Invocations:**
   - If a caller directly invokes `CustomerRiskOrchestrator.assess_customers`, `KPIEngine.calculate_*`, or `MartBuilder.build_*` with `execution_mode=ExecutionMode.PRODUCTION`, they strictly raise `PendingContractError`.

### 2.2 Distinguishing Package-Level PUB-D01 from K06 Candidate Gating
The pipeline strictly decouples package-level ingestion acceptance from metric-level candidate gating:
1. **Package-Level Gate (`PUB-D01`):**
   - Evaluates overall package health:
     a. Manifest validation passed & all required payloads present with matching checksums.
     b. Zero `FATAL` or `CRITICAL` data quality findings.
     c. Required field completeness passed (`completeness_passed == True`).
     d. Exact row count (`RC-D01`) and financial (`RC-D02`) reconciliations balanced with zero residual (`0.0000`).
   - *Effect of Failure:* Entire package is marked `QUARANTINED`, `passed=False`, and all downstream analytical marts are suppressed from publication.
2. **Metric-Level Candidate Gating (K06 Currency Cohort):**
   - Evaluated during `mart_loan_delinquency_kpis` construction under DD-09 lines 78–80.
   - If a delinquent loan (`DPD > 30`) has `PRINCIPAL_MISSING` or quarantined `PRINCIPAL_NEGATIVE`:
     - Candidate publication is blocked **only for that specific currency and business-date cohort** (`k06_publication_status[currency] = KPIPublicationStatus.BLOCKED_CANDIDATE`).
     - In `mart_loan_delinquency_kpis`, K06 for that currency outputs `None` (`Unavailable`).
     - Non-defective currency cohorts (e.g. `EUR`) within the same package remain `PUBLISHED` with accurate non-zero sums.
     - A K06 candidate gating defect does **not** fail the package-level `PUB-D01` gate, does **not** quarantine the entire package, and does **not** suppress other marts (`mart_transaction_kpis`, `mart_customer_risk_kpis`, `mart_complaint_kpis`).

### 2.3 Deterministic Identifiers, Manifest Ordering & Replay Semantics
- **Deterministic `run_id`:** Caller may supply an explicit `run_id`. If `None`, derived deterministically from the SHA-256 of the manifest JSON:
  `run_id = f"RUN-{hashlib.sha256(manifest_json.encode('utf-8')).hexdigest()[:12].upper()}"`.
- **Deterministic `created_at_utc`:** Caller may supply an explicit `created_at_utc`. If `None`, defaults deterministically to midnight UTC of the manifest's business date:
  `datetime(manifest.business_date.year, manifest.business_date.month, manifest.business_date.day, 0, 0, 0, tzinfo=timezone.utc)`.
- **Deterministic JSON Ordering:** JSON outputs use `indent=2, sort_keys=True`. Collections are sorted by primary / dimensional keys across all files.
- **Replay Semantics (`BatchStateTracker`):**
  1. *Identical Retry:* Matching `(source, section, business_date, revision, checksum)`. Permitted idempotent re-execution; logged as `REPLAY-IDENTICAL`. Downstream risk and marts recomputed identically.
  2. *Conflicting Same-Revision Payload:* Matching revision but mismatched checksum. Tracked as `REPLAY-PAYLOAD-CONFLICT` (CRITICAL). Execution blocked; batch quarantined; downstream risk and marts halted.
  3. *Stale Revision:* Lower revision number. Tracked as `REPLAY-STALE-REVISION` (CRITICAL). Execution blocked; batch quarantined; downstream risk and marts halted.
  4. *Superceding Valid Revision:* Higher revision number. Registered as new active revision; supersedes previous run.

### 2.4 Missing Evidence Handling for RC-01–RC-05
Under DD-04 and DD-06, missing relationship, history, mapping, or publication evidence maps to `ConditionState.UNKNOWN` with reason codes.
Classification aggregation adheres strictly to the approved $t$ (triggered) and $u$ (unknown) count thresholds:
- If catalog version or classification rule version is missing/invalid: `RiskClassification.UNAVAILABLE` (Priority 1).
- If $t \ge 2$: `RiskClassification.PROVISIONAL_HIGH_RISK` (Priority 2), regardless of whether $u > 0$.
- If $t < 2$ and $t + u \ge 2$: `RiskClassification.INCOMPLETE_EVIDENCE` (Priority 3).
- If $t < 2$ and $t + u < 2$: `RiskClassification.NOT_HIGH_RISK` (Priority 4). Note: when $t=0$ and $u=1$, $t + u = 1 < 2$, so classification is confirmed `NOT_HIGH_RISK` because the single unknown condition cannot push $t \ge 2$.
- In `mart_customer_risk_kpis`, `incomplete_evidence_customer_count` and `unavailable_assessment_customer_count` are reported as distinct unknown cohorts and **never** conflated with `not_high_risk_customer_count`.

### 2.5 Manifest Checksum Map & Exclusion of `manifest.json`
- `manifest.json` contains `"artifact_checksums": { ... }` indexing all other generated artifacts.
- To prevent self-referential hash cycles, `manifest.json` is **strictly excluded** from its own `artifact_checksums` map.
- A companion file `manifest.json.sha256` is emitted alongside `manifest.json` containing `<sha256_hex> *manifest.json\n`.
- The SHA-256 digest of `manifest.json` is exposed on `ConsolidatedRunResult.manifest_checksum`.

### 2.6 Realistic Test Fixture Expectations
- Default synthetic data generated by `SyntheticBankingDataGenerator` contains 0 closed complaints, 0 past-due loans, and 0 fraud-linked transactions.
- Tests against default packages assert correct zero-count and `Unavailable` handling.
- Acceptance tests requiring non-zero metrics (e.g. K04 fraud alerts, K05 delinquency, K08 closed complaints) use **explicitly constructed synthetic fixture packages** with known scenarios.

---

## 3. Acceptance Criteria (Given–When–Then)

### AC-ORCH-01: End-to-End Fixture Passing Flow (Default Package)
- **Given** a valid synthetic 27-section package with revision 1,
- **When** executed via `ConsolidatedPipelineRunner.run_package(..., execution_mode=ExecutionMode.FIXTURE, output_dir=tmp_dir)`,
- **Then** overall disposition is `ACCEPTED` and `passed` is `True`,
- **And** all 27 sections are accepted, DQ completeness is 100%, and row/financial reconciliations balance to `0.0000`,
- **And** customer risk assessments are generated for all customers,
- **And** all four analytical marts are populated with valid records matching the input data,
- **And** all output files (curated, quarantine, lineage, risk, marts, manifest, companion digest) are written with verifiable SHA-256 digests.

### AC-ORCH-02: Fail-Closed Production Boundary
- **Given** any delivered package payload,
- **When** executed via `ConsolidatedPipelineRunner.run_package(..., execution_mode=ExecutionMode.PRODUCTION, output_dir=tmp_dir)`,
- **Then** the runner immediately fails closed,
- **And** the returned result has `disposition = RecordDisposition.QUARANTINED`, `passed = False`, `risk_assessments = ()`, and `marts_result = None`,
- **And** zero output files or directories are created under `output_dir`,
- **And** findings indicate pending physical header/schema contracts (`HDR-PENDING`, `SCH-PENDING`),
- **And** no downstream risk or mart calculation is executed.

### AC-ORCH-03: Publication Gating on Upstream Critical Quality Findings
- **Given** a package containing an unrecoverable critical DQ defect,
- **When** executed via `ConsolidatedPipelineRunner.run_package(..., output_dir=tmp_dir)`,
- **Then** publication gate `PUB-D01` triggers and sets overall disposition to `QUARANTINED` (`passed=False`),
- **And** only diagnostic artifacts are written (`quarantine/`, `lineage/`, `dq_summary.json`, `reconciliation_summary.json`, `manifest.json`, `manifest.json.sha256`),
- **And** `accepted/`, `risk/`, and `marts/` directories are strictly omitted from `output_dir`.

### AC-ORCH-04: K06 Currency-Cohort Candidate Gating Isolation
- **Given** a loan portfolio where one loan in currency USD has `DPD = 35` and missing principal (`PRINCIPAL_MISSING`), while loans in EUR are fully valid,
- **When** executed through the consolidated runner,
- **Then** the overall package disposition remains `ACCEPTED` (provided row/financial reconciliations balance),
- **And** in `mart_loan_delinquency_kpis`, K06 for USD is `None` with `k06_publication_status = BLOCKED_CANDIDATE`,
- **And** K06 for EUR is `PUBLISHED` with its accurate non-zero principal sum,
- **And** other marts (`mart_transaction_kpis`, `mart_customer_risk_kpis`, `mart_complaint_kpis`) are published normally.

### AC-ORCH-05: Complete Risk-Condition State Fixture & Exact t/u Classification
- **Given** customer risk assessment fixtures representing various combinations of condition states:
  - Customer A: $t = 2, u = 1$ (2 triggered, 1 unknown)
  - Customer B: $t = 1, u = 2$ (1 triggered, 2 unknown, $t + u = 3 \ge 2$)
  - Customer C: $t = 0, u = 1$ (0 triggered, 1 unknown, $t + u = 1 < 2$)
  - Customer D: $t = 0, u = 0$ (0 triggered, 0 unknown)
- **When** evaluated by `CustomerRiskOrchestrator`,
- **Then** Customer A classifies as `RiskClassification.PROVISIONAL_HIGH_RISK` ($t \ge 2$),
- **And** Customer B classifies as `RiskClassification.INCOMPLETE_EVIDENCE` ($t < 2, t + u \ge 2$),
- **And** Customer C classifies as `RiskClassification.NOT_HIGH_RISK` ($t < 2, t + u < 2$),
- **And** Customer D classifies as `RiskClassification.NOT_HIGH_RISK` ($t = 0, u = 0$),
- **And** in `mart_customer_risk_kpis`, Customer B is strictly counted under `incomplete_evidence_customer_count` and excluded from `not_high_risk_customer_count`.

### AC-ORCH-06: Non-Additive Relationship Exposure
- **Given** `mart_customer_risk_kpis` produced by the pipeline runner,
- **When** verifying the output records,
- **Then** `relationship_exposure_non_additive` is strictly `True` across all rows.

### AC-ORCH-07: Manifest Checksum Map & Companion Digest Verification
- **Given** a successful run producing output directory artifacts,
- **When** inspecting `manifest.json`,
- **Then** `manifest.json` is strictly excluded from `artifact_checksums`,
- **And** every other file written in `accepted/`, `quarantine/`, `lineage/`, `risk/`, and `marts/` is present in `artifact_checksums` with its exact SHA-256 digest,
- **And** companion file `manifest.json.sha256` correctly verifies the digest of `manifest.json`.

### AC-ORCH-08: Stale and Conflicting Batch Replay Gating
- **Given** an already-processed package with revision 1,
- **When** the runner receives the same revision with a different payload checksum or a lower revision number,
- **Then** `BatchStateTracker` blocks execution, returns `disposition=RecordDisposition.QUARANTINED`, and halts downstream risk and mart generation.

---

## 4. Implementation Inventory

| Module | Purpose | Key Classes / Functions |
|---|---|---|
| `src/horizon_pipeline/analytics/risk_orchestrator.py` | Bridges curated entities to customer risk assessments | `CustomerRiskOrchestrator` |
| `src/horizon_pipeline/processing/writer.py` | Enhanced output artifact writer for consolidated packaging | `OutputArtifactWriter` (enhanced with risk, marts, and companion sha256) |
| `src/horizon_pipeline/orchestration/runner.py` | Top-level consolidated pipeline runner | `ConsolidatedPipelineRunner`, `ConsolidatedRunResult` |
| `src/horizon_pipeline/orchestration/__init__.py` | Orchestration package initialization and exports | Exports `ConsolidatedPipelineRunner`, `ConsolidatedRunResult` |
| `src/horizon_pipeline/analytics/__init__.py` | Export update | Exports `CustomerRiskOrchestrator` |
| `src/horizon_pipeline/__init__.py` | Package-level export update | Exports runner and result types |
| `tests/test_orchestration_runner.py` | Full end-to-end tests across default and enriched fixtures | 4 tests |
| `tests/test_orchestration_mode_isolation.py` | Production fail-closed tests | 3 tests |
| `tests/test_orchestration_gating.py` | PUB-D01 gating and K06 cohort isolation tests | 4 tests |
| `tests/test_orchestration_risk_flow.py` | Risk condition correlation & t/u classification tests | 4 tests |
| `tests/test_orchestration_replay.py` | Replay protection, retry, and conflict tests | 3 tests |

---

## 5. Review & Authorization Gate

Approval recorded: **2026-09-25** by Project Owner via `/approve sprint-3-package-3-increment-4-plan`.
Execution proceeding under local offline fixture mode.
