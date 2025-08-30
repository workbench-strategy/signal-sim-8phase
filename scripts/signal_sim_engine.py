# signal_sim_engine.py

# Placeholder for 8-phase NEMA dual-ring signal controller logic
# Simulates timing sequences for protected/permissive lefts,
# pedestrian LPIs, and flashing yellows.

from typing import Dict, List, Tuple, Optional
from enum import Enum


class SignalState(Enum):
    """Signal indication states."""
    RED = "R"
    YELLOW = "Y"
    GREEN = "G"
    FLASHING_YELLOW = "FY"
    OFF = "-"


PHASE_TO_DESCRIPTION: Dict[int, str] = {
    1: "Northbound Left (Protected)",
    2: "Southbound Left (Protected)",
    3: "Eastbound Left (Protected)",
    4: "Westbound Left (Protected)",
    5: "Southbound Through",
    6: "Northbound Through",
    7: "Westbound Through",
    8: "Eastbound Through",
}

PHASE_TO_SHORT_DESC: Dict[int, str] = {
    1: "NB Left",
    2: "SB Left", 
    3: "EB Left",
    4: "WB Left",
    5: "SB Thru",
    6: "NB Thru",
    7: "WB Thru",
    8: "EB Thru",
}


LEG_PHASE_LAYOUT: Dict[str, List[Tuple[int, str]]] = {
    "north": [(1, PHASE_TO_DESCRIPTION[1]), (6, PHASE_TO_DESCRIPTION[6])],
    "south": [(2, PHASE_TO_DESCRIPTION[2]), (5, PHASE_TO_DESCRIPTION[5])],
    "east": [(3, PHASE_TO_DESCRIPTION[3]), (8, PHASE_TO_DESCRIPTION[8])],
    "west": [(7, PHASE_TO_DESCRIPTION[7]), (4, PHASE_TO_DESCRIPTION[4])],
}
def get_leg_phase_layout() -> Dict[str, List[Tuple[int, str]]]:
    """Return phases arranged by intersection leg as requested.

    Legs are grouped as:
      - North: phases 1 and 6
      - South (opposite North): phases 2 and 5
      - East: phases 3 and 8
      - West (opposite East): phases 7 and 4
    """
    return {
        "north": [(1, PHASE_TO_DESCRIPTION[1]), (6, PHASE_TO_DESCRIPTION[6])],
        "south": [(2, PHASE_TO_DESCRIPTION[2]), (5, PHASE_TO_DESCRIPTION[5])],
        "east": [(3, PHASE_TO_DESCRIPTION[3]), (8, PHASE_TO_DESCRIPTION[8])],
        "west": [(7, PHASE_TO_DESCRIPTION[7]), (4, PHASE_TO_DESCRIPTION[4])],
    }


def format_phase_pair(phases: List[Tuple[int, str]], compact: bool = False) -> str:
    """Format a pair of phases for a single leg."""
    if len(phases) >= 2:
        left = phases[0]
        right = phases[1]
        if compact:
            left_desc = PHASE_TO_SHORT_DESC[left[0]]
            right_desc = PHASE_TO_SHORT_DESC[right[0]]
            return f"[{left[0]}: {left_desc}]  [{right[0]}: {right_desc}]"
        else:
            return f"[{left[0]}: {left[1]}]  [{right[0]}: {right[1]}]"
    elif len(phases) == 1:
        phase = phases[0]
        if compact:
            desc = PHASE_TO_SHORT_DESC[phase[0]]
            return f"[{phase[0]}: {desc}]"
        else:
            return f"[{phase[0]}: {phase[1]}]"
    return ""


def format_phase_with_state(phase_num: int, state: SignalState, compact: bool = False) -> str:
    """Format a single phase with its current signal state."""
    desc = PHASE_TO_SHORT_DESC[phase_num] if compact else PHASE_TO_DESCRIPTION[phase_num]
    return f"[{phase_num}: {desc} ({state.value})]"


def format_leg_with_states(
    phases: List[Tuple[int, str]], 
    states: Dict[int, SignalState],
    compact: bool = False
) -> str:
    """Format phases for a leg with their current signal states."""
    formatted_phases = []
    for phase_num, _ in phases:
        state = states.get(phase_num, SignalState.OFF)
        formatted_phases.append(format_phase_with_state(phase_num, state, compact))
    return "  ".join(formatted_phases)


def calculate_ascii_layout_dimensions(
    layout: Dict[str, List[Tuple[int, str]]], 
    compact: bool = False,
    states: Optional[Dict[int, SignalState]] = None
) -> Tuple[int, int, int]:
    """Calculate dimensions needed for proper ASCII layout alignment."""
    # Format all legs
    if states:
        north_str = format_leg_with_states(layout["north"], states, compact)
        south_str = format_leg_with_states(layout["south"], states, compact)
        east_str = format_leg_with_states(layout["east"], states, compact)
        west_str = format_leg_with_states(layout["west"], states, compact)
    else:
        north_str = format_phase_pair(layout["north"], compact)
        south_str = format_phase_pair(layout["south"], compact)
        east_str = format_phase_pair(layout["east"], compact)
        west_str = format_phase_pair(layout["west"], compact)
    
    # Calculate max widths
    ns_width = max(len(north_str), len(south_str))
    ew_width = len(west_str) + len(east_str)
    
    # We need a gap between west and east that's at least as wide as north/south
    min_gap = max(6, ns_width - ew_width + 6)
    
    return len(west_str), min_gap, ns_width


def print_intersection_layout(
    compact: bool = True,
    states: Optional[Dict[int, SignalState]] = None
) -> None:
    """Print an ASCII layout to visualize phases by intersection legs.
    
    Creates a cross-shaped layout with:
    - North leg at top
    - South leg at bottom  
    - East leg on right
    - West leg on left
    
    Args:
        compact: Use compact phase descriptions to fit in 80 columns
        states: Optional dict mapping phase numbers to signal states
    """
    layout = get_leg_phase_layout()
    
    # Format phase pairs for each leg
    if states:
        north_str = format_leg_with_states(layout["north"], states, compact)
        south_str = format_leg_with_states(layout["south"], states, compact)
        east_str = format_leg_with_states(layout["east"], states, compact)
        west_str = format_leg_with_states(layout["west"], states, compact)
    else:
        north_str = format_phase_pair(layout["north"], compact)
        south_str = format_phase_pair(layout["south"], compact)
        east_str = format_phase_pair(layout["east"], compact)
        west_str = format_phase_pair(layout["west"], compact)
    
    # Calculate layout dimensions
    west_width, center_gap, ns_width = calculate_ascii_layout_dimensions(layout, compact, states)
    
    # Calculate padding for north/south to center them
    total_width = len(west_str) + center_gap + len(east_str)
    ns_padding = max(0, (total_width - ns_width) // 2)
    
    # Build the intersection layout
    print()
    print(" " * ns_padding + north_str)
    print(west_str + " " * center_gap + east_str)
    print(" " * ns_padding + south_str)
    print()


def simulate_cycle() -> None:
    """Simulate a signal cycle with different phase states."""
    print("\n=== Signal Cycle Simulation ===")
    
    # Example phase states during a cycle
    example_states = {
        1: SignalState.GREEN,      # NB Left green
        2: SignalState.RED,        # SB Left red
        3: SignalState.RED,        # EB Left red  
        4: SignalState.RED,        # WB Left red
        5: SignalState.RED,        # SB Thru red
        6: SignalState.GREEN,      # NB Thru green
        7: SignalState.RED,        # WB Thru red
        8: SignalState.RED,        # EB Thru red
    }
    
    print("\nCurrent Phase State (Phases 1 & 6 active):")
    print_intersection_layout(compact=True, states=example_states)
    
    # Example of yellow transition
    example_states[1] = SignalState.YELLOW
    example_states[6] = SignalState.YELLOW
    
    print("\nTransition State (Phases 1 & 6 yellow):")
    print_intersection_layout(compact=True, states=example_states)


def demonstrate_layouts() -> None:
    """Demonstrate different layout options."""
    print("=== Signal Indication Layout Demo ===")
    
    print("\n1. Compact Layout (fits 80-column terminal):")
    print_intersection_layout(compact=True)
    
    print("\n2. Full Layout (may wrap on narrow terminals):")
    print_intersection_layout(compact=False)
    
    print("\n3. Layout with Signal States:")
    example_states = {
        1: SignalState.RED,
        2: SignalState.RED,
        3: SignalState.GREEN,
        4: SignalState.GREEN,
        5: SignalState.RED,
        6: SignalState.RED,
        7: SignalState.GREEN,
        8: SignalState.GREEN,
    }
    print_intersection_layout(compact=True, states=example_states)


if __name__ == '__main__':
    # Show different layout demonstrations
    demonstrate_layouts()
    
    # Run signal cycle simulation
    simulate_cycle()