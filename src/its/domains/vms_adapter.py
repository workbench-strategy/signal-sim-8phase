"""VMS / DMS stub adapter (NTCIP 1203 seam). Replace guts with real driver later."""

from __future__ import annotations

from typing import Any

from its.adapters import ApplyResult, DomainHealth, DomainStatus
from its.events import Recommendation
from its.profile import DeviceProfile


class VmsStubAdapter:
    """Offline VMS adapter for playbooks and policy development."""

    domain = "vms"

    def __init__(self, current_message: str = "ROAD WORK AHEAD") -> None:
        self._current_message = current_message

    async def probe(self, profile: DeviceProfile) -> DomainHealth:
        return DomainHealth(ok=True, detail=f"stub vms at {profile.endpoint}")

    async def get_status(self, profile: DeviceProfile) -> DomainStatus:
        return DomainStatus(
            domain=self.domain,
            profile_id=profile.profile_id,
            summary=f"message={self._current_message!r}",
            data={
                "message": self._current_message,
                "standard": "NTCIP 1203",
                "endpoint": profile.endpoint,
            },
        )

    async def recommend(
        self, profile: DeviceProfile, intent: str, **params: Any
    ) -> Recommendation:
        if intent != "post_message":
            raise ValueError(f"unsupported vms intent: {intent}")
        message = str(params.get("message", ""))
        return Recommendation(
            intent=intent,
            reason="VMS message post requested",
            payload={"message": message, "multi": message},
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
                detail="stub dry-run; message not sent to sign",
                data=recommendation.payload,
            )
        self._current_message = str(recommendation.payload["message"])
        return ApplyResult(
            success=True,
            dry_run=False,
            detail="stub applied message in memory only",
            data=recommendation.payload,
        )
