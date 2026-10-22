"""ASCII intersection layout driven by WSDOT config."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from src.controller.models import SignalState
from src.data.loader import Wsdot8PhaseConfig, load_config

MIN_CENTER_GAP = 4


def get_leg_phase_layout(config: Optional[Wsdot8PhaseConfig] = None) -> Dict[str, List[Tuple[int, str]]]:
    cfg = config or load_config()
    layout: Dict[str, List[Tuple[int, str]]] = {}
    for leg, phases in cfg.leg_layout.items():
        layout[leg] = [(p, cfg.phase_details[p].short) for p in phases]
    return layout


def format_phase_pair(phases: List[Tuple[int, str]], compact: bool = True) -> str:
    if len(phases) >= 2:
        left, right = phases[0], phases[1]
        if compact:
            return f"[{left[0]}: {left[1]}]  [{right[0]}: {right[1]}]"
        return f"[{left[0]}: {left[1]}]  [{right[0]}: {right[1]}]"
    if len(phases) == 1:
        p, desc = phases[0]
        return f"[{p}: {desc}]"
    return ""


def format_phase_with_state(
    phase_num: int,
    desc: str,
    state: SignalState,
) -> str:
    return f"[{phase_num}: {desc} ({state.value})]"


def format_leg_with_states(
    phases: List[Tuple[int, str]],
    states: Dict[int, SignalState],
) -> str:
    parts = []
    for phase_num, desc in phases:
        state = states.get(phase_num, SignalState.OFF)
        parts.append(format_phase_with_state(phase_num, desc, state))
    return "  ".join(parts)


def calculate_ascii_layout_dimensions(
    layout: Dict[str, List[Tuple[int, str]]],
    compact: bool,
    states: Optional[Dict[int, SignalState]],
) -> Tuple[int, int, int]:
    if states:
        north_str = format_leg_with_states(layout["north"], states)
        south_str = format_leg_with_states(layout["south"], states)
        east_str = format_leg_with_states(layout["east"], states)
        west_str = format_leg_with_states(layout["west"], states)
    else:
        north_str = format_phase_pair(layout["north"], compact)
        south_str = format_phase_pair(layout["south"], compact)
        east_str = format_phase_pair(layout["east"], compact)
        west_str = format_phase_pair(layout["west"], compact)

    ns_width = max(len(north_str), len(south_str))
    ew_width = len(west_str) + len(east_str)
    min_gap = max(MIN_CENTER_GAP, ns_width - ew_width + MIN_CENTER_GAP)
    return len(west_str), min_gap, ns_width


def print_intersection_layout(
    compact: bool = True,
    states: Optional[Dict[int, SignalState]] = None,
    config: Optional[Wsdot8PhaseConfig] = None,
) -> None:
    cfg = config or load_config()
    layout = get_leg_phase_layout(cfg)

    if states:
        north_str = format_leg_with_states(layout["north"], states)
        south_str = format_leg_with_states(layout["south"], states)
        east_str = format_leg_with_states(layout["east"], states)
        west_str = format_leg_with_states(layout["west"], states)
    else:
        north_str = format_phase_pair(layout["north"], compact)
        south_str = format_phase_pair(layout["south"], compact)
        east_str = format_phase_pair(layout["east"], compact)
        west_str = format_phase_pair(layout["west"], compact)

    west_width, center_gap, ns_width = calculate_ascii_layout_dimensions(
        layout, compact, states
    )
    total_width = len(west_str) + center_gap + len(east_str)
    ns_padding = max(0, (total_width - ns_width) // 2)

    print()
    print(" " * ns_padding + north_str)
    print(west_str + " " * center_gap + east_str)
    print(" " * ns_padding + south_str)
    print()
