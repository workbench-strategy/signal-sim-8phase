"""Tests for signals domain adapter."""

from __future__ import annotations

import pytest

from its.domains.signals_adapter import SignalsNtcipAdapter
from its.profile import device_profile_from_dict


@pytest.fixture
def profile():
    return device_profile_from_dict(
        {
            "profile_id": "test.signals",
            "domain": "signals",
            "display_name": "Test ASC",
            "protocol": "ntcip",
            "endpoint": "192.0.2.10",
            "capabilities": ["get_phase_status", "set_timing_plan"],
        }
    )


@pytest.mark.asyncio
async def test_get_status(profile):
    adapter = SignalsNtcipAdapter()
    try:
        status = await adapter.get_status(profile)
        assert status.domain == "signals"
        assert status.data["green_phases"] == [2, 5]
    finally:
        await adapter.close()


@pytest.mark.asyncio
async def test_apply_dry_run_default(profile):
    adapter = SignalsNtcipAdapter()
    try:
        result = await adapter.apply(
            profile, "set_timing_plan", plan_number=3, dry_run=True
        )
        assert result.dry_run is True
        assert result.success is True
    finally:
        await adapter.close()
