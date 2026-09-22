"""Render a review inventory from the approved logical field dictionary.

This script never converts logical fields into asserted physical CSV headers.
"""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/03-execution/sprint-02-data-design"
SOURCE = BASE / "field-level-dictionary.md"
TARGET = ROOT / "docs/03-execution/sprint-03-physical-design/source-field-inventory.md"

SECTIONS = (
    ("SRC-01", "customers", "customer, customer_identity, customer_version", "source_system + source_customer_id; governed identity/version keys are resolved", "FR-01/02/03/05; US-01/02/08; RC-01/RC-05"),
    ("SRC-01", "accounts", "account", "source_system + source_account_id", "FR-01/02/03/05; K01-K04; RC-01/RC-05"),
    ("SRC-01", "holders", "account_customer", "account + customer + role + effective start", "DD-02; FR-03; RC-01/RC-05"),
    ("SRC-01", "transactions", "transaction", "source_system + source_transaction_id; version selected per publication", "K01-K04; RC-01; DD-05/06"),
    ("SRC-01", "account_restriction_state", "account_restriction_state", "source-qualified account + effective state version", "RC-05; DD-04/06"),
    ("SRC-01", "account_branch_assignment", "account_branch_assignment", "source_system + source_assignment_id; effective version", "DD-12; K01-K04"),
    ("SRC-02", "loans", "loan", "source_system + source_loan_id", "US-04; K05/K06; RC-03"),
    ("SRC-02", "borrowers", "loan_customer", "loan + customer + role + effective start", "DD-02; US-04; RC-03"),
    ("SRC-02", "positions", "loan_snapshot", "loan + business date + selected snapshot version", "DD-03; K05/K06; RC-03"),
    ("SRC-02", "payments", "loan_payment", "source_system + source_payment_id; immutable event version", "DD-11; US-04; K05/K06"),
    ("SRC-02", "loan_schedule", "loan_schedule", "source_system + source_schedule_id; version/effective interval", "DD-11; US-04"),
    ("SRC-02", "loan_obligation", "loan_obligation", "source_system + source_obligation_id; version", "DD-11; US-04"),
    ("SRC-02", "payment_allocation", "payment_allocation", "source_system + source_allocation_id + component; version", "DD-11; US-04"),
    ("SRC-02", "payment_unapplied", "payment_unapplied", "source-qualified payment + unapplied version", "DD-11; US-04"),
    ("SRC-02", "payment_adjustment", "payment_adjustment", "source_system + source_adjustment_id; version", "DD-11; US-04"),
    ("SRC-02", "loan_account", "loan_account", "source-qualified relationship ID; effective loan/account/role version", "DD-11; US-04"),
    ("SRC-02", "loan_branch_assignment", "loan_branch_assignment", "source_system + source_assignment_id; effective version", "DD-12; K05/K06"),
    ("SRC-03", "alerts", "fraud_alert", "source_system + source_alert_id", "RC-02; FR-07/08"),
    ("SRC-03", "fraud_alert_state", "fraud_alert_state", "source-qualified alert + effective state version", "RC-02; DD-04/06"),
    ("SRC-04", "complaints", "complaint", "source_system + source_complaint_id", "K08-K10; RC-04"),
    ("SRC-04", "complaint_snapshot", "complaint_snapshot", "complaint + business date + selected snapshot version", "DD-03; K08-K10; RC-04"),
    ("SRC-04", "complaint_history_event", "complaint_history_event", "source-qualified complaint + history event version", "DD-03/06; K08-K10"),
    ("SRC-04", "complaint_branch_assignment", "complaint_branch_assignment", "source_system + source_assignment_id; effective version", "DD-12; K08-K10"),
    ("SRC-05", "organizational_unit", "organizational_unit", "source_system + unit_type + source_id", "DD-12; FR-09/10"),
    ("SRC-05", "region", "region", "source_system + region_id + valid_from", "DD-12; FR-09/10"),
    ("SRC-05", "branches", "branch", "source_system + branch_id + valid_from", "DD-12; K01-K10"),
    ("SRC-05", "organizational_successor", "organizational_successor", "predecessor + successor + valid_from", "DD-12; FR-09/10"),
)

DICTIONARIES = {
    "customers": "segment RETAIL/SMALL_BUSINESS; identity crosswalk governed separately",
    "accounts": "account_type CHECKING/SAVINGS",
    "holders": "relationship_role PRIMARY/JOINT",
    "transactions": "transaction_type TRANSFER/PAYMENT/WITHDRAWAL/DEPOSIT; canonical status via DD-06 mapping; debit/credit direction",
    "account_restriction_state": "NONE/RESTRICTED/FROZEN/BLOCKED; RC-05 restricted mapping DD-06",
    "account_branch_assignment": "SERVICING/ORIGINATION",
    "loans": "loan_type PERSONAL/AUTO/MORTGAGE; canonical active/status mapping DD-06",
    "borrowers": "relationship_role PRIMARY/CO_BORROWER",
    "positions": "canonical loan status DD-06; DPD 0..36500",
    "payments": "PENDING/POSTED/FAILED/CANCELLED; POSTED posted_at policy DD-11",
    "loan_schedule": "DD-11 schedule/effective version and currency contract",
    "loan_obligation": "DD-11 component/currency and due_date contract",
    "payment_allocation": "PRINCIPAL/INTEREST/FEE components under DD-11",
    "payment_unapplied": "DD-11 source-confirmed unapplied amount state",
    "payment_adjustment": "REVERSAL/REFUND under DD-11",
    "loan_account": "REPORTING relationship under DD-11",
    "loan_branch_assignment": "SERVICING/ORIGINATION",
    "alerts": "fraud case OPEN/CLOSED; severity LOW/MEDIUM/HIGH/CRITICAL; RC-02 mapping DD-06",
    "fraud_alert_state": "fraud open/severity mapping DD-06",
    "complaints": "OPEN/IN_PROGRESS/REOPENED/CLOSED; Critical/High/Medium/Low; PHONE/WEB/BRANCH",
    "complaint_snapshot": "complaint status/priority DD-06; as-of DD-03",
    "complaint_history_event": "closure/reopening event DD-06",
    "complaint_branch_assignment": "RESPONSIBLE",
    "organizational_unit": "REGION/BRANCH",
    "region": "DD-12 effective region history",
    "branches": "DD-12 effective branch/region history",
    "organizational_successor": "DD-12 same-unit-type successor; no automatic access grant",
}


def read_entities():
    text = SOURCE.read_text(encoding="utf-8")
    blocks = re.split(r"(?m)^## ([a-z][a-z0-9_]*)\s*$", text)
    entities = {}
    for i in range(1, len(blocks), 2):
        name, body = blocks[i], blocks[i + 1]
        pk = re.search(r"Logical PK: `([^`]+)`", body)
        fields = []
        for line in body.splitlines():
            if line.startswith("| ") and not line.startswith("| Field ") and not line.startswith("| ---"):
                cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
                if len(cells) == 5:
                    fields.append(cells[:4])
        if pk and fields:
            entities[name] = (pk.group(1), fields)
    return entities


def main():
    entities = read_entities()
    lines = [
        "# SRC-01 through SRC-05 source-field reconciliation inventory",
        "",
        "Status: **Draft — not approved**. Derived from the approved G3 logical [field inventory](../sprint-02-data-design/field-level-dictionary.md), [synthetic source contract](../sprint-02-data-design/synthetic-source-contract.md), [source definitions](../sprint-02-data-design/source-system-definitions.md), and [contract trace](../sprint-02-data-design/synthetic-contract-traceability.md). These are logical target fields, not verified received CSV headers. `R`, `O`, and `C` below are **logical** required, optional and conditional states. Generated keys, derived values and review evidence must not be demanded from source rows merely because their target field is `R`. Field meaning/type text is preserved from the authoritative dictionary; consult that dictionary for complete cross-field rules.",
        "",
        "Every section has a source/entity/business-date/revision manifest identity, exact row count, checksum and required schema-version field under DD-01/DD-09. Actual schema-version **values**, physical header mapping, serialization and financial-control layout are **Pending confirmation** for all 27 sections. The synthetic contract fixes Chicago business-day/cutoff and correction/replay semantics; individual event dates, due dates, effective intervals and snapshot dates below retain their different meanings. Currency-separated signed scale-4 controls are required where applicable; exact control populations/physical fields remain Pending confirmation.",
        "",
        "| Source | Section | Logical target(s) | Documented business identity or grain | Requirement/KPI/risk trace |",
        "| --- | --- | --- | --- | --- |",
    ]
    for source, section, targets, key, refs in SECTIONS:
        lines.append(f"| {source} | `{section}` | {targets} | {key} | {refs} |")
    lines += ["", "## Cross-section contract dimensions", "", "The following dictionary/reference entries are approved synthetic logical domains and policies, not confirmed raw-code/header mappings. The approved status-mapping version must be applied before KPI/risk use; unrecognized values are not silently accepted.", "", "| Source | Section | Applicable approved dictionary/reference policy | Logical monetary fields requiring field/currency/status-separated controls where applicable |", "| --- | --- | --- | --- |"]
    for source, section, targets, _, _ in SECTIONS:
        money = []
        for target in targets.split(", "):
            money.extend(f"`{target}.{field}`" for field, kind, _, _ in entities[target][1] if kind.startswith("decimal"))
        lines.append(f"| {source} | `{section}` | {DICTIONARIES[section]} | {', '.join(money) if money else 'No decimal logical target field; count controls still apply'} |")
    for source, section, targets, key, refs in SECTIONS:
        lines += ["", f"## {source} / {section}", "", f"Logical target(s): `{targets}`. Source business identity/grain: {key}. Relevant trace: {refs}. Physical source key/header aliases: **Pending confirmation** where the G3 proposal has not been fixture-confirmed.", "", "| Logical target | Field | Logical type/format | Logical requiredness | Approved meaning/derivation |", "| --- | --- | --- | --- | --- |"]
        for target in targets.split(", "):
            if target not in entities:
                raise SystemExit(f"Missing dictionary entity: {target}")
            pk, fields = entities[target]
            for field, kind, required, meaning in fields:
                lines.append(f"| `{target}` | `{field}` | {kind} | {required} | {meaning} |")
    TARGET.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(SECTIONS)} sections, {sum(len(entities[t][1]) for _, _, targets, _, _ in SECTIONS for t in targets.split(', '))} logical target field rows")


if __name__ == "__main__":
    main()
