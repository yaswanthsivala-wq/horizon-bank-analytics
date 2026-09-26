"""Unit tests for contract lifecycle states and findings."""

import unittest

from horizon_pipeline.contracts.findings import (
    Disposition,
    FindingSeverity,
    ValidationFinding,
)
from horizon_pipeline.contracts.states import (
    ContractError,
    ContractState,
    ContractValidationError,
    PendingContractError,
    UnsupportedContractError,
)


class ContractStateTests(unittest.TestCase):
    def test_contract_state_values(self):
        self.assertEqual(ContractState.ACTIVE.value, "ACTIVE")
        self.assertEqual(ContractState.PENDING.value, "PENDING")
        self.assertEqual(ContractState.UNSUPPORTED.value, "UNSUPPORTED")

    def test_pending_contract_error_formatting(self):
        err = PendingContractError(
            "Physical header unresolved",
            contract_type="PD-01",
            source="SRC-01",
            section="customers",
            identifier="HCB.SYN.SRC-01.customers.v001",
        )
        msg = str(err)
        self.assertIn("Physical header unresolved", msg)
        self.assertIn("contract_type=PD-01", msg)
        self.assertIn("source=SRC-01", msg)
        self.assertIn("section=customers", msg)
        self.assertIn("state=PENDING", msg)
        self.assertEqual(err.state, ContractState.PENDING)

    def test_unsupported_contract_error_formatting(self):
        err = UnsupportedContractError(
            "Unknown schema ID",
            contract_type="PD-02",
            source="SRC-02",
            section="loans",
            identifier="unknown-v999",
        )
        self.assertEqual(err.state, ContractState.UNSUPPORTED)
        self.assertIn("state=UNSUPPORTED", str(err))

    def test_validation_finding_summary(self):
        finding = ValidationFinding(
            code="MAN-01",
            severity=FindingSeverity.FATAL,
            source="SRC-01",
            section="transactions",
            field_name="amount",
            record_identity="row_42",
            message="Checksum mismatch",
            disposition=Disposition.REJECTED,
        )
        summary = finding.to_summary()
        self.assertIn("[FATAL]", summary)
        self.assertIn("SRC-01/transactions", summary)
        self.assertIn("record=row_42", summary)
        self.assertIn("field=amount", summary)
        self.assertIn("MAN-01 - Checksum mismatch", summary)


if __name__ == "__main__":
    unittest.main()
