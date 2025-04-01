#!/usr/bin/env python3
"""
Manual test script for the FileConverter dependency management system.

This script allows for interactive testing of the dependency management 
features, including:
1. Dependency detection
2. Python package installation
3. External dependency handling
4. Offline bundle creation and usage
5. CLI integration

Usage:
    python tests/test_dependency_system.py [--offline-path PATH] [--skip-install]
"""

import os
import sys
import argparse
import tempfile
import shutil
import platform
from pathlib import Path

# Add parent directory to path to import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def print_header(title, char='='):
    """Print a formatted header."""
    width = 70
    print("\n" + char * width)
    print(f" {title}")
    print(char * width)

def print_section(title):
    """Print a section title."""
    print(f"\n{'-' * 50}")
    print(f" {title}")
    print(f"{'-' * 50}")

def print_result(name, success):
    """Print a test result."""
    status = "✓ PASSED" if success else "✗ FAILED"
    print(f"{status} - {name}")

def test_dependency_detection():
    """Test dependency detection functionality."""
    print_section("Testing Dependency Detection")
    
    from fileconverter.dependency_manager import detect_missing_dependencies, get_platform
    
    # Test detecting all dependencies
    print("Testing complete dependency detection...")
    all_deps = detect_missing_dependencies()
    print(f"Detected {len(all_deps['python'])} missing Python packages")
    print(f"Detected {len(all_deps['external'])} missing external tools")
    
    # Test detecting specific format dependencies
    print("\nTesting format-specific dependency detection...")
    for format_name in ["document", "spreadsheet", "image", "archive", "gui"]:
        format_deps = detect_missing_dependencies([format_name])
        python_count = len(format_deps["python"])
        external_count = len(format_deps["external"])
        print(f"Format '{format_name}': {python_count} Python packages, {external_count} external tools")
    
    # Test platform-specific external dependencies
    platform_name = get_platform()
    print(f"\nCurrent platform: {platform_name}")
    
    return True

def test_package_checking():
    """Test Python package checking functionality."""
    print_section("Testing Python Package Detection")
    
    from fileconverter.dependency_manager import check_python_package
    
    # Test with packages that should definitely exist
    standard_packages = ["os", "sys", "pathlib"]
    for pkg in standard_packages:
        result = check_python_package(pkg)
        print(f"Package '{pkg}': {'Found' if result else 'Not found'}")
        assert result, f"Standard package {pkg} should be installed"
    
    # Test with packages that likely don't exist
    fake_packages = ["non_existent_pkg_123", "another_fake_package_456"]
    for pkg in fake_packages:
        result = check_python_package(pkg)
        print(f"Package '{pkg}': {'Found' if result else 'Not found'}")
        assert not result, f"Fake package {pkg} should not be found"
    
    return True

def test_executable_detection():
    """Test external executable detection."""
    print_section("Testing External Tool Detection")
    
    from fileconverter.dependency_manager import find_executable
    
    # Test with executables that should exist on all platforms
    if platform.system() == "Windows":
        common_cmds = ["cmd.exe", "powershell.exe", "notepad.exe"]
    else:
        common_cmds = ["bash", "ls", "pwd"]
    
    for cmd in common_cmds:
        path = find_executable(cmd)
        print(f"Command '{cmd}': {'Found at ' + path if path else 'Not found'}")
    
    # Test with custom paths
    if platform.system() == "Windows":
        paths = [os.environ.get("WINDIR", "C:\\Windows"), os.environ.get("WINDIR", "C:\\Windows") + "\\System32"]
        cmd = "notepad.exe"
    else:
        paths = ["/usr/bin", "/bin"]
        cmd = "ls"
    
    path = find_executable(cmd, paths)
    print(f"Command '{cmd}' (with custom paths): {'Found at ' + path if path else 'Not found'}")
    
    return True

def test_report_generation():
    """Test dependency report generation."""
    print_section("Testing Report Generation")
    
    from fileconverter.dependency_manager import (
        detect_missing_dependencies, 
        generate_report
    )
    
    # Generate a sample missing dependencies structure
    missing_deps = detect_missing_dependencies()
    
    # Create a sample installation results structure
    install_results = {
        "success": ["package1", "package2"],
        "failure": ["package3"],
        "manual_action_required": ["external-tool1"]
    }
    
    # Generate the report
    report = generate_report(missing_deps, install_results)
    
    # Display the report
    print("\nGenerated dependency report:")
    print(report)
    
    return True

def test_offline_bundle(temp_dir):
    """Test offline bundle creation."""
    print_section("Testing Offline Bundle Creation")
    
    from fileconverter.dependency_manager import create_dependency_bundle
    
    # Create a temporary output directory
    output_dir = os.path.join(temp_dir, "bundle_test")
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")
    
    # Create the offline bundle
    print("\nCreating offline bundle...")
    bundle_path = create_dependency_bundle(output_dir)
    
    if bundle_path:
        print(f"Bundle created successfully at: {bundle_path}")
        
        # Check the structure of the bundle
        subdirs = [d for d in os.listdir(bundle_path) if os.path.isdir(os.path.join(bundle_path, d))]
        print(f"Bundle subdirectories: {', '.join(subdirs)}")
        
        # Check for critical files
        readme_path = os.path.join(bundle_path, "README.txt")
        if os.path.exists(readme_path):
            print("Found README.txt")
        
        # Check installer scripts
        installer_dir = os.path.join(bundle_path, "installer")
        if os.path.exists(installer_dir):
            installer_files = os.listdir(installer_dir)
            print(f"Installer files: {', '.join(installer_files)}")
        
        return True
    else:
        print("Failed to create offline bundle")
        return False

def test_installation(offline_path=None, skip_install=False):
    """Test dependency installation."""
    print_section("Testing Dependency Installation")
    
    from fileconverter.dependency_manager import (
        detect_missing_dependencies,
        auto_install_dependencies
    )
    
    # Detect missing dependencies
    print("Detecting missing dependencies...")
    missing_deps = detect_missing_dependencies()
    
    # Display what we're going to install
    print("\nMissing Python packages:")
    for pkg_name in missing_deps["python"]:
        pkg_info = missing_deps["python"][pkg_name]
        required = "Required" if pkg_info.get("required", False) else "Optional"
        print(f"- {pkg_name} ({required}): {pkg_info.get('purpose', 'No purpose specified')}")
    
    print("\nMissing external tools:")
    for tool_name in missing_deps["external"]:
        tool_info = missing_deps["external"][tool_name]
        print(f"- {tool_info.get('name', tool_name)}: {tool_info.get('purpose', 'No purpose specified')}")
    
    if skip_install:
        print("\nSkipping installation as requested")
        return True
    
    # Confirm installation
    response = input("\nProceed with installation? (y/n): ")
    if response.lower() != 'y':
        print("Installation skipped")
        return True
    
    # Install dependencies
    print("\nInstalling dependencies...")
    results = auto_install_dependencies(missing_deps, offline_path, interactive=True)
    
    # Display results
    print("\nInstallation results:")
    for result_type in results:
        if results[result_type]:
            print(f"{result_type}: {', '.join(results[result_type])}")
    
    return True

def test_cli_integration():
    """Test CLI integration for dependency management."""
    print_section("Testing CLI Integration")
    
    # Import the CLI module
    try:
        from fileconverter.cli import main as cli_main
        import shlex
        
        # Test the 'dependencies check' command
        print("Testing 'dependencies check' command...")
        sys.argv = shlex.split("fileconverter dependencies check")
        try:
            cli_main()
        except SystemExit:
            pass
        
        # Test the 'dependencies check --format=document' command
        print("\nTesting 'dependencies check --format=document' command...")
        sys.argv = shlex.split("fileconverter dependencies check --format=document")
        try:
            cli_main()
        except SystemExit:
            pass
        
        return True
    except ImportError:
        print("CLI module not found. Can't test CLI integration.")
        return False
    except Exception as e:
        print(f"Error testing CLI: {e}")
        return False

def main():
    """Run all dependency management tests."""
    parser = argparse.ArgumentParser(description="Test the FileConverter dependency management system")
    parser.add_argument("--offline-path", help="Path to offline package repository")
    parser.add_argument("--skip-install", action="store_true", help="Skip dependency installation tests")
    
    args = parser.parse_args()
    
    print_header("FileConverter Dependency Management System Tester", char='*')
    
    temp_dir = tempfile.mkdtemp()
    print(f"Using temporary directory: {temp_dir}")
    
    results = []
    
    try:
        # Test dependency detection
        success = test_dependency_detection()
        results.append(("Dependency Detection", success))
        
        # Test package checking
        success = test_package_checking()
        results.append(("Package Checking", success))
        
        # Test executable detection
        success = test_executable_detection()
        results.append(("Executable Detection", success))
        
        # Test report generation
        success = test_report_generation()
        results.append(("Report Generation", success))
        
        # Test offline bundle
        success = test_offline_bundle(temp_dir)
        results.append(("Offline Bundle Creation", success))
        
        # Test installation
        success = test_installation(args.offline_path, args.skip_install)
        results.append(("Dependency Installation", success))
        
        # Test CLI integration
        success = test_cli_integration()
        results.append(("CLI Integration", success))
        
    finally:
        # Clean up
        try:
            shutil.rmtree(temp_dir)
            print(f"\nCleaned up temporary directory: {temp_dir}")
        except Exception as e:
            print(f"Warning: Failed to clean up temporary directory {temp_dir}: {e}")
    
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