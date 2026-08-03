"""
Signals domain adapter -- bridges ITS platform intents to NtcipManager.

This is the reference adapter showing how a real vertical plugs into
DomainAdapter without leaking SNMP types upward.
"""

from __future__ import annotations

import time
from typing import Any, Optional

from its.adapters import ApplyResult, DomainHealth, DomainStatus
from its.events import Recommendation
from its.profile import DeviceProfile
from ntcip.business.manager import NtcipManager
from ntcip.factory import create_ntcip_manager


class SignalsNtcipAdapter:
    """ASC / signal status via the NTCIP Manager facade."""

    domain = "signals"

    def __init__(self, manager: Optional[NtcipManager] = None) -> None:
        self._manager = manager or create_ntcip_manager(demo_data=True)
        self._owns_manager = manager is None

    async def probe(self, profile: DeviceProfile) -> DomainHealth:
        started = time.perf_counter()
        identity = await self._manager.get_unit_identity(profile.endpoint)
        latency = (time.perf_counter() - started) * 1000.0
        ok = bool(identity.unit_id)
        return DomainHealth(
            ok=ok,
            detail=f"unit_id={identity.unit_id}",
            latency_ms=latency,
        )

    async def get_status(self, profile: DeviceProfile) -> DomainStatus:
        snapshot = await self._manager.get_phase_status(profile.endpoint)
        summary = (
            f"greens={snapshot.green_phases()} "
            f"map={snapshot.summary()}"
        )
        return DomainStatus(
            domain=self.domain,
            profile_id=profile.profile_id,
            summary=summary,
            data={
                "green_phases": snapshot.green_phases(),
                "phase_map": snapshot.summary(),
                "host": snapshot.host,
            },
        )

    async def recommend(
        self, profile: DeviceProfile, intent: str, **params: Any
    ) -> Recommendation:
        if intent == "set_timing_plan":
            plan = int(params.get("plan_number", 1))
            return Recommendation(
                intent=intent,
                reason="Operator or policy requested timing plan change",
                payload={"plan_number": plan, "host": profile.endpoint},
                profile_id=profile.profile_id,
            )
        raise ValueError(f"unsupported signals intent: {intent}")

    async def apply(
        self,
        profile: DeviceProfile,
        intent: str,
        *,
        dry_run: bool = True,
        **params: Any,
    ) -> ApplyResult:
        recommendation = await self.recommend(profile, intent, **params)
        if dry_run:
            return ApplyResult(
                success=True,
                dry_run=True,
                detail="shadow/dry-run only; no SNMP SET sent",
                data=recommendation.payload,
            )
        from ntcip.business.intents import SetSignalTimingPlan

        plan = int(recommendation.payload["plan_number"])
        await self._manager.set_signal_timing_plan(
            SetSignalTimingPlan(host=profile.endpoint, plan_number=plan)
        )
        return ApplyResult(
            success=True,
            dry_run=False,
            detail=f"applied timing plan {plan}",
            data=recommendation.payload,
        )

    async def close(self) -> None:
        if self._owns_manager:
            await self._manager.close()
