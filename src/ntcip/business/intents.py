"""Business-level intent and result types (Layer 3)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ntcip.mib.objects.asc_1202 import PhaseStatusGroup


@dataclass(frozen=True)
class PhaseStatusSnapshot:
    """Typed view of ASC phase color status for one controller."""

    host: str
    greens: PhaseStatusGroup
    yellows: PhaseStatusGroup
    reds: PhaseStatusGroup

    def green_phases(self) -> List[int]:
        return self.greens.active_phases()

    def summary(self) -> Dict[int, str]:
        """Map phase number -> R/Y/G (G wins if multiple bits are set)."""
        result: Dict[int, str] = {}
        for phase in range(1, 9):
            if self.greens.is_active(phase):
                result[phase] = "G"
            elif self.yellows.is_active(phase):
                result[phase] = "Y"
            elif self.reds.is_active(phase):
                result[phase] = "R"
            else:
                result[phase] = "-"
        return result


@dataclass(frozen=True)
class SetSignalTimingPlan:
    """
    Example business intent: apply a named timing plan to a controller.

    The adapter expands this into one or more NTCIP SET operations against
    ASC pattern / split tables (scaffold: plan identifier only).
    """

    host: str
    plan_number: int
    community: str = "private"
    metadata: Dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        if self.plan_number < 1 or self.plan_number > 255:
            raise ValueError("plan_number must be in 1..255")


@dataclass(frozen=True)
class UnitIdentity:
    """NTCIP 1201 unit identification snapshot."""

    host: str
    unit_id: str
    unit_location: Optional[str] = None
