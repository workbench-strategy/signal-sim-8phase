from src.data.loader import load_config


def test_phase_sum_rule_major():
    config = load_config()
    assert config.phase_details[2].short == "NB Thru"
    assert config.phase_details[5].short == "NB Left"
    assert 2 + 5 == 7
    assert config.phase_details[6].short == "SB Thru"
    assert config.phase_details[1].short == "SB Left"
    assert 6 + 1 == 7


def test_phase_sum_rule_minor():
    config = load_config()
    assert config.phase_details[4].short == "WB Thru"
    assert config.phase_details[7].short == "WB Left"
    assert 4 + 7 == 11
    assert config.phase_details[8].short == "EB Thru"
    assert config.phase_details[3].short == "EB Left"
    assert 8 + 3 == 11


def test_leg_layout_dm1330():
    config = load_config()
    assert config.leg_layout["north"] == [5, 2]
    assert config.leg_layout["south"] == [1, 6]
    assert config.leg_layout["west"] == [7, 4]
    assert config.leg_layout["east"] == [3, 8]


def test_concurrent_groups_approach_pairs():
    config = load_config()
    groups = [set(g.phases) for g in config.concurrent_groups]
    assert {2, 5} in groups
    assert {1, 6} in groups
    assert {4, 7} in groups
    assert {3, 8} in groups


def test_wiring_channels_include_first_layer_metadata():
    config = load_config()
    channel = next(ch for ch in config.wiring_channels if ch.phase == 2 and ch.indication == "green")
    assert channel.leg == "north"
    assert channel.approach == "NB"
    assert channel.movement_group == "through"
    assert channel.street_role == "major"
    assert channel.head_type == "ball"


def test_wiring_head_type_arrow_for_left_phases():
    config = load_config()
    left_channel = next(ch for ch in config.wiring_channels if ch.phase == 5 and ch.indication == "green")
    assert left_channel.head_type == "arrow"
    assert left_channel.movement_group == "left"
