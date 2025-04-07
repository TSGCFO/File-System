#!/usr/bin/env python3
"""
Main module for FileConverter.

This module provides the main entry points for the FileConverter application,
including both command-line and GUI interfaces.
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

def check_dependencies(silent=False):
    """Check for required dependencies before launching the application."""
    try:
        from fileconverter.dependency_manager import detect_missing_dependencies
        
        # Only check critical dependencies for startup
        critical_formats = ["core"]
        if "--gui" in sys.argv or any(arg.startswith("--format=gui") for arg in sys.argv):
            critical_formats.append("gui")
            
        missing_deps = detect_missing_dependencies(critical_formats)
        
        if missing_deps["python"] or missing_deps["external"]:
            if not silent:
                print("Warning: Some dependencies are missing.")
                print("Run 'fileconverter dependencies check' for details or 'fileconverter dependencies install' to fix.")
                
                # Give more specific guidance
                if missing_deps["python"]:
                    print("\nMissing Python packages:")
                    for pkg_name, pkg_info in missing_deps["python"].items():
                        if pkg_info["required"]:
                            print(f"  • {pkg_name} - {pkg_info['purpose']} (REQUIRED)")
                        else:
                            print(f"  • {pkg_name} - {pkg_info['purpose']}")
                
                if missing_deps["external"]:
                    print("\nMissing external tools:")
                    for dep_name, dep_info in missing_deps["external"].items():
                        print(f"  • {dep_info['name']} - {dep_info['purpose']}")
            
            # Return True if any required dependencies are missing
            return any(pkg_info["required"] for pkg_info in missing_deps["python"].values())
        return False
    except ImportError:
        # If the dependency_manager module itself can't be imported,
        # we're probably running from source before installation
        if not silent:
            print("Note: Dependency manager not available. Running in development mode.")
        return False

def setup_logging(verbose=False):
    """Set up logging configuration."""
    log_level = logging.DEBUG if verbose else logging.INFO
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    
    logging.basicConfig(level=log_level, format=log_format)
    
    # Also log to a file in the user's home directory
    user_home = Path.home()
    log_dir = user_home / ".fileconverter" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "fileconverter.log"
    file_handler = logging.FileHandler(log_file, mode="a")
    file_handler.setFormatter(logging.Formatter(log_format))
    
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    
    logger.debug(f"Logging initialized. Log file: {log_file}")

def launch_cli():
    """Launch the command-line interface."""
    from fileconverter.cli import main as cli_main
    return cli_main()

def launch_gui():
    """Launch the graphical user interface."""
    try:
        from fileconverter.gui.main_window import MainWindow
        from PyQt6.QtWidgets import QApplication
        
        logger.debug("Starting GUI application")
        app = QApplication(sys.argv)
        
        # Set application information
        app.setApplicationName("FileConverter")
        app.setOrganizationName("TSG Fulfillment")
        app.setOrganizationDomain("tsgfulfillment.com")
        
        # Create and show the main window
        main_window = MainWindow()
        main_window.show()
        
        # Start the event loop
        return app.exec()
    except ImportError as e:
        logger.error(f"Failed to import GUI components: {e}")
        print(f"Error: Could not launch GUI. {e}")
        print("Make sure PyQt6 is installed (pip install fileconverter[gui]).")
        return 1
    except Exception as e:
        logger.error(f"Error launching GUI: {e}", exc_info=True)
        print(f"Error launching GUI: {e}")
        return 1

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="FileConverter")
    parser.add_argument("--gui", action="store_true", help="Launch the GUI")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--skip-dependency-check", action="store_true", 
                        help="Skip dependency checking (for advanced users)")
    
    # For compatibility with arguments that might be passed to cli.py or gui modules
    args, unknown = parser.parse_known_args()
    return args

def main():
    """Main entry point for the application."""
    args = parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    
    # Check dependencies unless explicitly skipped
    missing_critical = False
    if not args.skip_dependency_check:
        missing_critical = check_dependencies()
        
        if missing_critical:
            # Exit with error if critical dependencies are missing
            print("Error: Critical dependencies are missing. Cannot continue.")
            print("Please install the required dependencies and try again.")
            print("Run 'python -m fileconverter.dependency_manager --install' to install missing dependencies.")
            return 1
    
    # Launch GUI or CLI based on arguments
    if args.gui:
        return launch_gui()
    else:
        return launch_cli()

if __name__ == "__main__":
    sys.exit(main())
