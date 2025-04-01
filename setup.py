#!/usr/bin/env python3
import os
import sys
import platform
import site
import shutil
import subprocess
from pathlib import Path
from setuptools import setup, find_packages, Command
from setuptools.command.install import install
from setuptools.command.develop import develop
from fileconverter.version import __version__

# Read the long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Parse requirements.txt to get dependencies
def get_requirements():
    with open("requirements.txt", "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Function to generate the icon for the application
def generate_icon():
    try:
        from fileconverter.gui.resources.icon_generator import generate_icon
        generate_icon()
        print("Successfully generated application icon")
    except Exception as e:
        print(f"Warning: Could not generate icon: {e}")
        print("Application will use default system icons")

# Function to create desktop shortcut
def create_desktop_shortcut():
    home_dir = Path.home()
    desktop_dir = home_dir / "Desktop"
    
    # First generate the icon
    generate_icon()
    
    if platform.system() == "Windows":
        try:
            # Windows desktop shortcut
            import winshell
            from win32com.client import Dispatch
            
            desktop = Path(winshell.desktop())
            shortcut_path = desktop / "FileConverter.lnk"
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(str(shortcut_path))
            
            # Get executable path
            python_executable = sys.executable
            shortcut.Targetpath = python_executable
            shortcut.Arguments = "-m fileconverter.main --gui"
            shortcut.IconLocation = os.path.join(sys.prefix, "Lib", "site-packages", "fileconverter", "gui", "resources", "icon.ico")
            shortcut.WorkingDirectory = str(home_dir)
            shortcut.save()
            
            print(f"Created desktop shortcut at {shortcut_path}")
        except Exception as e:
            print(f"Could not create Windows desktop shortcut: {e}")
        
    elif platform.system() == "Linux":
        try:
            # Linux desktop entry
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
            
            # Copy to desktop
            desktop_shortcut = desktop_dir / "fileconverter.desktop"
            if desktop_dir.exists():
                shutil.copy(desktop_entry_path, desktop_shortcut)
                os.chmod(desktop_shortcut, 0o755)
                print(f"Created desktop shortcut at {desktop_shortcut}")
        except Exception as e:
            print(f"Could not create Linux desktop shortcut: {e}")
        
    elif platform.system() == "Darwin":  # macOS
        try:
            # macOS application shortcut
            app_script = """#!/usr/bin/env bash
python -m fileconverter.main --gui
"""
            app_dir = home_dir / "Applications" / "FileConverter.app" / "Contents" / "MacOS"
            os.makedirs(app_dir, exist_ok=True)
            
            with open(app_dir / "FileConverter", "w") as f:
                f.write(app_script)
            
            os.chmod(app_dir / "FileConverter", 0o755)
            
            # Link to desktop if available
            if desktop_dir.exists():
                desktop_link = desktop_dir / "FileConverter.app"
                if desktop_link.exists() or os.path.islink(desktop_link):
                    if os.path.islink(desktop_link):
                        os.remove(desktop_link)
                    else:
                        shutil.rmtree(desktop_link)
                os.symlink(app_dir.parent.parent, desktop_link)
                print(f"Created desktop shortcut at {desktop_link}")
        except Exception as e:
            print(f"Could not create macOS desktop shortcut: {e}")

# Custom install command
class CustomInstallCommand(install):
    def run(self):
        # Make sure we have the icon generated before we run the installation
        generate_icon()
        install.run(self)
        
        try:
            self.execute(create_desktop_shortcut, [], msg="Creating desktop shortcut...")
            self.execute(self.add_to_path, [], msg="Adding to system PATH...")
            self.execute(self.register_application, [], msg="Registering application...")
        except Exception as e:
            print(f"Warning: Some installation steps failed: {e}")
            print("The application will still work, but some system integration features may be limited.")
    
    def add_to_path(self):
        if platform.system() == "Windows":
            try:
                # Create executable wrapper in a directory that's in PATH
                scripts_dir = Path(sys.prefix) / "Scripts"
                os.makedirs(scripts_dir, exist_ok=True)
                exe_path = scripts_dir / "fileconverter.exe"
                
                # Check if pyinstaller is available to create a standalone executable
                try:
                    import PyInstaller
                    print("Creating standalone executable with PyInstaller...")
                    spec_content = """
# -*- mode: python ; coding: utf-8 -*-
a = Analysis(['fileconverter_launcher.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='fileconverter',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          icon='fileconverter/gui/resources/icon.ico')
"""
                    # Create launcher script
                    launcher_script = """
import sys
from fileconverter.main import main
if __name__ == "__main__":
    sys.exit(main())
"""
                    with open("fileconverter_launcher.py", "w") as f:
                        f.write(launcher_script)
                    
                    with open("fileconverter.spec", "w") as f:
                        f.write(spec_content)
                    
                    subprocess.run(["pyinstaller", "fileconverter.spec"], check=True)
                    
                    # Copy executable to scripts directory
                    shutil.copy("dist/fileconverter.exe", exe_path)
                    
                    # Cleanup
                    for temp_file in ["fileconverter_launcher.py", "fileconverter.spec"]:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                    for temp_dir in ["build", "dist", "__pycache__"]:
                        if os.path.exists(temp_dir):
                            shutil.rmtree(temp_dir)
                    
                except (ImportError, subprocess.CalledProcessError) as e:
                    print(f"Could not create standalone executable: {e}")
                    print("Falling back to script-based launcher...")
                    
                    # Create a batch file launcher
                    batch_content = """@echo off
python -m fileconverter.cli %*
"""
                    gui_batch_content = """@echo off
python -m fileconverter.main --gui
"""
                    with open(scripts_dir / "fileconverter.bat", "w") as f:
                        f.write(batch_content)
                    with open(scripts_dir / "fileconverter-gui.bat", "w") as f:
                        f.write(gui_batch_content)
                    
                    print(f"Created batch launchers in {scripts_dir}")
            except Exception as e:
                print(f"Error setting up Windows executables: {e}")
        
        elif platform.system() == "Linux":
            try:
                # Create executable scripts in /usr/local/bin if possible, otherwise in ~/.local/bin
                bin_dirs = ["/usr/local/bin", os.path.expanduser("~/.local/bin")]
                
                for bin_dir in bin_dirs:
                    bin_path = Path(bin_dir)
                    if not bin_path.exists():
                        os.makedirs(bin_path, exist_ok=True)
                    
                    if os.access(bin_dir, os.W_OK):
                        for script_name, command in [
                            ("fileconverter", "python3 -m fileconverter.cli \"$@\""),
                            ("fileconverter-gui", "python3 -m fileconverter.main --gui")
                        ]:
                            script_path = bin_path / script_name
                            with open(script_path, "w") as f:
                                f.write(f"#!/bin/bash\n{command}\n")
                            os.chmod(script_path, 0o755)
                        
                        print(f"Created executable scripts in {bin_dir}")
                        break
                else:
                    print("Could not create executable scripts in system directories.")
                    print("Make sure ~/.local/bin is in your PATH.")
            except Exception as e:
                print(f"Error setting up Linux executables: {e}")
        
        elif platform.system() == "Darwin":  # macOS
            try:
                # Create executable scripts in /usr/local/bin if possible
                bin_dir = "/usr/local/bin"
                if os.access(bin_dir, os.W_OK):
                    for script_name, command in [
                        ("fileconverter", "python3 -m fileconverter.cli \"$@\""),
                        ("fileconverter-gui", "python3 -m fileconverter.main --gui")
                    ]:
                        script_path = os.path.join(bin_dir, script_name)
                        with open(script_path, "w") as f:
                            f.write(f"#!/bin/bash\n{command}\n")
                        os.chmod(script_path, 0o755)
                    
                    print(f"Created executable scripts in {bin_dir}")
                else:
                    print("Could not create executable scripts in system directories.")
                    print("Consider adding the scripts manually or adjusting permissions.")
            except Exception as e:
                print(f"Error setting up macOS executables: {e}")
    
    def register_application(self):
        if platform.system() == "Windows":
            try:
                import winreg
                
                # Register application in Windows registry
                key_path = r"Software\FileConverter"
                
                # Create the main application key
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
                winreg.SetValueEx(key, "InstallPath", 0, winreg.REG_SZ, os.path.abspath("."))
                winreg.SetValueEx(key, "Version", 0, winreg.REG_SZ, __version__)
                winreg.CloseKey(key)
                
                # Add to App Paths for Windows searching
                app_paths_key = r"Software\Microsoft\Windows\CurrentVersion\App Paths\fileconverter.exe"
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, app_paths_key)
                scripts_dir = Path(sys.prefix) / "Scripts"
                exe_path = scripts_dir / "fileconverter.exe"
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, str(exe_path))
                winreg.CloseKey(key)
                
                print("Registered application in Windows registry")
            except ImportError:
                print("Could not import winreg, skipping Windows registry registration")
            except Exception as e:
                print(f"Error registering application: {e}")
        
        elif platform.system() == "Linux":
            # Already created a .desktop file in create_desktop_shortcut
            pass
        
        elif platform.system() == "Darwin":  # macOS
            # macOS applications are typically registered by their presence in /Applications
            pass

# Define extra dependencies
extras_require = {
    'gui': ['PyQt6>=6.5.2', 'PyQt6-QScintilla>=2.14.1', 'Pillow>=10.0.0'],  # Added Pillow for icon generation
    'dev': [
        'pytest>=7.4.0', 'black>=23.7.0', 'mypy>=1.5.1',
        'flake8>=6.1.0', 'isort>=5.12.0', 'sphinx>=7.1.2',
        'sphinx-rtd-theme>=1.3.0'
    ],
    'windows_installer': ['pywin32', 'winshell', 'pyinstaller'],
    'installer': [],  # Platform-specific dependencies will be added during setup
    'all': []  # Will be populated below
}

# Add platform-specific dependencies
if platform.system() == "Windows":
    extras_require['installer'] = extras_require['windows_installer']

# Add a meta extra that includes everything
extras_require['all'] = sorted(set(sum((deps for name, deps in extras_require.items()
                                    if name != 'all'), [])))

setup(
    name="fileconverter",
    version=__version__,
    author="TSG Fulfillment",
    author_email="it@tsgfulfillment.com",
    description="A comprehensive file conversion utility for IT administrators",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tsgfulfillment/fileconverter",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'fileconverter': [
            'gui/resources/*.ico',
            'gui/resources/*.png',
            'gui/resources/styles/*.qss',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        "Topic :: File Formats",
    ],
    python_requires=">=3.10",
    install_requires=get_requirements(),
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "fileconverter=fileconverter.cli:main",
        ],
        "gui_scripts": [
            "fileconverter-gui=fileconverter.main:launch_gui",  # Fixed entry point
        ],
    },
    zip_safe=False,
    cmdclass={
        'install': CustomInstallCommand,
    },
)
