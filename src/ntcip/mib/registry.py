"""
Generic MIB registry / OID tree for NTCIP managed objects.

Stores OID -> ASN.1 type -> domain mapping metadata. Populate via
:class:`MibRegistryBuilder` or :func:`build_default_ntcip_registry`.
"""

from __future__ import annotations

from typing import Dict, Iterable, Iterator, List, Optional

from ntcip.exceptions import OidNotFoundError
from ntcip.mib.types import MibObjectDefinition


class MibRegistry:
    """
    In-memory OID catalog.

    Lookup strategy:
      1. Exact OID match (preferred for instances).
      2. Longest-prefix match against registered columnar/scalar bases.
    """

    def __init__(self, definitions: Optional[Iterable[MibObjectDefinition]] = None) -> None:
        self._by_oid: Dict[str, MibObjectDefinition] = {}
        self._by_name: Dict[str, MibObjectDefinition] = {}
        if definitions:
            for definition in definitions:
                self.register(definition)

    def register(self, definition: MibObjectDefinition) -> None:
        """Add or replace a MIB object definition."""
        self._by_oid[definition.oid] = definition
        self._by_name[definition.name] = definition

    def get_by_oid(self, oid: str) -> MibObjectDefinition:
        """Exact OID lookup."""
        try:
            return self._by_oid[oid]
        except KeyError as exc:
            raise OidNotFoundError(oid) from exc

    def get_by_name(self, name: str) -> MibObjectDefinition:
        """Symbolic name lookup."""
        try:
            return self._by_name[name]
        except KeyError as exc:
            raise OidNotFoundError(name) from exc

    def resolve(self, oid: str) -> MibObjectDefinition:
        """Exact match, else longest registered prefix."""
        if oid in self._by_oid:
            return self._by_oid[oid]
        best: Optional[MibObjectDefinition] = None
        best_len = -1
        for registered_oid, definition in self._by_oid.items():
            if oid == registered_oid or oid.startswith(registered_oid + "."):
                if len(registered_oid) > best_len:
                    best = definition
                    best_len = len(registered_oid)
        if best is None:
            raise OidNotFoundError(oid)
        return best

    def __contains__(self, oid: str) -> bool:
        try:
            self.resolve(oid)
            return True
        except OidNotFoundError:
            return False

    def __iter__(self) -> Iterator[MibObjectDefinition]:
        return iter(self._by_oid.values())

    def __len__(self) -> int:
        return len(self._by_oid)

    def oids(self) -> List[str]:
        return list(self._by_oid.keys())


class MibRegistryBuilder:
    """Fluent builder for composing MIB modules (1201, 1202, vendor)."""

    def __init__(self) -> None:
        self._definitions: List[MibObjectDefinition] = []

    def add(self, definition: MibObjectDefinition) -> "MibRegistryBuilder":
        self._definitions.append(definition)
        return self

    def add_all(
        self, definitions: Iterable[MibObjectDefinition]
    ) -> "MibRegistryBuilder":
        self._definitions.extend(definitions)
        return self

    def build(self) -> MibRegistry:
        return MibRegistry(self._definitions)


def build_default_ntcip_registry() -> MibRegistry:
    """
    Construct a registry preloaded with example NTCIP 1201 / 1202 objects.

    This is a scaffold subset -- production systems load full MIB modules
    from ``mibs/`` (SMI parsers or generated Python bindings).
    """
    from ntcip.mib.objects.asc_1202 import asc_1202_definitions
    from ntcip.mib.objects.global_1201 import global_1201_definitions

    return (
        MibRegistryBuilder()
        .add_all(global_1201_definitions())
        .add_all(asc_1202_definitions())
        .build()
    )
