#!/usr/bin/env python
# src/cli/main.py

import sys
import argparse
from typing import Optional
import os

# Add the scripts directory to the path so we can import signal_sim_engine
scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts')
sys.path.insert(0, scripts_dir)

try:
    from signal_sim_engine import (
        print_intersection_layout, 
        demonstrate_layouts,
        simulate_cycle,
        SignalState
    )
except ImportError:
    print("Error: Could not import signal_sim_engine. Make sure you're running from the project root.")
    sys.exit(1)


def main():
    """Main CLI entry point for the signal simulation system."""
    parser = argparse.ArgumentParser(
        description="GIS-Based Signal Simulation with 8-Phase NEMA Controller",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show signal layout with compact descriptions
  python src/cli/main.py layout
  
  # Show signal layout with full descriptions  
  python src/cli/main.py layout --full
  
  # Show signal layout with example states
  python src/cli/main.py layout --states
  
  # Run signal cycle simulation
  python src/cli/main.py simulate
  
  # Show all demonstration layouts
  python src/cli/main.py demo
"""
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Layout command
    layout_parser = subparsers.add_parser('layout', help='Display intersection signal layout')
    layout_parser.add_argument(
        '--full', 
        action='store_true',
        help='Use full phase descriptions (may wrap on narrow terminals)'
    )
    layout_parser.add_argument(
        '--states',
        action='store_true', 
        help='Show example signal states'
    )
    
    # Simulate command
    simulate_parser = subparsers.add_parser('simulate', help='Run signal cycle simulation')
    
    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Show all layout demonstrations')
    
    args = parser.parse_args()
    
    if args.command == 'layout':
        compact = not args.full
        states = None
        
        if args.states:
            # Example states showing east-west green
            states = {
                1: SignalState.RED,
                2: SignalState.RED,
                3: SignalState.GREEN,
                4: SignalState.GREEN,
                5: SignalState.RED,
                6: SignalState.RED,
                7: SignalState.GREEN,
                8: SignalState.GREEN,
            }
        
        print_intersection_layout(compact=compact, states=states)
        
    elif args.command == 'simulate':
        simulate_cycle()
        
    elif args.command == 'demo':
        demonstrate_layouts()
        
    else:
        # Default action when no command is specified
        print("Signal Sim 8-Phase CLI")
        print("\nShowing compact intersection layout:")
        print_intersection_layout(compact=True)
        print("\nUse 'python src/cli/main.py --help' for more options.")


if __name__ == "__main__":
    main()
