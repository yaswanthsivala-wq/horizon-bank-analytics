"""Deterministic Synthetic Banking Data Generator.

NOTICE: SYNTHETIC / NON-PRODUCTION ONLY.
Uses Python standard library random.Random with deterministic seed.
Preserves referential integrity across customer, account, transaction,
loan, fraud, complaint, and branch entities.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

from ..intake import REQUIRED_SECTIONS
from .models import (
    SyntheticAccount,
    SyntheticBranch,
    SyntheticComplaint,
    SyntheticCustomer,
    SyntheticFraudAlert,
    SyntheticHolder,
    SyntheticLoan,
    SyntheticLoanPayment,
    SyntheticLoanPosition,
    SyntheticTransaction,
)


@dataclass(frozen=True)
class SyntheticDataset:
    """Container holding in-memory logical records for all 27 sections."""

    business_date: date
    seed: int
    sections: dict[tuple[str, str], list[dict[str, Any]]]


class SyntheticBankingDataGenerator:
    """Generates deterministic synthetic banking data across SRC-01..SRC-05."""

    def __init__(self, seed: int = 42, business_date: date = date(2025, 3, 9)) -> None:
        self.seed = seed
        self.business_date = business_date
        self.rng = random.Random(seed)

    def generate(
        self,
        num_customers: int = 20,
        num_accounts_per_cust: int = 2,
        num_transactions: int = 50,
        num_loans: int = 10,
        include_risk_scenarios: bool = False,
    ) -> SyntheticDataset:
        """Generate logical records for all 27 mandatory sections."""
        # Initialize dictionary for all 27 mandatory sections
        sections: dict[tuple[str, str], list[dict[str, Any]]] = {
            (src, sec): [] for src, sec_names in REQUIRED_SECTIONS.items() for sec in sec_names
        }

        # 1. SRC-05: Organization, Region, Branches
        regions = [
            {"region_id": "REG-01", "region_name": "Midwest Metro", "valid_from": "2024-01-01"},
            {"region_id": "REG-02", "region_name": "Northern Lakes", "valid_from": "2024-01-01"},
        ]
        sections[("SRC-05", "region")].extend(regions)

        branches = [
            {"branch_id": "BR-101", "region_id": "REG-01", "branch_name": "Downtown Central", "valid_from": "2024-01-01"},
            {"branch_id": "BR-102", "region_id": "REG-01", "branch_name": "West Suburbs", "valid_from": "2024-01-01"},
            {"branch_id": "BR-201", "region_id": "REG-02", "branch_name": "Lakefront North", "valid_from": "2024-01-01"},
        ]
        sections[("SRC-05", "branches")].extend(branches)

        org_units = [
            {"unit_id": "OU-CORP", "unit_type": "REGION", "parent_id": ""},
            {"unit_id": "OU-REG-01", "unit_type": "REGION", "parent_id": "OU-CORP"},
            {"unit_id": "OU-BR-101", "unit_type": "BRANCH", "parent_id": "OU-REG-01"},
        ]
        sections[("SRC-05", "organizational_unit")].extend(org_units)

        # 2. SRC-01: Customers
        customers: list[dict[str, Any]] = []
        for i in range(1, num_customers + 1):
            cust_id = f"CUST-{i:05d}"
            seg = "RETAIL" if self.rng.random() < 0.75 else "SMALL_BUSINESS"
            branch = self.rng.choice(branches)["branch_id"]
            masked_ssn = f"XXX-XX-{self.rng.randint(1000, 9999)}"
            cust_rec = {
                "customer_id": cust_id,
                "tax_identifier_masked": masked_ssn,
                "customer_name": f"Synthetic Client {i}",
                "customer_segment": seg,
                "primary_branch_id": branch,
                "business_date": self.business_date.isoformat(),
            }
            customers.append(cust_rec)
        sections[("SRC-01", "customers")].extend(customers)

        # 3. SRC-01: Accounts & Holders
        accounts: list[dict[str, Any]] = []
        holders: list[dict[str, Any]] = []
        acc_counter = 1
        for cust in customers:
            c_id = cust["customer_id"]
            b_id = cust["primary_branch_id"]
            for _ in range(self.rng.randint(1, num_accounts_per_cust)):
                acc_id = f"ACC-{acc_counter:07d}"
                acc_type = "CHECKING" if self.rng.random() < 0.6 else "SAVINGS"
                acc_rec = {
                    "account_id": acc_id,
                    "customer_id": c_id,
                    "account_type": acc_type,
                    "currency": "USD",
                    "branch_id": b_id,
                    "account_status": "ACTIVE",
                    "business_date": self.business_date.isoformat(),
                }
                accounts.append(acc_rec)

                # Primary holder
                holders.append({
                    "account_id": acc_id,
                    "customer_id": c_id,
                    "relationship_role": "PRIMARY",
                    "effective_start": "2024-06-01",
                })

                # Branch assignment
                sections[("SRC-01", "account_branch_assignment")].append({
                    "account_id": acc_id,
                    "branch_id": b_id,
                    "branch_role": "SERVICING",
                    "effective_start": "2024-06-01",
                })

                # Restriction state
                sections[("SRC-01", "account_restriction_state")].append({
                    "account_id": acc_id,
                    "restriction_status": "NONE",
                    "effective_start": "2024-06-01",
                })

                acc_counter += 1

        sections[("SRC-01", "accounts")].extend(accounts)
        sections[("SRC-01", "holders")].extend(holders)

        # 4. SRC-01: Transactions
        tx_list: list[dict[str, Any]] = []
        for i in range(1, num_transactions + 1):
            tx_id = f"TX-{i:08d}"
            acc = self.rng.choice(accounts)
            tx_type = self.rng.choice(["TRANSFER", "PAYMENT", "WITHDRAWAL", "DEPOSIT"])
            amt = Decimal(str(round(self.rng.uniform(5.00, 2500.00), 2))).quantize(Decimal("0.0001"))
            tx_status = "SUCCESSFUL" if self.rng.random() < 0.95 else "FAILED"
            # Timestamp in Chicago local normalized to UTC
            hour = self.rng.randint(8, 17)
            minute = self.rng.randint(0, 59)
            second = self.rng.randint(0, 59)
            ts_utc = f"{self.business_date.isoformat()}T{hour:02d}:{minute:02d}:{second:02d}.000000Z"
            tx_rec = {
                "transaction_id": tx_id,
                "account_id": acc["account_id"],
                "business_date": self.business_date.isoformat(),
                "amount": str(amt),
                "currency": "USD",
                "transaction_type": tx_type,
                "transaction_status": tx_status,
                "posted_at": ts_utc,
            }
            tx_list.append(tx_rec)
        sections[("SRC-01", "transactions")].extend(tx_list)

        # 5. SRC-02: Loans, Borrowers, Positions, Payments
        loan_counter = 1
        for i in range(1, num_loans + 1):
            loan_id = f"LN-{loan_counter:06d}"
            cust = self.rng.choice(customers)
            l_type = self.rng.choice(["PERSONAL", "AUTO", "MORTGAGE"])
            principal = Decimal(str(self.rng.choice([15000, 25000, 250000, 400000]))).quantize(Decimal("0.0001"))
            loan_rec = {
                "loan_id": loan_id,
                "customer_id": cust["customer_id"],
                "loan_type": l_type,
                "original_principal": str(principal),
                "currency": "USD",
                "origination_date": "2024-09-01",
                "branch_id": cust["primary_branch_id"],
            }
            sections[("SRC-02", "loans")].append(loan_rec)

            sections[("SRC-02", "borrowers")].append({
                "loan_id": loan_id,
                "customer_id": cust["customer_id"],
                "relationship_role": "PRIMARY",
                "effective_start": "2024-09-01",
            })

            # Position
            sections[("SRC-02", "positions")].append({
                "loan_id": loan_id,
                "business_date": self.business_date.isoformat(),
                "outstanding_principal": str(principal),
                "currency": "USD",
                "days_past_due": 0,
                "loan_status": "ACTIVE",
            })

            # Loan schedule & obligation
            sections[("SRC-02", "loan_schedule")].append({
                "schedule_id": f"SCHED-{loan_id}",
                "loan_id": loan_id,
                "payment_frequency": "MONTHLY",
                "installment_amount": "450.0000",
                "currency": "USD",
            })
            sections[("SRC-02", "loan_obligation")].append({
                "obligation_id": f"OBL-{loan_id}-01",
                "loan_id": loan_id,
                "due_date": self.business_date.isoformat(),
                "scheduled_amount": "450.0000",
                "currency": "USD",
            })

            # Payment
            pmt_id = f"PMT-{loan_id}-01"
            sections[("SRC-02", "payments")].append({
                "payment_id": pmt_id,
                "loan_id": loan_id,
                "amount": "450.0000",
                "currency": "USD",
                "payment_status": "POSTED",
                "paid_at": f"{self.business_date.isoformat()}T12:00:00.000000Z",
                "posted_at": f"{self.business_date.isoformat()}T12:05:00.000000Z",
            })
            sections[("SRC-02", "payment_allocation")].append({
                "allocation_id": f"ALC-{pmt_id}-01",
                "payment_id": pmt_id,
                "allocation_component": "PRINCIPAL",
                "amount": "350.0000",
                "currency": "USD",
            })
            sections[("SRC-02", "payment_allocation")].append({
                "allocation_id": f"ALC-{pmt_id}-02",
                "payment_id": pmt_id,
                "allocation_component": "INTEREST",
                "amount": "100.0000",
                "currency": "USD",
            })
            sections[("SRC-02", "payment_unapplied")].append({
                "payment_id": pmt_id,
                "amount": "0.0000",
                "currency": "USD",
            })

            # Loan branch & account
            sections[("SRC-02", "loan_branch_assignment")].append({
                "loan_id": loan_id,
                "branch_id": cust["primary_branch_id"],
                "branch_role": "SERVICING",
                "effective_start": "2024-09-01",
            })
            matching_acc = next((a for a in accounts if a["customer_id"] == cust["customer_id"]), None)
            if matching_acc:
                sections[("SRC-02", "loan_account")].append({
                    "loan_id": loan_id,
                    "account_id": matching_acc["account_id"],
                    "relationship_role": "REPORTING",
                })

            loan_counter += 1

        # 6. SRC-03: Fraud Monitoring
        alert_id = "ALT-00001"
        sample_acc = accounts[0]
        sections[("SRC-03", "alerts")].append({
            "alert_id": alert_id,
            "customer_id": sample_acc["customer_id"],
            "account_id": sample_acc["account_id"],
            "severity": "HIGH",
            "alert_reason": "VELOCITY",
            "case_status": "OPEN",
            "created_at": f"{self.business_date.isoformat()}T09:30:00.000000Z",
        })
        sections[("SRC-03", "fraud_alert_state")].append({
            "alert_id": alert_id,
            "case_status": "OPEN",
            "effective_start": f"{self.business_date.isoformat()}T09:30:00.000000Z",
        })

        # 7. SRC-04: CRM Complaints
        comp_id = "CMP-00001"
        cust_c = customers[0]
        sections[("SRC-04", "complaints")].append({
            "complaint_id": comp_id,
            "customer_id": cust_c["customer_id"],
            "channel": "PHONE",
            "priority": "Medium",
            "complaint_status": "OPEN",
            "created_at": f"{self.business_date.isoformat()}T10:15:00.000000Z",
        })
        sections[("SRC-04", "complaint_snapshot")].append({
            "complaint_id": comp_id,
            "business_date": self.business_date.isoformat(),
            "complaint_status": "OPEN",
            "priority": "Medium",
        })
        sections[("SRC-04", "complaint_history_event")].append({
            "event_id": f"EVT-{comp_id}-01",
            "complaint_id": comp_id,
            "event_type": "CREATION",
            "event_at": f"{self.business_date.isoformat()}T10:15:00.000000Z",
        })
        sections[("SRC-04", "complaint_branch_assignment")].append({
            "complaint_id": comp_id,
            "branch_id": cust_c["primary_branch_id"],
            "branch_role": "RESPONSIBLE",
            "effective_start": "2024-09-01",
        })

        # Optional additive risk fixtures. Default output remains byte-compatible.
        if include_risk_scenarios:
            restricted_account = accounts[0]
            sections[("SRC-01", "account_restriction_state")].append({
                "account_id": restricted_account["account_id"],
                "restriction_status": "FROZEN",
                "effective_start": f"{self.business_date.isoformat()}T08:00:00.000000Z",
            })
            sections[("SRC-03", "fraud_alert_state")].append({
                "alert_id": alert_id,
                "case_status": "CLOSED",
                "effective_start": f"{self.business_date.isoformat()}T18:00:00.000000Z",
            })
            sections[("SRC-04", "complaint_snapshot")].append({
                "complaint_id": comp_id,
                "business_date": self.business_date.isoformat(),
                "complaint_status": "REOPENED",
                "priority": "Medium",
            })
            sections[("SRC-04", "complaint_history_event")].extend([
                {
                    "event_id": f"EVT-{comp_id}-02",
                    "complaint_id": comp_id,
                    "event_type": "CLOSED",
                    "event_at": f"{self.business_date.isoformat()}T14:00:00.000000Z",
                },
                {
                    "event_id": f"EVT-{comp_id}-03",
                    "complaint_id": comp_id,
                    "event_type": "REOPENED",
                    "event_at": f"{self.business_date.isoformat()}T16:00:00.000000Z",
                },
            ])

        return SyntheticDataset(business_date=self.business_date, seed=self.seed, sections=sections)
