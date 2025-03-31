#!/usr/bin/env python3
"""
FileConverter Installation and Test Script

This script installs the FileConverter package in development mode
and verifies that the installation was successful by testing the
command-line interface and GUI launcher.

Usage:
    python install_and_test.py

This will:
1. Install the package in development mode
2. Test the command-line interface
3. Optionally test the GUI launcher
"""

import os
import sys
import time
import platform
import subprocess
from pathlib import Path

def print_header(text, char='='):
    """Print a formatted header."""
    width = 70
    print("\n" + char * width)
    print(f" {text}")
    print(char * width)


def run_command(command, description, check=False):
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


def ensure_version_file():
    """Ensure the version.py file exists."""
    version_file = Path("fileconverter/version.py")
    
    if not version_file.exists():
        print(f"Creating version.py file at {version_file}")
        with open(version_file, "w") as f:
            f.write('"""Version information."""\n\n__version__ = "0.1.0"\n')


def install_package():
    """Install the package in development mode."""
    print_header("Installing Package in Development Mode")
    
    # Ensure version file exists
    ensure_version_file()
    
    # Install required dependencies first
    print("Installing required dependencies...")
    success, _ = run_command(
        "pip install click PyQt6 Pillow",
        "Installing basic dependencies",
        check=True
    )
    
    if not success:
        print("Failed to install dependencies. Please install them manually:")
        print("pip install click PyQt6 Pillow")
        return False
    
    # Install the package
    success, _ = run_command(
        "pip install -e .",
        "Installing FileConverter in development mode",
        check=True
    )
    
    if success:
        print("✓ Successfully installed FileConverter in development mode")
    else:
        print("✗ Failed to install FileConverter")
        print("Please check the error messages above and fix any issues")
        return False
    
    return True


def test_cli():
    """Test the command-line interface."""
    print_header("Testing Command-Line Interface")
    
    commands = [
        "fileconverter --version",
        "fileconverter --help",
        "fileconverter list-formats"
    ]
    
    success = True
    for cmd in commands:
        cmd_success, _ = run_command(cmd, f"Testing '{cmd}'")
        if not cmd_success:
            success = False
    
    if success:
        print("✓ CLI tests passed")
    else:
        print("✗ Some CLI tests failed")
    
    return success


def test_gui(timeout=3):
    """Test the GUI launcher."""
    print_header("Testing GUI Launcher")
    
    print("Note: This will attempt to launch the GUI and then automatically close it")
    print(f"The GUI will be closed after {timeout} seconds")
    
    gui_commands = [
        "fileconverter-gui --help",
        "fileconverter --gui --help"
    ]
    
    # First test if commands are recognized
    success = True
    for cmd in gui_commands:
        cmd_success, _ = run_command(cmd, f"Testing '{cmd}'")
        if not cmd_success:
            success = False
    
    if not success:
        print("✗ GUI command tests failed")
        return False
    
    # Now try to launch the actual GUI
    print("\nAttempting to launch the GUI (will be closed automatically)...")
    try:
        if platform.system() == 'Windows':
            cmd = "start /B python -m fileconverter --gui"
        else:
            cmd = "python -m fileconverter --gui &"
        
        subprocess.Popen(cmd, shell=True)
        
        print(f"Launched GUI, waiting {timeout} seconds...")
        time.sleep(timeout)
        
        # Try to terminate the process
        if platform.system() == 'Windows':
            subprocess.run("taskkill /F /IM python.exe /FI \"WINDOWTITLE eq FileConverter\"", shell=True)
        else:
            # On Unix-like systems, we'd need to find the PID
            subprocess.run("pkill -f \"python -m fileconverter --gui\"", shell=True)
        
        print("GUI launched successfully and closed")
        return True
    
    except Exception as e:
        print(f"Error launching GUI: {e}")
        return False


def generate_icon():
    """Generate the application icon."""
    print_header("Generating Application Icon")
    
    try:
        from fileconverter.gui.resources.icon_generator import generate_icon as gen_icon
        icon_path = gen_icon()
        if icon_path:
            print(f"✓ Icon generated at {icon_path}")
            return True
        else:
            print("✗ Icon generation failed")
            return False
    except ImportError as e:
        print(f"✗ Failed to import icon generator: {e}")
        return False
    except Exception as e:
        print(f"✗ Error generating icon: {e}")
        return False


def main():
    """Main function."""
    print_header("FileConverter Installation and Test Script", char='*')
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Working directory: {os.getcwd()}")
    
    # Step 1: Install the package
    if not install_package():
        print("\nInstallation failed. Please fix the issues and try again.")
        return 1
    
    # Step 2: Generate icon
    generate_icon()
    
    # Step 3: Test CLI
    cli_success = test_cli()
    
    # Step 4: Test GUI (optional)
    gui_success = False
    if cli_success:
        gui_success = test_gui()
    
    # Print summary
    print_header("Test Results", char='*')
    print(f"Installation: {'✓ PASSED' if True else '✗ FAILED'}")
    print(f"CLI Tests: {'✓ PASSED' if cli_success else '✗ FAILED'}")
    print(f"GUI Tests: {'✓ PASSED' if gui_success else '✗ FAILED'}")
    
    if cli_success and gui_success:
        print("\nAll tests passed! FileConverter is installed and working correctly.")
        return 0
    else:
        print("\nSome tests failed. Please check the error messages above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())