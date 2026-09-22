# Sprint 3 Executable Implementation Package 2 — Implementation Record & Evidence Audit

Status: **Sprint 3 Executable Implementation Package 2 — Approved by Project Owner — Committed locally** (2026-09-22). Approval covers the audited offline transformation, data quality, quarantine, lineage, replay, reconciliation, writer, and processing orchestration implementation described here. Sprint 3 remains in progress and is **not approved**. PD02 database execution, PostgreSQL connections, remote synchronization, Package 3, and production publication remain **unauthorized**.

## 1. Scope & Authority

This package establishes the second executable layer for Horizon Community Bank Analytics, implementing the offline transformation, data quality, quarantine, lineage, and curated processing pipeline under `src/horizon_pipeline/processing/`.

Following Project Owner review, every newly implemented operational constant, algorithm, and boundary rule was subjected to an evidence-level audit against the approved documentary baselines (Sprint 1, Sprint 2, Gateway 3, and Sprint 3 Physical Design). No assumption, fixture convention, or design candidate is permitted to act as an active production rule unless explicitly established by approved baselines.

---

## 2. Implementation Evidence Matrix

The following matrix records the evidence audit for every operational rule, algorithm, and boundary condition implemented in Package 2:

| Rule / Feature Area | Authoritative Repository Evidence (Path & Identifier) | Classification | Production Execution Mode Behavior | Fixture Execution Mode Behavior |
| --- | --- | --- | --- | --- |
| **Currency: ISO 4217 Format** | `docs/03-execution/sprint-02-data-design/field-level-dictionary.md` line 16 ("Currency is exactly three uppercase ISO 4217 characters") | **APPROVED_PRODUCTION** | Active: Validates `^[A-Z]{3}$`; rejects non-compliant codes with `DQ-D07` ERROR. | Active: Validates `^[A-Z]{3}$`; rejects non-compliant codes with `DQ-D07` ERROR. |
| **Currency: Whitelist** | `docs/03-execution/sprint-03-physical-design/synthetic-source-contract.md` line 45; `synthetic-data-specification.md` line 127 | Production: **PENDING**<br>Fixture: **FIXTURE_ONLY** | Fails closed on production whitelist enforcement (whitelist PENDING confirmation). Currency segregation enforced without netting. | Enforces approved fixture currencies `{"USD", "EUR"}`. Rejects other currencies with `DQ-D07` ERROR. |
| **Currency: USD-Only Assumption** | Audited against entire baseline; no USD-only restriction exists; multi-currency (USD, EUR) in baseline | **UNSUPPORTED** | Demoted/Removed: USD-only whitelist is prohibited in production. | Fixture supports both USD and EUR without cross-currency netting. |
| **Retention: Quarantined Row Payload** | `docs/03-execution/sprint-02-data-design/retention-and-disposal-design.md` (DD-10) line 69 ("Quarantined row payloads follow the same 24-month business/event anchor...") | **APPROVED_PRODUCTION** | Active: Quarantined records default to `RetentionCategory.ANALYTICAL_24M`. | Active: Quarantined records default to `RetentionCategory.ANALYTICAL_24M`. |
| **Retention: Audit / Lineage Metadata** | `docs/03-execution/sprint-02-data-design/retention-and-disposal-design.md` (DD-10) lines 45, 70 ("Seven-year quality logs retain reason, counts, amounts, tokens and disposition, not the quarantined payload") | **APPROVED_PRODUCTION** | Active: Execution run metadata, lineage events, and quality summary logs follow `RetentionCategory.AUDIT_7Y`. | Active: Execution run metadata, lineage events, and quality summary logs follow `RetentionCategory.AUDIT_7Y`. |
| **Masking: Fixed Mask + Final 4** | `docs/03-execution/sprint-02-data-design/security-and-masking-design.md` (DD-08) lines 41-42; `data-quality-and-reconciliation.md` line 33 (`DQ-D08`) | **APPROVED_PRODUCTION** (Framework/Rule) | Active framework; unconfirmed physical algorithm calls fail closed with `PendingContractError`. | Implemented with synthetic masking logic for test execution. |
| **Masking: Concrete String Formats** | `docs/03-execution/sprint-02-data-design/security-and-masking-design.md` (DD-08) line 37 ("exact transformation contract and residual reidentification checks require review before release") | **FIXTURE_ONLY** / **PENDING** | Fails closed: Calling `mask_tax_identifier`, `mask_account_id`, `mask_customer_name` raises `PendingContractError`. | Evaluates synthetic formats (`***-**-1234`, `******1234`, `***oe`). |
| **Natural Keys: Logical Composite Keys** | `scripts/reconcile_source_fields.py` lines 16-42; `docs/03-execution/sprint-02-data-design/field-level-dictionary.md` line 21 | **APPROVED_PRODUCTION** (Logical) | Active logical key definitions across all 27 sections. | Active logical key definitions across all 27 sections. |
| **Natural Keys: Physical Column Extraction** | `docs/03-execution/sprint-03-physical-design/physical-delivery-manifest.md` (PD-01) | Production: **PENDING**<br>Fixture: **FIXTURE_ONLY** | Fails closed: Physical CSV headers are PENDING (0 active production headers under PD-01); emits `DQ-D02` CRITICAL. | Extracts natural keys from confirmed fixture payload columns. |
| **Data Quality: Catalog Rules (DQ-D01..DQ-D13)** | `docs/03-execution/sprint-02-data-design/data-quality-and-reconciliation.md` (DD-09) lines 25-38 | **APPROVED_PRODUCTION** (Framework) | Evaluates structural/integrity rules; fails closed where underlying physical contracts are PENDING. | Evaluates full catalog against synthetic test packages. |
| **Quarantine Severity & Publication (PUB-D01)** | `docs/03-execution/sprint-02-data-design/data-quality-and-reconciliation.md` (DD-09) lines 42-45 | **APPROVED_PRODUCTION** | Active: `CRITICAL` or `FATAL` findings strictly block publication (`disposition=QUARANTINED`, `passed=False`). No override permitted. | Active: `CRITICAL` or `FATAL` findings strictly block publication (`disposition=QUARANTINED`, `passed=False`). |
| **Batch Replay & Revision Tracking** | `docs/03-execution/sprint-02-data-design/data-quality-and-reconciliation.md` (DD-09) lines 17-21, 26 | **APPROVED_PRODUCTION** | Active: Same revision + same checksum = Replay (INFO); same revision + diff checksum = Conflict (CRITICAL); stale revision = Stale (CRITICAL). | Active: Same revision + same checksum = Replay (INFO); same revision + diff checksum = Conflict (CRITICAL); stale revision = Stale (CRITICAL). |
| **Reconciliation: RC-D01 Row Balance** | `docs/03-execution/sprint-02-data-design/data-quality-and-reconciliation.md` (DD-09) line 37; `synthetic-source-contract.md` line 80 | **APPROVED_PRODUCTION** | Active: Exact row equation `received = accepted + quarantined + approved_excluded`; non-zero residual emits `RC-D01` CRITICAL. | Active: Exact row equation `received = accepted + quarantined + approved_excluded`; non-zero residual emits `RC-D01` CRITICAL. |
| **Reconciliation: RC-D02 Financial Balance** | `docs/03-execution/sprint-02-data-design/data-quality-and-reconciliation.md` (DD-09) line 38; `field-level-dictionary.md` line 16 | Production: **PENDING**<br>Fixture: **FIXTURE_ONLY** | Preserves Package 1 boundary: 0 active production controls, 7 pending, tolerance is `None / PENDING`. Residual calculated via scale-4 Decimal; status `PENDING_TOLERANCE`. | Evaluates scale-4 exact-zero residual on fixture controls (`is_fixture=True`). |
| **Domain Value Mappings (PD-06)** | `docs/03-execution/sprint-03-physical-design/canonical-mapping-registry.md` (PD-06) | Production: **PENDING**<br>Fixture: **FIXTURE_ONLY** | Preserves Package 1 boundary: 23 domain groups remain PENDING; 0 active production mapping rows. Fails closed against `MasterProductionRegistry`. | Binds to isolated fixture mapping entries (`FIXTURE_MAP_V1`). |

---

## 3. Processing Pipeline Architecture

The offline processing engine operates in sequential stages:

```
Validated CSV Section Payloads & manifest.json
  ↓
[Stage 1] Contract Engine Binding & Mode Verification
  ├─ ExecutionMode.PRODUCTION → Fails closed against MasterProductionRegistry (PENDING)
  └─ ExecutionMode.FIXTURE → Binds to isolated test fixture contracts
  ↓
[Stage 2] Raw Record Ingestion & Parsing
  └─ Immutable RawRecord instances per CSV row with source, section, record_id, revision, fields
  ↓
[Stage 3] Batch Delivery & Replay State Tracking (DD-09)
  ├─ Identical payload delivery (same revision + checksum) → Emits DQ-D02 INFO finding
  ├─ Conflicting payload delivery (same revision + different checksum) → Emits DQ-D02 CRITICAL finding
  ├─ Superseding revision (higher revision) → Registers new active batch
  └─ Stale revision (lower revision) → Emits DQ-D02 CRITICAL finding
  ↓
[Stage 4] Natural Key Identity & In-Batch Deduplication (DD-09)
  ├─ In PRODUCTION mode → Fails closed with DQ-D02 CRITICAL (unconfirmed physical headers)
  ├─ In FIXTURE mode exact duplicate rows (identical key & identical fields) → Emits DQ-D02 INFO
  └─ In FIXTURE mode conflicting duplicate rows (identical key & different fields) → Quarantined, emits DQ-D02 CRITICAL
  ↓
[Stage 5] Data Quality Evaluation (DD-09 Rule Catalog)
  ├─ DQ-D03: Required field presence & non-blank validation
  ├─ DQ-D04: Referential integrity (customer, account, loan, branch)
  ├─ DQ-D07: Monetary precision (scale <= 4) & ISO 4217 3-letter uppercase format (fixture whitelist: USD, EUR)
  ├─ DQ-D08: Valid date formats (YYYY-MM-DD) & non-future business date
  ├─ DQ-D09: America/Chicago temporal parsing & UTC microsecond normalization
  └─ DQ-D10: Canonical status code resolution via StatusMappingRegistry (PD-06)
  ↓
[Stage 6] Deterministic Transformation & Masking (DD-08, DD-10)
  ├─ In PRODUCTION mode → Masking calls fail closed with PendingContractError
  ├─ Error findings → Quarantined to QuarantineLedger (RetentionCategory.ANALYTICAL_24M payload)
  └─ Clean records → Transformed to Curated Domain Entities (RetentionCategory.ANALYTICAL_24M)
  ↓
[Stage 7] Lineage Capture (DD-09, DD-10)
  └─ Immutable LineageRecord mapping each record to source, checksum, rules, disposition (RetentionCategory.AUDIT_7Y)
  ↓
[Stage 8] Exact Reconciliation (DD-09 RC-D01, RC-D02)
  ├─ RC-D01: Row balance equation: received = accepted + quarantined + approved_excluded
  └─ RC-D02: Financial balance equation: source_total = accepted + quarantined + approved_excluded
  ↓
[Stage 9] Publication Gate Evaluation (PUB-D01)
  └─ CRITICAL / FATAL findings, completeness failures, or reconciliation residuals block publication
  ↓
[Stage 10] Deterministic Output Artifact Serialization
  └─ accepted/*.json, quarantine/*.json, lineage/*.json, dq_summary.json, reconciliation_summary.json, manifest.json
```

---

## 4. Implemented Modules

All Package 2 modules are located under `src/horizon_pipeline/processing/`:

### 4.1 Domain & Record Models (`records.py`)
- `ExecutionMode`: Enum defining `FIXTURE` and `PRODUCTION`.
- `RetentionCategory`: Enum defining `ANALYTICAL_24M` and `AUDIT_7Y`.
- `RecordDisposition`: Enum defining `ACCEPTED`, `QUARANTINED`, and `EXCLUDED`.
- `RawRecord`: Frozen dataclass capturing raw row content, source, section, revision, and row index.
- Curated Domain Entities: Frozen, typed dataclasses with explicit lineage IDs and retention classifications:
  - `CuratedCustomer` (SRC-01): Governed masked tax identifier, customer segment, primary branch.
  - `CuratedAccount` (SRC-01): Masked account ID, account type, status, branch attribution.
  - `CuratedAccountHolder` (SRC-01): Account-customer relationship and role.
  - `CuratedTransaction` (SRC-01): Exact scale-4 Decimal amount, canonical transaction status, posted timestamp.
  - `CuratedLoan` (SRC-02): Original principal (scale 4), loan type, origination date, branch.
  - `CuratedBorrower` (SRC-02): Loan-borrower relationship and role.
  - `CuratedPosition` (SRC-02): Outstanding principal (scale 4), days past due, loan status.
  - `CuratedPayment` (SRC-02): Exact scale-4 Decimal payment amount, canonical status, paid/posted instants.
  - `CuratedFraudAlert` (SRC-03): Alert severity, case status, created timestamp.
  - `CuratedComplaint` (SRC-04): Customer complaint, priority, status, created timestamp.
  - `CuratedBranch` (SRC-05): Branch reference entity, region, valid from date.
  - `CuratedSupportingRecord`: Supporting, event, assignment, and schedule entities without dedicated domain models.

### 4.2 Transformation & Masking Engine (`transform.py`)
- `mask_tax_identifier`: In `ExecutionMode.PRODUCTION`, raises `PendingContractError` citing DD-08 lines 37, 41-42. In `ExecutionMode.FIXTURE`, preserves last 4 digits (`***-**-1234`).
- `mask_account_id`: In `ExecutionMode.PRODUCTION`, raises `PendingContractError`. In `ExecutionMode.FIXTURE`, returns fixed prefix plus final 4 digits (`******1234`).
- `mask_customer_name`: In `ExecutionMode.PRODUCTION`, raises `PendingContractError`. In `ExecutionMode.FIXTURE`, masks name preserving final characters (`***oe` or `[REDACTED]`).
- `parse_scale4_decimal`: Strict scale-4 Decimal parsing; rejects non-numeric or scale >4 inputs.
- `parse_iso_date`: Strict `YYYY-MM-DD` parsing.
- `parse_instant_utc`: Parses ISO-8601 timestamps with offset normalization to UTC.
- `parse_date_or_instant`: Helper for fields accepting dates or timestamps.
- Entity transformers: Deterministically map `RawRecord` instances to curated entities, enforcing mode checks on masking functions and resolving canonical codes via `StatusMappingRegistry`.

### 4.3 Data Quality Engine (`quality.py`)
- Evaluates rules `DQ-D01` through `DQ-D13` against raw records.
- Enforces mandatory fields across all 27 sections via `SECTION_REQUIRED_FIELDS`.
- Validates currency format: enforces 3-letter uppercase ISO 4217 in all modes; in `ExecutionMode.FIXTURE`, validates against approved fixture currencies `{"USD", "EUR"}`.
- Validates monetary amounts with exact scale-4 Decimal parsing.
- Evaluates referential integrity for customer, account, loan, and branch relationships.
- Records structured `RecordFinding` instances with rule ID, field, severity, disposition, observed value, and expected rule.
- Produces consolidated `DQSummary` with cell-level completeness accounting.

### 4.4 Quarantine Ledger (`quarantine.py`)
- `QuarantinedRecord`: Frozen dataclass capturing complete raw fields, findings, quarantine timestamp, and `RetentionCategory.ANALYTICAL_24M` (DD-10 line 69).
- `QuarantineLedger`: Preserves quarantined records, calculates section monetary totals for financial reconciliation, and exports JSON-serializable dictionaries.

### 4.5 Identity & Deduplication Engine (`identity.py`)
- `RecordIdentityEngine`: Enforces composite natural keys per section matching the baseline logical dictionary (`scripts/reconcile_source_fields.py`).
- In `ExecutionMode.PRODUCTION`, fails closed with `DQ-D02` CRITICAL because physical CSV headers remain PENDING under PD-01.
- In `ExecutionMode.FIXTURE`:
  - Exact duplicates (same key, identical fields): deduplicated, emits `DQ-D02` INFO.
  - Conflicting duplicates (same key, different fields): quarantines conflicting records, emits `DQ-D02` CRITICAL.

### 4.6 Replay & Batch State Tracker (`replay.py`)
- `BatchStateTracker`: Tracks deliveries by `(source, section, business_date, revision, checksum)`.
- Enforces delivery state transitions:
  - New delivery: registers active delivery.
  - Identical delivery (same revision, identical checksum): emits `DQ-D02` INFO.
  - Conflicting delivery (same revision, different checksum): emits `DQ-D02` CRITICAL.
  - Superseding delivery (higher revision): updates active delivery.
  - Stale delivery (lower revision): emits `DQ-D02` CRITICAL.

### 4.7 Lineage Ledger (`lineage.py`)
- `LineageRecord`: Frozen dataclass linking each curated or quarantined record back to `source_system`, `section`, `source_record_id`, `source_checksum`, transformation rules applied, disposition, and retention category (`RetentionCategory.AUDIT_7Y` for run metadata per DD-10 line 70).
- `LineageLedger`: Preserves complete lineage records and provides fast lookup by lineage ID.

### 4.8 Offline Reconciliation Engine (`reconciliation.py`)
- Implements exact scale-4 Decimal arithmetic for reconciliation.
- `RC-D01` Row Reconciliation: Validates `received = accepted + quarantined + approved_excluded` per section; non-zero residual emits `RC-D01` CRITICAL.
- `RC-D02` Financial Reconciliation: Validates `source_total = accepted + quarantined + approved_excluded`; in production mode, unresolved tolerance reports `PENDING_TOLERANCE`; in fixture mode, exact zero tolerance is verified.

### 4.9 Output Artifact Writer (`writer.py`)
- `OutputArtifactWriter`: Deterministically writes run outputs to disk with sorted keys, standard indent, and UTF-8 encoding.
- Computes SHA-256 digest for each output artifact and records digests in `artifact_checksums`.

### 4.10 Offline Processing Orchestrator (`engine.py`)
- `OfflineProcessingEngine`: Coordinates end-to-end execution across all stages, enforcing mode-specific binding, disposition determination, publication gating, and output writing.

---

## 5. Contract State & Execution Modes

| Feature | ExecutionMode.PRODUCTION | ExecutionMode.FIXTURE |
| --- | --- | --- |
| Contract Registry | `MasterProductionRegistry` | Isolated test fixture registries |
| PD-01 Physical Headers | 27 sections PENDING (fails closed) | 27 fixture contracts active |
| PD-02 Schema Contracts | 27 schemas PENDING (fails closed) | 27 fixture schemas active |
| PD-04 Applicability | 51 predicates PENDING (fails closed) | Active fixture predicates |
| PD-05 Financial Controls | 7 controls PENDING; tolerance `None / PENDING` | Fixture controls; exact-zero tolerance (`is_fixture=True`) |
| PD-06 Status Mappings | 23 groups PENDING (fails closed) | Fixture mappings active |
| Masking Algorithms | Fails closed (`PendingContractError`) | Active synthetic masking |
| Currency Whitelist | Production whitelist PENDING; ISO format validated | Active fixture whitelist (`USD`, `EUR`) |
| Natural Key Identity | Fails closed (`DQ-D02` CRITICAL) | Active composite natural key dedup |
| Disposition on Pending | `RecordDisposition.QUARANTINED`, `passed=False` | `RecordDisposition.ACCEPTED`, `passed=True` (on valid data) |

---

## 6. Verification Evidence

### 6.1 Test Suite Results
- Test discovery: `python -m unittest discover -s tests -v` executed **135 tests**:
  - **135 passed**, 0 failed, 0 errors, 0 skipped.
  - Package 1 baseline tests: 90 passed (including 15 PD-07 temporal cases and 5 PD-05 tolerance boundary tests).
  - Package 2 new tests: 45 passed across 10 dedicated test modules:
    - `test_processing_records.py`: 6 tests (immutability, enums, retention categories)
    - `test_processing_transform.py`: 9 tests (masking, scale-4 parsing, entity transformers, status mapping, production fail-closed on masking)
    - `test_processing_quality.py`: 7 tests (DQ-D03, DQ-D04, DQ-D07 scale and ISO format/fixture whitelist, DQ-D08, DQ-D09, DQ-D10)
    - `test_processing_quarantine.py`: 3 tests (ledger recording, 24M analytical retention, monetary summation)
    - `test_processing_identity.py`: 5 tests (natural keys, exact dedup, conflicting dedup, composite keys, production fail-closed)
    - `test_processing_replay.py`: 4 tests (new, identical replay, conflicting revision, superseding/stale)
    - `test_processing_lineage.py`: 2 tests (lineage recording and lookup)
    - `test_processing_reconciliation.py`: 4 tests (RC-D01 row balance, RC-D02 financial balance, pending tolerance)
    - `test_processing_writer.py`: 1 test (artifact structure, JSON determinism, SHA-256 digests)
    - `test_processing_e2e.py`: 8 tests (passing fixture flow, production fail-closed, mixed quarantine with 24M retention, EUR acceptance, production masking fail-closed, production natural key fail-closed, replay/conflict, registry isolation)

### 6.2 Backward Compatibility
- `python -m unittest tests/test_intake.py`: 11/11 tests pass.
- `python scripts/reconcile_source_fields.py`: exactly 27 sections and 333 logical target field rows verified.

---

## 7. Scope Boundaries, Prohibitions & Package 3 Recommendation

### 7.1 Scope Boundaries & Constraints
- **Approval / checkpoint boundary**: Project Owner approved Package 2 through `/approve sprint-3-package-2`, authorizing its local checkpoint commit. Push, merge, PR creation, Package 3, and remote synchronization remain unauthorized.
- **No PostgreSQL / PD02**: Database execution remains unauthorized; no database migrations or connections initiated.
- **No Remote Services**: No external services, cloud providers, or remote repositories connected.
- **Dependencies Unchanged**: Implementation uses Python standard library exclusively; no third-party packages installed.
- **Package 3 Unauthorized**: Analytical marts and subsequent processing packages have not been started.

### 7.2 Package 3 Scope Framing
When authorized, Package 3 must **NOT** be framed as an unapproved composite "Customer Risk Scoring" engine. Instead, it must strictly implement:
1. **Governed Condition Evaluation**: Automated evaluation of the 5 approved risk conditions defined in DD-04 and DD-09:
   - `RC-01`: Large Cash / Velocity Threshold Conditions
   - `RC-02`: High-Severity Fraud Alert Exposure Conditions
   - `RC-03`: Serious Loan Delinquency Conditions (DPD >= 90)
   - `RC-04`: Repeat Escalated Customer Complaint Conditions
   - `RC-05`: Account Restriction and Frozen Status Conditions
2. **Deterministic KPI Aggregations**: Computation of the 10 approved core banking KPIs (K01 through K10) using exact scale-4 Decimal arithmetic.
3. **Dimensional Analytical Marts**: Star-schema curated dimensional tables (customers, accounts, loans, branches, calendar) supporting downstream reporting without modifying raw evidence.
