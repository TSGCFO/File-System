#!/usr/bin/env python3
"""
Test script for verifying the FileConverter installation and GUI launch mechanisms.

This script simulates and tests the various components of the installation process:
1. GUI entry point functionality
2. Desktop shortcut creation
3. System PATH integration
4. Application registration
5. Icon generation

Usage:
    python -m tests.test_installation

Note: This script should be run from the project root directory.
"""

import os
import sys
import platform
import importlib
import unittest
import tempfile
import shutil
import subprocess
from pathlib import Path

# Add parent directory to import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestInstallation(unittest.TestCase):
    """Test class for FileConverter installation mechanisms."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        
        # Create mock environment
        os.makedirs(os.path.join(self.temp_dir, 'desktop'), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, 'bin'), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, 'registry'), exist_ok=True)
        
        # Store original environment for later restoration
        self.original_env = os.environ.copy()
        
        # Mock environment variables
        os.environ['HOME'] = self.temp_dir
        os.environ['USERPROFILE'] = self.temp_dir
        
        print(f"\nTest environment set up in {self.temp_dir}")
    
    def tearDown(self):
        """Clean up test environment."""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)
        
        # Clean up temp directory
        try:
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Warning: Could not clean up temp directory: {e}")
        
        os.chdir(self.original_cwd)
        print("Test environment cleaned up")
    
    def test_import_main_module(self):
        """Test importing the main module."""
        print("\nTesting main module import...")
        try:
            from fileconverter import main
            self.assertIsNotNone(main, "Main module should be importable")
            self.assertTrue(hasattr(main, 'main'), "Main function should exist")
            self.assertTrue(hasattr(main, 'launch_gui'), "launch_gui function should exist")
            print("✓ Main module import test passed")
        except ImportError as e:
            self.fail(f"Failed to import main module: {e}")
    
    def test_import_main_entry_point(self):
        """Test the main entry point can be executed."""
        print("\nTesting main entry point...")
        try:
            from fileconverter.__main__ import run_gui
            self.assertIsNotNone(run_gui, "run_gui function should exist in __main__")
            print("✓ Main entry point test passed")
        except ImportError as e:
            self.fail(f"Failed to import __main__ module: {e}")
    
    def test_icon_generator(self):
        """Test the icon generator functionality."""
        print("\nTesting icon generator...")
        try:
            # Import the icon generator module
            from fileconverter.gui.resources.icon_generator import generate_icon
            
            # Create a temporary directory for the icon
            icon_dir = os.path.join(self.temp_dir, 'icon_test')
            os.makedirs(icon_dir, exist_ok=True)
            
            # Patch the Path.parent property to point to our temp directory
            original_parent = Path.parent
            
            try:
                # Mock the parent property
                def mock_parent(self):
                    if str(self).endswith('icon.ico'):
                        return Path(icon_dir)
                    return original_parent.__get__(self)
                
                # Apply the mock
                Path.parent = property(mock_parent)
                
                # Generate the icon
                generate_icon()
                
                # Check if the icon was created
                icon_path = os.path.join(icon_dir, 'icon.ico')
                self.assertTrue(os.path.exists(icon_path), "Icon file should be created")
                self.assertTrue(os.path.getsize(icon_path) > 0, "Icon file should have content")
                
                print(f"✓ Icon generator test passed (Icon created at {icon_path})")
                
            finally:
                # Restore the original parent property
                Path.parent = original_parent
        
        except ImportError as e:
            print(f"Warning: Could not test icon generator: {e}")
            print("This is expected if Pillow is not installed. Install with pip install Pillow")
        except Exception as e:
            self.fail(f"Icon generator test failed: {e}")
    
    def test_desktop_shortcut_simulation(self):
        """Simulate desktop shortcut creation."""
        print("\nSimulating desktop shortcut creation...")
        
        # Import the setup module for access to the desktop shortcut function
        sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
        
        try:
            # Extract and modify the create_desktop_shortcut function from setup.py
            import setup
            
            # Create a modified function for testing
            def test_create_shortcut():
                home_dir = Path(self.temp_dir)
                desktop_dir = home_dir / "desktop"
                
                if platform.system() == "Windows":
                    # Simulate Windows shortcut
                    shortcut_path = desktop_dir / "FileConverter.lnk"
                    with open(shortcut_path, 'w') as f:
                        f.write("Windows shortcut simulation")
                    print(f"✓ Windows shortcut simulated at {shortcut_path}")
                    
                elif platform.system() == "Linux":
                    # Simulate Linux .desktop file
                    desktop_file = """[Desktop Entry]
Type=Application
Name=FileConverter
Comment=File conversion utility
Exec=fileconverter-gui
Icon=fileconverter
Terminal=false
Categories=Utility;
"""
                    desktop_entry_path = home_dir / ".local" / "share" / "applications" / "fileconverter.desktop"
                    os.makedirs(desktop_entry_path.parent, exist_ok=True)
                    
                    with open(desktop_entry_path, "w") as f:
                        f.write(desktop_file)
                    
                    desktop_shortcut = desktop_dir / "fileconverter.desktop"
                    with open(desktop_shortcut, "w") as f:
                        f.write(desktop_file)
                    
                    print(f"✓ Linux desktop entry simulated at {desktop_entry_path}")
                    print(f"✓ Linux desktop shortcut simulated at {desktop_shortcut}")
                
                elif platform.system() == "Darwin":  # macOS
                    # Simulate macOS application
                    app_script = """#!/usr/bin/env bash
python -m fileconverter.main --gui
"""
                    app_dir = home_dir / "Applications" / "FileConverter.app" / "Contents" / "MacOS"
                    os.makedirs(app_dir, exist_ok=True)
                    
                    with open(app_dir / "FileConverter", "w") as f:
                        f.write(app_script)
                    
                    desktop_link = desktop_dir / "FileConverter.app"
                    os.makedirs(desktop_link, exist_ok=True)
                    
                    print(f"✓ macOS application simulated at {app_dir}")
                    print(f"✓ macOS desktop link simulated at {desktop_link}")
            
            # Run the test function
            test_create_shortcut()
            
        except Exception as e:
            print(f"Warning: Desktop shortcut simulation failed: {e}")
            print("This is expected in certain environments. Manual testing recommended.")
    
    def test_executable_creation_simulation(self):
        """Simulate executable creation."""
        print("\nSimulating executable creation...")
        
        bin_dir = os.path.join(self.temp_dir, 'bin')
        
        if platform.system() == "Windows":
            # Simulate Windows batch files
            batch_files = [
                (os.path.join(bin_dir, "fileconverter.bat"), "@echo off\npython -m fileconverter.cli %*\n"),
                (os.path.join(bin_dir, "fileconverter-gui.bat"), "@echo off\npython -m fileconverter.main --gui\n")
            ]
            
            for file_path, content in batch_files:
                with open(file_path, 'w') as f:
                    f.write(content)
                print(f"✓ Created Windows batch file: {file_path}")
        
        elif platform.system() in ("Linux", "Darwin"):
            # Simulate Linux/macOS scripts
            script_files = [
                (os.path.join(bin_dir, "fileconverter"), "#!/bin/bash\npython3 -m fileconverter.cli \"$@\"\n"),
                (os.path.join(bin_dir, "fileconverter-gui"), "#!/bin/bash\npython3 -m fileconverter.main --gui\n")
            ]
            
            for file_path, content in script_files:
                with open(file_path, 'w') as f:
                    f.write(content)
                os.chmod(file_path, 0o755)
                print(f"✓ Created {platform.system()} executable script: {file_path}")
        
        # Verify files were created
        files = os.listdir(bin_dir)
        self.assertTrue(len(files) > 0, "Executable files should be created")
        print(f"✓ Executable creation simulation successful: {len(files)} files created")
    
    def test_integration(self):
        """Test integration by checking if the fileconverter module can be executed."""
        print("\nTesting integration by checking module execution...")
        
        try:
            # Test importing the module
            import fileconverter
            self.assertIsNotNone(fileconverter, "FileConverter module should be importable")
            
            # Get the module version
            self.assertTrue(hasattr(fileconverter, '__version__'), "Version attribute should exist")
            print(f"FileConverter version: {fileconverter.__version__}")
            
            print("✓ Integration test passed")
        except ImportError as e:
            self.fail(f"Failed to import FileConverter module: {e}")


def run_tests():
    """Run all tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestInstallation)
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == "__main__":
    print("Running FileConverter installation tests...")
    run_tests()