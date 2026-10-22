"""Default :class:`MibObjectMapper` implementation."""

from __future__ import annotations

from typing import Any, Optional, Type, TypeVar

from ntcip.exceptions import OidMismatchError
from ntcip.mib.registry import MibRegistry
from ntcip.mib.types import Asn1Type, MibObjectDefinition
from ntcip.protocol.models import SnmpVarBind

T = TypeVar("T")

# Types that are considered compatible for mismatch checks.
_COMPATIBLE = {
    Asn1Type.INTEGER: {"INTEGER", "Integer32", "INTEGER32", "int"},
    Asn1Type.INTEGER32: {"INTEGER", "Integer32", "INTEGER32", "int"},
    Asn1Type.UNSIGNED32: {"Unsigned32", "Gauge32", "UNSIGNED32", "int"},
    Asn1Type.OCTET_STRING: {"OCTET STRING", "OCTETSTRING", "bytes", "str"},
    Asn1Type.DISPLAY_STRING: {
        "DisplayString",
        "OCTET STRING",
        "OCTETSTRING",
        "str",
    },
    Asn1Type.DATE_AND_TIME: {
        "DateAndTime",
        "OCTET STRING",
        "OCTETSTRING",
        "bytes",
    },
    Asn1Type.OBJECT_IDENTIFIER: {"OBJECT IDENTIFIER", "OID"},
    Asn1Type.COUNTER32: {"Counter32", "COUNTER32"},
    Asn1Type.GAUGE32: {"Gauge32", "GAUGE32", "Unsigned32"},
    Asn1Type.TIMETICKS: {"TimeTicks", "TIMETICKS"},
}


class DefaultMibObjectMapper:
    """Registry-backed mapper with ASN.1 SYNTAX validation."""

    def __init__(self, registry: MibRegistry) -> None:
        self._registry = registry

    @property
    def registry(self) -> MibRegistry:
        return self._registry

    def resolve(self, oid: str) -> MibObjectDefinition:
        return self._registry.resolve(oid)

    def validate_type(
        self, oid: str, reported_asn1_type: Optional[str]
    ) -> MibObjectDefinition:
        definition = self._registry.resolve(oid)
        if reported_asn1_type is None:
            return definition
        expected = definition.asn1_type
        allowed = _COMPATIBLE.get(expected, {expected.value})
        normalized = reported_asn1_type.strip()
        if normalized not in allowed and normalized != expected.value:
            raise OidMismatchError(oid, expected.value, normalized)
        return definition

    def to_domain(self, varbind: SnmpVarBind) -> Any:
        definition = self.validate_type(varbind.oid, varbind.asn1_type)
        return definition.decode(varbind.value)

    def to_domain_as(self, varbind: SnmpVarBind, domain_type: Type[T]) -> T:
        value = self.to_domain(varbind)
        if not isinstance(value, domain_type):
            raise OidMismatchError(
                varbind.oid,
                domain_type.__name__,
                type(value).__name__,
            )
        return value

    def to_varbind(self, oid: str, value: Any) -> SnmpVarBind:
        definition = self._registry.resolve(oid)
        if definition.read_only:
            raise OidMismatchError(oid, "writable object", "read-only object")
        encoded = definition.encode(value)
        return SnmpVarBind(
            oid=oid,
            value=encoded,
            asn1_type=definition.asn1_type.value,
        )
