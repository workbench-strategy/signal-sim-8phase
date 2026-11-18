"""
Example mappings from NTCIP 1202 -- Object Definitions for ASC.

OID tree::

    1.3.6.1.4.1.1206.4.2.1     -- asc (Actuated Signal Controller)
      .1                       -- phase
        .4                     -- phaseStatusGroupTable
          .1                   -- phaseStatusGroupEntry
            .2                 -- phaseStatusGroupReds
            .3                 -- phaseStatusGroupYellows
            .4                 -- phaseStatusGroupGreens

Each status group is an OCTET STRING bitfield where bit N (1-based in the
NTCIP sense: bit 0 of the first octet = phase 1) indicates that phase's
red/yellow/green status is active.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from ntcip.mib.types import Asn1Type, MibObjectDefinition

_PHASE_STATUS_ENTRY = "1.3.6.1.4.1.1206.4.2.1.1.4.1"

PHASE_STATUS_GROUP_REDS_OID = f"{_PHASE_STATUS_ENTRY}.2.1"
PHASE_STATUS_GROUP_YELLOWS_OID = f"{_PHASE_STATUS_ENTRY}.3.1"
PHASE_STATUS_GROUP_GREENS_OID = f"{_PHASE_STATUS_ENTRY}.4.1"
"""phaseStatusGroupGreens.1 -- green bits for phases 1..8 (typical group)."""


@dataclass(frozen=True)
class PhaseStatusGroup:
    """
    Decoded phase status bitfield for one status group (usually phases 1-8).

    NTCIP 1202 encodes eight phases per octet; bit ``(phase - 1)`` is set
    when that color is active for the phase.
    """

    raw: bytes
    group_index: int = 1

    @classmethod
    def from_octet(cls, value: object, group_index: int = 1) -> "PhaseStatusGroup":
        if isinstance(value, int):
            raw = bytes([value & 0xFF])
        elif isinstance(value, (bytes, bytearray)):
            raw = bytes(value)
        elif isinstance(value, str):
            # Allow hex strings from stubs / logs
            raw = bytes.fromhex(value) if all(
                c in "0123456789abcdefABCDEF" for c in value
            ) else value.encode("ascii")
        else:
            raise TypeError(f"unsupported phase status value: {type(value)!r}")
        if not raw:
            raw = b"\x00"
        return cls(raw=raw, group_index=group_index)

    def is_active(self, phase: int) -> bool:
        """Return True if ``phase`` (1-based) has this color active."""
        if phase < 1:
            raise ValueError("phase numbers are 1-based")
        byte_index, bit_index = divmod(phase - 1, 8)
        if byte_index >= len(self.raw):
            return False
        return bool(self.raw[byte_index] & (1 << bit_index))

    def active_phases(self, max_phase: int = 8) -> List[int]:
        return [p for p in range(1, max_phase + 1) if self.is_active(p)]


def _decode_phase_status(raw: object) -> PhaseStatusGroup:
    return PhaseStatusGroup.from_octet(raw)


def _encode_phase_status(value: object) -> bytes:
    if isinstance(value, PhaseStatusGroup):
        return value.raw
    return PhaseStatusGroup.from_octet(value).raw


def asc_1202_definitions() -> List[MibObjectDefinition]:
    """Return scaffold definitions for selected NTCIP 1202 ASC objects."""
    return [
        MibObjectDefinition(
            oid=PHASE_STATUS_GROUP_REDS_OID,
            name="phaseStatusGroupReds",
            asn1_type=Asn1Type.OCTET_STRING,
            standard="NTCIP 1202",
            domain_type=PhaseStatusGroup,
            description="Bitfield of phases currently showing Red.",
            decoder=_decode_phase_status,
            encoder=_encode_phase_status,
            read_only=True,
        ),
        MibObjectDefinition(
            oid=PHASE_STATUS_GROUP_YELLOWS_OID,
            name="phaseStatusGroupYellows",
            asn1_type=Asn1Type.OCTET_STRING,
            standard="NTCIP 1202",
            domain_type=PhaseStatusGroup,
            description="Bitfield of phases currently showing Yellow.",
            decoder=_decode_phase_status,
            encoder=_encode_phase_status,
            read_only=True,
        ),
        MibObjectDefinition(
            oid=PHASE_STATUS_GROUP_GREENS_OID,
            name="phaseStatusGroupGreens",
            asn1_type=Asn1Type.OCTET_STRING,
            standard="NTCIP 1202",
            domain_type=PhaseStatusGroup,
            description="Bitfield of phases currently showing Green (Go).",
            decoder=_decode_phase_status,
            encoder=_encode_phase_status,
            read_only=True,
        ),
    ]
