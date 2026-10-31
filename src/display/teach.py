"""Teaching narration and Type 332 cabinet frame metadata for the 2D demo."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Sequence

from src.controller.models import ControllerSnapshot, StepPhase
from src.data.loader import Wsdot8PhaseConfig, WiringChannel
from src.wiring.table import WiringTable


CABINET_ASSEMBLIES = (
    {
        "id": "detector_test",
        "label": "Detector Test Panel (2U)",
        "role": "input",
        "plan_ref": "J-80.15 / J-80.10 Note 3",
    },
    {
        "id": "controller",
        "label": "Type 2070 Controller (4U)",
        "role": "controller",
        "plan_ref": "J-80.10",
    },
    {
        "id": "input_file_i",
        "label": "Input File LX I (3U)",
        "role": "input",
        "plan_ref": "J-80.10",
    },
    {
        "id": "input_file_j",
        "label": "Input File LX J (3U)",
        "role": "input",
        "plan_ref": "J-80.10",
    },
    {
        "id": "pda",
        "label": "Power Distribution Assembly #2LX (4U)",
        "role": "power",
        "plan_ref": "J-80.10",
    },
    {
        "id": "output_file_1",
        "label": "Output File #1 LX (6U)",
        "role": "output",
        "plan_ref": "J-80.10 Note 4 / J-80.12",
    },
    {
        "id": "output_file_2",
        "label": "Output File #2 LX #420 (3U)",
        "role": "output_optional",
        "plan_ref": "J-80.10 Note 5",
    },
    {
        "id": "conflict_monitor",
        "label": "Conflict Monitor + Red Interface",
        "role": "monitor",
        "plan_ref": "J-80.10 Note 8",
    },
)


# WSDOT field terminal numbers from Standard Plan J-80.12 (phase R/Y/G).
FIELD_TERMINALS: Dict[tuple[int, str], str] = {
    (1, "red"): "611",
    (1, "yellow"): "612",
    (1, "green"): "613",
    (2, "red"): "621",
    (2, "yellow"): "622",
    (2, "green"): "623",
    (3, "red"): "631",
    (3, "yellow"): "632",
    (3, "green"): "633",
    (4, "red"): "641",
    (4, "yellow"): "642",
    (4, "green"): "643",
    (5, "red"): "651",
    (5, "yellow"): "652",
    (5, "green"): "653",
    (6, "red"): "661",
    (6, "yellow"): "662",
    (6, "green"): "663",
    (7, "red"): "671",
    (7, "yellow"): "672",
    (7, "green"): "673",
    (8, "red"): "681",
    (8, "yellow"): "682",
    (8, "green"): "683",
}


@dataclass(frozen=True)
class TeachFrame:
    concept: str
    why: str
    checkpoint: str
    pause: bool
    pause_reason: str
    active_assemblies: List[str]
    energized: List[Dict[str, str]]
    plan_refs: List[str]

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


def field_terminal_for(phase: int, indication: str) -> str:
    return FIELD_TERMINALS.get((phase, indication), "")


def enrich_channel_cabinet_fields(channel: WiringChannel) -> WiringChannel:
    """Attach J-80.12 field terminal + Output File #1 LX assembly when missing."""
    if channel.field_terminal and channel.cabinet_assembly:
        return channel
    terminal = channel.field_terminal or field_terminal_for(channel.phase, channel.indication)
    assembly = channel.cabinet_assembly or "Output File #1 LX"
    return WiringChannel(
        output_id=channel.output_id,
        phase=channel.phase,
        indication=channel.indication,
        label=channel.label,
        wsdot_ref=channel.wsdot_ref,
        leg=channel.leg,
        approach=channel.approach,
        movement_group=channel.movement_group,
        street_role=channel.street_role,
        head_type=channel.head_type,
        field_terminal=terminal,
        cabinet_assembly=assembly,
    )


def _greens_label(greens: Sequence[int], config: Wsdot8PhaseConfig) -> str:
    if not greens:
        return "none"
    parts = []
    for phase in sorted(greens):
        short = config.phase_details[phase].short if phase in config.phase_details else f"Ph{phase}"
        parts.append(f"Ph{phase} {short}")
    return ", ".join(parts)


def _concept_for(
    snapshot: ControllerSnapshot,
    config: Wsdot8PhaseConfig,
    previous: Optional[ControllerSnapshot] = None,
) -> tuple[str, str, str]:
    greens = sorted(snapshot.active_greens)
    green_text = _greens_label(greens, config)
    barrier = snapshot.barrier_status

    if snapshot.step_phase == StepPhase.GREEN:
        if set(greens) in ({1, 5}, {3, 7}):
            return (
                "Protected lefts across both rings",
                f"Controller holds {green_text}. Same-street lefts can run together because they sit on different rings and stay on one side of the barrier.",
                "Which ring owns each green phase? Ring 1 is 1-4; Ring 2 is 5-8.",
            )
        if set(greens) in ({2, 6}, {4, 8}):
            return (
                "Through movements (ball heads)",
                f"Controller holds {green_text}. Through greens drive ball load switches; opposing lefts stay red.",
                "Name the approach pair sum rule that pairs each through with its protected left.",
            )
        if set(greens) in ({1, 6}, {5, 2}, {3, 8}, {7, 4}):
            return (
                "Lead/lag approach pair",
                f"Controller holds {green_text}. This is an approach pair (thru + left on one approach), common in lead/lag plans and preemption channels.",
                "Which WSDOT preemption channel matches this approach pair?",
            )
        return (
            "Concurrent greens",
            f"Active greens: {green_text}. Dual-ring logic only allows concurrent groups from the timing plan / DM 1330 pairing.",
            "Could these two greens sit on the same ring? Why or why not?",
        )

    if snapshot.step_phase == StepPhase.YELLOW:
        return (
            "Yellow clearance",
            f"Leaving {green_text}. Output File #1 LX switches from green to yellow field terminals while the conflict monitor still expects a valid color per channel.",
            "What field terminal digit pattern marks yellow vs green for a phase (J-80.12)?",
        )

    if snapshot.step_phase == StepPhase.ALL_RED:
        closed = []
        if barrier.barrier_23_closed:
            closed.append("barrier 2|3")
        if barrier.barrier_67_closed:
            closed.append("barrier 6|7")
        closed_text = ", ".join(closed) if closed else "rings parked for all-red"
        after_yellow = previous is not None and previous.step_phase == StepPhase.YELLOW
        if after_yellow:
            return (
                "All-red / barrier sync",
                f"Both rings show red ({closed_text}). On a Type 332 rack the conflict monitor is checking red enables through the Output File #1 LX red monitor program board before the next side of the barrier starts.",
                "Why must both rings finish clearance before crossing the barrier?",
            )
        return (
            "Red dwell before next green",
            f"Cabinet outputs are on red field terminals ({closed_text}). Watch Output File #1 LX and the conflict monitor stay active while the 2070 prepares the next concurrent pair.",
            "Which assembly drives the field wires: controller CPU or output file load switches?",
        )

    return (
        "Plan idle",
        "Timing plan finished. Reset or re-export to replay the cabinet/controller story.",
        "Which assembly in the Type 332 rack actually switched the field wires you just watched?",
    )


def _active_assemblies(snapshot: ControllerSnapshot) -> List[str]:
    active = ["controller", "output_file_1", "conflict_monitor", "pda"]
    if snapshot.step_phase == StepPhase.GREEN:
        active.append("input_file_i")
    if snapshot.step_phase == StepPhase.ALL_RED:
        # Emphasize monitor during barrier / red enable checks.
        active = ["controller", "output_file_1", "conflict_monitor", "pda"]
    return active


def _should_pause(snapshot: ControllerSnapshot, previous: Optional[ControllerSnapshot]) -> tuple[bool, str]:
    """Pause only when entering all-red after yellow clearance (barrier teach moment)."""
    if snapshot.step_phase != StepPhase.ALL_RED:
        return False, ""
    if previous is not None and previous.step_phase == StepPhase.YELLOW:
        return True, "barrier_all_red"
    return False, ""


def build_teach_frame(
    snapshot: ControllerSnapshot,
    config: Wsdot8PhaseConfig,
    previous: Optional[ControllerSnapshot] = None,
) -> TeachFrame:
    concept, why, checkpoint = _concept_for(snapshot, config, previous)
    pause, pause_reason = _should_pause(snapshot, previous)
    wiring = WiringTable.from_config(config)
    energized_rows: List[Dict[str, str]] = []
    for out in wiring.energized_outputs(snapshot.phase_states):
        channel = next(
            (
                enrich_channel_cabinet_fields(ch)
                for ch in config.wiring_channels
                if ch.output_id == out.output_id
            ),
            None,
        )
        terminal = channel.field_terminal if channel else field_terminal_for(out.phase, out.indication)
        assembly = channel.cabinet_assembly if channel else "Output File #1 LX"
        energized_rows.append(
            {
                "output_id": out.output_id,
                "label": out.label,
                "phase": str(out.phase),
                "indication": out.indication,
                "field_terminal": terminal,
                "cabinet_assembly": assembly,
                "wsdot_ref": out.wsdot_ref,
            }
        )

    plan_refs = ["DM 1330", "J-80.10 Type 332", "J-80.12 field terminals"]
    if snapshot.step_phase == StepPhase.GREEN:
        plan_refs.append("Input File / detector calls (J-80.15)")

    return TeachFrame(
        concept=concept,
        why=why,
        checkpoint=checkpoint,
        pause=pause,
        pause_reason=pause_reason,
        active_assemblies=_active_assemblies(snapshot),
        energized=energized_rows,
        plan_refs=plan_refs,
    )


def build_teach_sequence(
    snapshots: Sequence[ControllerSnapshot],
    config: Wsdot8PhaseConfig,
) -> List[Dict[str, object]]:
    frames: List[Dict[str, object]] = []
    previous: Optional[ControllerSnapshot] = None
    for snap in snapshots:
        frames.append(build_teach_frame(snap, config, previous).as_dict())
        previous = snap
    return frames
