"""Cabinet output / wiring table from WSDOT config."""

from __future__ import annotations

from dataclasses import dataclass
from collections import defaultdict
from typing import DefaultDict, Dict, List

from src.controller.models import SignalState
from src.data.loader import Wsdot8PhaseConfig, WiringChannel, load_config


@dataclass(frozen=True)
class EnergizedOutput:
    output_id: str
    label: str
    wsdot_ref: str
    phase: int
    indication: str


class WiringTable:
    def __init__(self, channels: List[WiringChannel]) -> None:
        self._channels = channels

    @classmethod
    def from_config(cls, config: Wsdot8PhaseConfig | None = None) -> "WiringTable":
        cfg = config or load_config()
        return cls(cfg.wiring_channels)

    def energized_outputs(
        self,
        phase_states: Dict[int, SignalState],
        ped_states: Dict[int, SignalState] | None = None,
    ) -> List[EnergizedOutput]:
        indication_map = {
            SignalState.GREEN: "green",
            SignalState.YELLOW: "yellow",
            SignalState.RED: "red",
        }
        result: List[EnergizedOutput] = []
        for ch in self._channels:
            if getattr(ch, "channel_kind", "vehicle") == "ped":
                if ped_states is None:
                    continue
                state = ped_states.get(ch.phase, SignalState.RED)
            else:
                state = phase_states.get(ch.phase, SignalState.RED)
            if state == SignalState.OFF:
                continue
            expected = indication_map.get(state)
            if expected and ch.indication == expected:
                result.append(
                    EnergizedOutput(
                        output_id=ch.output_id,
                        label=ch.label,
                        wsdot_ref=ch.wsdot_ref,
                        phase=ch.phase,
                        indication=ch.indication,
                    )
                )
        return sorted(result, key=lambda o: o.output_id)

    def channels_by_phase(self) -> Dict[int, List[WiringChannel]]:
        grouped: DefaultDict[int, List[WiringChannel]] = defaultdict(list)
        for ch in self._channels:
            grouped[ch.phase].append(ch)
        return {phase: sorted(channels, key=lambda ch: (ch.indication, ch.output_id)) for phase, channels in grouped.items()}

    def channels_by_approach(self) -> Dict[str, List[WiringChannel]]:
        grouped: DefaultDict[str, List[WiringChannel]] = defaultdict(list)
        for ch in self._channels:
            if ch.approach:
                grouped[ch.approach].append(ch)
        return {approach: sorted(channels, key=lambda ch: (ch.phase, ch.indication, ch.output_id)) for approach, channels in grouped.items()}

    def channels_by_head_type(self) -> Dict[str, List[WiringChannel]]:
        grouped: DefaultDict[str, List[WiringChannel]] = defaultdict(list)
        for ch in self._channels:
            grouped[ch.head_type or "unknown"].append(ch)
        return {head_type: sorted(channels, key=lambda ch: (ch.phase, ch.indication, ch.output_id)) for head_type, channels in grouped.items()}

    def summary_rows(self) -> List[str]:
        rows = []
        for phase, channels in sorted(self.channels_by_phase().items()):
            vehicle = [ch for ch in channels if getattr(ch, "channel_kind", "vehicle") != "ped"]
            ped = [ch for ch in channels if getattr(ch, "channel_kind", "vehicle") == "ped"]
            if vehicle:
                green = next((ch.output_id for ch in vehicle if ch.indication == "green"), "-")
                yellow = next((ch.output_id for ch in vehicle if ch.indication == "yellow"), "-")
                red = next((ch.output_id for ch in vehicle if ch.indication == "red"), "-")
                approach = vehicle[0].approach or "?"
                group = vehicle[0].movement_group or "?"
                head = vehicle[0].head_type or "?"
                rows.append(f"Ph{phase} {approach:<2} {group:<6} {head:<5} G:{green:<7} Y:{yellow:<7} R:{red}")
            if ped:
                green = next((ch.output_id for ch in ped if ch.indication == "green"), "-")
                yellow = next((ch.output_id for ch in ped if ch.indication == "yellow"), "-")
                red = next((ch.output_id for ch in ped if ch.indication == "red"), "-")
                rows.append(f"Ph{phase} ped    ped   ped   G:{green:<7} Y:{yellow:<7} R:{red}")
        return rows


def format_energized_panel(
    wiring: WiringTable,
    phase_states: Dict[int, SignalState],
    ped_states: Dict[int, SignalState] | None = None,
) -> str:
    outputs = wiring.energized_outputs(phase_states, ped_states=ped_states)
    if not outputs:
        return "  (none - all red or plan idle)"
    lines = []
    by_id = {ch.output_id: ch for ch in wiring._channels}
    for out in outputs:
        channel = by_id.get(out.output_id)
        terminal = getattr(channel, "field_terminal", "") if channel else ""
        terminal_bit = f" FT:{terminal}" if terminal else ""
        lines.append(
            f"  ON: {out.output_id}{terminal_bit} {out.label} [{out.wsdot_ref}]"
        )
    return "\n".join(lines)


def format_wiring_summary_panel(wiring: WiringTable) -> str:
    lines = ["Wiring summary:"]
    lines.append("  By phase:")
    for row in wiring.summary_rows():
        lines.append(f"    {row}")

    lines.append("  By approach:")
    for approach, channels in sorted(wiring.channels_by_approach().items()):
        labels = ", ".join(f"P{ch.phase}:{ch.indication[0].upper()}" for ch in channels)
        lines.append(f"    {approach}: {labels}")

    lines.append("  By head type:")
    for head_type, channels in sorted(wiring.channels_by_head_type().items()):
        lines.append(f"    {head_type}: {len(channels)} channels")

    return "\n".join(lines)
