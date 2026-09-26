"""Customer Risk Assessment Orchestrator for Horizon Bank Analytics.

Coordinates the evaluation of risk conditions RC-01 through RC-05 across
curated domain entities and classifies each customer into immutable
RiskAssessment records under DD-04, DD-05, and DD-06 policies.

Executes strictly in pure offline fixture mode. In ExecutionMode.PRODUCTION,
fails closed immediately with PendingContractError.
"""

from __future__ import annotations

import dataclasses
from collections import defaultdict
from datetime import date, datetime, timezone
from typing import Any, Mapping, Sequence

from ..contracts.registry import MasterProductionRegistry
from ..contracts.risk import RiskRuleCatalogContract, RiskRuleCatalogRegistry
from ..contracts.states import ContractState, PendingContractError
from ..contracts.temporal import CHICAGO_TZ
from ..processing.records import ExecutionMode
from .risk_classification import (
    EvidenceState,
    RiskAssessment,
    RiskClassification,
    RiskClassificationEngine,
)
from .risk_conditions import (
    ConditionState,
    PublicationEvidence,
    RiskConditionEvaluator,
    RiskConditionResult,
    _publication_evidence,
)

DEFAULT_CATALOG_VERSION = "CAT-RISK-2026A-FIXTURE"
DEFAULT_CLASSIFY_VERSION = "DD04-CLASSIFY-v1"
DEFAULT_CONDITION_VERSIONS = {
    "RC-01": "DD04-DD06-RC01-v1",
    "RC-02": "DD04-DD06-RC02-v1",
    "RC-03": "DD04-DD06-RC03-v1",
    "RC-04": "DD04-DD06-RC04-v1",
    "RC-05": "DD04-DD06-RC05-v1",
}


def build_default_fixture_risk_catalog() -> RiskRuleCatalogContract:
    """Build the default fixture risk rule catalog contract."""
    return RiskRuleCatalogContract(
        catalog_version=DEFAULT_CATALOG_VERSION,
        classification_rule_version=DEFAULT_CLASSIFY_VERSION,
        condition_versions=DEFAULT_CONDITION_VERSIONS,
        state=ContractState.ACTIVE,
        is_fixture=True,
        approval_reference="FIXTURE-APPROVAL-S3P3-INC4",
    )


class CustomerRiskOrchestrator:
    """Coordinates customer risk assessment across curated entities."""

    def __init__(
        self,
        catalog_registry: RiskRuleCatalogRegistry | None = None,
    ) -> None:
        self.catalog_registry = catalog_registry or RiskRuleCatalogRegistry()
        if not self.catalog_registry.all_catalogs():
            self.catalog_registry.register(build_default_fixture_risk_catalog())

    @staticmethod
    def _require_execution_mode(execution_mode: object) -> ExecutionMode:
        if type(execution_mode) is not ExecutionMode:
            raise TypeError("execution_mode must be an ExecutionMode enum member")
        if execution_mode is ExecutionMode.PRODUCTION:
            raise PendingContractError(
                "MasterProductionRegistry contracts remain pending confirmation; "
                "production customer risk assessment is fail-closed."
            )
        return execution_mode

    @staticmethod
    def _to_dict(record: Any, pub_version: str, rev: int) -> dict[str, Any]:
        """Convert a record or dataclass to a dict prepared for condition evaluation."""
        if dataclasses.is_dataclass(record) and not isinstance(record, type):
            d = dataclasses.asdict(record)
        elif isinstance(record, dict):
            d = dict(record)
        else:
            d = {k: getattr(record, k) for k in dir(record) if not k.startswith("_")}

        d.setdefault("publication_version", pub_version)
        d.setdefault("revision", rev)
        lin_id = d.get("lineage_id")
        if lin_id and "lineage_references" not in d:
            d["lineage_references"] = (str(lin_id),)
        elif "lineage_references" not in d:
            d["lineage_references"] = (f"LIN-{d.get('source_system', 'SRC')}-{d.get('entity_name', 'RAW')}-{d.get('record_id', 'REC')}",)
        return d

    def assess_customers(
        self,
        *,
        customers: Sequence[Any] = (),
        accounts: Sequence[Any] = (),
        account_holders: Sequence[Any] = (),
        transactions: Sequence[Any] = (),
        loans: Sequence[Any] = (),
        borrowers: Sequence[Any] = (),
        positions: Sequence[Any] = (),
        complaints: Sequence[Any] = (),
        fraud_alerts: Sequence[Any] = (),
        account_restrictions: Sequence[Any] = (),
        business_date: date,
        as_of_time: datetime | None = None,
        publication: PublicationEvidence | None = None,
        catalog_version: str = DEFAULT_CATALOG_VERSION,
        classification_rule_version: str = DEFAULT_CLASSIFY_VERSION,
        execution_mode: ExecutionMode = ExecutionMode.FIXTURE,
    ) -> tuple[RiskAssessment, ...]:
        """Assess risk for all curated customers on a business date.

        In ExecutionMode.PRODUCTION, strictly raises PendingContractError.
        In ExecutionMode.FIXTURE, evaluates RC-01..RC-05 and classifies each customer.
        """
        self._require_execution_mode(execution_mode)

        if as_of_time is None:
            as_of_time = datetime(
                business_date.year, business_date.month, business_date.day,
                12, 0, 0, tzinfo=timezone.utc,
            )

        pub_ver = publication.publication_version if publication else f"PUB-{business_date.isoformat()}"
        rev = publication.revision if publication else 1

        if publication is None:
            publication = PublicationEvidence(
                business_date=business_date,
                publication_version=pub_ver,
                revision=rev,
                selected_publication_version=pub_ver,
                selected_revision=rev,
                manifest_present=True,
                population_complete=True,
                mapping_versions={
                    "SRC-01:transaction_status": "FIXTURE-TX-v1",
                    "SRC-01:restriction_status": "FIXTURE-RESTRICTION-v1",
                    "SRC-02:loan_status": "FIXTURE-LOAN-v1",
                    "SRC-03:fraud_case_status": "FIXTURE-FRAUD-STATUS-v1",
                    "SRC-03:fraud_severity": "FIXTURE-FRAUD-SEVERITY-v1",
                    "SRC-04:complaint_status": "FIXTURE-COMPLAINT-STATUS-v1",
                    "SRC-04:complaint_priority": "FIXTURE-COMPLAINT-PRIORITY-v1",
                },
            )

        # Index accounts and holders by customer
        cust_accounts: dict[str, list[str]] = defaultdict(list)
        for acc in accounts:
            cid = str(getattr(acc, "customer_id", None) or (acc.get("customer_id") if isinstance(acc, dict) else ""))
            aid = str(getattr(acc, "account_id", None) or (acc.get("account_id") if isinstance(acc, dict) else ""))
            if cid and aid:
                cust_accounts[cid].append(aid)

        for h in account_holders:
            cid = str(getattr(h, "customer_id", None) or (h.get("customer_id") if isinstance(h, dict) else ""))
            aid = str(getattr(h, "account_id", None) or (h.get("account_id") if isinstance(h, dict) else ""))
            if cid and aid and aid not in cust_accounts[cid]:
                cust_accounts[cid].append(aid)

        # Index loans and borrowers by customer
        cust_loans: dict[str, list[str]] = defaultdict(list)
        for l in loans:
            cid = str(getattr(l, "customer_id", None) or (l.get("customer_id") if isinstance(l, dict) else ""))
            lid = str(getattr(l, "loan_id", None) or (l.get("loan_id") if isinstance(l, dict) else ""))
            if cid and lid:
                cust_loans[cid].append(lid)

        for b in borrowers:
            cid = str(getattr(b, "customer_id", None) or (b.get("customer_id") if isinstance(b, dict) else ""))
            lid = str(getattr(b, "loan_id", None) or (b.get("loan_id") if isinstance(b, dict) else ""))
            if cid and lid and lid not in cust_loans[cid]:
                cust_loans[cid].append(lid)

        # Prepare normalized rows for condition evaluation
        tx_rows_by_account: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for tx in transactions:
            aid = str(getattr(tx, "account_id", None) or (tx.get("account_id") if isinstance(tx, dict) else ""))
            if aid:
                tx_d = self._to_dict(tx, pub_ver, rev)
                tx_rows_by_account[aid].append(tx_d)

        alert_rows_by_cust: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for al in fraud_alerts:
            cid = str(getattr(al, "customer_id", None) or (al.get("customer_id") if isinstance(al, dict) else ""))
            al_d = self._to_dict(al, pub_ver, rev)
            if cid:
                alert_rows_by_cust[cid].append(al_d)
            else:
                # Fallback to account association
                aid = str(getattr(al, "account_id", None) or (al.get("account_id") if isinstance(al, dict) else ""))
                for c_k, acc_list in cust_accounts.items():
                    if aid in acc_list:
                        alert_rows_by_cust[c_k].append(al_d)

        position_rows: list[dict[str, Any]] = [self._to_dict(p, pub_ver, rev) for p in positions]

        complaint_rows_by_cust: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for c in complaints:
            cid = str(getattr(c, "customer_id", None) or (c.get("customer_id") if isinstance(c, dict) else ""))
            if cid:
                c_d = self._to_dict(c, pub_ver, rev)
                complaint_rows_by_cust[cid].append(c_d)

        restriction_rows: list[dict[str, Any]] = [self._to_dict(r, pub_ver, rev) for r in account_restrictions]

        assessments: list[RiskAssessment] = []

        for cust in customers:
            cid = str(getattr(cust, "customer_id", None) or (cust.get("customer_id") if isinstance(cust, dict) else ""))
            if not cid:
                continue

            cust_accs = cust_accounts.get(cid, [])
            cust_lids = cust_loans.get(cid, [])
            cust_lin = [f"LIN-CUST-{cid}-{rev}"]

            # Collect transactions for this customer
            c_txs: list[dict[str, Any]] = []
            for aid in cust_accs:
                c_txs.extend(tx_rows_by_account.get(aid, []))

            # 1. RC-01: Transaction velocity / spike
            if c_txs:
                rc01_res = RiskConditionEvaluator.rc01_customer_day(
                    current_transactions=c_txs,
                    prior_transactions=(),
                    customer_id=cid,
                    as_of=as_of_time,
                    publication=publication,
                    window_complete=True,
                    mapping_ready=True,
                    execution_mode=execution_mode,
                    lineage_references=cust_lin,
                )
            else:
                # No transactions on business date -> NOT_TRIGGERED with valid delivery lineage
                rc01_res = RiskConditionResult(
                    condition_id="RC-01",
                    state=ConditionState.NOT_TRIGGERED,
                    evidence=tuple(_publication_evidence(publication)),
                    lineage_references=tuple(cust_lin),
                    rule_version=RiskConditionEvaluator.RC01_VERSION,
                    as_of=as_of_time,
                )

            # 2. RC-02: Fraud alerts
            c_alerts = alert_rows_by_cust.get(cid, [])
            rc02_res = RiskConditionEvaluator.rc02(
                alerts=c_alerts,
                as_of=as_of_time,
                mapping_ready=True,
                execution_mode=execution_mode,
                publication=publication,
                lineage_references=cust_lin,
            )

            # 3. RC-03: Loan delinquency
            rc03_res = RiskConditionEvaluator.rc03(
                positions=position_rows,
                related_loan_ids=cust_lids,
                as_of=as_of_time,
                mapping_ready=True,
                execution_mode=execution_mode,
                publication=publication,
                lineage_references=cust_lin,
            )

            # 4. RC-04: Complaints SLA
            c_comps = complaint_rows_by_cust.get(cid, [])
            rc04_res = RiskConditionEvaluator.rc04(
                complaints=c_comps,
                as_of=as_of_time,
                mapping_ready=True,
                execution_mode=execution_mode,
                publication=publication,
                lineage_references=cust_lin,
            )

            # 5. RC-05: Account restrictions
            rc05_res = RiskConditionEvaluator.rc05(
                states=restriction_rows,
                related_account_ids=cust_accs,
                as_of=as_of_time,
                mapping_ready=True,
                execution_mode=execution_mode,
                publication=publication,
                lineage_references=cust_lin,
            )

            condition_results = (rc01_res, rc02_res, rc03_res, rc04_res, rc05_res)

            assessment_id = f"ASM-{cid}-{business_date.isoformat()}"
            assessment = RiskClassificationEngine.classify(
                assessment_id=assessment_id,
                customer_id=cid,
                business_date=business_date,
                assessment_at=as_of_time,
                condition_results=condition_results,
                catalog_version=catalog_version,
                classification_rule_version=classification_rule_version,
                catalog_registry=self.catalog_registry,
                lineage_references=cust_lin,
                publication_version=pub_ver,
                execution_mode=execution_mode,
            )
            assessments.append(assessment)

        assessments.sort(key=lambda a: (a.business_date, a.customer_id))
        return tuple(assessments)
