"""
Concrete async :class:`SnmpEngine` with timeout and retry policy.

Wraps a pluggable :class:`SnmpBackend` so the rest of the stack never talks
to a vendor SNMP API directly (Open/Closed + Dependency Inversion).
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional, Sequence

from ntcip.exceptions import SnmpError, SnmpTimeoutError, SnmpTransportError
from ntcip.protocol.backends import StubSnmpBackend
from ntcip.protocol.interfaces import SnmpBackend
from ntcip.protocol.models import (
    SnmpCredentials,
    SnmpGetRequest,
    SnmpResponse,
    SnmpSetRequest,
    SnmpVarBind,
    TrapCallback,
    TrapSubscription,
    as_oid_tuple,
)

logger = logging.getLogger(__name__)


class AsyncSnmpEngine:
    """
    Non-blocking SNMP engine for NTCIP Managers.

    Concurrency model: ``asyncio`` tasks / awaitables. Each GET/SET is an
    independent coroutine; callers may gather many in parallel toward
    different field devices.
    """

    def __init__(
        self,
        backend: Optional[SnmpBackend] = None,
        *,
        default_credentials: Optional[SnmpCredentials] = None,
    ) -> None:
        self._backend: SnmpBackend = backend or StubSnmpBackend()
        self._default_credentials = default_credentials or SnmpCredentials()
        self._subscriptions: dict[str, TrapSubscription] = {}

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
        request = SnmpGetRequest(
            host=host,
            oids=as_oid_tuple(oids),
            credentials=credentials or self._default_credentials,
            port=port,
            timeout_seconds=timeout_seconds,
            retries=retries,
        )
        return await self._with_retries(request, self._backend.send_get)

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
        if not varbinds:
            raise ValueError("At least one varbind is required for SET")
        request = SnmpSetRequest(
            host=host,
            varbinds=tuple(varbinds),
            credentials=credentials or self._default_credentials,
            port=port,
            timeout_seconds=timeout_seconds,
            retries=retries,
        )
        return await self._with_retries(request, self._backend.send_set)

    async def subscribe_to_traps(
        self,
        callback: TrapCallback,
        *,
        listen_host: str = "0.0.0.0",
        listen_port: int = 162,
        credentials: Optional[SnmpCredentials] = None,
    ) -> TrapSubscription:
        sub = await self._backend.start_trap_listener(
            listen_host,
            listen_port,
            callback,
            credentials or self._default_credentials,
        )
        self._subscriptions[sub.subscription_id] = sub
        return sub

    async def unsubscribe_from_traps(self, subscription: TrapSubscription) -> None:
        await self._backend.stop_trap_listener(subscription)
        self._subscriptions.pop(subscription.subscription_id, None)

    async def close(self) -> None:
        for sub in list(self._subscriptions.values()):
            try:
                await self._backend.stop_trap_listener(sub)
            except SnmpError:
                logger.exception("Error stopping trap subscription %s", sub)
        self._subscriptions.clear()
        await self._backend.close()

    async def _with_retries(self, request, send_coro) -> SnmpResponse:
        """
        Apply timeout + retry around a backend send call.

        NTCIP field networks are lossy; a single UDP retry is typical for
        Manager GET/SET profiles (see NTCIP 1103 retransmission guidance).
        """
        attempts = max(0, request.retries) + 1
        last_error: Optional[BaseException] = None
        oid_hint = self._oid_hint(request)

        for attempt in range(attempts):
            try:
                return await asyncio.wait_for(
                    send_coro(request),
                    timeout=request.timeout_seconds,
                )
            except asyncio.TimeoutError as exc:
                last_error = SnmpTimeoutError(
                    host=request.host,
                    oid=oid_hint,
                    timeout_seconds=request.timeout_seconds,
                )
                logger.warning(
                    "SNMP timeout host=%s oid=%s attempt=%s/%s",
                    request.host,
                    oid_hint,
                    attempt + 1,
                    attempts,
                )
                _ = exc
            except SnmpTimeoutError as exc:
                last_error = exc
                logger.warning(
                    "SNMP backend timeout host=%s oid=%s attempt=%s/%s",
                    request.host,
                    oid_hint,
                    attempt + 1,
                    attempts,
                )
            except SnmpError:
                # Auth and explicit transport errors are not retried.
                raise
            except OSError as exc:
                last_error = SnmpTransportError(request.host, str(exc))
                logger.warning(
                    "SNMP OSError host=%s attempt=%s/%s: %s",
                    request.host,
                    attempt + 1,
                    attempts,
                    exc,
                )

        assert last_error is not None
        raise last_error

    @staticmethod
    def _oid_hint(request) -> str:
        if isinstance(request, SnmpGetRequest) and request.oids:
            return request.oids[0]
        if isinstance(request, SnmpSetRequest) and request.varbinds:
            return request.varbinds[0].oid
        return "?"
