"""Load WSDOT 8-phase configuration from JSON."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class PhaseDetail:
    phase: int
    movement: str
    leg: str
    short: str
    full: str
    street_role: str = ""


@dataclass(frozen=True)
class ConcurrentGroup:
    phases: Tuple[int, ...]
    label: str


@dataclass(frozen=True)
class Barrier:
    id: str
    between: Tuple[int, int]
    description: str


@dataclass(frozen=True)
class TimingStep:
    label: str
    greens: Tuple[int, ...]
    green_time_s: int
    yellow_clearance_s: int
    all_red_s: int


@dataclass(frozen=True)
class WiringChannel:
    output_id: str
    phase: int
    indication: str
    label: str
    wsdot_ref: str
    leg: str = ""
    approach: str = ""
    movement_group: str = ""
    street_role: str = ""
    head_type: str = ""


@dataclass
class Wsdot8PhaseConfig:
    description: str
    leg_layout: Dict[str, List[int]]
    phase_details: Dict[int, PhaseDetail]
    ring_1: Tuple[int, ...]
    ring_2: Tuple[int, ...]
    barriers: List[Barrier]
    concurrent_groups: List[ConcurrentGroup]
    timing_steps: List[TimingStep]
    tick_seconds: int
    wiring_channels: List[WiringChannel]


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_config_path() -> Path:
    return _project_root() / "data" / "wsdot_8phase.json"


def load_config(path: Optional[Path] = None) -> Wsdot8PhaseConfig:
    config_path = path or default_config_path()
    with open(config_path, encoding="utf-8") as f:
        raw = json.load(f)

    layout = raw["intersection_layout"]
    legs = layout["intersection_legs"]
    leg_layout = {
        "north": list(legs["north"]["phases"]),
        "south": list(legs["south"]["phases"]),
        "east": list(legs["east"]["phases"]),
        "west": list(legs["west"]["phases"]),
    }

    phase_details: Dict[int, PhaseDetail] = {}
    for key, detail in layout["phase_details"].items():
        p = int(key)
        phase_details[p] = PhaseDetail(
            phase=p,
            movement=detail["movement"],
            leg=detail["leg"],
            short=detail["short"],
            full=detail["full"],
            street_role=detail.get("street_role", ""),
        )

    dr = raw["dual_ring"]
    barriers = [
        Barrier(
            id=b["id"],
            between=(b["between"][0], b["between"][1]),
            description=b["description"],
        )
        for b in dr["barriers"]
    ]
    concurrent_groups = [
        ConcurrentGroup(
            phases=tuple(g["phases"]),
            label=g["label"],
        )
        for g in dr["concurrent_groups"]
    ]

    tp = raw["timing_plan"]
    timing_steps = [
        TimingStep(
            label=s["label"],
            greens=tuple(s["greens"]),
            green_time_s=int(s["green_time_s"]),
            yellow_clearance_s=int(s["yellow_clearance_s"]),
            all_red_s=int(s["all_red_s"]),
        )
        for s in tp["steps"]
    ]

    wiring_channels = [
        WiringChannel(
            output_id=c["output_id"],
            phase=int(c["phase"]),
            indication=c["indication"],
            label=c["label"],
            wsdot_ref=c["wsdot_ref"],
            leg=phase_details[int(c["phase"])].leg,
            approach=_approach_from_movement(
                phase_details[int(c["phase"])].movement
            ),
            movement_group=_movement_group(
                phase_details[int(c["phase"])].movement
            ),
            street_role=phase_details[int(c["phase"])].street_role,
            head_type=_head_type(c["indication"], c["label"]),
        )
        for c in raw["wiring"]["channels"]
    ]

    return Wsdot8PhaseConfig(
        description=raw.get("description", ""),
        leg_layout=leg_layout,
        phase_details=phase_details,
        ring_1=tuple(dr["ring_1"]),
        ring_2=tuple(dr["ring_2"]),
        barriers=barriers,
        concurrent_groups=concurrent_groups,
        timing_steps=timing_steps,
        tick_seconds=int(tp.get("tick_seconds", 1)),
        wiring_channels=wiring_channels,
    )


def _approach_from_movement(movement: str) -> str:
    if movement.startswith("northbound"):
        return "NB"
    if movement.startswith("southbound"):
        return "SB"
    if movement.startswith("eastbound"):
        return "EB"
    if movement.startswith("westbound"):
        return "WB"
    return ""


def _movement_group(movement: str) -> str:
    if movement.endswith("left"):
        return "left"
    if movement.endswith("through"):
        return "through"
    return "other"


def _head_type(indication: str, label: str) -> str:
    if "arrow" in label.lower():
        return "arrow"
    if "ball" in label.lower():
        return "ball"
    return indication.lower()
