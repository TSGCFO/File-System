#!/usr/bin/env python3
"""
Test script for the FileConverter dependency management system.

This script tests various aspects of the dependency management system:
1. Detection of missing dependencies
2. Installation of Python packages
3. External dependency checks
4. Offline installation support
5. Platform-specific behaviors
"""

import os
import sys
import unittest
import tempfile
import shutil
import platform
import subprocess
from unittest.mock import patch, MagicMock

# Add parent directory to path to import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestDependencyManager(unittest.TestCase):
    """Test cases for the dependency management system."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        
        # Import the dependency manager
        try:
            from fileconverter.dependency_manager import (
                detect_missing_dependencies,
                auto_install_dependencies,
                check_python_package,
                find_executable,
                create_dependency_bundle
            )
            self.dependency_manager = sys.modules['fileconverter.dependency_manager']
        except ImportError:
            self.skipTest("dependency_manager module not found")
    
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_dir)
        shutil.rmtree(self.temp_dir)
    
    def test_detect_missing_dependencies(self):
        """Test the detection of missing dependencies."""
        # Mock import checks to simulate missing packages
        with patch.object(self.dependency_manager, 'check_python_package', return_value=False):
            # Mock executable checks to simulate missing external tools
            with patch.object(self.dependency_manager, 'find_executable', return_value=None):
                missing_deps = self.dependency_manager.detect_missing_dependencies()
                
                # Verify we detected missing dependencies
                self.assertTrue(len(missing_deps["python"]) > 0)
                self.assertTrue(len(missing_deps["external"]) > 0)
    
    def test_check_python_package(self):
        """Test Python package detection."""
        # Test with a package that should definitely exist (os)
        self.assertTrue(self.dependency_manager.check_python_package("os"))
        
        # Test with a package that should not exist (non_existent_package_xyz)
        self.assertFalse(self.dependency_manager.check_python_package("non_existent_package_xyz"))
    
    def test_find_executable(self):
        """Test executable detection."""
        # Test with a command that should exist on all platforms (python)
        python_cmd = "python.exe" if platform.system() == "Windows" else "python"
        self.assertIsNotNone(self.dependency_manager.find_executable(python_cmd))
        
        # Test with a command that should not exist
        self.assertIsNone(self.dependency_manager.find_executable("non_existent_command_xyz"))
    
    @patch('subprocess.run')
    def test_install_python_package(self, mock_run):
        """Test Python package installation."""
        # Mock successful installation
        mock_run.return_value = MagicMock(returncode=0)
        
        result = self.dependency_manager.install_python_package("test-package")
        self.assertTrue(result)
        mock_run.assert_called_once()
        
        # Mock failed installation
        mock_run.side_effect = subprocess.CalledProcessError(1, "pip")
        result = self.dependency_manager.install_python_package("test-package")
        self.assertFalse(result)
    
    @patch('fileconverter.dependency_manager.check_internet_connection')
    def test_auto_install_offline_mode(self, mock_check_internet):
        """Test auto-installation in offline mode."""
        # Mock no internet connection
        mock_check_internet.return_value = False
        
        # Create a mock missing_deps structure
        missing_deps = {
            "python": {
                "test-package": {
                    "import_name": "test_package",
                    "required": True,
                    "purpose": "Testing"
                }
            },
            "external": {}
        }
        
        # Test auto-installation without offline path
        with patch.object(self.dependency_manager, 'install_python_package', return_value=True):
            results = self.dependency_manager.auto_install_dependencies(
                missing_deps, 
                offline_path=None,
                interactive=False
            )
            
            # Should fail without offline path and no internet
            self.assertTrue("test-package" in results["failure"])
        
        # Test auto-installation with offline path
        with patch.object(self.dependency_manager, 'install_python_package', return_value=True):
            results = self.dependency_manager.auto_install_dependencies(
                missing_deps, 
                offline_path=self.temp_dir,
                interactive=False
            )
            
            # Should succeed with offline path even without internet
            self.assertTrue("test-package" in results["success"])
    
    @patch('subprocess.run')
    def test_create_dependency_bundle(self, mock_run):
        """Test creation of offline dependency bundle."""
        # Mock successful bundle creation
        mock_run.return_value = MagicMock(returncode=0)
        
        bundle_path = self.dependency_manager.create_dependency_bundle(self.temp_dir)
        self.assertIsNotNone(bundle_path)
        mock_run.assert_called_once()
        
        # Check that the README was created
        readme_path = os.path.join(bundle_path, "README.txt")
        self.assertTrue(os.path.exists(readme_path))
        
        # Mock failed bundle creation
        mock_run.side_effect = subprocess.CalledProcessError(1, "pip")
        bundle_path = self.dependency_manager.create_dependency_bundle(self.temp_dir)
        self.assertIsNone(bundle_path)
    
    @patch('fileconverter.dependency_manager.get_platform')
    @patch('fileconverter.dependency_manager.check_package_manager')
    def test_platform_specific_behavior(self, mock_check_pm, mock_get_platform):
        """Test platform-specific dependency handling."""
        # Test Windows
        mock_get_platform.return_value = "windows"
        mock_check_pm.return_value = "chocolatey"
        
        with patch.object(self.dependency_manager, 'find_executable', return_value=None):
            missing_deps = self.dependency_manager.detect_missing_dependencies(["document"])
            
            # Verify Windows-specific dependencies are checked
            self.assertIn("libreoffice", missing_deps["external"])
            self.assertIn("chocolatey", missing_deps["external"]["libreoffice"]["package_manager_info"])
        
        # Test macOS
        mock_get_platform.return_value = "macos"
        mock_check_pm.return_value = "homebrew"
        
        with patch.object(self.dependency_manager, 'find_executable', return_value=None):
            missing_deps = self.dependency_manager.detect_missing_dependencies(["document"])
            
            # Verify macOS-specific dependencies are checked
            self.assertIn("libreoffice", missing_deps["external"])
            self.assertIn("homebrew", missing_deps["external"]["libreoffice"]["package_manager_info"])
        
        # Test Linux
        mock_get_platform.return_value = "linux"
        mock_check_pm.return_value = "apt"
        
        with patch.object(self.dependency_manager, 'find_executable', return_value=None):
            missing_deps = self.dependency_manager.detect_missing_dependencies(["document"])
            
            # Verify Linux-specific dependencies are checked
            self.assertIn("libreoffice", missing_deps["external"])
            self.assertIn("apt", missing_deps["external"]["libreoffice"]["package_manager_info"])

def run_tests():
    """Run all dependency manager tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDependencyManager)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
    print("Testing FileConverter dependency management system...")
    run_tests()