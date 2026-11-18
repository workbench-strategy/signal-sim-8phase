from src.data.loader import load_config
from src.display.teach import (
    FIELD_TERMINALS,
    build_teach_frame,
    build_teach_sequence,
    field_terminal_for,
)
from src.display.two_d import collect_animation_snapshots, render_animation_html


def test_field_terminals_cover_all_phase_colors():
    for phase in range(1, 9):
        for indication in ("red", "yellow", "green"):
            assert field_terminal_for(phase, indication)
            assert (phase, indication) in FIELD_TERMINALS


def test_teach_pauses_after_yellow_clearance(mini_config_path):
    config = load_config(mini_config_path)
    snapshots = collect_animation_snapshots(config)
    teach = build_teach_sequence(snapshots, config)

    assert teach[0]["pause"] is False
    pause_indexes = [idx for idx, frame in enumerate(teach) if frame["pause"]]
    assert pause_indexes, "expected at least one barrier auto-pause"
    for idx in pause_indexes:
        assert snapshots[idx - 1].step_phase.value == "yellow"
        assert snapshots[idx].step_phase.value == "all_red"
        assert "barrier" in teach[idx]["concept"].lower()


def test_teach_frame_lists_energized_field_terminals():
    config = load_config()
    snapshots = collect_animation_snapshots(config)
    green_idx = next(
        idx
        for idx, snap in enumerate(snapshots)
        if snap.step_phase.value == "green" and snap.active_greens == {2, 6}
    )
    frame = build_teach_frame(snapshots[green_idx], config, snapshots[green_idx - 1])
    assert frame.energized
    vehicle_rows = [row for row in frame.energized if row.get("channel_kind") != "ped"]
    ped_rows = [row for row in frame.energized if row.get("channel_kind") == "ped"]
    assert vehicle_rows
    assert ped_rows
    assert all(row["field_terminal"] for row in vehicle_rows)
    assert any(row["field_terminal"] == "722" for row in ped_rows)  # Ph2 Walk
    assert "output_file_1" in frame.active_assemblies
    assert "controller" in frame.active_assemblies
    assert "detector_test" in frame.active_assemblies
    assert frame.detectors
    assert "WALK" in frame.ped_summary or "P2:WALK" in frame.ped_summary


def test_animate_html_includes_teach_and_cabinet_chrome(mini_config_path):
    config = load_config(mini_config_path)
    snapshots = collect_animation_snapshots(config)
    html = render_animation_html(snapshots, config, plan="lead-lead")

    assert "Teach panel" in html
    assert "Type 332 cabinet (J-80.10)" in html
    assert "Presentation cycle length" in html
    assert "Display tempo only" in html
    assert "Resume after checkpoint" in html
    assert "Output File #1 LX" in html
    assert "Detector Test Panel (J-80.15)" in html
    assert "DET. 1" in html
    assert "extending green" in html
    assert '"pause": true' in html or '"pause":true' in html
