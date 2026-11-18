"""
Shared exception hierarchy for the NTCIP stack.

All layers raise subclasses of :class:`NtcipError` so callers can catch
transport, authentication, and object-mapping failures uniformly.
"""

from __future__ import annotations


class NtcipError(Exception):
    """Base exception for all NTCIP stack failures."""


class SnmpError(NtcipError):
    """Layer 1: SNMP protocol / transport failure."""


class SnmpTimeoutError(SnmpError):
    """No response received before the configured timeout expired."""

    def __init__(self, host: str, oid: str, timeout_seconds: float) -> None:
        self.host = host
        self.oid = oid
        self.timeout_seconds = timeout_seconds
        super().__init__(
            f"SNMP timeout after {timeout_seconds:.2f}s talking to {host} "
            f"for OID {oid}"
        )


class SnmpAuthenticationError(SnmpError):
    """SNMPv1/v2c community or SNMPv3 USM credentials were rejected."""

    def __init__(self, host: str, detail: str = "authentication failure") -> None:
        self.host = host
        self.detail = detail
        super().__init__(f"SNMP authentication failed for {host}: {detail}")


class SnmpTransportError(SnmpError):
    """UDP send/receive or socket-level failure."""

    def __init__(self, host: str, detail: str) -> None:
        self.host = host
        self.detail = detail
        super().__init__(f"SNMP transport error for {host}: {detail}")


class MibError(NtcipError):
    """Layer 2: MIB registry / OID mapping failure."""


class OidNotFoundError(MibError):
    """Requested OID is not registered in the MIB tree."""

    def __init__(self, oid: str) -> None:
        self.oid = oid
        super().__init__(f"OID not found in MIB registry: {oid}")


class OidMismatchError(MibError):
    """
    Runtime value type does not match the ASN.1 type declared for the OID.

    Per NTCIP practice, Managers must validate returned SYNTAX against the
    MIB definition before promoting a value into a domain object.
    """

    def __init__(self, oid: str, expected: str, actual: str) -> None:
        self.oid = oid
        self.expected = expected
        self.actual = actual
        super().__init__(
            f"OID type mismatch for {oid}: expected {expected}, got {actual}"
        )


class Asn1CodecError(MibError):
    """ASN.1 BER encode/decode failure for an NTCIP data type."""


class BusinessLogicError(NtcipError):
    """Layer 3: invalid business intent or adapter failure."""
