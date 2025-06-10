# tests/conftest.py
import pytest

@pytest.fixture(scope='module')
def sample_fixture():
    return "sample"
