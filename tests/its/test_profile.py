"""Tests for device profile loading."""

from __future__ import annotations

from pathlib import Path

import pytest

from its.profile import device_profile_from_dict, load_device_profile


def test_load_signals_demo_profile():
    root = Path(__file__).resolve().parents[2]
    profile = load_device_profile(root / "profiles" / "examples" / "signals_demo.json")
    assert profile.domain == "signals"
    assert profile.supports("get_phase_status")
    assert profile.endpoint.startswith("192.0.2.")


def test_missing_required_field():
    with pytest.raises(ValueError):
        device_profile_from_dict({"profile_id": "x"})
