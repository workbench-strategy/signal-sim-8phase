import pytest

from src.controller.dual_ring import DualRingController, DualRingError
from src.data.loader import load_config


def test_valid_dm1330_channel_c():
    config = load_config()
    dr = DualRingController(config)
    dr.validate_greens([1, 6])


def test_valid_nb_approach_pair():
    config = load_config()
    dr = DualRingController(config)
    dr.validate_greens([2, 5])


def test_valid_sb_approach_pair():
    config = load_config()
    dr = DualRingController(config)
    dr.validate_greens([1, 6])


def test_rejects_two_phases_same_ring():
    config = load_config()
    dr = DualRingController(config)
    with pytest.raises(DualRingError, match="Ring 1"):
        dr.validate_greens([1, 2])


def test_rejects_invalid_concurrent_group():
    config = load_config()
    dr = DualRingController(config)
    with pytest.raises(DualRingError, match="concurrent group"):
        dr.validate_greens([2, 8])


def test_ring_positions_major_through():
    config = load_config()
    dr = DualRingController(config)
    pos = dr.ring_positions([2, 6])
    assert pos.ring_1_phase == 2
    assert pos.ring_2_phase == 6
