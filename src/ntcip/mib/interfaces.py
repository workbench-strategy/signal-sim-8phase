"""Layer 2 interfaces for OID <-> domain object translation."""

from __future__ import annotations

from typing import Any, Optional, Protocol, Type, TypeVar, runtime_checkable

from ntcip.mib.types import MibObjectDefinition
from ntcip.protocol.models import SnmpVarBind

T = TypeVar("T")


@runtime_checkable
class MibObjectMapper(Protocol):
    """
    Translates SNMP varbinds to/from strongly typed domain values.

    Implementations consult a :class:`~ntcip.mib.registry.MibRegistry` for
    SYNTAX metadata and optional codec hooks.
    """

    def resolve(self, oid: str) -> MibObjectDefinition:
        """Look up the MIB definition for an OID (exact or prefix)."""

    def to_domain(self, varbind: SnmpVarBind) -> Any:
        """Decode a varbind into a domain value using the registered codec."""

    def to_domain_as(self, varbind: SnmpVarBind, domain_type: Type[T]) -> T:
        """Decode and assert the result is an instance of ``domain_type``."""

    def to_varbind(self, oid: str, value: Any) -> SnmpVarBind:
        """Encode a domain value into a varbind for SNMP SET."""

    def validate_type(
        self, oid: str, reported_asn1_type: Optional[str]
    ) -> MibObjectDefinition:
        """
        Ensure the reported ASN.1 type is compatible with the MIB SYNTAX.

        Raises:
            OidMismatchError: on incompatible types.
            OidNotFoundError: if the OID is unknown.
        """
