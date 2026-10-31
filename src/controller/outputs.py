"""Derive per-phase signal indications from controller state."""

from __future__ import annotations

from typing import Dict, Iterable, Set

from src.controller.models import SignalState, StepPhase
from src.data.loader import Wsdot8PhaseConfig

# Even through phases carry pedestrian overlaps on Output File #1 (J-80.12).
PED_PHASES = (2, 4, 6, 8)


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


def ped_states_for_step(
    step_phase: StepPhase,
    greens: Set[int],
    yellow_phases: Set[int],
    ped_phases: Iterable[int] = PED_PHASES,
) -> Dict[int, SignalState]:
    """Map even-phase ped overlaps to Walk / FDW / Don't Walk.

    Teaching model (simplified):
    - Walk (green) while the parent through phase is green
    - Flashing Don't Walk / ped clearance (yellow) while that through is yellow
    - Don't Walk (red) otherwise
    """
    states: Dict[int, SignalState] = {}
    for phase in ped_phases:
        if step_phase == StepPhase.GREEN and phase in greens:
            states[phase] = SignalState.GREEN
        elif step_phase == StepPhase.YELLOW and phase in yellow_phases:
            states[phase] = SignalState.YELLOW
        else:
            states[phase] = SignalState.RED
    return states
