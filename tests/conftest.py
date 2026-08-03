# tests/conftest.py
import sys
from pathlib import Path

import pytest

# Ensure src/ is importable even when a tests/ subtree shares a package name.
_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


@pytest.fixture(scope="module")
def sample_fixture():
    return "sample"
