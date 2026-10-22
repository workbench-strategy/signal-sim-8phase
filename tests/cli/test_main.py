import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def test_main_default(capsys):
    original_argv = sys.argv[:]
    try:
        sys.argv = ["main.py"]
        from src.cli.main import main
        main()
        captured = capsys.readouterr()
        assert "Signal Sim 8-Phase CLI" in captured.out
        assert "[5: NB Left]" in captured.out
        assert "[2: NB Thru]" in captured.out
        assert "[1: SB Left]" in captured.out
        assert "[6: SB Thru]" in captured.out
    finally:
        sys.argv = original_argv


def test_layout_command(capsys):
    original_argv = sys.argv[:]
    try:
        sys.argv = ["main.py", "layout"]
        from src.cli.main import main
        main()
        captured = capsys.readouterr()
        assert "[5: NB Left]" in captured.out
        assert "[2: NB Thru]" in captured.out
        assert "[1: SB Left]" in captured.out
        assert "[4: WB Thru]" in captured.out
    finally:
        sys.argv = original_argv


def test_layout_with_states(capsys):
    original_argv = sys.argv[:]
    try:
        sys.argv = ["main.py", "layout", "--states"]
        from src.cli.main import main
        main()
        captured = capsys.readouterr()
        assert "(R)" in captured.out
        assert "(G)" in captured.out
    finally:
        sys.argv = original_argv


def test_simulate_no_sleep(capsys, mini_config_path):
    original_argv = sys.argv[:]
    try:
        sys.argv = [
            "main.py",
            "--config",
            str(mini_config_path),
            "simulate",
        ]
        from src.cli.main import main
        main()
        captured = capsys.readouterr()
        assert "Plan complete" in captured.out
        assert "Ring1@" in captured.out
    finally:
        sys.argv = original_argv


def test_step_advances(capsys, mini_config_path, tmp_path, monkeypatch):
    import src.cli.session as session

    state_file = tmp_path / "state.json"
    monkeypatch.setattr(session, "_state_path", lambda: state_file)

    original_argv = sys.argv[:]
    try:
        sys.argv = ["main.py", "reset"]
        from src.cli.main import main
        main()

        sys.argv = [
            "main.py",
            "--config",
            str(mini_config_path),
            "step",
        ]
        main()
        captured = capsys.readouterr()
        assert "Step 1" in captured.out or "Mini" in captured.out
    finally:
        sys.argv = original_argv


def test_animate2d_exports_html(capsys, mini_config_path, tmp_path):
    original_argv = sys.argv[:]
    output = tmp_path / "demo.html"
    try:
        sys.argv = [
            "main.py",
            "--config",
            str(mini_config_path),
            "animate2d",
            "--output",
            str(output),
        ]
        from src.cli.main import main

        main()
        captured = capsys.readouterr()
        assert "Wrote 2D animation HTML" in captured.out
        assert output.exists()
        html = output.read_text(encoding="utf-8")
        assert "<svg" in html
        assert "Signal Sim 8-Phase 2D Animation" in html
    finally:
        sys.argv = original_argv


def test_animate2d_lead_lag_plan(capsys, mini_config_path, tmp_path):
    original_argv = sys.argv[:]
    output = tmp_path / "demo-lag.html"
    try:
        sys.argv = [
            "main.py",
            "--config",
            str(mini_config_path),
            "animate2d",
            "--output",
            str(output),
            "--plan",
            "lead-lag",
        ]
        from src.cli.main import main

        main()
        captured = capsys.readouterr()
        assert "Wrote 2D animation HTML" in captured.out
        assert output.exists()
        html = output.read_text(encoding="utf-8")
        assert 'selected>Plan B: Lead/Lag' in html
    finally:
        sys.argv = original_argv


def test_wiring_summary_command(capsys):
    original_argv = sys.argv[:]
    try:
        sys.argv = ["main.py", "wiring-summary"]
        from src.cli.main import main

        main()
        captured = capsys.readouterr()
        assert "Wiring summary:" in captured.out
        assert "By phase:" in captured.out
        assert "By approach:" in captured.out
        assert "By head type:" in captured.out
    finally:
        sys.argv = original_argv
