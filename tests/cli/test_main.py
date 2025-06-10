# tests/cli/test_main.py
def test_main(capsys):
    from src.cli.main import main
    main()
    captured = capsys.readouterr()
    assert "Signal Sim 8-Phase CLI entry point." in captured.out
