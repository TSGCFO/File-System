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
    extras = []
    if include_gui:
        extras.append("gui")
    if include_dev:
        extras.append("dev")
    
    # Always include core document, spreadsheet, and image formats
    format_extras = ["document", "spreadsheet", "image"]
    extras.extend(format_extras)
    
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
        # Find project root - this is where docs should be
        project_root = find_project_root()
        if project_root:
            # Copy main documentation files
            for doc_file in ["README.md", "docs/installation.md", "docs/troubleshooting.md", 
                             "docs/dependency_management_implementation.md"]:
                src_path = os.path.join(project_root, doc_file)
                if os.path.exists(src_path):
                    dest_path = os.path.join(docs_dir, os.path.basename(doc_file))
                    shutil.copy(src_path, dest_path)
                    print(f"✓ Copied {doc_file} to docs directory")
                else:
                    print(f"Warning: Could not find {doc_file}")
            
            # Create a specific offline installation guide
            create_offline_guide(docs_dir)
        else:
            print("Warning: Could not find project root, skipping documentation copy")
    except Exception as e:
        print(f"Warning: Could not copy some documentation files: {e}")
    
    # Create README for offline bundle
    create_offline_readme(bundle_dir, extras_str)
    
    print(f"\nOffline bundle created successfully at: {bundle_dir}")
    return True

def find_project_root():
    """Find the root directory of the project."""
    # Start from the directory of this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Go up to three levels looking for a setup.py file
    for _ in range(3):
        if os.path.exists(os.path.join(current_dir, "setup.py")):
            return current_dir
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # We've reached the root
            break
        current_dir = parent_dir
    
    # If we can't find it, return the current directory as a fallback
    return os.path.dirname(os.path.abspath(__file__))

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

def create_offline_guide(docs_dir):
    """Create a guide specifically for offline installation."""
    guide_path = os.path.join(docs_dir, "OFFLINE_INSTALLATION.md")
    
    with open(guide_path, "w") as f:
        f.write("# FileConverter Offline Installation Guide\n\n")
        f.write("This document provides instructions for installing FileConverter in environments without internet access.\n\n")
        
        f.write("## Quick Start\n\n")
        f.write("### Windows\n\n")
        f.write("1. Navigate to the `installer` directory\n")
        f.write("2. Run `install.bat`\n")
        f.write("3. Follow the on-screen instructions\n\n")
        
        f.write("### macOS/Linux\n\n")
        f.write("1. Navigate to the `installer` directory\n")
        f.write("2. Run `./install.sh`\n")
        f.write("3. Follow the on-screen instructions\n\n")
        
        f.write("## Manual Installation\n\n")
        f.write("If the installer scripts don't work, you can install manually:\n\n")
        f.write("```bash\n")
        f.write("# Navigate to the bundle directory\n")
        f.write("cd fileconverter-offline\n\n")
        f.write("# Install FileConverter with pip\n")
        f.write("pip install --no-index --find-links=vendor fileconverter[gui]\n")
        f.write("```\n\n")
        
        f.write("## Installing External Dependencies\n\n")
        f.write("After installing the Python packages, you'll need to install external tools required for certain conversions:\n\n")
        
        f.write("### Windows\n\n")
        f.write("1. LibreOffice: Download and install from https://www.libreoffice.org/download/download/\n")
        f.write("2. wkhtmltopdf: Download and install from https://wkhtmltopdf.org/downloads.html\n")
        f.write("3. ImageMagick: Download and install from https://imagemagick.org/script/download.php#windows\n\n")
        
        f.write("### macOS\n\n")
        f.write("If you have access to a mac with internet and Homebrew installed, you can download these packages as bottles:\n\n")
        f.write("```bash\n")
        f.write("brew fetch --bottle libreoffice wkhtmltopdf imagemagick\n")
        f.write("```\n\n")
        f.write("Then transfer the downloaded bottles to the offline machine and install them with `brew install`.\n\n")
        
        f.write("### Linux\n\n")
        f.write("Download the packages on a machine with internet access:\n\n")
        f.write("```bash\n")
        f.write("# For Debian/Ubuntu\n")
        f.write("apt download libreoffice wkhtmltopdf imagemagick\n\n")
        f.write("# For RHEL/CentOS\n")
        f.write("yumdownloader libreoffice wkhtmltopdf ImageMagick\n")
        f.write("```\n\n")
        f.write("Transfer the downloaded packages to the offline machine and install them with `dpkg -i` or `rpm -i`.\n\n")
        
        f.write("## Troubleshooting\n\n")
        f.write("If you encounter issues with the offline installation:\n\n")
        f.write("1. Check that Python and pip are installed and in your PATH\n")
        f.write("2. Verify that all required package files are present in the `vendor` directory\n")
        f.write("3. For more detailed errors, run pip with the `-v` flag for verbose output\n")
        f.write("4. Consult the full documentation in the `docs` directory\n")
    
    print("✓ Created offline installation guide")

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
        
        f.write("For detailed instructions, see docs/OFFLINE_INSTALLATION.md\n")
    
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