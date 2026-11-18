"""Adapter: ASC phase status GET -> :class:`PhaseStatusSnapshot`."""

from __future__ import annotations

import logging
from typing import Optional

from ntcip.business.intents import PhaseStatusSnapshot
from ntcip.exceptions import BusinessLogicError, NtcipError
from ntcip.mib.interfaces import MibObjectMapper
from ntcip.mib.objects.asc_1202 import (
    PHASE_STATUS_GROUP_GREENS_OID,
    PHASE_STATUS_GROUP_REDS_OID,
    PHASE_STATUS_GROUP_YELLOWS_OID,
    PhaseStatusGroup,
)
from ntcip.protocol.interfaces import SnmpEngine
from ntcip.protocol.models import SnmpCredentials

logger = logging.getLogger(__name__)


class PhaseStatusAdapter:
    """
    Translates "get current phase status" into three NTCIP GETs
    (reds/yellows/greens status groups) and a typed snapshot.
    """

    def __init__(self, engine: SnmpEngine, mapper: MibObjectMapper) -> None:
        self._engine = engine
        self._mapper = mapper

    async def get_phase_status(
        self,
        host: str,
        *,
        credentials: Optional[SnmpCredentials] = None,
        timeout_seconds: float = 2.0,
    ) -> PhaseStatusSnapshot:
        oids = (
            PHASE_STATUS_GROUP_REDS_OID,
            PHASE_STATUS_GROUP_YELLOWS_OID,
            PHASE_STATUS_GROUP_GREENS_OID,
        )
        try:
            response = await self._engine.get_async(
                host,
                oids,
                credentials=credentials,
                timeout_seconds=timeout_seconds,
            )
        except NtcipError:
            raise
        except Exception as exc:  # pragma: no cover - defensive
            raise BusinessLogicError(f"phase status GET failed: {exc}") from exc

        if len(response.varbinds) != 3:
            raise BusinessLogicError(
                f"expected 3 varbinds for phase status, got {len(response.varbinds)}"
            )

        reds = self._mapper.to_domain_as(response.varbinds[0], PhaseStatusGroup)
        yellows = self._mapper.to_domain_as(response.varbinds[1], PhaseStatusGroup)
        greens = self._mapper.to_domain_as(response.varbinds[2], PhaseStatusGroup)

        snapshot = PhaseStatusSnapshot(
            host=host, greens=greens, yellows=yellows, reds=reds
        )
        logger.info(
            "Phase status from %s: greens=%s summary=%s",
            host,
            greens.active_phases(),
            snapshot.summary(),
        )
        return snapshot
