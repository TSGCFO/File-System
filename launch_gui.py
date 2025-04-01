#!/usr/bin/env python3
"""
FileConverter GUI Launcher Script

This script directly launches the FileConverter GUI without requiring installation.
It's a workaround for users who have issues with the standard installation process.

Usage:
    python launch_gui.py
"""

import os
import sys
import importlib.util
from pathlib import Path

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f" {text}")
    print("=" * 70)

def ensure_dependencies():
    """Ensure all required dependencies are installed."""
    try:
        import PyQt6
        print("✓ PyQt6 is installed")
        return True
    except ImportError:
        print("✗ PyQt6 is not installed")
        print("Please install PyQt6 with: pip install PyQt6")
        return False

def generate_icon():
    """Generate the application icon if needed."""
    try:
        from fileconverter.gui.resources.icon_generator import generate_icon as gen_icon
        icon_path = gen_icon()
        if icon_path:
            print(f"✓ Icon is available at {icon_path}")
        return True
    except Exception as e:
        print(f"Warning: Could not generate icon: {e}")
        print("The application will use default system icons")
        return True  # Not critical, can continue

def launch_gui():
    """Launch the FileConverter GUI."""
    try:
        from fileconverter.main import launch_gui as run_gui
        print("Launching FileConverter GUI...")
        return run_gui()
    except ImportError as e:
        print(f"Error importing launch_gui: {e}")
        return 1
    except Exception as e:
        print(f"Error launching GUI: {e}")
        return 1

def main():
    """Main function."""
    print_header("FileConverter GUI Launcher")
    
    # Add project root to sys.path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    # Check for dependencies
    if not ensure_dependencies():
        return 1
    
    # Generate icon if needed
    generate_icon()
    
    # Launch the GUI
    return launch_gui()

if __name__ == "__main__":
    sys.exit(main())