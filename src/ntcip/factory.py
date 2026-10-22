"""
Composition root for the NTCIP stack.

Wires Layer 1 (engine) + Layer 2 (registry/mapper) + Layer 3 (manager)
without leaking concrete dependencies into business callers.
"""

from __future__ import annotations

from typing import Optional

from ntcip.business.manager import NtcipManager
from ntcip.mib.mapper import DefaultMibObjectMapper
from ntcip.mib.registry import MibRegistry, build_default_ntcip_registry
from ntcip.protocol.async_engine import AsyncSnmpEngine
from ntcip.protocol.backends import PysnmpBackend, StubSnmpBackend
from ntcip.protocol.interfaces import SnmpBackend
from ntcip.mib.date_and_time import NtcipDateAndTime
from ntcip.mib.objects.asc_1202 import (
    PHASE_STATUS_GROUP_GREENS_OID,
    PHASE_STATUS_GROUP_REDS_OID,
    PHASE_STATUS_GROUP_YELLOWS_OID,
)
from ntcip.mib.objects.global_1201 import UNIT_ID_OID, UNIT_LOCATION_OID
from ntcip.protocol.models import SnmpCredentials


def create_stub_backend_with_demo_data() -> StubSnmpBackend:
    """Backend pre-seeded with realistic ASC / global demo values."""
    backend = StubSnmpBackend(latency_seconds=0.01)
    # Phases 2 and 5 green (bit 1 and bit 4) -- typical SB left + SB thru.
    green_bits = bytes([0b00010010])  # phases 2 and 5
    red_bits = bytes([0b11101101])  # everyone else red
    yellow_bits = bytes([0b00000000])
    backend.seed(PHASE_STATUS_GROUP_GREENS_OID, green_bits, "OCTET STRING")
    backend.seed(PHASE_STATUS_GROUP_YELLOWS_OID, yellow_bits, "OCTET STRING")
    backend.seed(PHASE_STATUS_GROUP_REDS_OID, red_bits, "OCTET STRING")
    backend.seed(UNIT_ID_OID, "ASC-DEMO-001", "DisplayString")
    backend.seed(UNIT_LOCATION_OID, "Main St & 1st Ave", "DisplayString")
    backend.seed(
        "1.3.6.1.4.1.1206.4.2.6.3.2.0",
        NtcipDateAndTime(2026, 8, 3, 12, 0, 0, 0).to_octets(),
        "DateAndTime",
    )
    return backend


def create_ntcip_manager(
    *,
    backend: Optional[SnmpBackend] = None,
    registry: Optional[MibRegistry] = None,
    credentials: Optional[SnmpCredentials] = None,
    use_pysnmp: bool = False,
    demo_data: bool = True,
) -> NtcipManager:
    """
    Build a fully wired :class:`NtcipManager`.

    Args:
        backend: Optional custom SNMP backend.
        registry: Optional MIB registry (defaults to 1201/1202 scaffold).
        credentials: Default SNMPv2c/v3 credentials.
        use_pysnmp: If True and no backend given, use :class:`PysnmpBackend`.
        demo_data: Seed the stub backend with demo OID values.
    """
    if backend is None:
        if use_pysnmp:
            backend = PysnmpBackend()
        elif demo_data:
            backend = create_stub_backend_with_demo_data()
        else:
            backend = StubSnmpBackend()

    engine = AsyncSnmpEngine(backend, default_credentials=credentials)
    reg = registry or build_default_ntcip_registry()
    mapper = DefaultMibObjectMapper(reg)
    return NtcipManager(engine, mapper, default_credentials=credentials)
