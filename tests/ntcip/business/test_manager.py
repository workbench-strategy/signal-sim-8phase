"""Tests for NtcipManager business facade."""

from __future__ import annotations

import pytest

from ntcip.business.intents import SetSignalTimingPlan
from ntcip.exceptions import BusinessLogicError
from ntcip.factory import create_ntcip_manager


@pytest.mark.asyncio
async def test_get_phase_status_typed_response():
    manager = create_ntcip_manager(demo_data=True)
    try:
        snapshot = await manager.get_phase_status("192.0.2.10")
        assert snapshot.host == "192.0.2.10"
        assert snapshot.green_phases() == [2, 5]
        assert snapshot.summary()[2] == "G"
        assert snapshot.summary()[1] == "R"
    finally:
        await manager.close()


@pytest.mark.asyncio
async def test_get_unit_identity():
    manager = create_ntcip_manager(demo_data=True)
    try:
        identity = await manager.get_unit_identity("192.0.2.10")
        assert identity.unit_id == "ASC-DEMO-001"
        assert identity.unit_location == "Main St & 1st Ave"
    finally:
        await manager.close()


@pytest.mark.asyncio
async def test_set_timing_plan_validation():
    manager = create_ntcip_manager(demo_data=True)
    try:
        with pytest.raises(BusinessLogicError):
            await manager.set_signal_timing_plan(
                SetSignalTimingPlan(host="192.0.2.10", plan_number=0)
            )
    finally:
        await manager.close()


@pytest.mark.asyncio
async def test_set_timing_plan_success():
    manager = create_ntcip_manager(demo_data=True)
    try:
        await manager.set_signal_timing_plan(
            SetSignalTimingPlan(host="192.0.2.10", plan_number=3)
        )
    finally:
        await manager.close()
