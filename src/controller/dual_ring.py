"""NEMA dual-ring validation and ring/barrier state."""

from __future__ import annotations

from typing import Iterable, List, Optional, Set, Tuple

from src.controller.models import BarrierStatus, RingPositions
from src.data.loader import ConcurrentGroup, Wsdot8PhaseConfig


class DualRingError(Exception):
    """Invalid concurrent phase or barrier violation."""


class DualRingController:
    def __init__(self, config: Wsdot8PhaseConfig) -> None:
        self._config = config
        self._ring_1 = set(config.ring_1)
        self._ring_2 = set(config.ring_2)

    def validate_greens(self, greens: Iterable[int]) -> None:
        green_set = set(greens)
        if not green_set:
            return

        self._validate_one_per_ring(green_set)
        self._validate_concurrent_group(green_set)
        self._validate_barriers(green_set)

    def ring_positions(self, greens: Iterable[int]) -> RingPositions:
        green_set = set(greens)
        r1 = next((p for p in green_set if p in self._ring_1), None)
        r2 = next((p for p in green_set if p in self._ring_2), None)
        return RingPositions(ring_1_phase=r1, ring_2_phase=r2)

    def barrier_status(self, greens: Iterable[int]) -> BarrierStatus:
        green_set = set(greens)
        r1_phases = {p for p in green_set if p in self._ring_1}
        r2_phases = {p for p in green_set if p in self._ring_2}

        # Barrier 2|3: closed if both sides of barrier could be active (simplified:
        # closed when ring has greens on both sides of split)
        b23 = self._barrier_engaged(r1_phases, low_phases={1, 2}, high_phases={3, 4})
        b67 = self._barrier_engaged(r2_phases, low_phases={5, 6}, high_phases={7, 8})
        return BarrierStatus(barrier_23_closed=b23, barrier_67_closed=b67)

    @staticmethod
    def _barrier_engaged(
        ring_phases: Set[int],
        low_phases: Set[int],
        high_phases: Set[int],
    ) -> bool:
        if not ring_phases:
            return False
        has_low = bool(ring_phases & low_phases)
        has_high = bool(ring_phases & high_phases)
        return has_low and has_high

    def _validate_one_per_ring(self, greens: Set[int]) -> None:
        r1_count = sum(1 for p in greens if p in self._ring_1)
        r2_count = sum(1 for p in greens if p in self._ring_2)
        if r1_count > 1:
            raise DualRingError(
                f"Ring 1 allows one green phase; got {r1_count}: "
                f"{sorted(p for p in greens if p in self._ring_1)}"
            )
        if r2_count > 1:
            raise DualRingError(
                f"Ring 2 allows one green phase; got {r2_count}: "
                f"{sorted(p for p in greens if p in self._ring_2)}"
            )

    def _validate_concurrent_group(self, greens: Set[int]) -> None:
        for group in self._config.concurrent_groups:
            if greens <= set(group.phases):
                return
        allowed = [list(g.phases) for g in self._config.concurrent_groups]
        raise DualRingError(
            f"Greens {sorted(greens)} are not a valid concurrent group. "
            f"Allowed: {allowed}"
        )

    def _validate_barriers(self, greens: Set[int]) -> None:
        r1 = {p for p in greens if p in self._ring_1}
        r2 = {p for p in greens if p in self._ring_2}
        if self._barrier_engaged(r1, {1, 2}, {3, 4}):
            raise DualRingError(
                "Barrier 2|3 violated: cannot run phases on both sides of ring 1 barrier"
            )
        if self._barrier_engaged(r2, {5, 6}, {7, 8}):
            raise DualRingError(
                "Barrier 6|7 violated: cannot run phases on both sides of ring 2 barrier"
            )
