"""Controller data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple


class SignalState(Enum):
    RED = "R"
    YELLOW = "Y"
    GREEN = "G"
    OFF = "-"


class StepPhase(Enum):
    """Sub-phase within a timing plan step."""
    GREEN = "green"
    YELLOW = "yellow"
    ALL_RED = "all_red"
    FINISHED = "finished"


@dataclass
class RingPositions:
    ring_1_phase: Optional[int]
    ring_2_phase: Optional[int]

    def format_panel(self) -> str:
        r1 = f"Ph{self.ring_1_phase}" if self.ring_1_phase else "idle"
        r2 = f"Ph{self.ring_2_phase}" if self.ring_2_phase else "idle"
        return f"Ring1@{r1} | Ring2@{r2}"


@dataclass
class BarrierStatus:
    barrier_23_closed: bool
    barrier_67_closed: bool

    def format_panel(self) -> str:
        b23 = "closed" if self.barrier_23_closed else "open"
        b67 = "closed" if self.barrier_67_closed else "open"
        return f"Barrier23:{b23} | Barrier67:{b67}"


@dataclass
class ControllerSnapshot:
    step_index: int
    step_label: str
    step_phase: StepPhase
    elapsed_s: int
    phase_in_step_total_s: int
    phase_in_step_remaining_s: int
    ring_positions: RingPositions
    barrier_status: BarrierStatus
    phase_states: Dict[int, SignalState]
    active_greens: Set[int] = field(default_factory=set)
    plan_finished: bool = False

    def title_line(self) -> str:
        phase_name = self.step_phase.value.replace("_", " ").title()
        return (
            f"Step {self.step_index + 1}: {self.step_label} "
            f"[{phase_name}] elapsed={self.elapsed_s}s "
            f"remaining={self.phase_in_step_remaining_s}s "
            f"of {self.phase_in_step_total_s}s"
        )
