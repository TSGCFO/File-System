#!/usr/bin/env python3
"""
Manual test script for FileConverter installation and GUI commands.

This script performs a series of tests on the FileConverter package to verify that
the installation process, entry points, and GUI launch mechanisms work as expected.

Usage:
    python tests/run_installation_test.py

Note: This should be run from the project root directory after installation.
"""

import os
import sys
import time
import platform
import subprocess
import importlib
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f" {text}")
    print("=" * 70)


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
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        return result.returncode == 0, result
    except Exception as e:
        print(f"Failed to execute command: {e}")
        return False, None


def test_import():
    """Test importing the FileConverter modules."""
    print_header("Testing Module Imports")
    
    modules = [
        "fileconverter",
        "fileconverter.main",
        "fileconverter.cli",
        "fileconverter.__main__",
        "fileconverter.gui.resources.icon_generator"
    ]
    
    all_succeeded = True
    for module_name in modules:
        try:
            module = importlib.import_module(module_name)
            print(f"✓ Successfully imported {module_name}")
            
            # Check for specific functions in main module
            if module_name == "fileconverter.main":
                if hasattr(module, "main"):
                    print(f"  ✓ Found 'main' function in {module_name}")
                else:
                    print(f"  ✗ Missing 'main' function in {module_name}")
                    all_succeeded = False
                
                if hasattr(module, "launch_gui"):
                    print(f"  ✓ Found 'launch_gui' function in {module_name}")
                else:
                    print(f"  ✗ Missing 'launch_gui' function in {module_name}")
                    all_succeeded = False
            
            # Check for run_gui in __main__ module
            if module_name == "fileconverter.__main__":
                if hasattr(module, "run_gui"):
                    print(f"  ✓ Found 'run_gui' function in {module_name}")
                else:
                    print(f"  ✗ Missing 'run_gui' function in {module_name}")
                    all_succeeded = False
            
        except ImportError as e:
            print(f"✗ Failed to import {module_name}: {e}")
            all_succeeded = False
    
    return all_succeeded


def test_cli_command():
    """Test the FileConverter CLI command."""
    print_header("Testing CLI Command")
    
    # Test version command
    success, _ = run_command(
        "fileconverter --version", 
        "Testing 'fileconverter --version' command"
    )
    
    # Test help command
    success_help, _ = run_command(
        "fileconverter --help", 
        "Testing 'fileconverter --help' command"
    )
    
    # Test list-formats command
    success_formats, _ = run_command(
        "fileconverter list-formats", 
        "Testing 'fileconverter list-formats' command"
    )
    
    return success and success_help and success_formats


def test_gui_commands():
    """Test the FileConverter GUI commands."""
    print_header("Testing GUI Commands")
    
    # We'll just check if the commands are recognized, but won't actually launch the GUI
    # since it would block the testing script
    
    gui_commands = [
        ("fileconverter-gui --help", "Testing 'fileconverter-gui --help' command", False),
        ("fileconverter --gui --help", "Testing 'fileconverter --gui --help' command", False)
    ]
    
    success = True
    for cmd, desc, check in gui_commands:
        cmd_success, result = run_command(cmd, desc, check)
        
        # Check if result indicates a recognized command (not "command not found")
        if result and result.returncode != 127:  # 127 is typically "command not found"
            print(f"✓ Command is recognized")
        else:
            print(f"✗ Command not recognized")
            success = False
    
    return success


def test_direct_module_execution():
    """Test executing the FileConverter module directly using python -m."""
    print_header("Testing Direct Module Execution")
    
    module_commands = [
        "python -m fileconverter --version",
        "python -m fileconverter --help",
        "python -m fileconverter.cli --version"
    ]
    
    success = True
    for cmd in module_commands:
        cmd_success, _ = run_command(cmd, f"Testing '{cmd}'")
        if not cmd_success:
            success = False
    
    return success


def check_desktop_shortcut():
    """Check if desktop shortcut was created."""
    print_header("Checking Desktop Shortcut")
    
    desktop_path = Path.home() / "Desktop"
    
    if platform.system() == "Windows":
        shortcut_path = desktop_path / "FileConverter.lnk"
        if shortcut_path.exists():
            print(f"✓ Windows desktop shortcut found at: {shortcut_path}")
            return True
        else:
            print(f"✗ Windows desktop shortcut not found at: {shortcut_path}")
    
    elif platform.system() == "Linux":
        shortcut_path = desktop_path / "fileconverter.desktop"
        if shortcut_path.exists():
            print(f"✓ Linux desktop shortcut found at: {shortcut_path}")
            return True
        else:
            print(f"✗ Linux desktop shortcut not found at: {shortcut_path}")
    
    elif platform.system() == "Darwin":  # macOS
        shortcut_path = desktop_path / "FileConverter.app"
        if shortcut_path.exists() or os.path.islink(shortcut_path):
            print(f"✓ macOS desktop shortcut found at: {shortcut_path}")
            return True
        else:
            print(f"✗ macOS desktop shortcut not found at: {shortcut_path}")
    
    print("Desktop shortcut not found. This is normal if you haven't installed the package with 'pip install .'")
    return False


def check_executable_in_path():
    """Check if FileConverter executables are in PATH."""
    print_header("Checking Executables in PATH")
    
    # Use 'where' on Windows, 'which' on Unix-like systems
    command = "where" if platform.system() == "Windows" else "which"
    
    executables = ["fileconverter", "fileconverter-gui"]
    
    success = True
    for exe in executables:
        cmd_success, result = run_command(
            f"{command} {exe}", 
            f"Checking if '{exe}' is in PATH",
            check=False
        )
        
        if cmd_success:
            print(f"✓ '{exe}' found in PATH")
        else:
            print(f"✗ '{exe}' not found in PATH")
            success = False
    
    if not success:
        print("\nNote: Executables not found in PATH. This is normal if you haven't installed")
        print("the package with 'pip install .' or if you're using development mode.")
    
    return success


def check_icon_generation():
    """Check if icon generation works."""
    print_header("Testing Icon Generation")
    
    try:
        print("Importing icon generator...")
        from fileconverter.gui.resources.icon_generator import generate_icon
        
        print("Executing icon generator...")
        generate_icon()
        
        # Check if icon was generated
        icon_dir = Path(__file__).resolve().parent.parent / "fileconverter" / "gui" / "resources"
        icon_path = icon_dir / "icon.ico"
        
        if icon_path.exists():
            print(f"✓ Icon successfully generated at: {icon_path}")
            print(f"  File size: {icon_path.stat().st_size} bytes")
            return True
        else:
            print(f"✗ Icon file not found at: {icon_path}")
            return False
    
    except ImportError as e:
        print(f"✗ Failed to import icon generator: {e}")
        print("  This may be due to missing Pillow dependency.")
        print("  Install with: pip install Pillow")
        return False
    except Exception as e:
        print(f"✗ Error testing icon generation: {e}")
        return False


def test_installation_development():
    """Test installation in development mode."""
    print_header("Testing Development Installation")
    
    # Install in development mode
    success, _ = run_command(
        "pip install -e .", 
        "Installing FileConverter in development mode"
    )
    
    if not success:
        print("✗ Failed to install in development mode")
        return False
    
    # Run tests
    print("\nRunning tests after development installation...")
    all_passed = True
    
    test_functions = [
        ("Module imports", test_import),
        ("CLI commands", test_cli_command),
        ("GUI commands", test_gui_commands),
        ("Direct module execution", test_direct_module_execution),
        ("Desktop shortcut", check_desktop_shortcut),
        ("Executables in PATH", check_executable_in_path),
        ("Icon generation", check_icon_generation)
    ]
    
    results = []
    for name, func in test_functions:
        result = func()
        results.append((name, result))
        if not result:
            all_passed = False
    
    # Print summary
    print_header("Test Summary")
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status} - {name}")
    
    return all_passed


if __name__ == "__main__":
    print("FileConverter Installation Test Script")
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Working directory: {os.getcwd()}")
    
    test_installation_development()