"""Tests for shadow bus and example policy."""

from __future__ import annotations

import pytest

from its.domains.signals_adapter import SignalsNtcipAdapter
from its.events import Recommendation
from its.policies.phase_green_monitor import PhaseGreenMonitorPolicy
from its.profile import device_profile_from_dict
from its.shadow import ShadowBus


def _demo_profile():
    return device_profile_from_dict(
        {
            "profile_id": "test.signals",
            "domain": "signals",
            "display_name": "Test",
            "protocol": "ntcip",
            "endpoint": "192.0.2.10",
            "capabilities": ["get_phase_status"],
        }
    )


@pytest.mark.asyncio
async def test_shadow_bus_records():
    bus = ShadowBus()
    rec = Recommendation(intent="x", reason="y", profile_id="p")
    bus.record(rec)
    assert len(bus.records) == 1
    assert bus.to_dicts()[0]["intent"] == "x"


@pytest.mark.asyncio
async def test_phase_green_monitor_recommends_on_mismatch():
    adapter = SignalsNtcipAdapter()
    policy = PhaseGreenMonitorPolicy(expected_greens=(1, 6))
    profile = _demo_profile()
    try:
        observation = await policy.observe(adapter, profile)
        recs = await policy.evaluate(observation)
        assert len(recs) == 1
        assert recs[0].intent == "operator_verify_intersection"
    finally:
        await adapter.close()


@pytest.mark.asyncio
async def test_phase_green_monitor_silent_when_match():
    adapter = SignalsNtcipAdapter()
    policy = PhaseGreenMonitorPolicy(expected_greens=(2, 5))
    profile = _demo_profile()
    try:
        observation = await policy.observe(adapter, profile)
        recs = await policy.evaluate(observation)
        assert recs == []
    finally:
        await adapter.close()
