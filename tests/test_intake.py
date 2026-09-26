import hashlib
import unittest
from datetime import date

from horizon_pipeline.intake import REQUIRED_SECTIONS, FieldContract, SectionContract, SectionManifest, validate_delivery

DAY = date(2025, 3, 9)
HEADER = b"source_system,entity_name,business_date,revision,source_id,amount\n"
CONTRACT = SectionContract("reviewed-v1", (
    FieldContract("source_system", "text", max_length=50),
    FieldContract("entity_name", "text", max_length=50),
    FieldContract("business_date", "date"),
    FieldContract("revision", "revision"),
    FieldContract("source_id", "text", max_length=100),
    FieldContract("amount", "decimal", required=False, precision=20, scale=4),
))
CONTRACTS = {(source, name): CONTRACT for source, names in REQUIRED_SECTIONS.items() for name in names}


def section(source="SRC-01", name="transactions", content=HEADER, version="reviewed-v1", count=0):
    return SectionManifest(source, name, DAY, 1, count, hashlib.sha256(content).hexdigest(), version), content


def delivery():
    return {(source, name): section(source, name) for source, names in REQUIRED_SECTIONS.items() for name in names}


def findings(content=HEADER, *, version="reviewed-v1", count=0):
    sections = delivery()
    sections["SRC-01", "transactions"] = section(content=content, version=version, count=count)
    return validate_delivery(DAY, sections, CONTRACTS).findings


class IntakeTests(unittest.TestCase):
    def test_zero_row_sections_have_headers_and_pass(self):
        self.assertTrue(validate_delivery(DAY, delivery(), CONTRACTS).passed)

    def test_valid_populated_section(self):
        content = HEADER + b"SRC-01,transactions,2025-03-09,1,T1,1.2300\n"
        self.assertEqual((), findings(content, count=1))

    def test_missing_section_blocks_delivery(self):
        sections = delivery()
        del sections["SRC-03", "alerts"]
        self.assertIn("SRC-03/alerts: missing required section", validate_delivery(DAY, sections, CONTRACTS).findings)

    def test_missing_and_unexpected_headers(self):
        result = findings(b"source_system,entity_name,business_date,revision,extra,amount\n")
        self.assertIn("SRC-01/transactions: missing field: source_id", result)
        self.assertIn("SRC-01/transactions: unexpected field: extra", result)

    def test_invalid_type_and_required_cell(self):
        content = HEADER + b"SRC-01,transactions,2025-03-09,no,,1.23456\n"
        result = findings(content, count=1)
        self.assertIn("SRC-01/transactions: row 2: invalid revision (revision)", result)
        self.assertIn("SRC-01/transactions: row 2: invalid source_id (text)", result)
        self.assertIn("SRC-01/transactions: row 2: invalid amount (decimal)", result)

    def test_malformed_date_and_identity_mismatch(self):
        content = HEADER + b"SRC-02,transactions,2025-02-30,1,T1,1.0000\n"
        result = findings(content, count=1)
        self.assertIn("SRC-01/transactions: row 2: invalid business_date (date)", result)
        self.assertIn("SRC-01/transactions: row 2: source_system differs from manifest", result)

    def test_malformed_manifest_date(self):
        sections = delivery()
        manifest, content = sections["SRC-01", "transactions"]
        sections["SRC-01", "transactions"] = SectionManifest(manifest.source, manifest.section, "2025-02-30", 1, 0, manifest.sha256, manifest.schema_version), content
        result = validate_delivery(DAY, sections, CONTRACTS).findings
        self.assertIn("SRC-01/transactions: invalid manifest business date", result)

    def test_schema_version_mismatch_and_missing_registry_fail_closed(self):
        self.assertIn("SRC-01/transactions: schema-version mismatch", findings(version="other-v1"))
        self.assertIn("SRC-01/transactions: approved physical field/schema contract unavailable", validate_delivery(DAY, delivery()).findings)
        self.assertIn("SRC-01/transactions: missing or invalid schema version", findings(version=""))

    def test_duplicate_header(self):
        result = findings(HEADER.replace(b"source_id,amount", b"source_id,source_id"))
        self.assertIn("SRC-01/transactions: duplicate header field", result)

    def test_changed_bytes_at_same_digest_are_rejected(self):
        sections = delivery()
        manifest, _ = sections["SRC-01", "transactions"]
        sections["SRC-01", "transactions"] = manifest, HEADER + b"SRC-01,transactions,2025-03-09,1,T1,1.0000\n"
        result = validate_delivery(DAY, sections, CONTRACTS).findings
        self.assertIn("SRC-01/transactions: checksum mismatch", result)
        self.assertIn("SRC-01/transactions: row count mismatch", result)

    def test_bom_and_crlf_are_rejected_even_with_matching_digest(self):
        content = b"\xef\xbb\xbf" + HEADER.replace(b"\n", b"\r\n")
        result = findings(content)
        self.assertIn("SRC-01/transactions: UTF-8 BOM is forbidden", result)
        self.assertIn("SRC-01/transactions: section must use LF and end with LF", result)


if __name__ == "__main__":
    unittest.main()
