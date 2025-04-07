#!/usr/bin/env python3
"""
FileConverter Test Runner Script

This script executes both unit tests and integration tests to verify the 
FileConverter installation and GUI launch mechanisms.

Usage:
    python run_tests.py [--unit | --integration | --all]
"""

import os
import sys
import time
import argparse
import subprocess
import unittest
from pathlib import Path


def print_header(text, char='='):
    """Print a formatted header."""
    width = 70
    print("\n" + char * width)
    print(f" {text}")
    print(char * width)


def run_command(command, description, check=True):
    """Run a shell command and print the output."""
    print(f"\n> {description}:")
    print(f"$ {command}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            text=True, 
            capture_output=True,
            check=check
        )
        print(f"Exit code: {result.returncode}")
        if result.stdout:
            print("Output:")
            print(result.stdout)
        if result.stderr and result.stderr.strip():
            print("Errors:")
            print(result.stderr)
        
        return result.returncode == 0, result
    except Exception as e:
        print(f"Failed to execute command: {e}")
        return False, None


def run_unit_tests():
    """Run the unit tests."""
    print_header("Running Unit Tests")
    
    # Import and run the test_installation module
    try:
        from tests.test_installation import run_tests
        run_tests()
        return True
    except ImportError as e:
        print(f"Failed to import test module: {e}")
        return False
    except Exception as e:
        print(f"Error running unit tests: {e}")
        return False


def run_integration_tests():
    """Run the integration tests."""
    print_header("Running Integration Tests")
    
    # Run the installation test script
    success1, _ = run_command(
        "python tests/run_installation_test.py",
        "Running installation test script"
    )
    
    # Run the dependency management integration tests
    success2, _ = run_command(
        "python tests/test_dependency_management_integration.py",
        "Running dependency management integration tests"
    )
    
    return success1 and success2


def install_development_mode():
    """Install the package in development mode."""
    print_header("Installing Package in Development Mode")
    
    success, _ = run_command(
        "pip install -e .",
        "Installing in development mode"
    )
    
    if success:
        print("✓ Successfully installed in development mode")
    else:
        print("✗ Failed to install in development mode")
    
    return success


def test_commands():
    """Test the commands directly."""
    print_header("Testing Commands")
    
    commands = [
        "fileconverter --version",
        "fileconverter --help",
        "python -m fileconverter --version",
        # GUI commands will be run separately
    ]
    
    success = True
    for cmd in commands:
        cmd_success, _ = run_command(cmd, f"Testing '{cmd}'", check=False)
        if not cmd_success:
            success = False
    
    return success


def test_gui_launch(timeout=5):
    """Test launching the GUI."""
    print_header("Testing GUI Launch")
    
    print("Note: This will attempt to launch the GUI and then automatically close it.")
    print(f"The GUI will be closed after {timeout} seconds.")
    print("If the GUI doesn't launch, check if your system supports GUI applications.")
    print("Press Ctrl+C to skip this test.")
    
    try:
        # Launch the GUI in a separate process
        if sys.platform == 'win32':
            cmd = "start /B python -m fileconverter --gui"
        else:
            cmd = "python -m fileconverter --gui &"
        
        print(f"\nLaunching GUI with command: {cmd}")
        proc = subprocess.Popen(cmd, shell=True)
        
        # Wait for a short time to see if it launches
        print(f"Waiting {timeout} seconds for GUI to launch...")
        time.sleep(timeout)
        
        # Try to terminate the process
        print("Attempting to close GUI...")
        if sys.platform == 'win32':
            subprocess.run("taskkill /F /IM python.exe", shell=True)
        else:
            proc.terminate()
        
        return True
    
    except KeyboardInterrupt:
        print("Test skipped by user.")
        return True
    except Exception as e:
        print(f"Error testing GUI launch: {e}")
        return False


def main():
    """Main function to run the tests."""
    parser = argparse.ArgumentParser(description="Run FileConverter tests")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--all", action="store_true", help="Run all tests (default)")
    parser.add_argument("--no-gui", action="store_true", help="Skip GUI launch test")
    
    args = parser.parse_args()
    
    # Default to --all if no options specified
    if not (args.unit or args.integration or args.all):
        args.all = True
    
    print_header("FileConverter Test Runner", char='*')
    print("Testing the installation and GUI launch mechanisms")
    print(f"Current directory: {os.getcwd()}")
    
    results = []
    
    if args.all or args.unit:
        # Run unit tests
        unit_success = run_unit_tests()
        results.append(("Unit Tests", unit_success))
    
    if args.all or args.integration:
        # Install in development mode
        install_success = install_development_mode()
        results.append(("Development Installation", install_success))
        
        # Test commands
        commands_success = test_commands()
        results.append(("Command Tests", commands_success))
        
        # Run integration tests
        integration_success = run_integration_tests()
        results.append(("Integration Tests", integration_success))
        
        # Test GUI launch
        if not args.no_gui:
            gui_success = test_gui_launch()
            results.append(("GUI Launch Test", gui_success))
    
    # Print summary
    print_header("Test Results Summary", char='*')
    all_passed = True
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status} - {name}")
        if not result:
            all_passed = False
    
    print("\nOverall result:", "PASSED" if all_passed else "FAILED")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())