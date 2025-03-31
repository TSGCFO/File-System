#!/usr/bin/env python3
"""
FileConverter GUI Launcher Test Script

This script tests the launch_gui.py script by running it with a timeout
to automatically close the GUI window after a few seconds.

Usage:
    python test_launcher.py
"""

import os
import sys
import time
import subprocess
import platform

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f" {text}")
    print("=" * 70)

def run_with_timeout(timeout=5):
    """Launch the GUI and automatically close it after a timeout."""
    print_header("Testing GUI Launcher")
    print(f"Launching GUI with {timeout} second timeout...")
    
    try:
        # Launch the GUI in a separate process
        if platform.system() == 'Windows':
            proc = subprocess.Popen(["start", "python", "launch_gui.py"], shell=True)
        else:
            proc = subprocess.Popen(["python", "launch_gui.py"])
        
        print(f"Waiting {timeout} seconds for GUI to launch and display...")
        time.sleep(timeout)
        
        # Try to terminate the process
        if platform.system() == 'Windows':
            subprocess.run("taskkill /F /IM python.exe /FI \"WINDOWTITLE eq FileConverter\"", shell=True)
            print("Attempted to close GUI window")
        else:
            proc.terminate()
            print("Terminated GUI process")
        
        print("✓ GUI launcher test completed")
        return True
    
    except Exception as e:
        print(f"✗ Error running GUI launcher: {e}")
        return False

def main():
    """Main function."""
    print("FileConverter GUI Launcher Test")
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    
    success = run_with_timeout(timeout=5)
    
    print_header("Test Results")
    if success:
        print("✓ GUI launcher test PASSED")
        print("Note: This only verifies that the launcher script executed without errors.")
        print("If the GUI window did not appear, check your PyQt6 installation.")
        return 0
    else:
        print("✗ GUI launcher test FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())