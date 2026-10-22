"""
Layer 1 interfaces (SOLID: Dependency Inversion).

Business and MIB layers depend on these Protocols; concrete SNMP libraries
are injected at composition time.
"""

from __future__ import annotations

from typing import Optional, Protocol, Sequence, runtime_checkable

from ntcip.protocol.models import (
    SnmpCredentials,
    SnmpGetRequest,
    SnmpResponse,
    SnmpSetRequest,
    SnmpVarBind,
    TrapCallback,
    TrapSubscription,
)


@runtime_checkable
class SnmpBackend(Protocol):
    """
    Low-level adapter around a concrete SNMP library (e.g. pysnmp).

    Implement this Protocol to plug in an alternate engine without changing
    Layer 2/3 code. See :mod:`ntcip.protocol.backends`.
    """

    async def send_get(self, request: SnmpGetRequest) -> SnmpResponse:
        """Issue a GET (or GET-NEXT batch) and return normalized varbinds."""

    async def send_set(self, request: SnmpSetRequest) -> SnmpResponse:
        """Issue a SET and return the echoed varbinds."""

    async def start_trap_listener(
        self,
        listen_host: str,
        listen_port: int,
        callback: TrapCallback,
        credentials: Optional[SnmpCredentials] = None,
    ) -> TrapSubscription:
        """Begin receiving SNMP traps/informs asynchronously."""

    async def stop_trap_listener(self, subscription: TrapSubscription) -> None:
        """Tear down a previously created trap listener."""

    async def close(self) -> None:
        """Release sockets and library resources."""


@runtime_checkable
class SnmpEngine(Protocol):
    """
    Application-facing async SNMP API used by the NTCIP Manager facade.

    Provides timeout/retry policy and a stable promise-style
    (``asyncio.Future`` / awaitable) surface over :class:`SnmpBackend`.
    """

    async def get_async(
        self,
        host: str,
        oids: Sequence[str],
        *,
        credentials: Optional[SnmpCredentials] = None,
        port: int = 161,
        timeout_seconds: float = 2.0,
        retries: int = 1,
    ) -> SnmpResponse:
        """Asynchronously GET one or more OIDs from a field device."""

    async def set_async(
        self,
        host: str,
        varbinds: Sequence[SnmpVarBind],
        *,
        credentials: Optional[SnmpCredentials] = None,
        port: int = 161,
        timeout_seconds: float = 2.0,
        retries: int = 1,
    ) -> SnmpResponse:
        """Asynchronously SET one or more OID values on a field device."""

    async def subscribe_to_traps(
        self,
        callback: TrapCallback,
        *,
        listen_host: str = "0.0.0.0",
        listen_port: int = 162,
        credentials: Optional[SnmpCredentials] = None,
    ) -> TrapSubscription:
        """Subscribe to inbound traps; invoke ``callback`` per notification."""

    async def unsubscribe_from_traps(self, subscription: TrapSubscription) -> None:
        """Cancel a trap subscription."""

    async def close(self) -> None:
        """Shut down the engine and underlying backend."""
