"""Policy contract -- experiments evaluate observations into recommendations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Protocol, runtime_checkable

from its.adapters import DomainAdapter, DomainStatus
from its.events import Recommendation
from its.profile import DeviceProfile


@dataclass(frozen=True)
class Observation:
    """Snapshot a policy uses as input (never a live write handle)."""

    profile: DeviceProfile
    status: DomainStatus
    extras: Dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class Policy(Protocol):
    """
    Fast-moving experiment surface.

    Policies must not open sockets; they only use adapters passed into
    ``observe`` / operate on :class:`Observation` values.
    """

    policy_id: str

    async def observe(
        self, adapter: DomainAdapter, profile: DeviceProfile
    ) -> Observation:
        """Gather status (and optional extras) for evaluation."""

    async def evaluate(self, observation: Observation) -> List[Recommendation]:
        """Return zero or more shadow-safe recommendations."""
