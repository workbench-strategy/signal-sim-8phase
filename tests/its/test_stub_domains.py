"""Smoke tests for VMS / RWIS / CCTV stubs."""

from __future__ import annotations

import pytest

from its.domains.cctv_adapter import CctvStubAdapter
from its.domains.rwis_adapter import RwisStubAdapter
from its.domains.vms_adapter import VmsStubAdapter
from its.profile import load_device_profile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.asyncio
async def test_vms_stub():
    profile = load_device_profile(ROOT / "profiles" / "examples" / "vms_demo.json")
    adapter = VmsStubAdapter()
    status = await adapter.get_status(profile)
    assert "message" in status.data
    result = await adapter.apply(
        profile, "post_message", message="FOG AHEAD", dry_run=True
    )
    assert result.dry_run is True


@pytest.mark.asyncio
async def test_rwis_stub():
    profile = load_device_profile(ROOT / "profiles" / "examples" / "rwis_demo.json")
    status = await RwisStubAdapter().get_status(profile)
    assert "air_temp_c" in status.data


@pytest.mark.asyncio
async def test_cctv_stub():
    profile = load_device_profile(ROOT / "profiles" / "examples" / "cctv_demo.json")
    adapter = CctvStubAdapter()
    status = await adapter.get_status(profile)
    assert "presets" in status.data
