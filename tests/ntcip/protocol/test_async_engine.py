"""Tests for async SNMP engine (timeouts, auth, GET/SET)."""

from __future__ import annotations

import pytest

from ntcip.exceptions import SnmpAuthenticationError, SnmpTimeoutError
from ntcip.protocol.async_engine import AsyncSnmpEngine
from ntcip.protocol.backends import StubSnmpBackend
from ntcip.protocol.models import SnmpCredentials, SnmpVarBind


@pytest.mark.asyncio
async def test_get_async_returns_seeded_value():
    backend = StubSnmpBackend()
    backend.seed("1.2.3", 42, "INTEGER")
    engine = AsyncSnmpEngine(backend)
    try:
        response = await engine.get_async("192.0.2.1", ["1.2.3"])
        assert response.varbinds[0].value == 42
    finally:
        await engine.close()


@pytest.mark.asyncio
async def test_set_async_updates_value():
    backend = StubSnmpBackend()
    engine = AsyncSnmpEngine(backend)
    try:
        await engine.set_async(
            "192.0.2.1",
            [SnmpVarBind(oid="1.2.3", value=7, asn1_type="INTEGER")],
        )
        response = await engine.get_async("192.0.2.1", ["1.2.3"])
        assert response.varbinds[0].value == 7
    finally:
        await engine.close()


@pytest.mark.asyncio
async def test_timeout_is_raised():
    backend = StubSnmpBackend(force_timeout=True)
    engine = AsyncSnmpEngine(backend)
    try:
        with pytest.raises(SnmpTimeoutError):
            await engine.get_async(
                "192.0.2.1",
                ["1.2.3"],
                timeout_seconds=0.05,
                retries=0,
            )
    finally:
        await engine.close()


@pytest.mark.asyncio
async def test_authentication_failure():
    backend = StubSnmpBackend(reject_community="bad")
    engine = AsyncSnmpEngine(backend)
    try:
        with pytest.raises(SnmpAuthenticationError):
            await engine.get_async(
                "192.0.2.1",
                ["1.2.3"],
                credentials=SnmpCredentials(community="bad"),
            )
    finally:
        await engine.close()


@pytest.mark.asyncio
async def test_trap_subscribe_unsubscribe():
    backend = StubSnmpBackend()
    engine = AsyncSnmpEngine(backend)

    async def _cb(_response):
        return None

    try:
        sub = await engine.subscribe_to_traps(_cb, listen_port=1162)
        assert sub.listen_port == 1162
        await engine.unsubscribe_from_traps(sub)
    finally:
        await engine.close()
