"""
Layer 1: Protocol Engine (SNMP Core).

Handles SNMPv1/v2c/v3 packet encode/decode and async UDP transport via a
pluggable backend (pysnmp, gosnmp bindings, Net-SNMP, etc.). Application
code depends only on :class:`~ntcip.protocol.interfaces.SnmpEngine`.
"""

from ntcip.protocol.async_engine import AsyncSnmpEngine
from ntcip.protocol.interfaces import SnmpBackend, SnmpEngine
from ntcip.protocol.models import (
    SnmpCredentials,
    SnmpGetRequest,
    SnmpSetRequest,
    SnmpVarBind,
    SnmpVersion,
    TrapSubscription,
)

__all__ = [
    "AsyncSnmpEngine",
    "SnmpBackend",
    "SnmpCredentials",
    "SnmpEngine",
    "SnmpGetRequest",
    "SnmpSetRequest",
    "SnmpVarBind",
    "SnmpVersion",
    "TrapSubscription",
]
