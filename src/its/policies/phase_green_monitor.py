"""
Example policy: observe ASC greens and recommend verification if unexpected.

Shadow-only by design -- it never calls apply().
"""

from __future__ import annotations

from typing import List, Sequence

from its.adapters import DomainAdapter
from its.events import Recommendation
from its.policies.base import Observation
from its.profile import DeviceProfile


class PhaseGreenMonitorPolicy:
    """Recommend operator attention when green phases drift from expected."""

    policy_id = "phase_green_monitor"

    def __init__(self, expected_greens: Sequence[int] = (2, 5)) -> None:
        self._expected = tuple(expected_greens)

    async def observe(
        self, adapter: DomainAdapter, profile: DeviceProfile
    ) -> Observation:
        status = await adapter.get_status(profile)
        return Observation(profile=profile, status=status)

    async def evaluate(self, observation: Observation) -> List[Recommendation]:
        greens = tuple(observation.status.data.get("green_phases") or ())
        if greens == self._expected:
            return []
        return [
            Recommendation(
                intent="operator_verify_intersection",
                reason=(
                    f"green phases {list(greens)} != expected "
                    f"{list(self._expected)}"
                ),
                payload={
                    "actual_greens": list(greens),
                    "expected_greens": list(self._expected),
                    "phase_map": observation.status.data.get("phase_map", {}),
                },
                profile_id=observation.profile.profile_id,
                policy_id=self.policy_id,
                confidence=0.8,
            )
        ]
