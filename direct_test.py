#!/usr/bin/env python3
"""
Direct test script for FileConverter GUI launch mechanisms.

This script directly tests the GUI entry points without requiring installation.
It verifies that the functions are correctly defined and can be imported.
"""

import os
import sys
import importlib
import traceback
from pathlib import Path

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f" {text}")
    print("=" * 70)

def test_import_and_functionality():
    """Test importing the main module and GUI functionality."""
    print_header("Testing Module Imports")
    
    success = True
    
    # Test 1: Import main module and check for launch_gui function
    try:
        from fileconverter import main
        print("✓ Successfully imported fileconverter.main")
        
        if hasattr(main, 'launch_gui'):
            print("✓ launch_gui function exists in fileconverter.main")
        else:
            print("✗ launch_gui function NOT found in fileconverter.main")
            success = False
    except ImportError as e:
        print(f"✗ Failed to import fileconverter.main: {e}")
        traceback.print_exc()
        success = False
    
    # Test 2: Check __main__.py for run_gui function
    try:
        sys.path.insert(0, os.path.abspath("."))
        from fileconverter import __main__
        print("✓ Successfully imported fileconverter.__main__")
        
        if hasattr(__main__, 'run_gui'):
            print("✓ run_gui function exists in fileconverter.__main__")
        else:
            print("✗ run_gui function NOT found in fileconverter.__main__")
            success = False
    except ImportError as e:
        print(f"✗ Failed to import fileconverter.__main__: {e}")
        traceback.print_exc()
        success = False
    
    # Test 3: Generate icon
    print_header("Testing Icon Generator")
    try:
        from fileconverter.gui.resources.icon_generator import generate_icon
        print("✓ Successfully imported icon_generator")
        
        icon_path = generate_icon()
        if icon_path and os.path.exists(icon_path):
            print(f"✓ Icon generated successfully at {icon_path}")
        else:
            print(f"✗ Icon generation failed or file not found")
            success = False
    except ImportError as e:
        print(f"✗ Failed to import icon_generator: {e}")
        traceback.print_exc()
        success = False
    except Exception as e:
        print(f"✗ Error generating icon: {e}")
        traceback.print_exc()
        success = False
    
    return success

def main():
    """Main function."""
    print("FileConverter Direct Test Script")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    success = test_import_and_functionality()
    
    print_header("Test Results")
    if success:
        print("✓ All tests PASSED")
        return 0
    else:
        print("✗ Some tests FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())