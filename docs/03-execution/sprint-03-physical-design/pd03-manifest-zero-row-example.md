# PD-03 zero-row manifest example — structural excerpt

Status: **Approved structural example only** (Project Owner review 2026-09-22). This is a one-section example, **not** a complete 27-section package or an approved `SRC-03/alerts` physical header. It demonstrates a manifest-confirmed empty section; it is not a missing source. The proposed header and candidate PD-02 version remain inactive. No dataset has been generated.

Exact illustrative bytes at `sections/SRC-03/alerts.csv` (UTF-8, one header line with a final LF):

```text
source_alert_id
```

SHA-256 of the exact bytes `source_alert_id\n` is `a4b2ccefefa7ce8b7de6c1fb364641b31c42d37ecba5254126280d91bcd27755`.

Illustrative `manifest.json` excerpt:

```json
{
  "manifest_version": "HCB.SYN.MANIFEST.v001",
  "business_date": "2025-03-09",
  "sections": [
    {
      "extract_id": "SYN-EXTRACT-SRC03-ALERTS-20250309-R1-ZERO-EXAMPLE",
      "source_system": "SRC-03",
      "entity_name": "alerts",
      "business_date": "2025-03-09",
      "revision": 1,
      "delivery_mode": "FULL_STATE",
      "schema_version": "HCB.SYN.SRC-03.alerts.v001",
      "cutoff_at": "2025-03-10T05:00:00.000000Z",
      "extracted_at": "2025-03-10T09:30:00.000000Z",
      "payload_path": "sections/SRC-03/alerts.csv",
      "row_count": 0,
      "checksum_algorithm": "SHA-256",
      "checksum_encoding": "LOWERCASE_HEX",
      "checksum": "a4b2ccefefa7ce8b7de6c1fb364641b31c42d37ecba5254126280d91bcd27755",
      "content_encoding": "UTF-8",
      "checksum_scope_reference": "CSV_EXACT_BYTES_V1",
      "mapping_version_references": [],
      "financial_control_references": []
    }
  ]
}
```

The payload exists, the header exists, `row_count` is zero and the checksum covers the header plus final LF. Missing `alerts.csv` or its manifest entry would be a **missing required section**, not this valid zero-row condition. The excerpt still fails complete-package and approved-header gates; empty mapping/control reference arrays provide no passing downstream evidence.
