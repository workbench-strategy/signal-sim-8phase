"""Derive per-phase signal indications from controller state."""

from __future__ import annotations

from typing import Dict, Iterable, Set

from src.controller.models import SignalState, StepPhase
from src.data.loader import Wsdot8PhaseConfig


def all_phases(config: Wsdot8PhaseConfig) -> Iterable[int]:
    return config.phase_details.keys()


def phase_states_for_step(
    config: Wsdot8PhaseConfig,
    step_phase: StepPhase,
    greens: Set[int],
    yellow_phases: Set[int],
) -> Dict[int, SignalState]:
    states: Dict[int, SignalState] = {}
    for phase in all_phases(config):
        if step_phase == StepPhase.GREEN:
            if phase in greens:
                states[phase] = SignalState.GREEN
            else:
                states[phase] = SignalState.RED
        elif step_phase == StepPhase.YELLOW:
            if phase in yellow_phases:
                states[phase] = SignalState.YELLOW
            else:
                states[phase] = SignalState.RED
        else:
            states[phase] = SignalState.RED
    return states
