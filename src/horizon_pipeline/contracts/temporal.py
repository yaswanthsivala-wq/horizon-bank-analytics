"""PD-07 America/Chicago Temporal Engine and Tzdb Verification Interface.

Enforces:
- Timezone: America/Chicago via Python standard library zoneinfo
- Parse offset-qualified ISO timestamps
- Reject missing offset
- Reject fractional precision > 6 digits (no silent truncation)
- Normalize instants to UTC with microsecond precision
- Derive Chicago local time and calendar date
- D+1 midnight cutoff with cutoff-minus-one-microsecond point matching
- Half-open effective intervals [start, end)
- Spring-forward gap and fall-back fold detection
- Supplied offset verification against America/Chicago
- IANA tzdb 2026a proof interface (reports PENDING when unverified)
"""

from __future__ import annotations

import re
import zoneinfo
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Any

from .findings import Disposition, FindingSeverity, ValidationFinding
from .states import ContractState

CHICAGO_TZ = zoneinfo.ZoneInfo("America/Chicago")
UTC = timezone.utc
DOCUMENTARY_TARGET_TZDB = "2026a"

TIMESTAMP_REGEX = re.compile(
    r"^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})(?:\.(\d+))?(Z|[+-]\d{2}:\d{2})$"
)


@dataclass(frozen=True)
class TzdbProofResult:
    """Proof status of the runtime IANA tzdb version."""

    target_version: str
    detected_version: str | None
    is_verified: bool
    state: ContractState
    evidence: str


@dataclass(frozen=True)
class NormalizedInstant:
    """An instant parsed with offset, normalized to UTC and Chicago local time."""

    raw_text: str
    utc_instant: datetime
    chicago_local: datetime
    chicago_date: date
    offset_str: str


def get_tzdb_runtime_proof(target_version: str = DOCUMENTARY_TARGET_TZDB) -> TzdbProofResult:
    """Inspect the Python runtime environment for tzdb version evidence.

    Does not fabricate version evidence. If target 2026a is unproven,
    returns state=PENDING.
    """
    detected_version: str | None = None
    try:
        import tzdata
        detected_version = getattr(tzdata, "__version__", None)
    except ImportError:
        pass

    if detected_version == target_version:
        return TzdbProofResult(
            target_version=target_version,
            detected_version=detected_version,
            is_verified=True,
            state=ContractState.ACTIVE,
            evidence=f"Runtime tzdata module verified at version {detected_version}",
        )

    # Could not prove target 2026a
    evidence_desc = (
        f"Detected runtime tzdata version '{detected_version}', which does not match target '{target_version}'"
        if detected_version
        else f"No runtime tzdata version metadata available to prove target '{target_version}'"
    )
    return TzdbProofResult(
        target_version=target_version,
        detected_version=detected_version,
        is_verified=False,
        state=ContractState.PENDING,
        evidence=evidence_desc,
    )


def parse_offset_timestamp(ts_str: str, check_chicago_offset: bool = True) -> NormalizedInstant:
    """Parse an offset-qualified timestamp string into a NormalizedInstant.

    Validates:
    - Missing offset rejected
    - Microsecond precision: >6 fractional digits rejected (no silent rounding)
    - Offset matches America/Chicago at that instant if check_chicago_offset=True
    """
    if not isinstance(ts_str, str):
        raise TypeError(f"Timestamp must be string, got {type(ts_str)}")

    match = TIMESTAMP_REGEX.fullmatch(ts_str.strip())
    if not match:
        raise ValueError(f"Timestamp '{ts_str}' does not match offset-qualified ISO format (missing offset or malformed)")

    date_part, time_part, frac_part, offset_part = match.groups()

    if frac_part is not None and len(frac_part) > 6:
        raise ValueError(
            f"Timestamp '{ts_str}' has {len(frac_part)} fractional digits; "
            "silent truncation beyond 6 digits is forbidden per PD-07"
        )

    # Pad or construct microseconds
    microsecond = int(frac_part.ljust(6, "0")) if frac_part else 0

    h, m, s = (int(x) for x in time_part.split(":"))
    y, mon, d = (int(x) for x in date_part.split("-"))

    # Parse offset
    if offset_part == "Z":
        tz = UTC
    else:
        sign = 1 if offset_part[0] == "+" else -1
        off_h = int(offset_part[1:3])
        off_m = int(offset_part[4:6])
        tz = timezone(sign * timedelta(hours=off_h, minutes=off_m))

    try:
        dt_local = datetime(y, mon, d, h, m, s, microsecond, tzinfo=tz)
    except ValueError as exc:
        raise ValueError(f"Invalid date/time values in '{ts_str}': {exc}") from exc

    # Normalize to UTC
    dt_utc = dt_local.astimezone(UTC)

    # Chicago local representation
    dt_chicago = dt_utc.astimezone(CHICAGO_TZ)

    # Validate that supplied offset matches America/Chicago if required
    if check_chicago_offset:
        # What is the actual Chicago offset at this UTC instant?
        expected_offset = dt_chicago.utcoffset()
        actual_offset = dt_local.utcoffset()
        if actual_offset != expected_offset:
            raise ValueError(
                f"Supplied offset '{offset_part}' does not match America/Chicago offset "
                f"({expected_offset}) at instant {dt_utc.isoformat()}"
            )

    return NormalizedInstant(
        raw_text=ts_str,
        utc_instant=dt_utc,
        chicago_local=dt_chicago,
        chicago_date=dt_chicago.date(),
        offset_str=offset_part,
    )


def chicago_midnight_utc(d: date) -> datetime:
    """Return the UTC instant corresponding to 00:00:00.000000 America/Chicago on date d.

    Handles 23-hour and 25-hour days correctly through the zone.
    """
    # Construct naive midnight, then localize with fold=0
    dt_local = datetime(d.year, d.month, d.day, 0, 0, 0, 0, tzinfo=CHICAGO_TZ)
    return dt_local.astimezone(UTC)


def chicago_next_midnight_utc(d: date) -> datetime:
    """Return the UTC instant of D+1 00:00:00.000000 America/Chicago."""
    return chicago_midnight_utc(d + timedelta(days=1))


def chicago_cutoff_minus_one_microsecond_utc(d: date) -> datetime:
    """Return the exclusive cutoff point match instant: D+1 midnight minus 1 microsecond."""
    next_midnight = chicago_next_midnight_utc(d)
    return next_midnight - timedelta(microseconds=1)


def is_in_chicago_business_day(instant: datetime, business_date: date) -> bool:
    """Check if an instant falls within Chicago business date [D 00:00, D+1 00:00)."""
    utc_instant = instant.astimezone(UTC)
    start_utc = chicago_midnight_utc(business_date)
    end_utc = chicago_next_midnight_utc(business_date)
    return start_utc <= utc_instant < end_utc


def is_in_half_open_interval(instant: datetime, start: datetime, end: datetime | None) -> bool:
    """Check if an instant is within [start, end). If end is None, interval is [start, infinity)."""
    utc_instant = instant.astimezone(UTC)
    utc_start = start.astimezone(UTC)
    if utc_instant < utc_start:
        return False
    if end is not None:
        utc_end = end.astimezone(UTC)
        if utc_instant >= utc_end:
            return False
    return True


def check_dst_gap_or_fold(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    second: int = 0,
    microsecond: int = 0,
) -> tuple[bool, bool]:
    """Check whether a wall-clock local time in America/Chicago is in a DST gap or DST fold.

    Returns (is_gap, is_fold):
    - is_gap: True if local time does not exist (e.g. spring forward 02:00 -> 03:00)
    - is_fold: True if local time is ambiguous (e.g. fall back 01:00 -> 02:00 occurs twice)
    """
    dt_fold0 = datetime(year, month, day, hour, minute, second, microsecond, fold=0, tzinfo=CHICAGO_TZ)
    dt_fold1 = datetime(year, month, day, hour, minute, second, microsecond, fold=1, tzinfo=CHICAGO_TZ)

    back0 = dt_fold0.astimezone(UTC).astimezone(CHICAGO_TZ)
    back1 = dt_fold1.astimezone(UTC).astimezone(CHICAGO_TZ)

    target_tuple = (year, month, day, hour, minute, second, microsecond)
    tuple0 = (back0.year, back0.month, back0.day, back0.hour, back0.minute, back0.second, back0.microsecond)
    tuple1 = (back1.year, back1.month, back1.day, back1.hour, back1.minute, back1.second, back1.microsecond)

    # If neither fold round-trips to the requested wall time, the wall time does not exist (GAP)
    if tuple0 != target_tuple and tuple1 != target_tuple:
        return True, False

    # If both round-trip to the requested wall time and their offsets differ, it occurs twice (FOLD)
    if dt_fold0.utcoffset() != dt_fold1.utcoffset():
        return False, True

    # Ordinary time
    return False, False
