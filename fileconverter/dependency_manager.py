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
    if not missing_deps["external"] and not any(dep in install_results["success"] for dep in EXTERNAL_DEPENDENCIES.get(get_platform(), {})):
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