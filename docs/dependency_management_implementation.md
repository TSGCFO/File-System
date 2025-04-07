# FileConverter Dependency Management Implementation Plan

This document provides a comprehensive, step-by-step guide for implementing a robust dependency management system for FileConverter. The goal is to create a seamless installation experience for all users, especially those with limited technical expertise.

## Table of Contents

1. [Overview](#overview)
2. [Implementation Steps](#implementation-steps)
3. [Testing Procedures](#testing-procedures)
4. [Documentation Updates](#documentation-updates)
5. [Rollout Strategy](#rollout-strategy)

## Overview

The dependency management system will automatically detect, install, and configure all required dependencies without user intervention. It will provide platform-specific approaches for Windows, macOS, and Linux, handle offline installations, and include graceful fallback mechanisms.

### Key Components

1. **Dependency Manager Module**: Central module for detecting and managing dependencies
2. **Setup Integration**: Enhanced installer integration
3. **Runtime Checks**: Dependency verification at application startup
4. **CLI Interface**: Commands for managing dependencies
5. **Offline Support**: Bundle creation for network-restricted environments
6. **Testing Framework**: Comprehensive testing of dependency management features

## Implementation Steps

### Step 1: Create the Dependency Manager Module

Create a new file `fileconverter/dependency_manager.py` with the following functionality:

```python
#!/usr/bin/env python3
"""
Dependency Manager for FileConverter.

This module handles detection, installation, and configuration of all dependencies
required by FileConverter, providing automatic installation and clear fallback
mechanisms when automatic installation is not possible.
"""

import os
import sys
import platform
import subprocess
import shutil
import importlib.util
import tempfile
import logging
import json
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set, Any, Union

# Configure logging
logger = logging.getLogger(__name__)

# Core Python packages required for basic functionality
CORE_PACKAGES = {
    "yaml": "PyYAML",
    "lxml": "lxml",
    "pillow": "Pillow",
    "psutil": "psutil",
}

# Format-specific Python packages
FORMAT_PACKAGES = {
    "document": {
        "docx": "python-docx",
        "markdown": "Markdown",
        "PyPDF2": "PyPDF2",
    },
    "spreadsheet": {
        "openpyxl": "openpyxl",
        "pandas": "pandas",
        "xlrd": "xlrd",
        "xlsxwriter": "XlsxWriter",
    },
    "image": {
        "PIL": "Pillow",
        "wand": "Wand",  # ImageMagick binding
    },
    "archive": {
        "py7zr": "py7zr",
        "pyzstd": "pyzstd",
    },
    "gui": {
        "PyQt6": "PyQt6",
        "PyQt6.QScintilla": "PyQt6-QScintilla",
    }
}

# External system binaries required for specific operations
EXTERNAL_DEPENDENCIES = {
    "windows": {
        "libreoffice": {
            "name": "LibreOffice",
            "command": "soffice.exe",
            "paths": [
                "C:\\Program Files\\LibreOffice\\program",
                "C:\\Program Files (x86)\\LibreOffice\\program",
            ],
            "choco_pkg": "libreoffice-fresh",
            "url": "https://www.libreoffice.org/download/download/",
            "purpose": "Required for DOC/DOCX/ODT conversions"
        },
        "wkhtmltopdf": {
            "name": "wkhtmltopdf",
            "command": "wkhtmltopdf.exe",
            "paths": [
                "C:\\Program Files\\wkhtmltopdf\\bin",
                "C:\\Program Files (x86)\\wkhtmltopdf\\bin",
            ],
            "choco_pkg": "wkhtmltopdf",
            "url": "https://wkhtmltopdf.org/downloads.html",
            "purpose": "Required for HTML to PDF conversions"
        },
        "imagemagick": {
            "name": "ImageMagick",
            "command": "magick.exe",
            "paths": [
                "C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI",
                "C:\\Program Files\\ImageMagick*",
            ],
            "choco_pkg": "imagemagick",
            "url": "https://imagemagick.org/script/download.php#windows",
            "purpose": "Required for advanced image conversions"
        },
    },
    "macos": {
        "libreoffice": {
            "name": "LibreOffice",
            "command": "soffice",
            "paths": [
                "/Applications/LibreOffice.app/Contents/MacOS",
                "/usr/local/bin",
            ],
            "brew_pkg": "libreoffice",
            "url": "https://www.libreoffice.org/download/download/",
            "purpose": "Required for DOC/DOCX/ODT conversions"
        },
        "wkhtmltopdf": {
            "name": "wkhtmltopdf",
            "command": "wkhtmltopdf",
            "paths": [
                "/usr/local/bin",
                "/opt/homebrew/bin",
            ],
            "brew_pkg": "wkhtmltopdf",
            "url": "https://wkhtmltopdf.org/downloads.html",
            "purpose": "Required for HTML to PDF conversions"
        },
        "imagemagick": {
            "name": "ImageMagick",
            "command": "convert",
            "paths": [
                "/usr/local/bin",
                "/opt/homebrew/bin",
            ],
            "brew_pkg": "imagemagick",
            "url": "https://imagemagick.org/script/download.php#macosx",
            "purpose": "Required for advanced image conversions"
        },
    },
    "linux": {
        "libreoffice": {
            "name": "LibreOffice",
            "command": "soffice",
            "paths": [
                "/usr/bin",
                "/usr/local/bin",
            ],
            "apt_pkg": "libreoffice",
            "yum_pkg": "libreoffice",
            "pacman_pkg": "libreoffice-fresh",
            "url": "https://www.libreoffice.org/download/download/",
            "purpose": "Required for DOC/DOCX/ODT conversions"
        },
        "wkhtmltopdf": {
            "name": "wkhtmltopdf",
            "command": "wkhtmltopdf",
            "paths": [
                "/usr/bin",
                "/usr/local/bin",
            ],
            "apt_pkg": "wkhtmltopdf",
            "yum_pkg": "wkhtmltopdf",
            "pacman_pkg": "wkhtmltopdf",
            "url": "https://wkhtmltopdf.org/downloads.html",
            "purpose": "Required for HTML to PDF conversions"
        },
        "imagemagick": {
            "name": "ImageMagick",
            "command": "convert",
            "paths": [
                "/usr/bin",
                "/usr/local/bin",
            ],
            "apt_pkg": "imagemagick",
            "yum_pkg": "ImageMagick",
            "pacman_pkg": "imagemagick",
            "url": "https://imagemagick.org/script/download.php#linux",
            "purpose": "Required for advanced image conversions"
        },
    }
}

# Standard package manager commands for different platforms
PACKAGE_MANAGERS = {
    "windows": {
        "name": "Chocolatey",
        "check_cmd": "choco --version",
        "install_cmd": "choco install {} -y",
        "install_url": "https://chocolatey.org/install",
    },
    "macos": {
        "name": "Homebrew",
        "check_cmd": "brew --version",
        "install_cmd": "brew install {}",
        "install_url": "https://brew.sh/",
    },
    "linux": {
        "name": "System Package Manager",
        "variants": {
            "apt": {
                "check_cmd": "apt --version",
                "install_cmd": "sudo apt install -y {}",
            },
            "yum": {
                "check_cmd": "yum --version",
                "install_cmd": "sudo yum install -y {}",
            },
            "dnf": {
                "check_cmd": "dnf --version",
                "install_cmd": "sudo dnf install -y {}",
            },
            "pacman": {
                "check_cmd": "pacman --version",
                "install_cmd": "sudo pacman -S --noconfirm {}",
            },
        }
    }
}

def get_platform() -> str:
    """Get standardized platform name."""
    if sys.platform.startswith('win'):
        return "windows"
    elif sys.platform == "darwin":
        return "macos"
    elif sys.platform.startswith('linux'):
        return "linux"
    else:
        return "unknown"

def check_internet_connection() -> bool:
    """Check if internet is available by attempting to connect to a known site."""
    try:
        urllib.request.urlopen("https://google.com", timeout=3)
        return True
    except:
        return False

def check_python_package(package_name: str) -> bool:
    """Check if a Python package is installed."""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def find_executable(executable: str, paths: List[str] = None) -> Optional[str]:
    """Find an executable in the specified paths or system PATH."""
    # First check if it's directly available in PATH
    system_path = shutil.which(executable)
    if system_path:
        return system_path
    
    # If not, check the specified paths
    if paths:
        for path in paths:
            path_expanded = os.path.expanduser(os.path.expandvars(path))
            if os.path.isdir(path_expanded):
                for pattern in [f"{executable}", f"{executable}.*"]:
                    for item in Path(path_expanded).glob(pattern):
                        if os.access(item, os.X_OK):
                            return str(item)
    
    return None

def detect_missing_dependencies(formats: Optional[List[str]] = None) -> Dict[str, Dict]:
    """
    Detect missing dependencies for the specified formats.
    
    Args:
        formats: List of format categories to check. If None, check all formats.
        
    Returns:
        Dictionary with 'python' and 'external' keys, each containing details about missing dependencies.
    """
    missing = {
        "python": {},
        "external": {}
    }
    
    # Check core Python packages
    for import_name, pkg_name in CORE_PACKAGES.items():
        if not check_python_package(import_name):
            missing["python"][pkg_name] = {
                "import_name": import_name,
                "required": True,
                "purpose": "Core functionality"
            }
    
    # Check format-specific Python packages
    if formats is None:
        formats = list(FORMAT_PACKAGES.keys())
        
    for format_name in formats:
        if format_name in FORMAT_PACKAGES:
            for import_name, pkg_name in FORMAT_PACKAGES[format_name].items():
                if not check_python_package(import_name):
                    missing["python"][pkg_name] = {
                        "import_name": import_name,
                        "required": False,  # Format-specific packages are optional
                        "purpose": f"Required for {format_name} format conversions"
                    }
    
    # Check external dependencies
    platform_name = get_platform()
    if platform_name in EXTERNAL_DEPENDENCIES:
        for dep_name, dep_info in EXTERNAL_DEPENDENCIES[platform_name].items():
            executable_path = find_executable(dep_info["command"], dep_info["paths"])
            if not executable_path:
                missing["external"][dep_name] = {
                    "name": dep_info["name"],
                    "command": dep_info["command"],
                    "purpose": dep_info["purpose"],
                    "url": dep_info["url"],
                    "package_manager_info": {}
                }
                
                # Add package manager info if available
                if platform_name == "windows" and "choco_pkg" in dep_info:
                    missing["external"][dep_name]["package_manager_info"]["chocolatey"] = dep_info["choco_pkg"]
                elif platform_name == "macos" and "brew_pkg" in dep_info:
                    missing["external"][dep_name]["package_manager_info"]["homebrew"] = dep_info["brew_pkg"]
                elif platform_name == "linux":
                    for pm in ["apt_pkg", "yum_pkg", "pacman_pkg"]:
                        if pm in dep_info:
                            pm_name = pm.split("_")[0]
                            missing["external"][dep_name]["package_manager_info"][pm_name] = dep_info[pm]
    
    return missing

def install_python_package(package_name: str, offline_path: Optional[str] = None) -> bool:
    """
    Install a Python package using pip.
    
    Args:
        package_name: Name of the package to install
        offline_path: Path to vendor directory for offline installation
        
    Returns:
        True if installation was successful, False otherwise
    """
    try:
        cmd = [sys.executable, "-m", "pip", "install"]
        
        if offline_path:
            logger.info(f"Attempting offline installation of {package_name} from {offline_path}")
            cmd.extend(["--no-index", "--find-links", offline_path])
        else:
            logger.info(f"Attempting online installation of {package_name}")
            
        cmd.append(package_name)
        logger.debug(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install {package_name}: {e}")
        logger.debug(f"stdout: {e.stdout}")
        logger.debug(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error installing {package_name}: {e}")
        return False

def check_package_manager(platform_name: str) -> Optional[str]:
    """
    Check if a package manager is available for the current platform.
    
    Returns:
        Name of available package manager, or None if none found
    """
    if platform_name not in PACKAGE_MANAGERS:
        return None
    
    pm_info = PACKAGE_MANAGERS[platform_name]
    
    if platform_name in ["windows", "macos"]:
        try:
            subprocess.run(pm_info["check_cmd"], shell=True, check=True, 
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return pm_info["name"].lower()
        except subprocess.CalledProcessError:
            return None
    elif platform_name == "linux":
        # Check each Linux package manager variant
        for pm_name, pm_details in pm_info["variants"].items():
            try:
                subprocess.run(pm_details["check_cmd"], shell=True, check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return pm_name
            except subprocess.CalledProcessError:
                continue
        return None
    
    return None

def install_external_dependency(dep_name: str, dep_info: Dict[str, Any]) -> bool:
    """
    Attempt to install an external dependency using system package manager.
    
    Returns:
        True if installation was successful or initiated, False otherwise
    """
    platform_name = get_platform()
    pm_name = check_package_manager(platform_name)
    
    if not pm_name:
        logger.warning(f"No package manager found for {platform_name}")
        return False
    
    # Get the appropriate package name for the detected package manager
    package_name = None
    install_cmd = None
    
    if platform_name == "windows" and pm_name == "chocolatey":
        if "choco_pkg" in dep_info:
            package_name = dep_info["choco_pkg"]
            install_cmd = PACKAGE_MANAGERS["windows"]["install_cmd"].format(package_name)
    elif platform_name == "macos" and pm_name == "homebrew":
        if "brew_pkg" in dep_info:
            package_name = dep_info["brew_pkg"]
            install_cmd = PACKAGE_MANAGERS["macos"]["install_cmd"].format(package_name)
    elif platform_name == "linux" and f"{pm_name}_pkg" in dep_info:
        package_name = dep_info[f"{pm_name}_pkg"]
        install_cmd = PACKAGE_MANAGERS["linux"]["variants"][pm_name]["install_cmd"].format(package_name)
    
    if not package_name or not install_cmd:
        logger.warning(f"No package information found for {dep_name} with package manager {pm_name}")
        return False
    
    try:
        logger.info(f"Attempting to install {dep_name} using {pm_name}")
        
        # On Windows, we need to run with elevated privileges
        if platform_name == "windows":
            if hasattr(sys, "frozen"):
                # If running as a compiled executable
                cmd = f'powershell.exe -Command "Start-Process -Verb RunAs cmd.exe -Args \'/c {install_cmd}\'"'
            else:
                # If running as a Python script
                cmd = f'powershell.exe -Command "Start-Process -Verb RunAs -FilePath \'{install_cmd}\'"'
            
            subprocess.Popen(cmd, shell=True)
            logger.info(f"Initiated installation of {dep_name}. Please follow the prompts in the new window.")
            return True
        else:
            # For macOS and Linux, we can run directly (may prompt for sudo password)
            subprocess.run(install_cmd, shell=True, check=True)
            logger.info(f"Successfully installed {dep_name}")
            return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install {dep_name}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error installing {dep_name}: {e}")
        return False

def auto_install_dependencies(missing_deps: Dict[str, Dict], 
                             offline_path: Optional[str] = None,
                             interactive: bool = True) -> Dict[str, List[str]]:
    """
    Attempt to automatically install missing dependencies.
    
    Args:
        missing_deps: Dictionary of missing dependencies from detect_missing_dependencies()
        offline_path: Path to vendor directory for offline installation
        interactive: Whether to prompt the user for confirmation
        
    Returns:
        Dictionary with 'success' and 'failure' lists of dependency names
    """
    results = {
        "success": [],
        "failure": [],
        "manual_action_required": []
    }
    
    # First, check internet connection if we're not in offline mode
    has_internet = check_internet_connection() if not offline_path else False
    
    # Install Python packages
    if missing_deps["python"]:
        logger.info("Installing missing Python packages...")
        
        for pkg_name, pkg_info in missing_deps["python"].items():
            if interactive:
                response = input(f"Install Python package '{pkg_name}'? (y/n): ").lower()
                if response != 'y':
                    results["manual_action_required"].append(pkg_name)
                    continue
            
            if has_internet or offline_path:
                success = install_python_package(pkg_name, offline_path)
                if success:
                    results["success"].append(pkg_name)
                else:
                    results["failure"].append(pkg_name)
            else:
                logger.warning(f"No internet connection and no offline path provided. Cannot install {pkg_name}.")
                results["failure"].append(pkg_name)
    
    # Handle external dependencies
    if missing_deps["external"]:
        logger.info("Handling external dependencies...")
        
        platform_name = get_platform()
        pm_name = check_package_manager(platform_name)
        
        for dep_name, dep_info in missing_deps["external"].items():
            if interactive:
                if pm_name:
                    response = input(f"Attempt to install {dep_info['name']} using {pm_name}? (y/n): ").lower()
                    if response != 'y':
                        results["manual_action_required"].append(dep_name)
                        continue
                else:
                    logger.info(f"No package manager detected. Manual installation required for {dep_info['name']}.")
                    print(f"Please install {dep_info['name']} manually from: {dep_info['url']}")
                    results["manual_action_required"].append(dep_name)
                    continue
            
            if has_internet and pm_name:
                success = install_external_dependency(dep_name, dep_info)
                if success:
                    results["success"].append(dep_name)
                else:
                    results["manual_action_required"].append(dep_name)
                    print(f"Automatic installation failed. Please install {dep_info['name']} manually from: {dep_info['url']}")
            else:
                logger.warning(f"Cannot automatically install {dep_info['name']}. Manual installation required.")
                results["manual_action_required"].append(dep_name)
                print(f"Please install {dep_info['name']} manually from: {dep_info['url']}")
    
    return results

def generate_report(missing_deps: Dict[str, Dict], install_results: Dict[str, List[str]]) -> str:
    """Generate a formatted report of dependency status."""
    lines = ["DEPENDENCY STATUS REPORT", "=======================", ""]
    
    # Report on Python packages
    lines.append("Python Packages:")
    if not missing_deps["python"] and not any(pkg in install_results["success"] for pkg in CORE_PACKAGES.values()):
        lines.append("  ✓ All required Python packages are installed")
    else:
        for pkg_name, pkg_info in missing_deps["python"].items():
            status = "✓ Installed" if pkg_name in install_results["success"] else \
                     "⚠ Installation Failed" if pkg_name in install_results["failure"] else \
                     "⚠ Manual Installation Required"
            lines.append(f"  {status}: {pkg_name} - {pkg_info['purpose']}")
    
    # Report on external dependencies
    lines.append("\nExternal Dependencies:")
    if not missing_deps["external"] and not any(dep in install_results["success"] for dep in EXTERNAL_DEPENDENCIES[get_platform()]):
        lines.append("  ✓ All required external tools are installed")
    else:
        for dep_name, dep_info in missing_deps["external"].items():
            status = "✓ Installed" if dep_name in install_results["success"] else \
                     "⚠ Manual Installation Required"
            lines.append(f"  {status}: {dep_info['name']} - {dep_info['purpose']}")
            if status.startswith("⚠"):
                lines.append(f"    → Download from: {dep_info['url']}")
                
                # Add package manager instructions if available
                platform_name = get_platform()
                if platform_name == "windows" and "chocolatey" in dep_info["package_manager_info"]:
                    lines.append(f"    → Or install with Chocolatey: choco install {dep_info['package_manager_info']['chocolatey']} -y")
                elif platform_name == "macos" and "homebrew" in dep_info["package_manager_info"]:
                    lines.append(f"    → Or install with Homebrew: brew install {dep_info['package_manager_info']['homebrew']}")
                elif platform_name == "linux":
                    pm = check_package_manager(platform_name)
                    if pm and pm in dep_info["package_manager_info"]:
                        cmd = PACKAGE_MANAGERS["linux"]["variants"][pm]["install_cmd"].format(dep_info["package_manager_info"][pm])
                        lines.append(f"    → Or install with {pm}: {cmd}")
    
    # Add summary
    total_missing = len(missing_deps["python"]) + len(missing_deps["external"])
    total_installed = len(install_results["success"])
    total_failed = len(install_results["failure"])
    total_manual = len(install_results["manual_action_required"])
    
    lines.append("\nSummary:")
    lines.append(f"  Total dependencies checked: {total_missing + total_installed}")
    lines.append(f"  Successfully installed: {total_installed}")
    lines.append(f"  Installation failed: {total_failed}")
    lines.append(f"  Manual installation required: {total_manual}")
    
    if total_failed > 0 or total_manual > 0:
        lines.append("\nRecommendations:")
        if total_failed > 0:
            lines.append("  • Run the dependency check again after resolving any network issues")
        if total_manual > 0:
            lines.append("  • Install the required external tools manually")
            lines.append("  • Consult the documentation at docs/installation.md for detailed instructions")
    
    return "\n".join(lines)

def create_dependency_bundle(output_dir: str, formats: Optional[List[str]] = None) -> str:
    """
    Create a bundle of dependencies for offline installation.
    
    Args:
        output_dir: Directory where the bundle will be created
        formats: List of format categories to include. If None, include all formats.
        
    Returns:
        Path to the created bundle directory
    """
    bundle_dir = os.path.join(output_dir, "fileconverter_vendor")
    os.makedirs(bundle_dir, exist_ok=True)
    
    # Collect all Python packages to bundle
    packages_to_bundle = list(CORE_PACKAGES.values())
    
    if formats is None:
        formats = list(FORMAT_PACKAGES.keys())
        
    for format_name in formats:
        if format_name in FORMAT_PACKAGES:
            packages_to_bundle.extend(FORMAT_PACKAGES[format_name].values())
    
    # Download packages
    logger.info(f"Downloading {len(packages_to_bundle)} packages to {bundle_dir}...")
    try:
        cmd = [
            sys.executable, "-m", "pip", "download",
            "--dest", bundle_dir,
            *packages_to_bundle
        ]
        subprocess.run(cmd, check=True)
        
        # Create README file with instructions
        readme_path = os.path.join(bundle_dir, "README.txt")
        with open(readme_path, "w") as f:
            f.write("FileConverter Offline Installation Package\n")
            f.write("======================================\n\n")
            f.write("This directory contains Python packages required by FileConverter for offline installation.\n\n")
            f.write("To install FileConverter with these packages:\n\n")
            f.write(f"pip install --no-index --find-links={bundle_dir} fileconverter[all]\n\n")
            f.write("Or for specific components:\n\n")
            f.write(f"pip install --no-index --find-links={bundle_dir} fileconverter[gui]\n")
        
        logger.info(f"Successfully created dependency bundle at {bundle_dir}")
        return bundle_dir
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create dependency bundle: {e}")
        return None

def main():
    """Main function to run the dependency manager."""
    import argparse
    
    parser = argparse.ArgumentParser(description="FileConverter Dependency Manager")
    parser.add_argument("--check", action="store_true", help="Check for missing dependencies")
    parser.add_argument("--install", action="store_true", help="Attempt to install missing dependencies")
    parser.add_argument("--offline", metavar="PATH", help="Use offline package repository")
    parser.add_argument("--create-bundle", metavar="PATH", help="Create an offline dependency bundle")
    parser.add_argument("--format", action="append", dest="formats", help="Specific format categories to check/bundle")
    parser.add_argument("--non-interactive", action="store_true", help="Don't prompt for confirmation")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")
    
    if args.create_bundle:
        output_dir = args.create_bundle
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        bundle_path = create_dependency_bundle(output_dir, args.formats)
        if bundle_path:
            print(f"Dependency bundle created successfully at {bundle_path}")
        else:
            print("Failed to create dependency bundle")
        return
    
    if args.check or args.install:
        missing_deps = detect_missing_dependencies(args.formats)
        
        if not missing_deps["python"] and not missing_deps["external"]:
            print("All dependencies are installed and ready to use.")
            return
        
        print(f"Found {len(missing_deps['python'])} missing Python packages and "
              f"{len(missing_deps['external'])} missing external dependencies.")
        
        if args.install:
            install_results = auto_install_dependencies(
                missing_deps, 
                offline_path=args.offline,
                interactive=not args.non_interactive
            )
            
            # Generate and print the report
            report = generate_report(missing_deps, install_results)
            print("\n" + report)
        else:
            # Just report what's missing without attempting installation
            for pkg_name, pkg_info in missing_deps["python"].items():
                print(f"Missing Python package: {pkg_name} - {pkg_info['purpose']}")
            
            for dep_name, dep_info in missing_deps["external"].items():
                print(f"Missing external dependency: {dep_info['name']} - {dep_info['purpose']}")
                print(f"  Download from: {dep_info['url']}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

### Step 2: Modify setup.py to Integrate Dependency Management

Update the `CustomInstallCommand` class in `setup.py`:

```python
# Add to existing import section
import importlib.util

# This section should be added to the CustomInstallCommand class in setup.py
def run(self):
    # Import and run dependency manager during installation
    try:
        # First try to import directly in case this is a reinstall
        spec = importlib.util.find_spec('fileconverter.dependency_manager')
        if spec:
            from fileconverter.dependency_manager import detect_missing_dependencies, auto_install_dependencies
            print("Checking for required dependencies...")
            missing_deps = detect_missing_dependencies()
            if missing_deps["python"] or missing_deps["external"]:
                print(f"Found {len(missing_deps['python'])} missing Python packages and "
                      f"{len(missing_deps['external'])} missing external dependencies.")
                
                # Only try to auto-install Python packages during setup, not external tools
                # This prevents elevated privilege issues and improves installation speed
                python_only_deps = {"python": missing_deps["python"], "external": {}}
                install_results = auto_install_dependencies(
                    python_only_deps,
                    interactive=False  # Non-interactive during setup
                )
                
                # Notify about external dependencies that will need manual installation
                if missing_deps["external"]:
                    print("\nSome external tools may require manual installation after setup:")
                    for dep_name, dep_info in missing_deps["external"].items():
                        print(f"  • {dep_info['name']} - {dep_info['purpose']}")
                        print(f"    Download from: {dep_info['url']}")
        else:
            print("Dependency manager will be available after installation")
    except Exception as e:
        print(f"Note: Dependency check could not be performed during installation: {e}")
        print("You can run the dependency check manually after installation with:")
        print("  python -m fileconverter.dependency_manager --check --install")
    
    # Continue with normal installation
    install.run(self)

    # Run remaining install steps
    try:
        self.execute(generate_icon, [], msg="Generating application icon...")
        self.execute(create_desktop_shortcut, [], msg="Creating desktop shortcut...")
        self.execute(self.add_to_path, [], msg="Adding to system PATH...")
        self.execute(self.register_application, [], msg="Registering application...")
    except Exception as e:
        print(f"Warning: Some installation steps failed: {e}")
        print("The application will still work, but some system integration features may be limited.")
```

### Step 3: Update Extras in setup.py

Update the `extras_require` dictionary in `setup.py` to organize dependencies by format:

```python
# Define extra dependencies
extras_require = {
    # GUI dependencies
    'gui': ['PyQt6>=6.5.2', 'PyQt6-QScintilla>=2.14.1', 'Pillow>=10.0.0'],
    
    # Format-specific dependencies
    'document': [
        'python-docx>=1.1.2', 'PyPDF2>=3.0.1', 'Markdown>=3.7',
        'dicttoxml>=1.7.16', 'xmltodict>=0.14.2', 'lxml>=5.3.1'
    ],
    'spreadsheet': [
        'openpyxl>=3.1.5', 'pandas>=2.2.3', 'xlrd>=2.0.1', 'XlsxWriter>=3.2.2',
        'tabulate>=0.9.0', 'et_xmlfile>=2.0.0'
    ],
    'image': [
        'Pillow>=11.1.0', 'Wand>=0.6.13'
    ],
    'archive': [
        'py7zr>=0.22.0', 'pyzstd>=0.16.2', 'pyppmd>=1.1.1',
        'pybcj>=1.0.3', 'inflate64>=1.0.1', 'multivolumefile>=0.2.3'
    ],
    
    # Development tools
    'dev': [
        'pytest>=8.3.5', 'black>=23.7.0', 'mypy>=1.5.1',
        'flake8>=6.1.0', 'isort>=5.12.0', 'sphinx>=7.1.2',
        'sphinx-rtd-theme>=1.3.0'
    ],
    
    # Platform-specific dependencies
    'windows_installer': ['pywin32', 'winshell', 'pyinstaller'],
    
    # Empty placeholder for platform-specific dependencies
    'installer': [],
    
    # All dependencies (will be populated)
    'all': []
}

# Add platform-specific dependencies
if platform.system() == "Windows":
    extras_require['installer'] = extras_require['windows_installer']

# Add a meta extra that includes everything
extras_require['all'] = sorted(set(sum((deps for name, deps in extras_require.items()
                                    if name != 'all'), [])))
```

### Step 4: Integrate Dependency Checks in Launch Scripts

Add dependency checking to `fileconverter/main.py`:

```python
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
                print("Run 'python -m fileconverter.dependency_manager --check --install' to fix.")
                
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

def main():
    """Main entry point for the application."""
    # Parse arguments first to check for --skip-dependency-check
    import argparse
    parser = argparse.ArgumentParser(description="FileConverter")
    parser.add_argument("--skip-dependency-check", action="store_true", 
                        help="Skip dependency checking (for advanced users)")
    parser.add_argument("--gui", action="store_true", help="Launch the GUI")
    
    # Parse only known args to avoid conflicts with other argument parsers
    args, remaining_args = parser.parse_known_args()
    
    # Check dependencies unless explicitly skipped
    missing_critical = False
    if not args.skip_dependency_check:
        missing_critical = check_dependencies()
        
        if missing_critical:
            # Exit with error if critical dependencies are missing
            print("Error: Critical dependencies are missing. Cannot continue.")
            print("Please install the required dependencies and try again.")
            return 1
    
    # Continue with original main function logic...
```

### Step 5: Add CLI Commands for Dependency Management

Add dependency commands to `fileconverter/cli.py`:

```python
def add_dependency_commands(subparsers):
    """Add dependency management commands to the CLI."""
    # Add dependency check command
    dep_parser = subparsers.add_parser(
        "dependencies",
        help="Manage dependencies"
    )
    dep_subparsers = dep_parser.add_subparsers(dest="dep_command")
    
    # Check subcommand
    check_parser = dep_subparsers.add_parser(
        "check",
        help="Check for missing dependencies"
    )
    check_parser.add_argument(
        "--format",
        action="append",
        dest="formats",
        help="Specific format categories to check"
    )
    
    # Install subcommand
    install_parser = dep_subparsers.add_parser(
        "install",
        help="Install missing dependencies"
    )
    install_parser.add_argument(
        "--offline",
        metavar="PATH",
        help="Use offline package repository"
    )
    install_parser.add_argument(
        "--format",
        action="append",
        dest="formats",
        help="Specific format categories to install"
    )
    
    # Bundle subcommand
    bundle_parser = dep_subparsers.add_parser(
        "bundle",
        help="Create an offline dependency bundle"
    )
    bundle_parser.add_argument(
        "output_dir",
        help="Directory where the bundle will be created"
    )
    bundle_parser.add_argument(
        "--format",
        action="append",
        dest="formats",
        help="Specific format categories to bundle"
    )

# Update the main parser setup to include dependency commands
def create_parser():
    # ... existing parser setup code ...
    
    # Add the dependency commands
    add_dependency_commands(subparsers)
    
    # ... rest of the parser setup ...

# Add handler for dependency commands in the main function
def main():
    # ... existing code to create parser and parse args ...
    
    if hasattr(args, 'dep_command'):
        from fileconverter.dependency_manager import (
            detect_missing_dependencies, 
            auto_install_dependencies,
            create_dependency_bundle,
            generate_report
        )
        
        if args.dep_command == "check":
            missing_deps = detect_missing_dependencies(args.formats)
            if not missing_deps["python"] and not missing_deps["external"]:
                print("All dependencies are installed and ready to use.")
                return 0
            
            # Create empty results structure for report
            empty_results = {"success": [], "failure": [], "manual_action_required": []}
            report = generate_report(missing_deps, empty_results)
            print(report)
            
        elif args.dep_command == "install":
            missing_deps = detect_missing_dependencies(args.formats)
            if not missing_deps["python"] and not missing_deps["external"]:
                print("All dependencies are installed and ready to use.")
                return 0
                
            install_results = auto_install_dependencies(
                missing_deps,
                offline_path=args.offline,
                interactive=True
            )
            
            report = generate_report(missing_deps, install_results)
            print(report)
            
        elif args.dep_command == "bundle":
            bundle_path = create_dependency_bundle(args.output_dir, args.formats)
            if bundle_path:
                print(f"Dependency bundle created successfully at {bundle_path}")
                return 0
            else:
                print("Failed to create dependency bundle")
                return 1
                
        return 0
    
    # ... rest of main function ...
```

### Step 6: Create Offline Installation Bundle Script

Create `scripts/create_offline_bundle.py` for bundling dependencies for offline installation:

```python
#!/usr/bin/env python3
"""
FileConverter Offline Installer Bundle Creator

This script creates a complete offline installation bundle for FileConverter,
including all required Python packages and instructions for external dependencies.
"""

import os
import sys
import shutil
import subprocess
import platform
import argparse
from pathlib import Path

def create_offline_bundle(output_dir, include_gui=True, include_dev=False):
    """Create a complete offline installation bundle."""
    bundle_dir = os.path.join(output_dir, "fileconverter-offline")
    os.makedirs(bundle_dir, exist_ok=True)
    
    # Create subdirectories
    vendor_dir = os.path.join(bundle_dir, "vendor")
    os.makedirs(vendor_dir, exist_ok=True)
    
    docs_dir = os.path.join(bundle_dir, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    
    installer_dir = os.path.join(bundle_dir, "installer")
    os.makedirs(installer_dir, exist_ok=True)
    
    # Get extras based on options
    extras = ["all"] if include_gui and include_dev else \
             ["gui"] if include_gui else \
             ["dev"] if include_dev else []
    extras_str = ",".join(extras) if extras else ""
    
    # Download all required packages to the vendor directory
    print(f"Downloading Python packages to {vendor_dir}...")
    extra_args = f"[{extras_str}]" if extras_str else ""
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "download",
            "--dest", vendor_dir,
            f"fileconverter{extra_args}"
        ], check=True)
        print("✓ Successfully downloaded Python packages")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading packages: {e}")
        return False
    
    # Create platform-specific installer scripts
    if platform.system() == "Windows":
        create_windows_installer(installer_dir, extras_str)
    elif platform.system() == "Darwin":  # macOS
        create_macos_installer(installer_dir, extras_str)
    elif platform.system() == "Linux":
        create_linux_installer(installer_dir, extras_str)
    
    # Copy documentation files
    try:
        shutil.copy("README.md", os.path.join(docs_dir, "README.md"))
        shutil.copy("docs/installation.md", os.path.join(docs_dir, "installation.md"))
        shutil.copy("docs/troubleshooting.md", os.path.join(docs_dir, "troubleshooting.md"))
        print("✓ Copied documentation files")
    except Exception as e:
        print(f"Warning: Could not copy some documentation files: {e}")
    
    # Create README for offline bundle
    create_offline_readme(bundle_dir, extras_str)
    
    print(f"\nOffline bundle created successfully at: {bundle_dir}")
    return True

def create_windows_installer(installer_dir, extras_str):
    """Create Windows batch file installer."""
    batch_path = os.path.join(installer_dir, "install.bat")
    
    with open(batch_path, "w") as f:
        f.write("@echo off\n")
        f.write("echo FileConverter Offline Installer\n")
        f.write("echo ============================\n")
        f.write("echo.\n")
        f.write("echo This will install FileConverter and its dependencies.\n")
        f.write("echo.\n")
        f.write("pause\n")
        f.write("echo.\n")
        f.write("echo Installing Python packages...\n")
        extra_args = f"[{extras_str}]" if extras_str else ""
        f.write(f'python -m pip install --no-index --find-links=..\\vendor fileconverter{extra_args}\n')
        f.write("if %ERRORLEVEL% NEQ 0 (\n")
        f.write("    echo Error during installation. Please check the error message above.\n")
        f.write("    pause\n")
        f.write("    exit /b 1\n")
        f.write(")\n")
        f.write("echo.\n")
        f.write("echo Installation complete!\n")
        f.write("echo.\n")
        f.write("echo You can now run FileConverter by typing 'fileconverter' in a command prompt\n")
        f.write("echo or by launching 'fileconverter-gui' for the graphical interface.\n")
        f.write("echo.\n")
        f.write("echo You may also need to install external tools. Run:\n")
        f.write("echo     fileconverter dependencies check\n")
        f.write("echo.\n")
        f.write("pause\n")
    
    print("✓ Created Windows installer script")

def create_macos_installer(installer_dir, extras_str):
    """Create macOS shell script installer."""
    script_path = os.path.join(installer_dir, "install.sh")
    
    with open(script_path, "w") as f:
        f.write("#!/bin/bash\n")
        f.write("echo \"FileConverter Offline Installer\"\n")
        f.write("echo \"============================\"\n")
        f.write("echo\n")
        f.write("echo \"This will install FileConverter and its dependencies.\"\n")
        f.write("echo\n")
        f.write("read -p \"Press Enter to continue...\"\n")
        f.write("echo\n")
        f.write("echo \"Installing Python packages...\"\n")
        extra_args = f"[{extras_str}]" if extras_str else ""
        f.write(f"python3 -m pip install --no-index --find-links=../vendor fileconverter{extra_args}\n")
        f.write("if [ $? -ne 0 ]; then\n")
        f.write("    echo \"Error during installation. Please check the error message above.\"\n")
        f.write("    read -p \"Press Enter to exit...\"\n")
        f.write("    exit 1\n")
        f.write("fi\n")
        f.write("echo\n")
        f.write("echo \"Installation complete!\"\n")
        f.write("echo\n")
        f.write("echo \"You can now run FileConverter by typing 'fileconverter' in a terminal\"\n")
        f.write("echo \"or by launching 'fileconverter-gui' for the graphical interface.\"\n")
        f.write("echo\n")
        f.write("echo \"You may also need to install external tools. Run:\"\n")
        f.write("echo \"    fileconverter dependencies check\"\n")
        f.write("echo\n")
        f.write("read -p \"Press Enter to exit...\"\n")
    
    # Make script executable
    os.chmod(script_path, 0o755)
    print("✓ Created macOS installer script")

def create_linux_installer(installer_dir, extras_str):
    """Create Linux shell script installer."""
    script_path = os.path.join(installer_dir, "install.sh")
    
    with open(script_path, "w") as f:
        f.write("#!/bin/bash\n")
        f.write("echo \"FileConverter Offline Installer\"\n")
        f.write("echo \"============================\"\n")
        f.write("echo\n")
        f.write("echo \"This will install FileConverter and its dependencies.\"\n")
        f.write("echo\n")
        f.write("read -p \"Press Enter to continue...\"\n")
        f.write("echo\n")
        f.write("echo \"Installing Python packages...\"\n")
        extra_args = f"[{extras_str}]" if extras_str else ""
        f.write(f"python3 -m pip install --no-index --find-links=../vendor fileconverter{extra_args}\n")
        f.write("if [ $? -ne 0 ]; then\n")
        f.write("    echo \"Error during installation. Please check the error message above.\"\n")
        f.write("    read -p \"Press Enter to exit...\"\n")
        f.write("    exit 1\n")
        f.write("fi\n")
        f.write("echo\n")
        f.write("echo \"Installation complete!\"\n")
        f.write("echo\n")
        f.write("echo \"You can now run FileConverter by typing 'fileconverter' in a terminal\"\n")
        f.write("echo \"or by launching 'fileconverter-gui' for the graphical interface.\"\n")
        f.write("echo\n")
        f.write("echo \"You may also need to install external tools. Run:\"\n")
        f.write("echo \"    fileconverter dependencies check\"\n")
        f.write("echo\n")
        f.write("read -p \"Press Enter to exit...\"\n")
    
    # Make script executable
    os.chmod(script_path, 0o755)
    print("✓ Created Linux installer script")

def create_offline_readme(bundle_dir, extras_str):
    """Create README file for the offline bundle."""
    readme_path = os.path.join(bundle_dir, "README.txt")
    
    with open(readme_path, "w") as f:
        f.write("FileConverter Offline Installation Bundle\n")
        f.write("======================================\n\n")
        f.write("This bundle contains everything you need to install FileConverter without an internet connection.\n\n")
        
        f.write("Quick Start:\n")
        f.write("------------\n")
        if platform.system() == "Windows":
            f.write("1. Run installer\\install.bat to install FileConverter\n")
        else:
            f.write("1. Run installer/install.sh to install FileConverter\n")
        f.write("2. Launch FileConverter using:\n")
        f.write("   - Command line: fileconverter\n")
        f.write("   - GUI: fileconverter-gui\n\n")
        
        f.write("Contents:\n")
        f.write("---------\n")
        f.write("- vendor/: Python packages for offline installation\n")
        f.write("- installer/: Installation scripts\n")
        f.write("- docs/: Documentation files\n\n")
        
        f.write("External Dependencies:\n")
        f.write("---------------------\n")
        f.write("Some FileConverter features require external tools that must be installed separately:\n\n")
        
        f.write("- LibreOffice: Required for DOC/DOCX/ODT conversions\n")
        f.write("  Download from: https://www.libreoffice.org/download/download/\n\n")
        
        f.write("- wkhtmltopdf: Required for HTML to PDF conversion\n")
        f.write("  Download from: https://wkhtmltopdf.org/downloads.html\n\n")
        
        f.write("- ImageMagick: Required for advanced image conversions\n")
        f.write("  Download from: https://imagemagick.org/script/download.php\n\n")
        
        f.write("Manual Installation:\n")
        f.write("-------------------\n")
        extra_args = f"[{extras_str}]" if extras_str else ""
        f.write(f"If the installer script fails, you can install manually with:\n\n")
        f.write(f"pip install --no-index --find-links=vendor fileconverter{extra_args}\n\n")
        
        f.write("For more information, see the documentation in the docs/ directory.\n")
    
    print("✓ Created offline bundle README")

def main():
    parser = argparse.ArgumentParser(description="Create FileConverter offline installation bundle")
    parser.add_argument("output_dir", help="Directory where the bundle will be created")
    parser.add_argument("--no-gui", action="store_true", help="Exclude GUI dependencies")
    parser.add_argument("--include-dev", action="store_true", help="Include development dependencies")
    
    args = parser.parse_args()
    
    output_dir = os.path.expanduser(os.path.expandvars(args.output_dir))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    create_offline_bundle(
        output_dir, 
        include_gui=not args.no_gui,
        include_dev=args.include_dev
    )

if __name__ == "__main__":
    main()
```

### Step 7: Create Dependency Manager Tests

Create `tests/test_dependency_manager.py` for testing the dependency management system:

```python
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

def run_tests():
    """Run all dependency manager tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDependencyManager)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
    print("Testing FileConverter dependency management system...")
    run_tests()
```

### Step 8: Update Documentation

Update `docs/installation.md` to add a section on dependency management:

```markdown
## Dependency Management

FileConverter now includes a sophisticated dependency management system that automatically detects, installs, and configures all required dependencies. This makes installation seamless for users with limited technical expertise.

### Automatic Dependency Detection

FileConverter automatically checks for required dependencies:

- When you first run the application
- During installation via `pip install`
- When you explicitly check with `fileconverter dependencies check`

The dependency manager detects both Python packages (installed via pip) and external tools (such as LibreOffice, wkhtmltopdf, and ImageMagick).

### Automatic Installation

If missing dependencies are detected, FileConverter can automatically install them:

```bash
# Check and install all missing dependencies
fileconverter dependencies install

# Install dependencies for specific formats
fileconverter dependencies install --format=document --format=image
```

For Python packages, installation happens automatically using pip. For external tools, the dependency manager will:

1. Detect your operating system
2. Check for available package managers (Chocolatey on Windows, Homebrew on macOS, apt/yum/dnf on Linux)
3. Attempt to install the tools using the appropriate package manager
4. Provide clear instructions if automatic installation is not possible

### Offline Installation

For environments without internet access, FileConverter provides robust offline installation options:

1. **Pre-built Offline Bundles**: Download complete offline installation bundles from the [releases page](https://github.com/tsgfulfillment/fileconverter/releases).

2. **Create Custom Offline Bundles**: If you have specific needs, you can create your own offline bundle:

   ```bash
   # Create a complete offline bundle
   fileconverter dependencies bundle /path/to/output/directory
   
   # Create a bundle for specific formats
   fileconverter dependencies bundle /path/to/output/directory --format=document
   ```

3. **Install from an Offline Bundle**:

   ```bash
   # Windows
   cd fileconverter-offline
   installer\install.bat
   
   # macOS/Linux
   cd fileconverter-offline
   ./installer/install.sh
   ```
```

Update `docs/troubleshooting.md` to add dependency-related troubleshooting:

```markdown
## Dependency Issues

### Python Package Installation Failures

If you encounter issues installing Python packages:

1. **Check your internet connection**
2. **Make sure pip is up to date**:
   ```bash
   python -m pip install --upgrade pip
   ```
3. **Try installing with verbose output**:
   ```bash
   python -m pip install package_name -v
   ```
4. **Use an offline bundle**:
   ```bash
   # Create an offline bundle from a machine with internet
   fileconverter dependencies bundle /path/to/output
   
   # Then transfer to the target machine and install
   ```

### External Tool Issues

If automatic installation of external tools fails:

1. **Check dependency status**:
   ```bash
   fileconverter dependencies check
   ```

2. **Install manually**:
   - **Windows**: Download installers from the provided URLs and run them
   - **macOS**: Use Homebrew or download installers
   - **Linux**: Use your system's package manager

3. **Verify installation paths**:
   - Make sure the tools are in standard installation locations
   - Add installation directories to your system PATH if needed

### Network-Restricted Environments

For environments with limited or no internet access:

1. **Create an offline bundle** on a machine with internet access
2. **Transfer the bundle** to the restricted environment
3. **Install using the offline installer**
4. **Manually install external tools** as needed
```

### Step 9: Run Tests

Run the dependency management tests:

```bash
python -m tests.test_dependency_manager
```

Ensure all tests pass before proceeding to the next step.

## Testing Procedures

After implementing the dependency management system, follow these testing procedures to verify its functionality:

### 1. Test Dependency Detection

```bash
# Run dependency check
python -m fileconverter.dependency_manager --check
```

Verify that:
- Python packages are correctly detected
- External tools are correctly detected
- Platform-specific detection works properly

### 2. Test Python Package Installation

```bash
# Install a specific package
python -m fileconverter.dependency_manager --install --format=document
```

Verify that:
- Required packages are installed automatically
- Installation progress is reported correctly
- Failures are handled gracefully

### 3. Test External Tool Installation

```bash
# Install external tools
python -m fileconverter.dependency_manager --install
```

Verify that:
- The system correctly detects available package managers
- Installation commands are correct for the platform
- Manual installation instructions are clear when automatic installation fails

### 4. Test Offline Installation

```bash
# Create an offline bundle
python -m fileconverter.dependency_manager --create-bundle ./offline_bundle
```

Verify that:
- The bundle contains all required packages
- Platform-specific installer scripts are created
- README instructions are clear and accurate

### 5. Test Integration with Application Launch

```bash
# Run the application
python -m fileconverter.main
```

Verify that:
- Dependency checks run at startup
- Missing dependencies are reported
- Critical dependency failures prevent application launch
- Non-critical dependencies show warnings but allow continuing

### 6. Test CLI Commands

```bash
# Check dependency status
python -m fileconverter.cli dependencies check

# Install dependencies
python -m fileconverter.cli dependencies install

# Create offline bundle
python -m fileconverter.cli dependencies bundle ./offline_bundle
```

Verify that:
- CLI commands work as expected
- Output is clear and helpful
- Error handling is robust

## Rollout Strategy

Follow these steps to roll out the dependency management system:

### 1. Initial Development Release

1. Implement the dependency manager as described in this document
2. Add comprehensive tests
3. Release as a beta feature in the next development version

### 2. Testing and Refinement

1. Gather feedback from early adopters
2. Refine the system based on feedback
3. Add support for additional external tools as needed

### 3. Documentation and Training

1. Update all documentation to include dependency management features
2. Create video tutorials showing dependency installation
3. Provide training for support staff

### 4. Full Release

1. Include the dependency management system in the next major release
2. Highlight the feature in release notes
3. Provide offline bundles for common platforms
4. Monitor support requests for dependency-related issues

### 5. Ongoing Maintenance

1. Regularly update the dependency mappings for new versions
2. Add support for new package managers as they become popular
3. Monitor for changes in external tool installation procedures
4. Expand the system to support additional dependencies as needed

## Conclusion

This implementation plan provides a comprehensive approach to dependency management for FileConverter. By following these steps, you'll create a robust system that:

1. Automatically detects and installs required dependencies
2. Supports all major platforms (Windows, macOS, Linux)
3. Provides clear feedback and instructions
4. Handles offline installations for network-restricted environments
5. Integrates smoothly with the existing codebase

The system is designed to be user-friendly for those with limited technical expertise while providing advanced options for power users and enterprise deployments.