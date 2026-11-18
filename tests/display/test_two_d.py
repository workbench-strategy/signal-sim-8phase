from src.data.loader import load_config
from src.display.two_d import collect_animation_snapshots, render_intersection_svg


def test_render_intersection_svg_contains_geometry(mini_config_path):
    config = load_config(mini_config_path)
    snapshot = collect_animation_snapshots(config)[0]

    svg = render_intersection_svg(snapshot, config)

    assert svg.startswith("<svg")
    assert "4-Leg 8-Phase Signalized Intersection" in svg
    assert "NB Left" in svg
    assert "Controller State" in svg
    assert "data-head-type=\"arrow\"" in svg
    assert "data-head-type=\"ball\"" in svg
    assert ">NB<" in svg
    assert ">SB<" in svg
    assert 'data-ped-phase="2"' in svg
    assert "WALK" in svg or "DW" in svg