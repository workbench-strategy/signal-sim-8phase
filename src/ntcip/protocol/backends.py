"""
Pluggable SNMP backends.

``StubSnmpBackend`` powers unit tests and the local demo without a live
controller. ``PysnmpBackend`` is a documented integration seam for the
preferred library (pysnmp); wire it when the dependency is available.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Dict, List, Optional

from ntcip.exceptions import (
    SnmpAuthenticationError,
    SnmpTimeoutError,
    SnmpTransportError,
)
from ntcip.protocol.models import (
    SnmpCredentials,
    SnmpGetRequest,
    SnmpResponse,
    SnmpSetRequest,
    SnmpVarBind,
    SnmpVersion,
    TrapCallback,
    TrapSubscription,
)

logger = logging.getLogger(__name__)


class StubSnmpBackend:
    """
    In-memory SNMP backend for tests and offline demos.

    Simulates latency, timeouts, and auth failures so Layer 2/3 can be
    exercised without a cabinet or SNMP library.
    """

    def __init__(
        self,
        *,
        values: Optional[Dict[str, SnmpVarBind]] = None,
        latency_seconds: float = 0.01,
        force_timeout: bool = False,
        reject_community: Optional[str] = None,
    ) -> None:
        self._values: Dict[str, SnmpVarBind] = dict(values or {})
        self._latency_seconds = latency_seconds
        self._force_timeout = force_timeout
        self._reject_community = reject_community
        self._trap_subs: Dict[str, TrapSubscription] = {}
        self._closed = False

    def seed(self, oid: str, value: object, asn1_type: str = "OCTET STRING") -> None:
        """Install or overwrite a simulated OID value."""
        self._values[oid] = SnmpVarBind(oid=oid, value=value, asn1_type=asn1_type)

    async def send_get(self, request: SnmpGetRequest) -> SnmpResponse:
        self._ensure_open()
        await self._simulate_network(request.host, request.oids[0], request)
        self._check_auth(request.host, request.credentials)
        varbinds: List[SnmpVarBind] = []
        for oid in request.oids:
            if oid not in self._values:
                varbinds.append(SnmpVarBind(oid=oid, value=None, asn1_type="NULL"))
            else:
                varbinds.append(self._values[oid])
        return SnmpResponse(host=request.host, varbinds=tuple(varbinds))

    async def send_set(self, request: SnmpSetRequest) -> SnmpResponse:
        self._ensure_open()
        first_oid = request.varbinds[0].oid if request.varbinds else ""
        await self._simulate_network(request.host, first_oid, request)
        self._check_auth(request.host, request.credentials)
        echoed: List[SnmpVarBind] = []
        for vb in request.varbinds:
            stored = SnmpVarBind(
                oid=vb.oid, value=vb.value, asn1_type=vb.asn1_type or "OCTET STRING"
            )
            self._values[vb.oid] = stored
            echoed.append(stored)
        return SnmpResponse(host=request.host, varbinds=tuple(echoed))

    async def start_trap_listener(
        self,
        listen_host: str,
        listen_port: int,
        callback: TrapCallback,
        credentials: Optional[SnmpCredentials] = None,
    ) -> TrapSubscription:
        self._ensure_open()
        sub = TrapSubscription(
            listen_host=listen_host,
            listen_port=listen_port,
            subscription_id=str(uuid.uuid4()),
        )
        self._trap_subs[sub.subscription_id] = sub
        logger.debug("Stub trap listener started: %s", sub.subscription_id)
        # callback retained for future emit_trap helpers; mark used
        _ = callback
        _ = credentials
        return sub

    async def stop_trap_listener(self, subscription: TrapSubscription) -> None:
        self._trap_subs.pop(subscription.subscription_id, None)

    async def close(self) -> None:
        self._trap_subs.clear()
        self._closed = True

    async def _simulate_network(
        self,
        host: str,
        oid: str,
        request: object,
    ) -> None:
        timeout = getattr(request, "timeout_seconds", 2.0)
        if self._force_timeout:
            await asyncio.sleep(0)
            raise SnmpTimeoutError(host=host, oid=oid, timeout_seconds=timeout)
        await asyncio.sleep(self._latency_seconds)

    def _check_auth(self, host: str, credentials: SnmpCredentials) -> None:
        if (
            self._reject_community is not None
            and credentials.version in (SnmpVersion.V1, SnmpVersion.V2C)
            and credentials.community == self._reject_community
        ):
            raise SnmpAuthenticationError(host, "invalid community string")

    def _ensure_open(self) -> None:
        if self._closed:
            raise SnmpTransportError("localhost", "backend is closed")


class PysnmpBackend:
    """
    Integration seam for `pysnmp` (preferred SNMP library for this stack).

    This scaffold does not vendor a full pysnmp implementation. When you add
    ``pysnmp`` to the environment, replace the ``NotImplementedError`` bodies
    with HLAPI v3 asyncio calls, mapping results into :class:`SnmpResponse`.

    Example sketch (pysnmp 5 / 6 asyncio HLAPI)::

        from pysnmp.hlapi.asyncio import getCmd, CommunityData, UdpTransportTarget, ...

        async def send_get(self, request):
            error_indication, error_status, error_index, var_binds = await getCmd(...)
            if error_indication:
                raise SnmpTransportError(request.host, str(error_indication))
            ...
    """

    def __init__(self) -> None:
        self._closed = False

    async def send_get(self, request: SnmpGetRequest) -> SnmpResponse:
        self._ensure_open()
        raise NotImplementedError(
            "PysnmpBackend.send_get requires the pysnmp package. "
            "Install pysnmp and implement HLAPI mapping, or use StubSnmpBackend."
        )

    async def send_set(self, request: SnmpSetRequest) -> SnmpResponse:
        self._ensure_open()
        raise NotImplementedError(
            "PysnmpBackend.send_set requires the pysnmp package. "
            "Install pysnmp and implement HLAPI mapping, or use StubSnmpBackend."
        )

    async def start_trap_listener(
        self,
        listen_host: str,
        listen_port: int,
        callback: TrapCallback,
        credentials: Optional[SnmpCredentials] = None,
    ) -> TrapSubscription:
        self._ensure_open()
        raise NotImplementedError(
            "PysnmpBackend.start_trap_listener requires pysnmp ntfrcv."
        )

    async def stop_trap_listener(self, subscription: TrapSubscription) -> None:
        self._ensure_open()
        raise NotImplementedError("PysnmpBackend.stop_trap_listener requires pysnmp.")

    async def close(self) -> None:
        self._closed = True

    def _ensure_open(self) -> None:
        if self._closed:
            raise SnmpTransportError("localhost", "pysnmp backend is closed")


# Convenience alias documenting the preferred production backend name.
PreferredSnmpBackend = PysnmpBackend
