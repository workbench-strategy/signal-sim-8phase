from src.controller.models import SignalState, StepPhase
from src.controller.outputs import ped_states_for_step
from src.controller.timing_plan import TimingPlanRunner
from src.data.loader import load_config


def test_ped_walk_follows_through_green():
    states = ped_states_for_step(StepPhase.GREEN, {2, 6}, set())
    assert states[2] == SignalState.GREEN
    assert states[6] == SignalState.GREEN
    assert states[4] == SignalState.RED
    assert states[8] == SignalState.RED


def test_ped_fdw_follows_through_yellow():
    states = ped_states_for_step(StepPhase.YELLOW, set(), {2, 6})
    assert states[2] == SignalState.YELLOW
    assert states[6] == SignalState.YELLOW
    assert states[4] == SignalState.RED


def test_runner_snapshot_includes_ped_states(mini_config_path):
    config = load_config(mini_config_path)
    runner = TimingPlanRunner(config)
    runner.reset()
    # Advance into first green (mini plan greens 1+5 -> no ped walk)
    while runner.snapshot().step_phase != StepPhase.GREEN and not runner.plan_finished:
        runner.tick()
    snap = runner.snapshot()
    assert snap.ped_states
    assert all(state == SignalState.RED for state in snap.ped_states.values())

    # Advance to second step greens 2+6
    while not runner.plan_finished:
        runner.tick()
        snap = runner.snapshot()
        if snap.step_phase == StepPhase.GREEN and snap.active_greens == {2, 6}:
            assert snap.ped_states[2] == SignalState.GREEN
            assert snap.ped_states[6] == SignalState.GREEN
            break
    else:
        raise AssertionError("never reached major thru green with ped walk")
