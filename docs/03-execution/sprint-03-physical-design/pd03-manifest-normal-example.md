# PD-03 one-row manifest example — structural excerpt

Status: **Approved structural example only** (Project Owner review 2026-09-22). This is a one-section example, **not** a complete 27-section package or an approved `SRC-03/alerts` physical header. `source_alert_id` is a proposed alias from the [G3 field trace](../sprint-02-data-design/synthetic-contract-traceability.md); other required received fields and PD-04/PD-06 evidence are not established here. The candidate PD-02 version remains inactive. No dataset has been generated.

Exact illustrative bytes at `sections/SRC-03/alerts.csv` (UTF-8, LF after **both** displayed lines):

```text
source_alert_id
SYN-ALERT-001
```

SHA-256 of the exact bytes `source_alert_id\nSYN-ALERT-001\n` is `57c7fd58cc8ec105772cd3faa40868f9f901e309d22b4d65eafc24aa81ad7bb2`.

Illustrative `manifest.json` excerpt:

```json
{
  "manifest_version": "HCB.SYN.MANIFEST.v001",
  "business_date": "2025-03-09",
  "sections": [
    {
      "extract_id": "SYN-EXTRACT-SRC03-ALERTS-20250309-R1",
      "source_system": "SRC-03",
      "entity_name": "alerts",
      "business_date": "2025-03-09",
      "revision": 1,
      "delivery_mode": "FULL_STATE",
      "schema_version": "HCB.SYN.SRC-03.alerts.v001",
      "cutoff_at": "2025-03-10T05:00:00.000000Z",
      "extracted_at": "2025-03-10T09:30:00.000000Z",
      "payload_path": "sections/SRC-03/alerts.csv",
      "row_count": 1,
      "checksum_algorithm": "SHA-256",
      "checksum_encoding": "LOWERCASE_HEX",
      "checksum": "57c7fd58cc8ec105772cd3faa40868f9f901e309d22b4d65eafc24aa81ad7bb2",
      "content_encoding": "UTF-8",
      "checksum_scope_reference": "CSV_EXACT_BYTES_V1",
      "mapping_version_references": [],
      "financial_control_references": []
    }
  ]
}
```

The row count and digest match this illustrative byte stream. The empty reference arrays mean **unresolved**, not mapping/control approval or inapplicability. The excerpt fails complete-package and approved-header gates, as it must.
