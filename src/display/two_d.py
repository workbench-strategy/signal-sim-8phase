"""2D SVG/HTML renderer for the 8-phase dual-ring controller demo."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence
from xml.sax.saxutils import escape

from src.controller.models import ControllerSnapshot, SignalState
from src.data.loader import Wsdot8PhaseConfig, TimingStep
from src.controller.timing_plan import TimingPlanRunner
from src.display.teach import CABINET_ASSEMBLIES, build_teach_sequence


SVG_WIDTH = 1240
SVG_HEIGHT = 820
PANEL_X = 880
PANEL_WIDTH = 300


LEAD_LAG_STEPS = [
    TimingStep(
        label="Major SB left + NB through (Ph 1 + Ph 6)",
        greens=(1, 6),
        green_time_s=5,
        yellow_clearance_s=3,
        all_red_s=2,
    ),
    TimingStep(
        label="Major NB left + SB through (Ph 5 + Ph 2)",
        greens=(5, 2),
        green_time_s=5,
        yellow_clearance_s=3,
        all_red_s=2,
    ),
    TimingStep(
        label="Minor EB left + EB through (Ph 3 + Ph 8)",
        greens=(3, 8),
        green_time_s=5,
        yellow_clearance_s=3,
        all_red_s=2,
    ),
    TimingStep(
        label="Minor WB left + WB through (Ph 7 + Ph 4)",
        greens=(7, 4),
        green_time_s=5,
        yellow_clearance_s=3,
        all_red_s=2,
    ),
]


def apply_plan(config: Wsdot8PhaseConfig, plan: str) -> Wsdot8PhaseConfig:
    """Return a config with the requested timing plan steps."""
    if plan == "lead-lag":
        return Wsdot8PhaseConfig(
            description=config.description,
            leg_layout=config.leg_layout,
            phase_details=config.phase_details,
            ring_1=config.ring_1,
            ring_2=config.ring_2,
            barriers=config.barriers,
            concurrent_groups=config.concurrent_groups,
            timing_steps=LEAD_LAG_STEPS,
            tick_seconds=config.tick_seconds,
            wiring_channels=config.wiring_channels,
            detector_channels=list(config.detector_channels),
        )
    return config


@dataclass(frozen=True)
class SignalHead:
    phase: int
    label: str
    x: int
    y: int
    leg: str
    approach: str = ""
    head_type: str = ""


def collect_animation_snapshots(config: Wsdot8PhaseConfig) -> List[ControllerSnapshot]:
    """Collect the full controller cycle as a frame sequence, excluding the finished sentinel."""
    runner = TimingPlanRunner(config)
    runner.reset()
    frames = [runner.snapshot()]
    safety_limit = sum(
        step.green_time_s + step.yellow_clearance_s + step.all_red_s
        for step in config.timing_steps
    ) + 10

    while not runner.plan_finished and safety_limit > 0:
        runner.tick()
        snap = runner.snapshot()
        if snap.step_phase.value != "finished":
            frames.append(snap)
        safety_limit -= 1

    return frames


def _state_color(state: SignalState) -> str:
    return {
        SignalState.GREEN: "#21c86a",
        SignalState.YELLOW: "#f2c94c",
        SignalState.RED: "#d64545",
        SignalState.OFF: "#7a8699",
    }.get(state, "#7a8699")


def _road_rect(x: int, y: int, width: int, height: int, fill: str = "#353945") -> str:
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="6" fill="{fill}" />'


def _text(x: int, y: int, value: str, size: int = 16, color: str = "#e8edf5", weight: str = "600", anchor: str = "middle") -> str:
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" '
        f'font-family="Inter, Segoe UI, Arial, sans-serif" font-size="{size}" '
        f'font-weight="{weight}" fill="{color}">{escape(value)}</text>'
    )


def _head(phase: int, label: str, leg: str, state: SignalState, x: int, y: int, head_type: str = "") -> str:
    color = _state_color(state)
    shape = ""
    if head_type == "arrow":
        shape = f'<polygon points="{x-10},{y+8} {x},{y-12} {x+10},{y+8}" fill="{color}" stroke="#111827" stroke-width="3" />'
    else:
        shape = f'<circle cx="{x}" cy="{y}" r="18" fill="{color}" stroke="#111827" stroke-width="3" />'
    head_attr = head_type or "ball"
    return (
        f'<g data-phase="{phase}" data-leg="{leg}" data-head-type="{head_attr}">'
        f'{shape}'
        f'{_text(x, y + 5, str(phase), size=15, color="#081018", weight="700")}'
        f'{_text(x, y + 34, label, size=12, color="#d9e1ee", weight="500")}'
        f'</g>'
    )


def _ped_label(state: SignalState) -> str:
    if state == SignalState.GREEN:
        return "WALK"
    if state == SignalState.YELLOW:
        return "FDW"
    return "DW"


def _ped_indicator(phase: int, state: SignalState, x: int, y: int) -> str:
    color = _state_color(state)
    label = _ped_label(state)
    return (
        f'<g data-ped-phase="{phase}" data-ped-state="{state.value}">'
        f'<rect x="{x - 28}" y="{y - 16}" width="56" height="32" rx="6" fill="{color}" stroke="#111827" stroke-width="2" />'
        f'{_text(x, y + 5, f"P{phase} {label}", size=11, color="#081018", weight="700")}'
        f'</g>'
    )


PED_LAYOUT = {
    2: (520, 250),  # NB thru / north crosswalk
    6: (320, 530),  # SB thru / south crosswalk
    4: (250, 300),  # WB thru / west crosswalk
    8: (590, 520),  # EB thru / east crosswalk
}


def _state_badge(state: SignalState) -> str:
    color = _state_color(state)
    return f'<span style="display:inline-flex;align-items:center;gap:8px;"><span style="width:12px;height:12px;border-radius:50%;background:{color};display:inline-block;"></span>{escape(state.name.title())}</span>'


def _phase_heads(config: Wsdot8PhaseConfig) -> List[SignalHead]:
    def _ht(phase: int) -> str:
        for ch in config.wiring_channels:
            if ch.phase == phase and ch.indication == "green":
                return ch.head_type
        return ""
    heads = {
        "north": [SignalHead(5, config.phase_details[5].short, 370, 160, "north", "NB", _ht(5)), SignalHead(2, config.phase_details[2].short, 470, 160, "north", "NB", _ht(2))],
        "south": [SignalHead(6, config.phase_details[6].short, 370, 660, "south", "SB", _ht(6)), SignalHead(1, config.phase_details[1].short, 470, 660, "south", "SB", _ht(1))],
        "west": [SignalHead(4, config.phase_details[4].short, 170, 365, "west", "WB", _ht(4)), SignalHead(7, config.phase_details[7].short, 170, 465, "west", "WB", _ht(7))],
        "east": [SignalHead(3, config.phase_details[3].short, 670, 365, "east", "EB", _ht(3)), SignalHead(8, config.phase_details[8].short, 670, 465, "east", "EB", _ht(8))],
    }
    ordered: List[SignalHead] = []
    for leg in ("north", "south", "west", "east"):
        ordered.extend(heads[leg])
    return ordered


def render_intersection_svg(snapshot: ControllerSnapshot, config: Wsdot8PhaseConfig) -> str:
    """Render one controller snapshot as a polished 2D SVG frame."""
    phase_states = snapshot.phase_states
    heads = _phase_heads(config)
    ring_1 = snapshot.ring_positions.ring_1_phase
    ring_2 = snapshot.ring_positions.ring_2_phase
    barrier_text = snapshot.barrier_status.format_panel()

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{SVG_HEIGHT}" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}">',
        "<defs>",
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#111827"/><stop offset="100%" stop-color="#0b1220"/></linearGradient>',
        '<linearGradient id="road" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#3f4653"/><stop offset="100%" stop-color="#2a2f39"/></linearGradient>',
        '<filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="12" stdDeviation="16" flood-color="#000000" flood-opacity="0.35"/></filter>',
        "</defs>",
        '<rect width="100%" height="100%" fill="url(#bg)" />',
        '<g filter="url(#softShadow)">',
        _road_rect(90, 120, 660, 120, "url(#road)"),
        _road_rect(90, 560, 660, 120, "url(#road)"),
        _road_rect(120, 90, 120, 600, "url(#road)"),
        _road_rect(560, 90, 120, 600, "url(#road)"),
        '<rect x="350" y="310" width="140" height="140" rx="20" fill="#242936" stroke="#556070" stroke-width="2" />',
        '<rect x="330" y="290" width="180" height="180" rx="28" fill="none" stroke="#8b95a7" stroke-dasharray="10 10" stroke-width="2" opacity="0.55" />',
        '<line x1="420" y1="120" x2="420" y2="690" stroke="#b4bccb" stroke-dasharray="10 12" stroke-width="2" opacity="0.45" />',
        '<line x1="90" y1="410" x2="750" y2="410" stroke="#b4bccb" stroke-dasharray="10 12" stroke-width="2" opacity="0.45" />',
        '</g>',
        _text(420, 50, "4-Leg 8-Phase Signalized Intersection", size=28, weight="700"),
        _text(420, 78, snapshot.step_label, size=18, color="#c7d0df", weight="500"),
        _text(420, 104, snapshot.title_line(), size=15, color="#9fb0c8", weight="400"),
        _text(420, 118, f"Ring 1: {ring_1 or 'idle'}   Ring 2: {ring_2 or 'idle'}", size=13, color="#7fd5ae", weight="600"),
        _text(420, 738, f"Barrier: {barrier_text}", size=14, color="#d7deeb", weight="500"),
        _text(170, 96, "NORTH", size=14, color="#94a3b8", weight="700"),
        _text(170, 704, "SOUTH", size=14, color="#94a3b8", weight="700"),
        _text(70, 420, "WEST", size=14, color="#94a3b8", weight="700", anchor="end"),
        _text(770, 420, "EAST", size=14, color="#94a3b8", weight="700", anchor="start"),
    ]

    for head in heads:
        state = phase_states.get(head.phase, SignalState.OFF)
        parts.append(_head(head.phase, head.label, head.leg, state, head.x, head.y, head.head_type))

    for ped_phase, (px, py) in PED_LAYOUT.items():
        ped_state = snapshot.ped_states.get(ped_phase, SignalState.RED)
        parts.append(_ped_indicator(ped_phase, ped_state, px, py))

    approach_groups = {}
    for head in heads:
        approach_groups.setdefault(head.approach, []).append(head)
    for approach, group in sorted(approach_groups.items()):
        first = group[0]
        parts.append(_text(first.x, first.y - 28, approach, size=11, color="#7fd5ae", weight="700"))

    barrier_23_state = 'closed' if snapshot.barrier_status.barrier_23_closed else 'open'
    barrier_67_state = 'closed' if snapshot.barrier_status.barrier_67_closed else 'open'
    barrier_23_color = '#d64545' if snapshot.barrier_status.barrier_23_closed else '#7fd5ae'
    barrier_67_color = '#d64545' if snapshot.barrier_status.barrier_67_closed else '#7fd5ae'

    panel_lines = [
        snapshot.step_phase.value.replace("_", " ").title(),
        f"Elapsed: {snapshot.elapsed_s}s",
        f"Remaining: {snapshot.phase_in_step_remaining_s}s / {snapshot.phase_in_step_total_s}s",
        f"Active greens: {', '.join(str(p) for p in sorted(snapshot.active_greens)) or 'none'}",
        f"Energized outputs: {len([s for s in snapshot.phase_states.values() if s != SignalState.RED and s != SignalState.OFF]) * 3}",
    ]

    parts.extend(
        [
            f'<g transform="translate({PANEL_X}, 140)">',
            f'<rect x="0" y="0" width="{PANEL_WIDTH}" height="510" rx="24" fill="#131a27" stroke="#334155" stroke-width="2" />',
            _text(150, 42, "Controller State", size=20, weight="700"),
            _text(150, 72, f"Step {snapshot.step_index + 1}", size=14, color="#9fb0c8"),
            _text(150, 102, snapshot.step_label, size=15, color="#d5def0", weight="600"),
        ]
    )

    y = 144
    for line in panel_lines:
        parts.append(_text(20, y, line, size=14, color="#d6deea", weight="500", anchor="start"))
        y += 34

    parts.extend(
        [
            _text(20, 318, "Barriers", size=16, weight="700", anchor="start"),
            _text(20, 342, f"Barrier 2|3: {barrier_23_state}", size=14, color=barrier_23_color, weight="600", anchor="start"),
            _text(20, 366, f"Barrier 6|7: {barrier_67_state}", size=14, color=barrier_67_color, weight="600", anchor="start"),
            _text(20, 400, "Phase Colors", size=16, weight="700", anchor="start"),
            f'<foreignObject x="20" y="414" width="260" height="100"><div xmlns="http://www.w3.org/1999/xhtml" style="font-family:Inter,Segoe UI,Arial,sans-serif;color:#d6deea;line-height:1.7;font-size:13px;">'
            f'{_state_badge(SignalState.GREEN)}<br/>{_state_badge(SignalState.YELLOW)}<br/>{_state_badge(SignalState.RED)}<br/>{_state_badge(SignalState.OFF)}'
            '</div></foreignObject>',
            _text(20, 530, "Legend", size=16, weight="700", anchor="start"),
            _text(20, 556, "Signal heads are fixed to approach lanes; colors advance from real controller ticks.", size=12, color="#9fb0c8", weight="400", anchor="start"),
            '</g>',
            '</svg>',
        ]
    )
    return "".join(parts)


def render_animation_html(
    snapshots: Sequence[ControllerSnapshot],
    config: Wsdot8PhaseConfig,
    interval_ms: int = 650,
    plan: str = "lead-lead",
) -> str:
    """Render a self-contained HTML animation that cycles through SVG frames."""
    frames = [render_intersection_svg(snapshot, config) for snapshot in snapshots]
    teach = build_teach_sequence(snapshots, config)
    meta = []
    for snapshot, teach_frame in zip(snapshots, teach):
        meta.append(
            {
                "state": snapshot.step_phase.value,
                "label": snapshot.step_label,
                "remaining": snapshot.phase_in_step_remaining_s,
                "elapsed": snapshot.elapsed_s,
                "phases": [
                    phase
                    for phase, state in snapshot.phase_states.items()
                    if state in (SignalState.GREEN, SignalState.YELLOW)
                ],
                "teach": teach_frame,
            }
        )
    phase_labels = [
        f"P{phase_num} {config.phase_details[phase_num].short}"
        for phase_num in range(1, 9)
    ]
    frames_json = json.dumps(frames)
    meta_json = json.dumps(meta)
    phase_labels_json = json.dumps(phase_labels)
    assemblies_json = json.dumps(list(CABINET_ASSEMBLIES))
    detectors_json = json.dumps(
        [
            {
                "detector_id": det.detector_id,
                "label": det.label,
                "connect": det.connect,
                "phase": det.phase,
                "kind": det.kind,
                "plan_ref": det.plan_ref,
            }
            for det in config.detector_channels
        ]
    )
    interval_ms = max(100, interval_ms)
    lead_selected = " selected" if plan == "lead-lead" else ""
    lag_selected = " selected" if plan == "lead-lag" else ""
    rack_rows = "".join(
        (
            f'<div class="rack-row" data-assembly="{escape(item["id"])}">'
            f'<span class="rack-label">{escape(item["label"])}</span>'
            f'<span class="rack-ref">{escape(item["plan_ref"])}</span>'
            f"</div>"
        )
        for item in CABINET_ASSEMBLIES
    )
    detector_rows_html = "".join(
        (
            f'<label class="det-row" data-detector="{escape(det.detector_id)}" data-phase="{det.phase}">'
            f'<input type="checkbox" class="det-switch" data-phase="{det.phase}" data-kind="{escape(det.kind)}" />'
            f'<span class="det-label">{escape(det.label)}</span>'
            f'<span class="det-connect">{escape(det.connect)} to Ph{det.phase}</span>'
            f'<span class="det-status" data-status-for="{escape(det.detector_id)}">idle</span>'
            f"</label>"
        )
        for det in config.detector_channels
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Signal Sim 8-Phase Teach Mode</title>
  <style>
    :root {{ color-scheme: dark; }}
    body {{ margin: 0; font-family: "IBM Plex Sans", "Segoe UI", sans-serif; background: #09111d; color: #e5edf7; }}
    .shell {{ max-width: 1320px; margin: 0 auto; padding: 24px; }}
    h1 {{ font-size: 1.35rem; margin: 0 0 8px; font-weight: 700; }}
    .lede {{ color: #9fb0c8; margin: 0 0 18px; font-size: 0.95rem; max-width: 70ch; }}
    .toolbar {{ display: flex; gap: 12px; align-items: center; margin-bottom: 16px; flex-wrap: wrap; }}
    .toolbar button, .toolbar select {{ border: 1px solid #334155; background: #121a28; color: #e5edf7; padding: 10px 14px; border-radius: 8px; cursor: pointer; }}
    .toolbar button:hover {{ background: #182235; }}
    .toolbar .meta {{ color: #9fb0c8; font-size: 14px; }}
    .speed {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; width: 100%; margin: 6px 0 14px; }}
    .speed .card {{ border: 1px solid #223047; background: #101827; border-radius: 10px; padding: 12px; }}
    .speed .card h4 {{ margin: 0 0 8px; font-size: 13px; color: #c7d0df; }}
    .speed .card .value {{ font-size: 12px; color: #9fb0c8; margin-top: 6px; }}
    .speed .hint {{ font-size: 11px; color: #7f8da3; margin-top: 4px; }}
    .speed input[type="range"] {{ width: 100%; }}
    .phase-grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; margin: 14px 0 18px; }}
    .phase-grid .card {{ border: 1px solid #223047; background: #101827; border-radius: 10px; padding: 10px 12px; }}
    .phase-grid .card h4 {{ margin: 0 0 8px; font-size: 12px; color: #c7d0df; }}
    .phase-grid .card .value {{ font-size: 11px; color: #9fb0c8; margin-top: 6px; }}
    .phase-grid input[type="range"] {{ width: 100%; }}
    .frame {{ border: 1px solid #253246; border-radius: 16px; overflow: hidden; background: #0b1220; }}
    .frame svg {{ display: block; width: 100%; height: auto; }}
    .teach-grid {{ display: grid; grid-template-columns: 1.2fr 1fr; gap: 14px; margin-top: 16px; }}
    @media (max-width: 900px) {{ .teach-grid, .speed, .phase-grid {{ grid-template-columns: 1fr; }} }}
    .panel {{ border: 1px solid #223047; background: #101827; border-radius: 12px; padding: 16px; }}
    .panel h2 {{ margin: 0 0 10px; font-size: 1rem; }}
    .concept {{ font-size: 1.05rem; font-weight: 700; color: #f3f7ff; margin-bottom: 8px; }}
    .why, .checkpoint, .refs {{ color: #b7c4d8; font-size: 0.92rem; line-height: 1.45; margin: 0 0 10px; }}
    .checkpoint {{ border-left: 3px solid #7fd5ae; padding-left: 10px; }}
    .pause-banner {{ display: none; margin: 0 0 12px; padding: 10px 12px; border: 1px solid #8a5a2b; background: #24180f; color: #f0d2a8; border-radius: 8px; font-size: 0.9rem; }}
    .pause-banner.active {{ display: block; }}
    .rack {{ display: grid; gap: 6px; }}
    .rack-row {{ display: flex; justify-content: space-between; gap: 8px; padding: 8px 10px; border: 1px solid #1f2a3c; border-radius: 8px; background: #0d1522; color: #8ea0b8; font-size: 0.82rem; }}
    .rack-row.active {{ border-color: #3d8f6a; background: #10271d; color: #d7ffe9; }}
    .rack-row.monitor.active {{ border-color: #d64545; background: #2a1212; color: #ffd0d0; }}
    .rack-label {{ font-weight: 600; }}
    .rack-ref {{ color: #7f8da3; white-space: nowrap; }}
    .outputs {{ margin-top: 12px; display: grid; gap: 6px; max-height: 220px; overflow: auto; }}
    .output {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: 0.78rem; padding: 7px 8px; border-radius: 6px; background: #0d1522; border: 1px solid #243247; color: #c9d6e8; }}
    .output.on-green {{ border-color: #2f9e68; }}
    .output.on-yellow {{ border-color: #c9a227; }}
    .output.on-red {{ border-color: #b84b4b; }}
    .output.ped {{ opacity: 0.95; border-style: dashed; }}
    .ped-line {{ margin: 0 0 10px; color: #9fb0c8; font-size: 0.86rem; }}
    .det-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; margin-top: 10px; }}
    .det-row {{ display: grid; grid-template-columns: auto 1fr; gap: 4px 8px; align-items: center; border: 1px solid #223047; border-radius: 8px; padding: 8px; background: #0d1522; font-size: 0.78rem; }}
    .det-row.active-serving {{ border-color: #2f9e68; background: #10271d; }}
    .det-row.active-call {{ border-color: #c9a227; background: #24180f; }}
    .det-label {{ font-weight: 700; color: #e5edf7; }}
    .det-connect {{ grid-column: 2; color: #8ea0b8; }}
    .det-status {{ grid-column: 2; color: #7fd5ae; }}
    .det-hint {{ margin-top: 8px; color: #7f8da3; font-size: 0.78rem; }}
    input[type="range"] {{ width: min(680px, 100%); }}
  </style>
</head>
<body>
  <div class="shell">
    <h1>Signal Sim 8-Phase Teach Mode</h1>
    <p class="lede">
      Intersection heads, ped Walk/FDW overlays, dual-ring timing, and a Type 332 cabinet story share one playhead.
      Presentation-speed sliders change playback only; ASC green/yellow/all-red seconds stay fixed in the exported frames.
      Detector Test switches (J-80.15) extend green presentation when a matching phase is being served.
    </p>
    <div class="toolbar">
      <button id="toggle">Pause</button>
      <button id="prev">Prev</button>
      <button id="next">Next</button>
      <button id="resumeTeach">Resume after checkpoint</button>
      <select id="planSelect"><option value="lead-lead"{lead_selected}>Plan A: Lead/Lead</option><option value="lead-lag"{lag_selected}>Plan B: Lead/Lag</option></select>
      <input id="scrub" type="range" min="0" max="{max(0, len(frames) - 1)}" value="0" />
      <div class="meta" id="counter" aria-live="polite"></div>
    </div>
    <div class="speed">
      <div class="card">
        <h4>Presentation cycle length</h4>
        <input id="cycleTiming" type="range" min="4000" max="40000" value="{max(interval_ms * len(frames), 4000)}" />
        <div class="value" id="cycleValue"></div>
        <div class="hint">Display tempo only (not ASC cycle seconds)</div>
      </div>
      <div class="card">
        <h4>Presentation green hold</h4>
        <input id="greenTiming" type="range" min="150" max="2500" value="{interval_ms}" />
        <div class="value" id="greenValue"></div>
        <div class="hint">How long green frames stay on screen</div>
      </div>
      <div class="card">
        <h4>Presentation yellow hold</h4>
        <input id="yellowTiming" type="range" min="100" max="1800" value="{max(150, interval_ms // 2)}" />
        <div class="value" id="yellowValue"></div>
        <div class="hint">How long yellow frames stay on screen</div>
      </div>
      <div class="card">
        <h4>Presentation red / all-red hold</h4>
        <input id="redTiming" type="range" min="80" max="1200" value="{max(100, interval_ms // 4)}" />
        <div class="value" id="redValue"></div>
        <div class="hint">How long red / barrier frames stay on screen</div>
      </div>
    </div>
    <div class="phase-grid">
      {''.join(
          f'<div class="card"><h4>{escape(label)}</h4><input id="phaseTiming{idx+1}" type="range" min="50" max="200" value="100" /><div class="value" id="phaseValue{idx+1}"></div><div class="hint">Relative presentation weight</div></div>'
          for idx, label in enumerate(phase_labels)
      )}
    </div>
    <div class="frame" id="frame"></div>
    <div class="teach-grid">
      <div class="panel">
        <h2>Teach panel</h2>
        <div id="pauseBanner" class="pause-banner"></div>
        <div class="concept" id="teachConcept"></div>
        <p class="why" id="teachWhy"></p>
        <p class="checkpoint" id="teachCheckpoint"></p>
        <p class="ped-line" id="teachPed"></p>
        <p class="refs" id="teachRefs"></p>
        <h2>Detector Test Panel (J-80.15)</h2>
        <div class="det-grid" id="detectorPanel">{detector_rows_html}</div>
        <p class="det-hint">Flip a switch to Test: if that phase is green, presentation green hold extends (call extension). If red, status shows call latched for next service. Switches are momentary in the field; here they stay on so you can teach.</p>
      </div>
      <div class="panel">
        <h2>Type 332 cabinet (J-80.10)</h2>
        <div class="rack" id="cabinetRack">{rack_rows}</div>
        <div class="outputs" id="energizedOutputs" aria-live="polite"></div>
      </div>
    </div>
  </div>
  <script>
    const frames = {frames_json};
    const meta = {meta_json};
    const phaseLabels = {phase_labels_json};
    const assemblies = {assemblies_json};
    const detectorCatalog = {detectors_json};
    const frameEl = document.getElementById('frame');
    const counter = document.getElementById('counter');
    const scrub = document.getElementById('scrub');
    const toggle = document.getElementById('toggle');
    const pauseBanner = document.getElementById('pauseBanner');
    const teachConcept = document.getElementById('teachConcept');
    const teachWhy = document.getElementById('teachWhy');
    const teachCheckpoint = document.getElementById('teachCheckpoint');
    const teachPed = document.getElementById('teachPed');
    const teachRefs = document.getElementById('teachRefs');
    const energizedOutputs = document.getElementById('energizedOutputs');
    const cycleTiming = document.getElementById('cycleTiming');
    const greenTiming = document.getElementById('greenTiming');
    const yellowTiming = document.getElementById('yellowTiming');
    const redTiming = document.getElementById('redTiming');
    const cycleValue = document.getElementById('cycleValue');
    const greenValue = document.getElementById('greenValue');
    const yellowValue = document.getElementById('yellowValue');
    const redValue = document.getElementById('redValue');
    const phaseControls = phaseLabels.map((_, idx) => document.getElementById(`phaseTiming${'{'}idx + 1{'}'}`));
    const phaseValues = phaseLabels.map((_, idx) => document.getElementById(`phaseValue${'{'}idx + 1{'}'}`));
    const detSwitches = Array.from(document.querySelectorAll('.det-switch'));
    let index = 0;
    let playing = true;
    let timer = null;
    let durations = [];
    let suppressPauseOnce = false;

    function testedPhases() {{
      return new Set(
        detSwitches.filter((el) => el.checked).map((el) => Number(el.getAttribute('data-phase')))
      );
    }}

    function phaseDelay(kind) {{
      if (kind === 'green') return Number(greenTiming.value);
      if (kind === 'yellow') return Number(yellowTiming.value);
      return Number(redTiming.value);
    }}

    function phaseFactor(phases) {{
      if (!phases || phases.length === 0) {{
        return 1;
      }}
      const sum = phases.reduce((acc, phaseNum) => acc + Number(phaseControls[phaseNum - 1].value), 0);
      return (sum / phases.length) / 100;
    }}

    function detectorExtendFactor(entry) {{
      if (entry.state !== 'green') {{
        return 1;
      }}
      const tested = testedPhases();
      const hit = (entry.phases || []).some((phaseNum) => tested.has(phaseNum));
      return hit ? 1.8 : 1;
    }}

    function rebuildDurations() {{
      const raw = meta.map((entry) => phaseDelay(entry.state) * phaseFactor(entry.phases) * detectorExtendFactor(entry));
      const totalRaw = raw.reduce((acc, value) => acc + value, 0) || 1;
      const targetCycle = Number(cycleTiming.value);
      const scale = targetCycle / totalRaw;
      durations = raw.map((value) => Math.max(60, Math.round(value * scale)));
    }}

    function refreshTimingLabels() {{
      cycleValue.textContent = `${'{'}cycleTiming.value{'}'} ms presentation cycle`;
      greenValue.textContent = `${'{'}greenTiming.value{'}'} ms per green frame`;
      yellowValue.textContent = `${'{'}yellowTiming.value{'}'} ms per yellow frame`;
      redValue.textContent = `${'{'}redTiming.value{'}'} ms per red / all-red frame`;
      phaseValues.forEach((node, idx) => {{
        node.textContent = `${'{'}phaseControls[idx].value{'}'}% presentation weight`;
      }});
    }}

    function renderTeach(current) {{
      const teach = current.teach || {{}};
      teachConcept.textContent = teach.concept || '';
      teachWhy.textContent = teach.why || '';
      teachCheckpoint.textContent = teach.checkpoint ? ('Checkpoint: ' + teach.checkpoint) : '';
      teachPed.textContent = teach.ped_summary ? ('Ped overlaps: ' + teach.ped_summary) : '';
      teachRefs.textContent = (teach.plan_refs || []).join(' | ');
      const active = new Set(teach.active_assemblies || []);
      const tested = testedPhases();
      if (tested.size) {{
        active.add('detector_test');
        active.add('input_file_i');
      }}
      document.querySelectorAll('.rack-row').forEach((row) => {{
        const id = row.getAttribute('data-assembly');
        row.classList.toggle('active', active.has(id));
        row.classList.toggle('monitor', id === 'conflict_monitor');
      }});
      const rows = teach.energized || [];
      if (!rows.length) {{
        energizedOutputs.innerHTML = '<div class="output">No load-switch channels energized (idle / all dark).</div>';
      }} else {{
        energizedOutputs.innerHTML = rows.map((row) => {{
          const ft = row.field_terminal ? ` FT ${'{'}row.field_terminal{'}'}` : '';
          const pedClass = row.channel_kind === 'ped' ? ' ped' : '';
          return `<div class="output on-${'{'}row.indication{'}'}${'{'}pedClass{'}'}">${'{'}row.output_id{'}'}${'{'}ft{'}'}  |  Ph${'{'}row.phase{'}'} ${'{'}row.indication{'}'}  |  ${'{'}row.label{'}'}</div>`;
        }}).join('');
      }}
      const serving = new Set(current.phases || []);
      document.querySelectorAll('.det-row').forEach((row) => {{
        const phase = Number(row.getAttribute('data-phase'));
        const box = row.querySelector('.det-switch');
        const status = row.querySelector('.det-status');
        const on = box && box.checked;
        let text = 'idle';
        row.classList.remove('active-serving', 'active-call');
        if (on && serving.has(phase) && current.state === 'green') {{
          text = 'extending green (presentation)';
          row.classList.add('active-serving');
        }} else if (on) {{
          text = 'call latched / waiting';
          row.classList.add('active-call');
        }} else if (serving.has(phase)) {{
          text = 'phase active';
        }}
        if (status) status.textContent = text;
      }});
    }}

    function showFrame(nextIndex) {{
      index = (nextIndex + frames.length) % frames.length;
      frameEl.innerHTML = frames[index];
      const current = meta[index];
      counter.textContent = `Frame ${'{'}index + 1{'}'} / ${'{'}frames.length{'}'}  |  ${'{'}current.label{'}'}  |  ${'{'}current.state.replaceAll('_', ' '){'}'}`;
      scrub.value = index;
      renderTeach(current);
      return current;
    }}

    function maybeAutoPause(current) {{
      if (suppressPauseOnce) {{
        suppressPauseOnce = false;
        pauseBanner.classList.remove('active');
        return false;
      }}
      if (current.teach && current.teach.pause) {{
        playing = false;
        toggle.textContent = 'Play';
        pauseBanner.textContent = 'Auto-paused at all-red / barrier sync. Use the checkpoint question, then Resume after checkpoint.';
        pauseBanner.classList.add('active');
        window.clearTimeout(timer);
        return true;
      }}
      pauseBanner.classList.remove('active');
      return false;
    }}

    function safeStep(delta) {{
      window.clearTimeout(timer);
      const current = showFrame(index + delta);
      maybeAutoPause(current);
      if (playing) loop();
    }}

    function loop() {{
      if (!playing) {{
        return;
      }}
      const currentDelay = durations[index] || phaseDelay(meta[index].state);
      timer = window.setTimeout(() => {{
        const current = showFrame(index + 1);
        if (!maybeAutoPause(current) && playing) {{
          loop();
        }}
      }}, currentDelay);
    }}

    toggle.addEventListener('click', () => {{
      playing = !playing;
      toggle.textContent = playing ? 'Pause' : 'Play';
      if (playing) {{
        pauseBanner.classList.remove('active');
        window.clearTimeout(timer);
        loop();
      }} else {{
        window.clearTimeout(timer);
      }}
    }});
    document.getElementById('prev').addEventListener('click', () => safeStep(-1));
    document.getElementById('next').addEventListener('click', () => safeStep(1));
    document.getElementById('resumeTeach').addEventListener('click', () => {{
      suppressPauseOnce = true;
      playing = true;
      toggle.textContent = 'Pause';
      pauseBanner.classList.remove('active');
      window.clearTimeout(timer);
      loop();
    }});
    scrub.addEventListener('input', (event) => {{
      window.clearTimeout(timer);
      const current = showFrame(Number(event.target.value));
      maybeAutoPause(current);
      if (playing) loop();
    }});
    document.getElementById('planSelect').addEventListener('change', (event) => {{
      window.location.href = window.location.pathname + '?plan=' + event.target.value;
    }});
    [cycleTiming, greenTiming, yellowTiming, redTiming, ...phaseControls].forEach((control) => control.addEventListener('input', () => {{
      refreshTimingLabels();
      rebuildDurations();
    }}));
    detSwitches.forEach((control) => control.addEventListener('change', () => {{
      rebuildDurations();
      renderTeach(meta[index]);
    }}));

    scrub.max = frames.length - 1;
    showFrame(0);
    refreshTimingLabels();
    rebuildDurations();
    loop();
  </script>
</body>
</html>
"""


def write_animation_html(
    snapshots: Sequence[ControllerSnapshot],
    config: Wsdot8PhaseConfig,
    output_path: str | Path,
    interval_ms: int = 650,
    plan: str = "lead-lead",
) -> Path:
    output = Path(output_path)
    output.write_text(
        render_animation_html(snapshots, config, interval_ms=interval_ms, plan=plan),
        encoding="utf-8",
    )
    return output
