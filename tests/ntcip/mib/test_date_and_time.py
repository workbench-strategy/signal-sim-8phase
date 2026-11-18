"""Tests for NTCIP DateAndTime codec."""

from __future__ import annotations

from datetime import datetime

import pytest

from ntcip.exceptions import Asn1CodecError
from ntcip.mib.date_and_time import NtcipDateAndTime


def test_round_trip_octets():
    original = NtcipDateAndTime(2026, 8, 3, 14, 30, 45, 7)
    encoded = original.to_octets()
    assert len(encoded) == 8
    assert encoded[0] == 0x07 and encoded[1] == 0xEA  # 2026
    decoded = NtcipDateAndTime.from_octets(encoded)
    assert decoded == original


def test_parse_and_format_hyphenated():
    text = "2026-08-03-14-30-45-7"
    value = NtcipDateAndTime.parse(text)
    assert value.format() == text
    assert str(value) == text


def test_from_datetime_deci_seconds():
    dt = datetime(2026, 1, 2, 3, 4, 5, 600_000)
    value = NtcipDateAndTime.from_datetime(dt)
    assert value.deci_second == 6
    assert value.to_datetime().microsecond == 600_000


def test_invalid_length_raises():
    with pytest.raises(Asn1CodecError):
        NtcipDateAndTime.from_octets(b"\x00\x01\x02")


def test_invalid_month_raises():
    with pytest.raises(Asn1CodecError):
        NtcipDateAndTime(2026, 13, 1, 0, 0, 0, 0)


def test_parse_bad_field_count():
    with pytest.raises(Asn1CodecError):
        NtcipDateAndTime.parse("2026-08-03")
