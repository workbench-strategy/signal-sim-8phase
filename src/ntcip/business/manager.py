"""
NTCIP Manager facade (Central System role).

The same abstraction can later host an Agent (field device) implementation
by swapping the facade; Layer 1/2 remain shared.
"""

from __future__ import annotations

import logging
from typing import Optional, Sequence

from ntcip.business.adapters.phase_adapter import PhaseStatusAdapter
from ntcip.business.adapters.timing_adapter import SignalTimingPlanAdapter
from ntcip.business.intents import (
    PhaseStatusSnapshot,
    SetSignalTimingPlan,
    UnitIdentity,
)
from ntcip.exceptions import BusinessLogicError, NtcipError
from ntcip.mib.interfaces import MibObjectMapper
from ntcip.mib.objects.global_1201 import UNIT_ID_OID, UNIT_LOCATION_OID
from ntcip.protocol.interfaces import SnmpEngine
from ntcip.protocol.models import SnmpCredentials, SnmpResponse

logger = logging.getLogger(__name__)


class NtcipManager:
    """
    Central-system entry point for NTCIP operations.

    Business callers depend on this facade (Interface Segregation) rather
    than on SNMP or MIB internals.
    """

    def __init__(
        self,
        engine: SnmpEngine,
        mapper: MibObjectMapper,
        *,
        default_credentials: Optional[SnmpCredentials] = None,
    ) -> None:
        self._engine = engine
        self._mapper = mapper
        self._default_credentials = default_credentials or SnmpCredentials()
        self._phase_adapter = PhaseStatusAdapter(engine, mapper)
        self._timing_adapter = SignalTimingPlanAdapter(engine, mapper)

    # -- low-level typed access ------------------------------------------------

    async def get_object(
        self,
        host: str,
        oid: str,
        *,
        credentials: Optional[SnmpCredentials] = None,
        timeout_seconds: float = 2.0,
    ) -> object:
        """GET a single OID and decode it to a domain value."""
        response = await self._engine.get_async(
            host,
            [oid],
            credentials=credentials or self._default_credentials,
            timeout_seconds=timeout_seconds,
        )
        if not response.varbinds:
            raise BusinessLogicError(f"empty GET response for {oid} from {host}")
        return self._mapper.to_domain(response.varbinds[0])

    async def set_object(
        self,
        host: str,
        oid: str,
        value: object,
        *,
        credentials: Optional[SnmpCredentials] = None,
        timeout_seconds: float = 2.0,
    ) -> SnmpResponse:
        """SET a single OID from a domain value (encoded via the mapper)."""
        varbind = self._mapper.to_varbind(oid, value)
        return await self._engine.set_async(
            host,
            [varbind],
            credentials=credentials or self._default_credentials,
            timeout_seconds=timeout_seconds,
        )

    async def get_objects(
        self,
        host: str,
        oids: Sequence[str],
        *,
        credentials: Optional[SnmpCredentials] = None,
        timeout_seconds: float = 2.0,
    ) -> list:
        """GET multiple OIDs; return a list of decoded domain values."""
        response = await self._engine.get_async(
            host,
            oids,
            credentials=credentials or self._default_credentials,
            timeout_seconds=timeout_seconds,
        )
        return [self._mapper.to_domain(vb) for vb in response.varbinds]

    # -- business intents ------------------------------------------------------

    async def get_phase_status(
        self,
        host: str,
        *,
        credentials: Optional[SnmpCredentials] = None,
        timeout_seconds: float = 2.0,
    ) -> PhaseStatusSnapshot:
        """
        Asynchronously read ASC phase status (NTCIP 1202) from a controller.

        This is the primary Manager-side GET example for the scaffold.
        """
        return await self._phase_adapter.get_phase_status(
            host,
            credentials=credentials or self._default_credentials,
            timeout_seconds=timeout_seconds,
        )

    async def set_signal_timing_plan(
        self,
        intent: SetSignalTimingPlan,
        *,
        timeout_seconds: float = 2.0,
    ) -> None:
        """Apply a timing-plan business intent via NTCIP SET."""
        await self._timing_adapter.apply(intent, timeout_seconds=timeout_seconds)

    async def get_unit_identity(
        self,
        host: str,
        *,
        credentials: Optional[SnmpCredentials] = None,
        timeout_seconds: float = 2.0,
    ) -> UnitIdentity:
        """Read NTCIP 1201 unitID / unitLocation."""
        try:
            values = await self.get_objects(
                host,
                [UNIT_ID_OID, UNIT_LOCATION_OID],
                credentials=credentials,
                timeout_seconds=timeout_seconds,
            )
        except NtcipError:
            raise
        unit_id = str(values[0]) if values[0] is not None else ""
        location = str(values[1]) if values[1] is not None else None
        return UnitIdentity(host=host, unit_id=unit_id, unit_location=location)

    async def close(self) -> None:
        """Release protocol resources."""
        await self._engine.close()
