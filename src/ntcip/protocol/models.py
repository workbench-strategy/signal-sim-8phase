"""
Transport-level SNMP models used by Layer 1.

These types intentionally stay library-agnostic so a pysnmp, Net-SNMP, or
custom backend can map them without leaking vendor APIs upward.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable, Optional, Sequence, Tuple


class SnmpVersion(str, Enum):
    """Supported SNMP protocol versions (NTCIP 1103 profiles)."""

    V1 = "1"
    V2C = "2c"
    V3 = "3"


@dataclass(frozen=True)
class SnmpCredentials:
    """
    Authentication material for an SNMP target.

    For v1/v2c, ``community`` is required. For v3, supply USM fields.
    """

    community: str = "public"
    version: SnmpVersion = SnmpVersion.V2C
    # SNMPv3 USM (optional)
    username: Optional[str] = None
    auth_key: Optional[str] = None
    priv_key: Optional[str] = None
    auth_protocol: Optional[str] = None  # e.g. "SHA", "MD5"
    priv_protocol: Optional[str] = None  # e.g. "AES", "DES"


@dataclass(frozen=True)
class SnmpVarBind:
    """A single OID/value binding in an SNMP PDU."""

    oid: str
    value: Any = None
    asn1_type: Optional[str] = None


@dataclass(frozen=True)
class SnmpGetRequest:
    """Async GET request parameters."""

    host: str
    oids: Tuple[str, ...]
    credentials: SnmpCredentials = field(default_factory=SnmpCredentials)
    port: int = 161
    timeout_seconds: float = 2.0
    retries: int = 1


@dataclass(frozen=True)
class SnmpSetRequest:
    """Async SET request parameters."""

    host: str
    varbinds: Tuple[SnmpVarBind, ...]
    credentials: SnmpCredentials = field(default_factory=SnmpCredentials)
    port: int = 161
    timeout_seconds: float = 2.0
    retries: int = 1


@dataclass(frozen=True)
class SnmpResponse:
    """Normalized response from any SNMP backend."""

    host: str
    varbinds: Tuple[SnmpVarBind, ...]
    request_id: Optional[int] = None
    error_status: int = 0
    error_index: int = 0


TrapCallback = Callable[[SnmpResponse], Awaitable[None]]


@dataclass(frozen=True)
class TrapSubscription:
    """Handle returned by :meth:`SnmpEngine.subscribe_to_traps`."""

    listen_host: str
    listen_port: int
    subscription_id: str


def as_oid_tuple(oids: Sequence[str]) -> Tuple[str, ...]:
    """Normalize a sequence of OID strings to an immutable tuple."""
    if not oids:
        raise ValueError("At least one OID is required")
    return tuple(oids)
