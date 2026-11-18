"""
Shadow-mode demo across the ITS platform.

Run::

    PYTHONPATH=src python -m its
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from its.domains.signals_adapter import SignalsNtcipAdapter  # noqa: E402
from its.policies.phase_green_monitor import PhaseGreenMonitorPolicy  # noqa: E402
from its.profile import load_device_profile  # noqa: E402
from its.shadow import ShadowBus  # noqa: E402


async def run_shadow_demo() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    log = logging.getLogger("its.demo")

    repo_root = Path(__file__).resolve().parents[2]
    profile_path = repo_root / "profiles" / "examples" / "signals_demo.json"
    profile = load_device_profile(profile_path)

    adapter = SignalsNtcipAdapter()
    policy = PhaseGreenMonitorPolicy(expected_greens=(1, 6))  # deliberate mismatch
    shadow = ShadowBus()

    try:
        health = await adapter.probe(profile)
        log.info("probe ok=%s detail=%s", health.ok, health.detail)

        observation = await policy.observe(adapter, profile)
        log.info("status: %s", observation.status.summary)

        recommendations = await policy.evaluate(observation)
        shadow.record_many(recommendations)

        if not recommendations:
            log.info("No recommendations (observation matched policy).")
        else:
            for item in recommendations:
                log.info(
                    "RECOMMEND intent=%s reason=%s payload=%s",
                    item.intent,
                    item.reason,
                    item.payload,
                )
        log.info("Shadow records: %s", len(shadow.records))
        return 0
    finally:
        await adapter.close()


def main() -> None:
    raise SystemExit(asyncio.run(run_shadow_demo()))


if __name__ == "__main__":
    main()
