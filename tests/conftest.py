"""Pytest configuration."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="module")
def sample_fixture():
    return "sample"


@pytest.fixture
def mini_config_path(tmp_path):
    """Minimal 2-step timing plan for fast CLI/controller tests."""
    src = ROOT / "data" / "wsdot_8phase.json"
    dst = tmp_path / "mini.json"
    data = json.loads(src.read_text(encoding="utf-8"))
    data["timing_plan"]["steps"] = [
        {
            "label": "Mini major lefts",
            "greens": [1, 5],
            "green_time_s": 1,
            "yellow_clearance_s": 1,
            "all_red_s": 1,
        },
        {
            "label": "Mini major thru",
            "greens": [2, 6],
            "green_time_s": 1,
            "yellow_clearance_s": 1,
            "all_red_s": 1,
        },
    ]
    dst.write_text(json.dumps(data), encoding="utf-8")
    return dst
