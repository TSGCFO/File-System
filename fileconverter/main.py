"""
Main entry point for the FileConverter package when run as a module.

Usage:
    python -m fileconverter [args]
    
This module provides both CLI and GUI entry points. If no arguments are
provided, it launches the GUI. Otherwise, it passes arguments to the CLI.
"""

import sys
from pathlib import Path


def launch_gui():
    """Launch the FileConverter GUI application."""
    try:
        from fileconverter.gui.main_window import MainWindow
        from PyQt6.QtWidgets import QApplication
        
        app = QApplication(sys.argv)
        app.setApplicationName("FileConverter")
        app.setOrganizationName("TSG Fulfillment")
        app.setOrganizationDomain("tsgfulfillment.com")
        
        window = MainWindow()
        window.show()
        
        sys.exit(app.exec())
    except ImportError:
        print("Error: GUI dependencies not installed. Install with 'pip install fileconverter[gui]'")
        sys.exit(1)


def main():
    """Main entry point for the FileConverter package."""
    if len(sys.argv) <= 1:
        # No arguments provided, launch GUI
        launch_gui()
    else:
        # Arguments provided, pass to CLI
        from fileconverter.cli import main as cli_main
        cli_main()


if __name__ == "__main__":
    main()
