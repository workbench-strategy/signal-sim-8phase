"""RWIS / ESS stub adapter (NTCIP 1204 seam)."""

from __future__ import annotations

from typing import Any, Dict

from its.adapters import ApplyResult, DomainHealth, DomainStatus
from its.events import Recommendation
from its.profile import DeviceProfile


class RwisStubAdapter:
    """Offline ESS/RWIS adapter with seeded weather observations."""

    domain = "rwis"

    def __init__(self, observations: Dict[str, Any] | None = None) -> None:
        self._observations = observations or {
            "air_temp_c": 4.0,
            "surface_temp_c": 1.5,
            "precipitation": "none",
            "visibility_m": 2000,
        }

    async def probe(self, profile: DeviceProfile) -> DomainHealth:
        return DomainHealth(ok=True, detail=f"stub rwis at {profile.endpoint}")

    async def get_status(self, profile: DeviceProfile) -> DomainStatus:
        return DomainStatus(
            domain=self.domain,
            profile_id=profile.profile_id,
            summary=(
                f"air={self._observations['air_temp_c']}C "
                f"surface={self._observations['surface_temp_c']}C"
            ),
            data={
                **self._observations,
                "standard": "NTCIP 1204",
                "endpoint": profile.endpoint,
            },
        )

    async def recommend(
        self, profile: DeviceProfile, intent: str, **params: Any
    ) -> Recommendation:
        if intent != "raise_weather_alert":
            raise ValueError(f"unsupported rwis intent: {intent}")
        level = str(params.get("level", "advisory"))
        return Recommendation(
            intent=intent,
            reason="Weather threshold crossed (stub/policy)",
            payload={"level": level, "observations": dict(self._observations)},
            profile_id=profile.profile_id,
        )

    async def apply(
        self,
        profile: DeviceProfile,
        intent: str,
        *,
        dry_run: bool = True,
        **params: Any,
    ) -> ApplyResult:
        recommendation = await self.recommend(profile, intent, **params)
        return ApplyResult(
            success=True,
            dry_run=dry_run,
            detail=(
                "stub alert recorded locally"
                if not dry_run
                else "stub dry-run; alert not dispatched"
            ),
            data=recommendation.payload,
        )
