import pytest

from src.controller.models import StepPhase, SignalState
from src.controller.timing_plan import TimingPlanRunner
from src.data.loader import load_config


def test_runner_reaches_major_left_green(mini_config_path):
    config = load_config(mini_config_path)
    runner = TimingPlanRunner(config)
    runner.tick()
    snap = runner.snapshot()
    assert snap.step_phase == StepPhase.GREEN
    assert snap.active_greens == {1, 5}
    assert snap.phase_states[1] == SignalState.GREEN
    assert snap.phase_states[5] == SignalState.GREEN


def test_runner_completes_mini_plan(mini_config_path):
    config = load_config(mini_config_path)
    runner = TimingPlanRunner(config)
    max_ticks = 30
    for _ in range(max_ticks):
        if runner.plan_finished:
            break
        runner.tick()
    assert runner.plan_finished
