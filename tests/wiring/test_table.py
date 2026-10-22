from src.controller.models import SignalState
from src.data.loader import load_config
from src.wiring.table import WiringTable


def test_energized_green_outputs():
    config = load_config()
    table = WiringTable.from_config(config)
    states = {p: SignalState.RED for p in config.phase_details}
    states[2] = SignalState.GREEN
    states[5] = SignalState.GREEN
    outputs = table.energized_outputs(states)
    phases = {o.phase for o in outputs}
    assert 2 in phases
    assert 5 in phases
    assert all(o.indication == "green" for o in outputs if o.phase in (2, 5))


def test_grouped_channels_support_first_layer_queries():
    config = load_config()
    table = WiringTable.from_config(config)

    by_phase = table.channels_by_phase()
    by_approach = table.channels_by_approach()
    by_head_type = table.channels_by_head_type()

    assert 2 in by_phase and len(by_phase[2]) == 3
    assert by_approach["NB"]
    assert by_approach["SB"]
    assert by_approach["WB"]
    assert by_approach["EB"]
    assert "ball" in by_head_type
    assert "arrow" in by_head_type


def test_summary_rows_include_compact_phase_table():
    config = load_config()
    table = WiringTable.from_config(config)
    rows = table.summary_rows()
    assert len(rows) == 8
    assert any("G:OUT" in row for row in rows)
    assert any("Y:OUT" in row for row in rows)
    assert any("R:OUT" in row for row in rows)
    assert any("arrow" in row for row in rows)
    assert any("ball" in row for row in rows)
