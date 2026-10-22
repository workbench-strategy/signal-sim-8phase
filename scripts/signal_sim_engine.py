# signal_sim_engine.py - compatibility shim (WSDOT DM 1330 phasing). Use src.cli.main for demo.

from src.controller.models import SignalState
from src.controller.timing_plan import TimingPlanRunner
from src.data.loader import load_config
from src.display.intersection import print_intersection_layout, get_leg_phase_layout
from src.display.demo_panel import print_demo_frame
from src.wiring.table import WiringTable


def demonstrate_layouts() -> None:
    """Show layout variants (static, no controller)."""
    from src.controller.models import SignalState as SS

    print("=== Signal Indication Layout Demo ===")
    print("\n1. Compact Layout:")
    print_intersection_layout(compact=True)
    print("\n2. Layout with example states (DM1330 minor through 4+8):")
    example = {
        1: SS.RED, 2: SS.RED, 3: SS.RED, 4: SS.GREEN,
        5: SS.RED, 6: SS.RED, 7: SS.RED, 8: SS.GREEN,
    }
    print_intersection_layout(compact=True, states=example)


def simulate_cycle() -> None:
    """Run one pass of the timing plan with demo frames."""
    config = load_config()
    runner = TimingPlanRunner(config)
    wiring = WiringTable.from_config(config)
    runner.reset()
    print_demo_frame(runner.snapshot(), wiring, config=config)
    max_ticks = sum(
        s.green_time_s + s.yellow_clearance_s + s.all_red_s
        for s in config.timing_steps
    ) + 50
    for _ in range(max_ticks):
        if runner.plan_finished:
            break
        runner.tick()
        print_demo_frame(runner.snapshot(), wiring, config=config)
    print("Cycle complete.")


__all__ = [
    "SignalState",
    "print_intersection_layout",
    "get_leg_phase_layout",
    "demonstrate_layouts",
    "simulate_cycle",
    "TimingPlanRunner",
    "WiringTable",
    "print_demo_frame",
]

if __name__ == "__main__":
    demonstrate_layouts()
    simulate_cycle()
