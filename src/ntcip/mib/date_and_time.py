"""
NTCIP DateAndTime codec (8-octet OCTET STRING).

Per NTCIP 1201 Global Object Definitions, DateAndTime is encoded as:

=======  ======  ==================  =========
Field    Octets  Contents            Range
=======  ======  ==================  =========
1        1-2     year (big-endian)   0..65535
2        3       month               1..12
3        4       day                 1..31
4        5       hour                0..23
5        6       minutes             0..59
6        7       seconds             0..60
7        8       deci-seconds        0..9
=======  ======  ==================  =========

The textual form used in documentation is ``YYYY-MM-DD-HH-MM-SS-hh``
where ``hh`` is the deci-second digit (0-9).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Union

from ntcip.exceptions import Asn1CodecError

_DateSource = Union[datetime, "NtcipDateAndTime", bytes, bytearray, str]


@dataclass(frozen=True)
class NtcipDateAndTime:
    """Strongly typed NTCIP DateAndTime value."""

    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int
    deci_second: int = 0

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not 0 <= self.year <= 65535:
            raise Asn1CodecError(f"year out of range: {self.year}")
        if not 1 <= self.month <= 12:
            raise Asn1CodecError(f"month out of range: {self.month}")
        if not 1 <= self.day <= 31:
            raise Asn1CodecError(f"day out of range: {self.day}")
        if not 0 <= self.hour <= 23:
            raise Asn1CodecError(f"hour out of range: {self.hour}")
        if not 0 <= self.minute <= 59:
            raise Asn1CodecError(f"minute out of range: {self.minute}")
        if not 0 <= self.second <= 60:
            raise Asn1CodecError(f"second out of range: {self.second}")
        if not 0 <= self.deci_second <= 9:
            raise Asn1CodecError(f"deci-second out of range: {self.deci_second}")

    # ------------------------------------------------------------------
    # Parsers / serializers
    # ------------------------------------------------------------------

    @classmethod
    def from_octets(cls, data: Union[bytes, bytearray]) -> "NtcipDateAndTime":
        """Decode an 8-octet NTCIP DateAndTime BER payload (value octets)."""
        if len(data) != 8:
            raise Asn1CodecError(
                f"DateAndTime requires 8 octets, got {len(data)}"
            )
        year = (data[0] << 8) | data[1]
        return cls(
            year=year,
            month=data[2],
            day=data[3],
            hour=data[4],
            minute=data[5],
            second=data[6],
            deci_second=data[7],
        )

    def to_octets(self) -> bytes:
        """Serialize to the canonical 8-octet NTCIP encoding."""
        self._validate()
        return bytes(
            [
                (self.year >> 8) & 0xFF,
                self.year & 0xFF,
                self.month,
                self.day,
                self.hour,
                self.minute,
                self.second,
                self.deci_second,
            ]
        )

    @classmethod
    def from_datetime(cls, dt: datetime) -> "NtcipDateAndTime":
        """Build from a :class:`datetime` (deci-seconds from microseconds)."""
        deci = min(9, dt.microsecond // 100_000)
        return cls(
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=dt.hour,
            minute=dt.minute,
            second=dt.second,
            deci_second=deci,
        )

    def to_datetime(self) -> datetime:
        """Convert to :class:`datetime` (naive, local cabinet time)."""
        return datetime(
            year=self.year,
            month=self.month,
            day=self.day,
            hour=self.hour,
            minute=self.minute,
            second=min(self.second, 59),
            microsecond=self.deci_second * 100_000,
        )

    @classmethod
    def parse(cls, text: str) -> "NtcipDateAndTime":
        """
        Parse ``YYYY-MM-DD-HH-MM-SS-hh`` (hyphen-separated, 7 fields).

        Also accepts ISO-8601 ``YYYY-MM-DDTHH:MM:SS`` (deci-second = 0).
        """
        text = text.strip()
        if "T" in text:
            dt = datetime.fromisoformat(text)
            return cls.from_datetime(dt)
        parts = text.split("-")
        if len(parts) != 7:
            raise Asn1CodecError(
                "DateAndTime text must be YYYY-MM-DD-HH-MM-SS-hh "
                f"(got {len(parts)} fields)"
            )
        try:
            nums = [int(p) for p in parts]
        except ValueError as exc:
            raise Asn1CodecError(f"invalid DateAndTime text: {text}") from exc
        return cls(
            year=nums[0],
            month=nums[1],
            day=nums[2],
            hour=nums[3],
            minute=nums[4],
            second=nums[5],
            deci_second=nums[6],
        )

    def format(self) -> str:
        """Format as ``YYYY-MM-DD-HH-MM-SS-hh``."""
        return (
            f"{self.year:04d}-{self.month:02d}-{self.day:02d}-"
            f"{self.hour:02d}-{self.minute:02d}-{self.second:02d}-"
            f"{self.deci_second:01d}"
        )

    def __str__(self) -> str:
        return self.format()

    @classmethod
    def coerce(cls, value: _DateSource) -> "NtcipDateAndTime":
        """Best-effort conversion from common source types."""
        if isinstance(value, cls):
            return value
        if isinstance(value, datetime):
            return cls.from_datetime(value)
        if isinstance(value, (bytes, bytearray)):
            return cls.from_octets(value)
        if isinstance(value, str):
            return cls.parse(value)
        raise Asn1CodecError(f"cannot coerce {type(value)!r} to DateAndTime")


def decode_date_and_time(raw: object) -> NtcipDateAndTime:
    """MIB decoder hook."""
    return NtcipDateAndTime.coerce(raw)  # type: ignore[arg-type]


def encode_date_and_time(value: object) -> bytes:
    """MIB encoder hook (wire value = 8 octets)."""
    return NtcipDateAndTime.coerce(value).to_octets()  # type: ignore[arg-type]
