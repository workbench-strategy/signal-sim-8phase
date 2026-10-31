"""Timing plan runner with green, yellow, and all-red sub-phases."""

from __future__ import annotations

from typing import Optional, Set

from src.controller.dual_ring import DualRingController
from src.controller.models import ControllerSnapshot, RingPositions, StepPhase
from src.controller.outputs import ped_states_for_step, phase_states_for_step
from src.data.loader import TimingStep, Wsdot8PhaseConfig


class TimingPlanRunner:
    def __init__(self, config: Wsdot8PhaseConfig) -> None:
        self._config = config
        self._dual_ring = DualRingController(config)
        self._step_index = 0
        self._step_phase = StepPhase.ALL_RED
        self._elapsed_in_phase = 0
        self._yellow_phases: Set[int] = set()
        self._active_greens: Set[int] = set()
        self._plan_finished = False
        self._total_elapsed = 0

    def reset(self) -> None:
        self._step_index = 0
        self._step_phase = StepPhase.ALL_RED
        self._elapsed_in_phase = 0
        self._yellow_phases = set()
        self._active_greens = set()
        self._plan_finished = False
        self._total_elapsed = 0

    @property
    def plan_finished(self) -> bool:
        return self._plan_finished

    def current_step(self) -> Optional[TimingStep]:
        if self._step_index >= len(self._config.timing_steps):
            return None
        return self._config.timing_steps[self._step_index]

    def snapshot(self) -> ControllerSnapshot:
        step = self.current_step()
        if step is None or self._plan_finished:
            states = phase_states_for_step(
                self._config, StepPhase.ALL_RED, set(), set()
            )
            ped_states = ped_states_for_step(StepPhase.ALL_RED, set(), set())
            return ControllerSnapshot(
                step_index=max(0, self._step_index - 1),
                step_label="Plan complete",
                step_phase=StepPhase.FINISHED,
                elapsed_s=self._total_elapsed,
                phase_in_step_total_s=0,
                phase_in_step_remaining_s=0,
                ring_positions=RingPositions(None, None),
                barrier_status=self._dual_ring.barrier_status(set()),
                phase_states=states,
                active_greens=set(),
                plan_finished=True,
                ped_states=ped_states,
            )

        greens = self._active_greens if self._step_phase == StepPhase.GREEN else set()
        rings = self._dual_ring.ring_positions(greens)
        barriers = self._dual_ring.barrier_status(greens)
        remaining = self._remaining_seconds(step)
        total = step.green_time_s + step.yellow_clearance_s + step.all_red_s
        states = phase_states_for_step(
            self._config,
            self._step_phase,
            self._active_greens,
            self._yellow_phases,
        )
        ped_states = ped_states_for_step(
            self._step_phase,
            self._active_greens,
            self._yellow_phases,
        )

        return ControllerSnapshot(
            step_index=self._step_index,
            step_label=step.label,
            step_phase=self._step_phase,
            elapsed_s=self._total_elapsed,
            phase_in_step_total_s=total,
            phase_in_step_remaining_s=remaining,
            ring_positions=rings,
            barrier_status=barriers,
            phase_states=states,
            active_greens=set(self._active_greens),
            plan_finished=False,
            ped_states=ped_states,
        )

    def tick(self) -> ControllerSnapshot:
        if self._plan_finished:
            return self.snapshot()

        step = self.current_step()
        if step is None:
            self._plan_finished = True
            return self.snapshot()

        self._total_elapsed += 1
        self._elapsed_in_phase += 1

        if self._step_phase == StepPhase.ALL_RED:
            if self._elapsed_in_phase >= step.all_red_s:
                self._begin_green(step)
        elif self._step_phase == StepPhase.GREEN:
            if self._elapsed_in_phase >= step.green_time_s:
                self._begin_yellow(step)
        elif self._step_phase == StepPhase.YELLOW:
            if self._elapsed_in_phase >= step.yellow_clearance_s:
                self._advance_after_step()

        return self.snapshot()

    def _remaining_seconds(self, step: TimingStep) -> int:
        if self._step_phase == StepPhase.GREEN:
            return max(0, step.green_time_s - self._elapsed_in_phase)
        if self._step_phase == StepPhase.YELLOW:
            return max(0, step.yellow_clearance_s - self._elapsed_in_phase)
        if self._step_phase == StepPhase.ALL_RED:
            return max(0, step.all_red_s - self._elapsed_in_phase)
        return 0

    def _begin_green(self, step: TimingStep) -> None:
        greens = set(step.greens)
        self._dual_ring.validate_greens(greens)
        self._active_greens = greens
        self._yellow_phases = set()
        self._step_phase = StepPhase.GREEN
        self._elapsed_in_phase = 0

    def _begin_yellow(self, step: TimingStep) -> None:
        self._yellow_phases = set(step.greens)
        self._active_greens = set()
        self._step_phase = StepPhase.YELLOW
        self._elapsed_in_phase = 0

    def _advance_after_step(self) -> None:
        self._step_index += 1
        self._active_greens = set()
        self._yellow_phases = set()
        if self._step_index >= len(self._config.timing_steps):
            self._plan_finished = True
            self._step_phase = StepPhase.FINISHED
        else:
            self._step_phase = StepPhase.ALL_RED
            self._elapsed_in_phase = 0
