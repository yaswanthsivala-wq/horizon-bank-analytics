"""Unit tests for PD-03 Manifest Contract and Payload Byte Validation."""

import hashlib
import json
import unittest
from datetime import date

from horizon_pipeline.contracts.manifests import (
    ManifestSectionEntry,
    parse_and_validate_manifest_json,
    validate_path_safety,
    validate_payload_bytes,
)


class ManifestValidationTests(unittest.TestCase):
    def setUp(self):
        self.valid_entry_dict = {
            "extract_id": "EXT-01",
            "source_system": "SRC-01",
            "entity_name": "accounts",
            "business_date": "2025-03-09",
            "revision": 1,
            "delivery_mode": "FULL_STATE",
            "schema_version": "FIXTURE.SYN.SRC-01.accounts.v001",
            "cutoff_at": "2025-03-09T23:59:59.999999Z",
            "extracted_at": "2025-03-09T04:30:00.000000Z",
            "payload_path": "sections/SRC-01/accounts.csv",
            "row_count": 1,
            "checksum_algorithm": "SHA-256",
            "checksum_encoding": "LOWERCASE_HEX",
            "checksum": "a" * 64,
            "content_encoding": "UTF-8",
            "checksum_scope_reference": "CSV_EXACT_BYTES_V1",
            "mapping_version_references": [],
            "financial_control_references": [],
        }

    def test_malformed_json(self):
        manifest, findings = parse_and_validate_manifest_json("{invalid json")
        self.assertIsNone(manifest)
        self.assertTrue(any(f.code == "MAN-MALFORMED-JSON" for f in findings))

    def test_invalid_manifest_version(self):
        data = {
            "manifest_version": "INVALID.v999",
            "business_date": "2025-03-09",
            "sections": [self.valid_entry_dict],
        }
        manifest, findings = parse_and_validate_manifest_json(json.dumps(data), require_all_27_sections=False)
        self.assertTrue(any(f.code == "MAN-INVALID-VERSION" for f in findings))

    def test_invalid_business_date(self):
        data = {
            "manifest_version": "HCB.SYN.MANIFEST.v001",
            "business_date": "2025-02-30",
            "sections": [self.valid_entry_dict],
        }
        manifest, findings = parse_and_validate_manifest_json(json.dumps(data), require_all_27_sections=False)
        self.assertTrue(any("DATE" in f.code for f in findings))

    def test_path_safety_checks(self):
        # Path traversal
        self.assertIsNotNone(validate_path_safety("../sections/SRC-01/accounts.csv", "SRC-01", "accounts"))
        self.assertIsNotNone(validate_path_safety("sections/../accounts.csv", "SRC-01", "accounts"))
        # Backslash
        self.assertIsNotNone(validate_path_safety("sections\\SRC-01\\accounts.csv", "SRC-01", "accounts"))
        # Absolute path / leading slash
        self.assertIsNotNone(validate_path_safety("/sections/SRC-01/accounts.csv", "SRC-01", "accounts"))
        # Drive letter
        self.assertIsNotNone(validate_path_safety("C:/sections/SRC-01/accounts.csv", "SRC-01", "accounts"))
        # Mismatched entity name
        self.assertIsNotNone(validate_path_safety("sections/SRC-01/other.csv", "SRC-01", "accounts"))
        # Valid path
        self.assertIsNone(validate_path_safety("sections/SRC-01/accounts.csv", "SRC-01", "accounts"))

    def test_duplicate_manifest_section_entry(self):
        data = {
            "manifest_version": "HCB.SYN.MANIFEST.v001",
            "business_date": "2025-03-09",
            "sections": [self.valid_entry_dict, self.valid_entry_dict],
        }
        manifest, findings = parse_and_validate_manifest_json(json.dumps(data), require_all_27_sections=False)
        self.assertTrue(any(f.code == "MAN-DUPLICATE-SECTION" for f in findings))
        self.assertTrue(any(f.code == "MAN-DUPLICATE-PATH" for f in findings))

    def test_invalid_revision_boolean(self):
        entry = dict(self.valid_entry_dict)
        entry["revision"] = True  # True is an instance of int in Python, but type(True) is bool
        data = {
            "manifest_version": "HCB.SYN.MANIFEST.v001",
            "business_date": "2025-03-09",
            "sections": [entry],
        }
        manifest, findings = parse_and_validate_manifest_json(json.dumps(data), require_all_27_sections=False)
        self.assertTrue(any(f.code == "MAN-INVALID-REVISION" for f in findings))

    def test_invalid_checksum_format(self):
        entry = dict(self.valid_entry_dict)
        entry["checksum"] = "UPPERCASE" + "a" * 55
        data = {
            "manifest_version": "HCB.SYN.MANIFEST.v001",
            "business_date": "2025-03-09",
            "sections": [entry],
        }
        manifest, findings = parse_and_validate_manifest_json(json.dumps(data), require_all_27_sections=False)
        self.assertTrue(any(f.code == "MAN-INVALID-CHECKSUM-FORMAT" for f in findings))

    def test_payload_bom_and_crlf_rejected(self):
        entry = ManifestSectionEntry(
            extract_id="EXT-1",
            source_system="SRC-01",
            entity_name="accounts",
            business_date=date(2025, 3, 9),
            revision=1,
            delivery_mode="FULL_STATE",
            schema_version="FIXTURE.SYN.SRC-01.accounts.v001",
            cutoff_at="2025-03-09T23:59:59.999999Z",
            extracted_at="2025-03-09T04:30:00.000000Z",
            payload_path="sections/SRC-01/accounts.csv",
            row_count=0,
            checksum_algorithm="SHA-256",
            checksum_encoding="LOWERCASE_HEX",
            checksum="",
            content_encoding="UTF-8",
            checksum_scope_reference="CSV_EXACT_BYTES_V1",
            mapping_version_references=(),
            financial_control_references=(),
        )

        # BOM test
        bom_bytes = b"\xef\xbb\xbfcol1,col2\n"
        _, findings = validate_payload_bytes(entry, bom_bytes)
        self.assertTrue(any(f.code == "PAY-BOM-FORBIDDEN" for f in findings))

        # CRLF test
        crlf_bytes = b"col1,col2\r\n"
        _, findings = validate_payload_bytes(entry, crlf_bytes)
        self.assertTrue(any(f.code == "PAY-INVALID-LINE-ENDINGS" for f in findings))

    def test_payload_checksum_and_row_count_validation(self):
        content = b"col1,col2\nval1,val2\n"
        digest = hashlib.sha256(content).hexdigest()

        entry_ok = ManifestSectionEntry(
            extract_id="EXT-1",
            source_system="SRC-01",
            entity_name="accounts",
            business_date=date(2025, 3, 9),
            revision=1,
            delivery_mode="FULL_STATE",
            schema_version="v1",
            cutoff_at="2025-03-09T23:59:59.999999Z",
            extracted_at="2025-03-09T04:30:00.000000Z",
            payload_path="sections/SRC-01/accounts.csv",
            row_count=1,
            checksum_algorithm="SHA-256",
            checksum_encoding="LOWERCASE_HEX",
            checksum=digest,
            content_encoding="UTF-8",
            checksum_scope_reference="CSV_EXACT_BYTES_V1",
            mapping_version_references=(),
            financial_control_references=(),
        )
        cols, findings = validate_payload_bytes(entry_ok, content)
        self.assertEqual(cols, ["col1", "col2"])
        self.assertEqual(findings, [])

        # Checksum mismatch
        entry_bad_csum = ManifestSectionEntry(
            **{**entry_ok.__dict__, "checksum": "f" * 64}
        )
        _, findings = validate_payload_bytes(entry_bad_csum, content)
        self.assertTrue(any(f.code == "PAY-CHECKSUM-MISMATCH" for f in findings))

        # Row count mismatch
        entry_bad_rc = ManifestSectionEntry(
            **{**entry_ok.__dict__, "row_count": 0}
        )
        _, findings = validate_payload_bytes(entry_bad_rc, content)
        self.assertTrue(any(f.code == "PAY-ROW-COUNT-MISMATCH" for f in findings))


if __name__ == "__main__":
    unittest.main()
