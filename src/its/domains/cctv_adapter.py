"""CCTV stub adapter (NTCIP 1205 / ONVIF seam)."""

from __future__ import annotations

from typing import Any, List

from its.adapters import ApplyResult, DomainHealth, DomainStatus
from its.events import Recommendation
from its.profile import DeviceProfile


class CctvStubAdapter:
    """Offline camera adapter -- bridge toward tunnel and airport video labs."""

    domain = "cctv"

    def __init__(self, presets: List[str] | None = None) -> None:
        self._presets = presets or ["overview", "approach_nb", "approach_sb"]
        self._current_preset = self._presets[0]

    async def probe(self, profile: DeviceProfile) -> DomainHealth:
        return DomainHealth(ok=True, detail=f"stub cctv at {profile.endpoint}")

    async def get_status(self, profile: DeviceProfile) -> DomainStatus:
        return DomainStatus(
            domain=self.domain,
            profile_id=profile.profile_id,
            summary=f"preset={self._current_preset}",
            data={
                "current_preset": self._current_preset,
                "presets": list(self._presets),
                "standards": ["NTCIP 1205", "ONVIF"],
                "endpoint": profile.endpoint,
            },
        )

    async def recommend(
        self, profile: DeviceProfile, intent: str, **params: Any
    ) -> Recommendation:
        if intent != "goto_preset":
            raise ValueError(f"unsupported cctv intent: {intent}")
        preset = str(params.get("preset", self._current_preset))
        return Recommendation(
            intent=intent,
            reason="Camera preset move requested for verification",
            payload={"preset": preset},
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
        if dry_run:
            return ApplyResult(
                success=True,
                dry_run=True,
                detail="stub dry-run; camera not moved",
                data=recommendation.payload,
            )
        self._current_preset = str(recommendation.payload["preset"])
        return ApplyResult(
            success=True,
            dry_run=False,
            detail=f"stub moved to preset {self._current_preset}",
            data=recommendation.payload,
        )
