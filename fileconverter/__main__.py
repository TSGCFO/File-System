#!/usr/bin/env python3
"""
Main entry point for the fileconverter package.
"""

import sys
import argparse
from fileconverter.cli import main as cli_main
from fileconverter.version import __version__

def main():
    """
    Main entry point function.
    """
    parser = argparse.ArgumentParser(
        description="File Converter - Convert files between various formats"
    )
    parser.add_argument(
        "--version", action="version", version=f"File Converter {__version__}"
    )
    parser.add_argument(
        "--gui", action="store_true", help="Launch the graphical user interface"
    )
    
    args, remaining_args = parser.parse_known_args()
    
    if args.gui:
        try:
            from fileconverter.gui.main_window import start_gui
            sys.exit(start_gui())
        except ImportError:
            print("GUI dependencies not installed. Please install PyQt5.")
            sys.exit(1)
    else:
        sys.exit(cli_main(remaining_args))

if __name__ == "__main__":
    main()
