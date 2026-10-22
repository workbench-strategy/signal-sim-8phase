"""Single-screen presenter output for controller demo."""

from __future__ import annotations

from src.controller.models import ControllerSnapshot, SignalState, StepPhase
from src.data.loader import Wsdot8PhaseConfig, load_config
from src.display.intersection import print_intersection_layout
from src.wiring.table import WiringTable, format_energized_panel


_STATE_GLYPHS = {
    SignalState.GREEN: ("█", "▓", "▒", "░", "."),
    SignalState.YELLOW: ("▒", "░", ".", ".", "."),
    SignalState.RED: ("░", ".", ".", ".", "."),
    SignalState.OFF: (".", ".", ".", ".", "."),
}


def _clamp_ratio(value: float) -> float:
    return max(0.0, min(1.0, value))


def _normalized_progress(snapshot: ControllerSnapshot) -> float:
    if snapshot.step_phase == StepPhase.FINISHED:
        return 1.0
    total = max(1, snapshot.phase_in_step_total_s)
    remaining = max(0, snapshot.phase_in_step_remaining_s)
    return _clamp_ratio(1.0 - (remaining / total))


def _phase_progress(snapshot: ControllerSnapshot) -> float:
    if snapshot.step_phase == StepPhase.FINISHED:
        return 1.0
    total = max(1, snapshot.phase_in_step_total_s)
    if snapshot.step_phase == StepPhase.GREEN:
        elapsed = total - max(0, snapshot.phase_in_step_remaining_s)
        return _clamp_ratio(elapsed / total)
    if snapshot.step_phase == StepPhase.YELLOW:
        yellow_total = max(1, total)
        yellow_elapsed = total - max(0, snapshot.phase_in_step_remaining_s)
        return _clamp_ratio(yellow_elapsed / yellow_total)
    if snapshot.step_phase == StepPhase.ALL_RED:
        red_elapsed = total - max(0, snapshot.phase_in_step_remaining_s)
        return _clamp_ratio(red_elapsed / total)
    return 0.0


def _bar(width: int, progress: float, state: SignalState) -> str:
    palette = _STATE_GLYPHS[state]
    progress = _clamp_ratio(progress)
    filled = int(round(progress * width))
    if filled <= 0:
        return "." * width

    bar = []
    gradient_steps = max(1, filled - 1)
    for idx in range(width):
        if idx >= filled:
            bar.append(".")
            continue
        ratio = idx / gradient_steps if gradient_steps else 0.0
        if ratio < 0.55:
            bar.append(palette[0])
        elif ratio < 0.75:
            bar.append(palette[1])
        elif ratio < 0.9:
            bar.append(palette[2])
        else:
            bar.append(palette[3])
    return "".join(bar)


def _phase_cell(
    phase_num: int,
    label: str,
    state: SignalState,
    progress: float,
    width: int = 10,
) -> str:
    suffix = _bar(width, progress, state)
    return f"{phase_num}:{label:<9} {suffix}"


def _fit(text: str, width: int) -> str:
    if len(text) <= width:
        return text
    if width <= 1:
        return text[:width]
    return text[: width - 1] + "…"


def _state_strip(snapshot: ControllerSnapshot) -> str:
    parts = []
    for phase_num in range(1, 9):
        state = snapshot.phase_states.get(phase_num, SignalState.OFF)
        parts.append(f"{phase_num}:{state.value}")
    return "  ".join(parts)


def render_signal_helix(snapshot: ControllerSnapshot, config: Wsdot8PhaseConfig) -> str:
    progress = _normalized_progress(snapshot)

    phases = config.phase_details
    ring_1 = [1, 2, 3, 4]
    ring_2 = [5, 6, 7, 8]

    top_cells = []
    bottom_cells = []
    for phase_num in ring_1:
        detail = phases[phase_num]
        state = snapshot.phase_states.get(phase_num, SignalState.OFF)
        cell_progress = progress if state == SignalState.GREEN else max(0.0, progress - 0.1)
        top_cells.append(_phase_cell(phase_num, detail.short, state, cell_progress))
    for phase_num in ring_2:
        detail = phases[phase_num]
        state = snapshot.phase_states.get(phase_num, SignalState.OFF)
        cell_progress = progress if state == SignalState.GREEN else max(0.0, progress - 0.1)
        bottom_cells.append(_phase_cell(phase_num, detail.short, state, cell_progress))

    barrier = "||" if snapshot.barrier_status.barrier_23_closed or snapshot.barrier_status.barrier_67_closed else "··"
    heat_state = SignalState.GREEN if snapshot.step_phase == StepPhase.GREEN else SignalState.YELLOW if snapshot.step_phase == StepPhase.YELLOW else SignalState.RED
    heat = _bar(18, _phase_progress(snapshot), heat_state)

    lines = [
        "╭────────────────────────────────────────────────────────────╮",
        f"│ {_fit(snapshot.step_label, 58):<58} │",
        f"│ {_fit(snapshot.title_line(), 58):<58} │",
        "│                                                            │",
        f"│ Ring 1  {top_cells[0]}   {top_cells[1]}   {barrier:<2}  Major side   │",
        f"│         {top_cells[2]}   {top_cells[3]}                     │",
        f"│ Ring 2  {bottom_cells[0]}   {bottom_cells[1]}   {barrier:<2}  Minor side   │",
        f"│         {bottom_cells[2]}   {bottom_cells[3]}                     │",
        "│                                                            │",
        f"│ Barrier sync  {_fit(snapshot.barrier_status.format_panel(), 42):<42} │",
        f"│ Timing band   {heat:<18}  phase {progress:>5.1%}         │",
        f"│ State strip   {_fit(_state_strip(snapshot), 42):<42} │",
        f"│ Legend        {_fit('█ stable  ▓ decay  ▒ stress  ░ clearance  . idle', 42):<42} │",
        "╰────────────────────────────────────────────────────────────╯",
    ]
    return "\n".join(lines)


def print_demo_frame(
    snapshot: ControllerSnapshot,
    wiring: WiringTable,
    config: Wsdot8PhaseConfig | None = None,
) -> None:
    cfg = config or load_config()
    print("=" * 72)
    print(render_signal_helix(snapshot, cfg))
    print("-" * 72)
    print(snapshot.ring_positions.format_panel() + " | " + snapshot.barrier_status.format_panel())
    print_intersection_layout(compact=True, states=snapshot.phase_states)
    print("-" * 72)
    print("Wiring (energized load switches):")
    print(format_energized_panel(wiring, snapshot.phase_states))
    print("=" * 72)
