#!/usr/bin/env python3
"""
Main entry point for the FileConverter package.

This module is executed when the package is run directly with 'python -m fileconverter'.
It also provides direct access to the GUI functionality when executed as 'fileconverter-gui'.
"""

import sys
from fileconverter.main import main, launch_gui

def run_gui():
    """Entry point for the GUI when launched via fileconverter-gui command."""
    return launch_gui()

if __name__ == "__main__":
    # Check if being run as fileconverter-gui
    if sys.argv[0].endswith('fileconverter-gui'):
        sys.exit(launch_gui())
    else:
        sys.exit(main())
