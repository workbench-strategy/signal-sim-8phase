# signal_sim_engine.py

# Placeholder for 8-phase NEMA dual-ring signal controller logic
# Simulates timing sequences for protected/permissive lefts,
# pedestrian LPIs, and flashing yellows.

from typing import Dict, List, Tuple


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


def format_phase_pair(phases: List[Tuple[int, str]]) -> str:
    left = phases[0]
    right = phases[1]
    return f"[{left[0]}: {left[1]}]  [{right[0]}: {right[1]}]"


def print_intersection_layout() -> None:
    """Print a simple ASCII layout to visualize phases by legs."""
    layout = get_leg_phase_layout()

    top = format_phase_pair(layout["north"])  # North leg at top
    bottom = format_phase_pair(layout["south"])  # South leg at bottom
    right = format_phase_pair(layout["east"])  # East leg on right
    left = format_phase_pair(layout["west"])  # West leg on left

    # Build rows for a simple cross layout
    spacer = " " * 6
    middle_gap = " " * 6

    print()
    print(f"{spacer}{top}")
    print(f"{left}{middle_gap}{right}")
    print(f"{spacer}{bottom}")
    print()


def simulate_cycle() -> None:
    print("Phase 1: Northbound Left (Protected)")
    # Logic placeholder...


if __name__ == '__main__':
    # Show the arranged layout example first, then run the simple cycle stub
    print_intersection_layout()
    simulate_cycle()