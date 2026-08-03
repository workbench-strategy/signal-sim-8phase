"""Adapter: SetSignalTimingPlan intent -> NTCIP SET operations."""

from __future__ import annotations

import logging
from typing import Optional

from ntcip.business.intents import SetSignalTimingPlan
from ntcip.exceptions import BusinessLogicError, NtcipError
from ntcip.mib.interfaces import MibObjectMapper
from ntcip.protocol.interfaces import SnmpEngine
from ntcip.protocol.models import SnmpCredentials, SnmpVarBind, SnmpVersion

logger = logging.getLogger(__name__)

# Scaffold OID: ASC pattern / timing plan selection leaf.
# Align with your compiled NTCIP 1202 pattern table before production use.
PATTERN_CONTROL_OID = "1.3.6.1.4.1.1206.4.2.1.5.1.0"


class SignalTimingPlanAdapter:
    """
    Expands :class:`SetSignalTimingPlan` into an SNMP SET.

    Production adapters typically write pattern, split, and coordination
    tables transactionally using NTCIP 1201 database transaction objects.
    """

    def __init__(self, engine: SnmpEngine, mapper: MibObjectMapper) -> None:
        self._engine = engine
        self._mapper = mapper

    async def apply(
        self,
        intent: SetSignalTimingPlan,
        *,
        timeout_seconds: float = 2.0,
        credentials: Optional[SnmpCredentials] = None,
    ) -> None:
        try:
            intent.validate()
        except ValueError as exc:
            raise BusinessLogicError(str(exc)) from exc

        creds = credentials or SnmpCredentials(
            community=intent.community,
            version=SnmpVersion.V2C,
        )
        # Pattern control is not in the default registry scaffold; send raw.
        varbind = SnmpVarBind(
            oid=PATTERN_CONTROL_OID,
            value=intent.plan_number,
            asn1_type="INTEGER",
        )
        try:
            await self._engine.set_async(
                intent.host,
                [varbind],
                credentials=creds,
                timeout_seconds=timeout_seconds,
            )
        except NtcipError:
            raise
        except Exception as exc:  # pragma: no cover
            raise BusinessLogicError(f"timing plan SET failed: {exc}") from exc

        logger.info(
            "Applied timing plan %s to %s", intent.plan_number, intent.host
        )
        # mapper retained for future transactional / typed SETs
        _ = self._mapper
