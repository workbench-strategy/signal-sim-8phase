"""
ASN.1 / MIB metadata types for Layer 2.

OID naming follows NTCIP 8004 (SMI) under the NEMA enterprise tree
``1.3.6.1.4.1.1206``.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional, Type


class Asn1Type(str, Enum):
    """
    Subset of ASN.1 / SNMPv2 SYNTAX types used by NTCIP MIBs.

    Values are string tags compared against backend-reported types and used
    for mismatch detection (:class:`~ntcip.exceptions.OidMismatchError`).
    """

    INTEGER = "INTEGER"
    INTEGER32 = "Integer32"
    UNSIGNED32 = "Unsigned32"
    OCTET_STRING = "OCTET STRING"
    OBJECT_IDENTIFIER = "OBJECT IDENTIFIER"
    COUNTER32 = "Counter32"
    GAUGE32 = "Gauge32"
    TIMETICKS = "TimeTicks"
    DISPLAY_STRING = "DisplayString"
    DATE_AND_TIME = "DateAndTime"  # NTCIP 8-octet OCTET STRING


# Domain decode/encode hooks bound to a MIB definition.
Decoder = Callable[[Any], Any]
Encoder = Callable[[Any], Any]


@dataclass(frozen=True)
class MibObjectDefinition:
    """
    Registry entry describing one NTCIP managed object.

    Attributes:
        oid: Dotted numeric OID (instance form, typically ending in ``.0``
            for scalars or ``.<index>`` for columnar objects).
        name: Symbolic MIB name (e.g. ``phaseStatusGroupGreens``).
        asn1_type: Declared SYNTAX from the MIB module.
        standard: Source standard identifier (e.g. ``NTCIP 1202``).
        domain_type: Optional Python type for decoded values.
        description: Human-readable object description.
        decoder / encoder: Optional hooks for complex SYNTAX (DateAndTime).
        read_only: True for read-only MAX-ACCESS objects.
    """

    oid: str
    name: str
    asn1_type: Asn1Type
    standard: str
    domain_type: Optional[Type[Any]] = None
    description: str = ""
    decoder: Optional[Decoder] = None
    encoder: Optional[Encoder] = None
    read_only: bool = False

    def decode(self, raw: Any) -> Any:
        if self.decoder is not None:
            return self.decoder(raw)
        return raw

    def encode(self, value: Any) -> Any:
        if self.encoder is not None:
            return self.encoder(value)
        return value
