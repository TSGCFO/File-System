"""
Main entry point for the FileConverter package.

This module provides the main function that serves as the entry point
for both the CLI and GUI interfaces of the FileConverter package.
"""

import sys
import logging
from pathlib import Path
from typing import List, Optional

from fileconverter.cli import main as cli_main
from fileconverter.version import __version__
from fileconverter.utils.logging_utils import get_logger

logger = get_logger(__name__)


def launch_gui() -> int:
    """Launch the FileConverter GUI application.
    
    Returns:
        Exit code, 0 for success or non-zero for error.
    """
    try:
        # Import GUI dependencies only when needed
        from fileconverter.gui.main_window import MainWindow
        from PyQt6.QtWidgets import QApplication
        
        app = QApplication(sys.argv)
        app.setApplicationName("FileConverter")
        app.setOrganizationName("TSG Fulfillment")
        app.setOrganizationDomain("tsgfulfillment.com")
        
        window = MainWindow()
        window.show()
        
        return app.exec()
    
    except ImportError as e:
        logger.error(f"GUI dependencies not installed: {str(e)}")
        print("Error: GUI dependencies not installed.")
        print("Please install with 'pip install fileconverter[gui]' or 'pip install PyQt6 PyQt6-QScintilla'")
        return 1
    except Exception as e:
        logger.exception("Error launching GUI")
        print(f"Error launching GUI: {str(e)}")
        return 1


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the FileConverter package.
    
    Args:
        argv: Command line arguments. If None, sys.argv is used.
    
    Returns:
        Exit code, 0 for success or non-zero for error.
    """
    if argv is None:
        argv = sys.argv[1:]
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # If no arguments and not being run as a script directly,
    # or if --gui/-g flag is present, launch GUI
    if (not argv and not sys.argv[0].endswith('fileconverter')) or '--gui' in argv or '-g' in argv:
        # Remove GUI flags if present to avoid confusion in CLI processing
        if '--gui' in argv:
            argv.remove('--gui')
        if '-g' in argv:
            argv.remove('-g')
        
        return launch_gui()
    
    # Otherwise, process as CLI command
    try:
        return cli_main(argv)
    except Exception as e:
        logger.exception("Error in CLI")
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
