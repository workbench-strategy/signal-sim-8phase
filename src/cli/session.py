"""Persist timing plan runner state between CLI invocations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from src.controller.timing_plan import TimingPlanRunner
from src.data.loader import load_config, default_config_path


def _state_path() -> Path:
    return Path(__file__).resolve().parents[2] / ".controller_demo_state.json"


def save_runner(runner: TimingPlanRunner) -> None:
    data: Dict[str, Any] = {
        "step_index": runner._step_index,
        "step_phase": runner._step_phase.value,
        "elapsed_in_phase": runner._elapsed_in_phase,
        "yellow_phases": sorted(runner._yellow_phases),
        "active_greens": sorted(runner._active_greens),
        "plan_finished": runner._plan_finished,
        "total_elapsed": runner._total_elapsed,
    }
    _state_path().write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_runner(config_path: Optional[Path] = None) -> TimingPlanRunner:
    path = _state_path()
    config = load_config(config_path)
    runner = TimingPlanRunner(config)
    if not path.exists():
        return runner

    from src.controller.models import StepPhase

    data = json.loads(path.read_text(encoding="utf-8"))
    runner._step_index = int(data["step_index"])
    runner._step_phase = StepPhase(data["step_phase"])
    runner._elapsed_in_phase = int(data["elapsed_in_phase"])
    runner._yellow_phases = set(data.get("yellow_phases", []))
    runner._active_greens = set(data.get("active_greens", []))
    runner._plan_finished = bool(data.get("plan_finished", False))
    runner._total_elapsed = int(data.get("total_elapsed", 0))
    return runner


def clear_runner_state() -> None:
    path = _state_path()
    if path.exists():
        path.unlink()
