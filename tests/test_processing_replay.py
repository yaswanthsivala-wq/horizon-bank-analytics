"""Unit Tests for Batch State, Replay, and Revision Management.

Verifies DD-09 delivery identity: (source, section, date, revision), identical replay
recognition (INFO), conflicting same-revision rejection (CRITICAL), and superseding revisions.
"""

from __future__ import annotations

import unittest
from datetime import date

from horizon_pipeline.contracts.findings import FindingSeverity
from horizon_pipeline.processing.replay import BatchStateTracker


class ProcessingReplayTests(unittest.TestCase):
    def setUp(self):
        self.tracker = BatchStateTracker()
        self.bdate = date(2025, 3, 9)

    def test_new_delivery_registration(self):
        """First delivery of a source/section/date must register as new."""
        res = self.tracker.register_batch(
            source="SRC-01",
            section="customers",
            business_date=self.bdate,
            revision=1,
            checksum="abc123sha256",
            run_id="RUN-1",
        )
        self.assertTrue(res.is_new)
        self.assertFalse(res.is_identical_replay)
        self.assertFalse(res.is_conflicting_revision)

    def test_verified_identical_replay_emits_info(self):
        """Re-delivery of identical checksum and revision must emit INFO finding."""
        self.tracker.register_batch(
            source="SRC-01",
            section="customers",
            business_date=self.bdate,
            revision=1,
            checksum="abc123sha256",
            run_id="RUN-1",
        )
        res = self.tracker.register_batch(
            source="SRC-01",
            section="customers",
            business_date=self.bdate,
            revision=1,
            checksum="abc123sha256",
            run_id="RUN-2",
        )
        self.assertFalse(res.is_new)
        self.assertTrue(res.is_identical_replay)
        self.assertFalse(res.is_conflicting_revision)
        self.assertEqual(len(res.findings), 1)
        self.assertEqual(res.findings[0].severity, FindingSeverity.INFO)

    def test_conflicting_same_revision_emits_critical(self):
        """Delivery with same revision but different checksum must emit CRITICAL finding."""
        self.tracker.register_batch(
            source="SRC-01",
            section="customers",
            business_date=self.bdate,
            revision=1,
            checksum="abc123sha256",
            run_id="RUN-1",
        )
        res = self.tracker.register_batch(
            source="SRC-01",
            section="customers",
            business_date=self.bdate,
            revision=1,
            checksum="different_checksum_456",
            run_id="RUN-3",
        )
        self.assertFalse(res.is_new)
        self.assertFalse(res.is_identical_replay)
        self.assertTrue(res.is_conflicting_revision)
        self.assertEqual(len(res.findings), 1)
        self.assertEqual(res.findings[0].severity, FindingSeverity.CRITICAL)

    def test_superseding_revision_and_stale_rejection(self):
        """Higher revision succeeds; lower revision is rejected as stale (CRITICAL)."""
        self.tracker.register_batch("SRC-01", "customers", self.bdate, 1, "chk1", "RUN-1")
        # Revision 2 supersedes
        res2 = self.tracker.register_batch("SRC-01", "customers", self.bdate, 2, "chk2", "RUN-2")
        self.assertTrue(res2.is_superseding_revision)
        self.assertEqual(self.tracker.get_latest_revision("SRC-01", "customers", self.bdate), 2)

        # Stale delivery with revision 1 rejected
        res_stale = self.tracker.register_batch("SRC-01", "customers", self.bdate, 1, "chk1_stale", "RUN-3")
        self.assertTrue(res_stale.is_stale_revision)
        self.assertTrue(any(f.severity == FindingSeverity.CRITICAL for f in res_stale.findings))


if __name__ == "__main__":
    unittest.main()
