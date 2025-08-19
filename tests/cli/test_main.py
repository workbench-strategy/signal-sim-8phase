# tests/cli/test_main.py
import sys

def test_main(capsys):
    """Test that the main CLI runs and displays the intersection layout."""
    # Save original argv
    original_argv = sys.argv[:]
    try:
        # Set argv to simulate running with no arguments
        sys.argv = ['main.py']
        
        from src.cli.main import main
        main()
        captured = capsys.readouterr()
        
        # Check that the output contains expected elements
        assert "Signal Sim 8-Phase CLI" in captured.out
        assert "[1: NB Left]" in captured.out
        assert "[6: NB Thru]" in captured.out
        assert "intersection layout:" in captured.out
    finally:
        # Restore original argv
        sys.argv = original_argv


def test_layout_command(capsys):
    """Test the layout command."""
    original_argv = sys.argv[:]
    try:
        sys.argv = ['main.py', 'layout']
        
        from src.cli.main import main
        main()
        captured = capsys.readouterr()
        
        # Check that the layout is displayed
        assert "[1: NB Left]" in captured.out
        assert "[7: WB Thru]" in captured.out
    finally:
        sys.argv = original_argv


def test_layout_with_states(capsys):
    """Test the layout command with states."""
    original_argv = sys.argv[:]
    try:
        sys.argv = ['main.py', 'layout', '--states']
        
        from src.cli.main import main
        main()
        captured = capsys.readouterr()
        
        # Check that the layout includes signal states
        assert "(R)" in captured.out  # Red signals
        assert "(G)" in captured.out  # Green signals
    finally:
        sys.argv = original_argv
