"""Unit tests for PD-07 America/Chicago Temporal Engine.

Translates the approved 15 PD-07 documentary temporal cases into executable unit tests:
- T01 standard-time ordinary date
- T02 daylight-time ordinary date
- T03 spring transition
- T04 spring gap
- T05 fall transition
- T06 fall fold
- T07 23-hour local day
- T08 25-hour local day
- T09 local midnight
- T10 due/calendar date
- T11 cutoff minus one microsecond
- T12 cutoff exact boundary
- T13 effective intervals [start, end)
- T14 supplied-offset mismatch
- T15 excess precision and tzdb proof interface
"""

import unittest
from datetime import date, datetime, timedelta, timezone

from horizon_pipeline.contracts.states import ContractState
from horizon_pipeline.contracts.temporal import (
    CHICAGO_TZ,
    UTC,
    check_dst_gap_or_fold,
    chicago_cutoff_minus_one_microsecond_utc,
    chicago_midnight_utc,
    chicago_next_midnight_utc,
    get_tzdb_runtime_proof,
    is_in_chicago_business_day,
    is_in_half_open_interval,
    parse_offset_timestamp,
)


class TemporalEngineTests(unittest.TestCase):
    def test_t01_standard_time_ordinary_date(self):
        """T01: Winter standard-time date has -06:00 offset and round-trips to UTC."""
        ts = "2025-01-15T12:00:00.000000-06:00"
        parsed = parse_offset_timestamp(ts)
        self.assertEqual(parsed.chicago_date, date(2025, 1, 15))
        self.assertEqual(parsed.utc_instant, datetime(2025, 1, 15, 18, 0, 0, tzinfo=UTC))
        self.assertEqual(parsed.offset_str, "-06:00")

    def test_t02_daylight_time_ordinary_date(self):
        """T02: Summer daylight-time date has -05:00 offset and round-trips to UTC."""
        ts = "2025-07-15T12:00:00.000000-05:00"
        parsed = parse_offset_timestamp(ts)
        self.assertEqual(parsed.chicago_date, date(2025, 7, 15))
        self.assertEqual(parsed.utc_instant, datetime(2025, 7, 15, 17, 0, 0, tzinfo=UTC))
        self.assertEqual(parsed.offset_str, "-05:00")

    def test_t03_spring_transition(self):
        """T03: Spring transition on 2025-03-09 shifts offset from -06:00 to -05:00."""
        # 01:59:59 Chicago is standard time (-06:00) -> 07:59:59Z
        before_gap = parse_offset_timestamp("2025-03-09T01:59:59.000000-06:00")
        self.assertEqual(before_gap.utc_instant, datetime(2025, 3, 9, 7, 59, 59, tzinfo=UTC))

        # 03:00:00 Chicago is daylight time (-05:00) -> 08:00:00Z
        after_gap = parse_offset_timestamp("2025-03-09T03:00:00.000000-05:00")
        self.assertEqual(after_gap.utc_instant, datetime(2025, 3, 9, 8, 0, 0, tzinfo=UTC))

        # Exactly 1 second elapsed in UTC
        self.assertEqual(after_gap.utc_instant - before_gap.utc_instant, timedelta(seconds=1))

    def test_t04_spring_gap_rejected(self):
        """T04: Local wall time in spring-forward gap (02:00-02:59) is nonexistent."""
        is_gap, is_fold = check_dst_gap_or_fold(2025, 3, 9, 2, 30, 0)
        self.assertTrue(is_gap, "2025-03-09 02:30 must be detected as a DST gap")
        self.assertFalse(is_fold)

        # Attempting to declare 02:30 with -06:00 or -05:00 offset fails Chicago offset verification
        with self.assertRaises(ValueError):
            parse_offset_timestamp("2025-03-09T02:30:00.000000-06:00", check_chicago_offset=True)

    def test_t05_fall_transition(self):
        """T05: Fall transition on 2025-11-02 shifts offset from -05:00 to -06:00."""
        # 00:59:59 Chicago before transition is daylight time (-05:00)
        ts1 = parse_offset_timestamp("2025-11-02T00:59:59.000000-05:00")
        self.assertEqual(ts1.utc_instant, datetime(2025, 11, 2, 5, 59, 59, tzinfo=UTC))

        # First 01:30:00 Chicago with -05:00 -> 06:30:00Z
        ts_fold0 = parse_offset_timestamp("2025-11-02T01:30:00.000000-05:00")
        self.assertEqual(ts_fold0.utc_instant, datetime(2025, 11, 2, 6, 30, 0, tzinfo=UTC))

        # Second 01:30:00 Chicago with -06:00 -> 07:30:00Z
        ts_fold1 = parse_offset_timestamp("2025-11-02T01:30:00.000000-06:00")
        self.assertEqual(ts_fold1.utc_instant, datetime(2025, 11, 2, 7, 30, 0, tzinfo=UTC))

        # Distinct UTC instants 1 hour apart
        self.assertEqual(ts_fold1.utc_instant - ts_fold0.utc_instant, timedelta(hours=1))

    def test_t06_fall_fold_detection(self):
        """T06: Fall fold (01:00-01:59) is detected as ambiguous fold."""
        is_gap, is_fold = check_dst_gap_or_fold(2025, 11, 2, 1, 30, 0)
        self.assertFalse(is_gap)
        self.assertTrue(is_fold, "2025-11-02 01:30 must be detected as a DST fold")

        # Offset-free string is rejected by parser
        with self.assertRaises(ValueError):
            parse_offset_timestamp("2025-11-02T01:30:00.000000")

    def test_t07_23_hour_local_day(self):
        """T07: 2025-03-09 Chicago has 23 hours: 00:00 is 06:00Z, next 00:00 is 05:00Z."""
        m_start = chicago_midnight_utc(date(2025, 3, 9))
        m_end = chicago_next_midnight_utc(date(2025, 3, 9))
        self.assertEqual(m_start, datetime(2025, 3, 9, 6, 0, 0, tzinfo=UTC))
        self.assertEqual(m_end, datetime(2025, 3, 10, 5, 0, 0, tzinfo=UTC))
        self.assertEqual(m_end - m_start, timedelta(hours=23))

    def test_t08_25_hour_local_day(self):
        """T08: 2025-11-02 Chicago has 25 hours: 00:00 is 05:00Z, next 00:00 is 06:00Z."""
        m_start = chicago_midnight_utc(date(2025, 11, 2))
        m_end = chicago_next_midnight_utc(date(2025, 11, 2))
        self.assertEqual(m_start, datetime(2025, 11, 2, 5, 0, 0, tzinfo=UTC))
        self.assertEqual(m_end, datetime(2025, 11, 3, 6, 0, 0, tzinfo=UTC))
        self.assertEqual(m_end - m_start, timedelta(hours=25))

    def test_t09_local_midnight(self):
        """T09: Business date D maps to exact Chicago midnight in UTC."""
        # Winter date
        m_winter = chicago_midnight_utc(date(2025, 1, 15))
        self.assertEqual(m_winter, datetime(2025, 1, 15, 6, 0, 0, tzinfo=UTC))

        # Summer date
        m_summer = chicago_midnight_utc(date(2025, 7, 15))
        self.assertEqual(m_summer, datetime(2025, 7, 15, 5, 0, 0, tzinfo=UTC))

    def test_t10_due_calendar_date(self):
        """T10: Due date is a calendar date resolved via Chicago calendar, not fixed UTC midnight."""
        due_d = date(2025, 3, 9)
        due_midnight = chicago_midnight_utc(due_d)
        # Resolved at Chicago midnight (06:00Z), not 00:00Z
        self.assertEqual(due_midnight, datetime(2025, 3, 9, 6, 0, 0, tzinfo=UTC))

    def test_t11_cutoff_minus_one_microsecond(self):
        """T11: Cutoff point match is exactly D+1 midnight minus 1 microsecond."""
        bdate = date(2025, 3, 9)
        next_m = chicago_next_midnight_utc(bdate)
        cutoff_pt = chicago_cutoff_minus_one_microsecond_utc(bdate)

        self.assertEqual(cutoff_pt, next_m - timedelta(microseconds=1))
        # Cutoff point is still within business date D [D 00:00, D+1 00:00)
        self.assertTrue(is_in_chicago_business_day(cutoff_pt, bdate))

    def test_t12_cutoff_exact_boundary(self):
        """T12: Event at exclusive cutoff boundary belongs to next period, not D."""
        bdate = date(2025, 3, 9)
        next_m = chicago_next_midnight_utc(bdate)
        # Exact boundary is exclusive for D
        self.assertFalse(is_in_chicago_business_day(next_m, bdate))
        # Belongs to D+1
        self.assertTrue(is_in_chicago_business_day(next_m, date(2025, 3, 10)))

    def test_t13_effective_interval_half_open(self):
        """T13: Half-open interval [start, end) selects versions without overlap or backfill."""
        start = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)
        end = datetime(2025, 6, 1, 0, 0, 0, tzinfo=UTC)

        # Exact start is included
        self.assertTrue(is_in_half_open_interval(start, start, end))
        # Midpoint is included
        mid = datetime(2025, 3, 15, 12, 0, 0, tzinfo=UTC)
        self.assertTrue(is_in_half_open_interval(mid, start, end))
        # Exact end is excluded
        self.assertFalse(is_in_half_open_interval(end, start, end))
        # Instant before start is excluded
        before = start - timedelta(microseconds=1)
        self.assertFalse(is_in_half_open_interval(before, start, end))

    def test_t14_supplied_offset_mismatch(self):
        """T14: Reject timestamp where supplied offset contradicts America/Chicago at that instant."""
        # On 2025-01-15 (winter), Chicago is UTC-6. Supplying +01:00 or -05:00 fails verification
        with self.assertRaises(ValueError):
            parse_offset_timestamp("2025-01-15T12:00:00.000000-05:00", check_chicago_offset=True)

    def test_t15_excess_precision_and_tzdb_proof(self):
        """T15: Reject >6 fractional digits and verify tzdb proof interface reports PENDING."""
        # >6 fractional digits rejected (no silent truncation)
        with self.assertRaises(ValueError):
            parse_offset_timestamp("2025-01-15T12:00:00.1234567-06:00")

        # Runtime proof interface
        proof = get_tzdb_runtime_proof("2026a")
        self.assertFalse(proof.is_verified)
        self.assertEqual(proof.state, ContractState.PENDING)


if __name__ == "__main__":
    unittest.main()
