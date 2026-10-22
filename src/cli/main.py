#!/usr/bin/env python
"""CLI for 8-phase NEMA dual-ring controller demo."""

from __future__ import annotations

import argparse
import os
import sys
import time

# Project root on path for `src` and `scripts` imports
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.controller.models import SignalState, StepPhase
from src.controller.timing_plan import TimingPlanRunner
from src.data.loader import load_config, default_config_path
from src.display.demo_panel import print_demo_frame
from src.display.intersection import print_intersection_layout
from src.display.two_d import collect_animation_snapshots, write_animation_html, apply_plan
from src.wiring.table import WiringTable, format_energized_panel, format_wiring_summary_panel
from src.cli.session import load_runner, save_runner, clear_runner_state


def _cmd_layout(args: argparse.Namespace) -> None:
    states = None
    if args.states:
        # DM1330 minor through step (phases 4 + 8)
        states = {
            1: SignalState.RED,
            2: SignalState.RED,
            3: SignalState.RED,
            4: SignalState.GREEN,
            5: SignalState.RED,
            6: SignalState.RED,
            7: SignalState.RED,
            8: SignalState.GREEN,
        }
    print_intersection_layout(compact=not args.full, states=states)


def _cmd_status(args: argparse.Namespace) -> None:
    runner = load_runner(args.config)
    snap = runner.snapshot()
    print(snap.title_line())
    print(snap.ring_positions.format_panel())
    print(snap.barrier_status.format_panel())
    if snap.plan_finished:
        print("Plan: finished")
    else:
        print(f"Sub-phase: {snap.step_phase.value}")


def _cmd_wiring(args: argparse.Namespace) -> None:
    runner = load_runner(args.config)
    wiring = WiringTable.from_config(load_config(args.config))
    snap = runner.snapshot()
    print(snap.title_line())
    print(format_energized_panel(wiring, snap.phase_states))


def _cmd_wiring_summary(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    wiring = WiringTable.from_config(config)
    print(format_wiring_summary_panel(wiring))


def _cmd_step(args: argparse.Namespace) -> None:
    runner = load_runner(args.config)
    config = load_config(args.config)
    wiring = WiringTable.from_config(config)
    if runner.plan_finished and args.reset:
        runner.reset()
        clear_runner_state()
    if not runner.plan_finished:
        runner.tick()
    print_demo_frame(runner.snapshot(), wiring, config=config)
    save_runner(runner)


def _cmd_run(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    runner = TimingPlanRunner(config)
    wiring = WiringTable.from_config(config)
    runner.reset()
    clear_runner_state()

    print_demo_frame(runner.snapshot(), wiring, config=config)
    sleep_s = 0.0 if args.no_sleep else args.interval

    while not runner.plan_finished:
        runner.tick()
        print_demo_frame(runner.snapshot(), wiring, config=config)
        save_runner(runner)
        if sleep_s > 0:
            time.sleep(sleep_s)

    print("Plan complete.")


def _cmd_animate(args: argparse.Namespace) -> None:
    _cmd_run(args)


def _cmd_animate2d(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    config = apply_plan(config, args.plan)
    snapshots = collect_animation_snapshots(config)
    output = write_animation_html(snapshots, config, args.output, interval_ms=args.interval_ms, plan=args.plan)
    print(f"Wrote 2D animation HTML to {output}")


def _cmd_reset(args: argparse.Namespace) -> None:
    clear_runner_state()
    print("Controller demo state cleared.")


def _cmd_demo(args: argparse.Namespace) -> None:
    from scripts.signal_sim_engine import demonstrate_layouts

    demonstrate_layouts()


def _cmd_simulate(args: argparse.Namespace) -> None:
    _cmd_run(
        argparse.Namespace(
            config=args.config,
            no_sleep=True,
            interval=0,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="8-Phase NEMA dual-ring controller demo (WSDOT-aligned)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/cli/main.py run
  python src/cli/main.py step
  python src/cli/main.py status
  python src/cli/main.py wiring
  python src/cli/main.py layout --states
  python src/cli/main.py reset
""",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to wsdot_8phase.json (default: data/wsdot_8phase.json)",
    )

    sub = parser.add_subparsers(dest="command")

    layout_p = sub.add_parser("layout", help="ASCII intersection layout")
    layout_p.add_argument("--full", action="store_true")
    layout_p.add_argument("--states", action="store_true")

    run_p = sub.add_parser("run", help="Auto-step full timing plan")
    run_p.add_argument(
        "--interval",
        type=float,
        default=0.8,
        help="Seconds between ticks (default 0.8)",
    )
    run_p.add_argument("--no-sleep", action="store_true", help="No pause between steps")

    animate_p = sub.add_parser("animate", help="Animated traffic-signal cycle view")
    animate_p.add_argument(
        "--interval",
        type=float,
        default=0.8,
        help="Seconds between ticks (default 0.8)",
    )
    animate_p.add_argument("--no-sleep", action="store_true", help="No pause between steps")

    animate2d_p = sub.add_parser("animate2d", help="Export a 2D animated intersection view")
    animate2d_p.add_argument(
        "--output",
        type=str,
        default="signal-sim-8phase-2d.html",
        help="Output HTML file (default signal-sim-8phase-2d.html)",
    )
    animate2d_p.add_argument(
        "--interval-ms",
        type=int,
        default=650,
        help="Animation interval in milliseconds (default 650)",
    )
    animate2d_p.add_argument(
        "--plan",
        type=str,
        choices=["lead-lead", "lead-lag"],
        default="lead-lead",
        help="Timing plan: lead-lead (default) or lead-lag",
    )

    step_p = sub.add_parser("step", help="Advance one controller tick")
    step_p.add_argument(
        "--reset",
        action="store_true",
        help="Reset plan before step if already finished",
    )

    sub.add_parser("status", help="Ring/barrier/step status")
    sub.add_parser("wiring", help="Energized cabinet outputs")
    sub.add_parser("wiring-summary", help="Grouped first-layer wiring summary")
    sub.add_parser("reset", help="Clear saved step session state")
    sub.add_parser("demo", help="Static layout demonstrations")
    sub.add_parser("simulate", help="Run full plan with no sleep")

    args = parser.parse_args()
    if args.config:
        args.config = os.path.abspath(args.config)
    else:
        args.config = str(default_config_path())

    if args.command == "layout":
        _cmd_layout(args)
    elif args.command == "run":
        _cmd_run(args)
    elif args.command == "animate":
        _cmd_animate(args)
    elif args.command == "animate2d":
        _cmd_animate2d(args)
    elif args.command == "step":
        _cmd_step(args)
    elif args.command == "status":
        _cmd_status(args)
    elif args.command == "wiring":
        _cmd_wiring(args)
    elif args.command == "wiring-summary":
        _cmd_wiring_summary(args)
    elif args.command == "reset":
        _cmd_reset(args)
    elif args.command == "demo":
        _cmd_demo(args)
    elif args.command == "simulate":
        _cmd_simulate(args)
    else:
        print("Signal Sim 8-Phase CLI (NEMA dual-ring demo)")
        print("\nCompact intersection layout:")
        print_intersection_layout(compact=True)
        print("\nCommands: run, animate, animate2d, step, status, wiring, wiring-summary, layout, demo, reset")
        print("Use: python src/cli/main.py --help")


if __name__ == "__main__":
    main()
