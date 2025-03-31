# FileConverter Installation Guide

This guide provides detailed instructions for installing FileConverter on various platforms and configurations.

## Table of Contents

- [System Requirements](#system-requirements)
- [Quick Installation](#quick-installation)
- [Detailed Installation](#detailed-installation)
  - [Windows](#windows)
  - [macOS](#macos)
  - [Linux](#linux)
- [Installation Options](#installation-options)
- [External Dependencies](#external-dependencies)
- [Virtual Environments](#virtual-environments)
- [Development Installation](#development-installation)
- [Upgrading](#upgrading)
- [Troubleshooting](#troubleshooting)

## System Requirements

FileConverter requires:

- **Python**: Version 3.10 or higher
- **Operating System**: Windows 10/11, macOS 11+, or modern Linux distributions
- **Disk Space**: Approximately 100MB for the base installation, plus additional space for dependencies
- **Memory**: Minimum 512MB RAM, 2GB+ recommended for processing large files
- **External Dependencies**: Various external libraries depending on which file formats you plan to use

## Quick Installation

The quickest way to install FileConverter is via pip:

```bash
# Basic installation
pip install fileconverter

# With GUI support
pip install fileconverter[gui]

# Full installation with all dependencies
pip install fileconverter[all]
```

After installation, verify that FileConverter is working:

```bash
fileconverter --version
```

## Detailed Installation

### Windows

#### Step 1: Install Python

1. Download Python 3.10 or newer from [python.org](https://www.python.org/downloads/)
2. Run the installer, ensuring you check "Add Python to PATH"
3. Verify the installation by opening a command prompt and typing:
   ```
   python --version
   pip --version
   ```

#### Step 2: Install FileConverter

1. Open a command prompt (cmd or PowerShell)
2. Install FileConverter using pip:
   ```
   pip install fileconverter[gui]
   ```

#### Step 3: Install External Dependencies (as needed)

For document conversions:
- LibreOffice: Download from [libreoffice.org](https://www.libreoffice.org/download/download/) and install
- wkhtmltopdf: Download from [wkhtmltopdf.org](https://wkhtmltopdf.org/downloads.html) and install

For image conversions:
- ImageMagick: Download from [imagemagick.org](https://imagemagick.org/script/download.php#windows) and install

#### Step 4: Verify Installation

1. Open a command prompt
2. Run:
   ```
   fileconverter list-formats
   ```
3. For GUI verification:
   ```
   fileconverter-gui
   ```

### macOS

#### Step 1: Install Python

1. Install Homebrew if not already installed:
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Install Python using Homebrew:
   ```
   brew install python
   ```
3. Verify the installation:
   ```
   python3 --version
   pip3 --version
   ```

#### Step 2: Install FileConverter

1. Open Terminal
2. Install FileConverter using pip:
   ```
   pip3 install fileconverter[gui]
   ```

#### Step 3: Install External Dependencies (as needed)

For document conversions:
```
brew install libreoffice wkhtmltopdf
```

For image conversions:
```
brew install imagemagick
```

#### Step 4: Verify Installation

1. Open Terminal
2. Run:
   ```
   fileconverter list-formats
   ```
3. For GUI verification:
   ```
   fileconverter-gui
   ```

### Linux

These instructions are for Ubuntu and similar distributions. Adjust package names for your distribution.

#### Step 1: Install Python

1. Update package lists:
   ```
   sudo apt update
   ```
2. Install Python and development tools:
   ```
   sudo apt install python3 python3-pip python3-dev build-essential
   ```
3. Verify the installation:
   ```
   python3 --version
   pip3 --version
   ```

#### Step 2: Install Required Libraries

For GUI support:
```
sudo apt install python3-pyqt6 python3-pyqt6.qsci
```

For document handling:
```
sudo apt install libreoffice wkhtmltopdf
```

For image processing:
```
sudo apt install imagemagick libmagickwand-dev
```

#### Step 3: Install FileConverter

1. Install using pip:
   ```
   pip3 install fileconverter[gui]
   ```
   
   If you encounter permission issues, use:
   ```
   pip3 install --user fileconverter[gui]
   ```

#### Step 4: Verify Installation

1. Run:
   ```
   fileconverter list-formats
   ```
2. For GUI verification:
   ```
   fileconverter-gui
   ```
3. Verify desktop shortcuts and system integration:
   - Check if a FileConverter icon was created on your desktop
   - Verify the application appears in Windows search or application list

## Installation Options

FileConverter offers several installation options to meet different needs:

### Basic Installation

Installs the core package with minimal dependencies:

```bash
pip install fileconverter
```

### GUI Support

Installs the package with GUI dependencies:

```bash
pip install fileconverter[gui]
```

### Development Tools

Installs the package with development tools for contributing:

```bash
pip install fileconverter[dev]
```

### Full Installation

Installs all dependencies for maximum format support:

```bash
pip install fileconverter[all]
```

### Custom Installation

You can combine options:

```bash
pip install fileconverter[gui,dev]
```

### Format-Specific Dependencies

Install only what you need:

```bash
# For document conversions
pip install fileconverter[document]

# For image conversions
pip install fileconverter[image]

# For spreadsheet conversions
pip install fileconverter[spreadsheet]
```

## External Dependencies

FileConverter relies on external libraries and tools for certain conversions:

### Document Conversions

- **LibreOffice**: For DOC, DOCX, ODT conversions
- **wkhtmltopdf**: For HTML to PDF conversion
- **WeasyPrint**: Alternative for HTML to PDF conversion

### Image Conversions

- **ImageMagick**: For advanced image processing
- **Pillow**: Python Imaging Library
- **Wand**: Python bindings for ImageMagick

### Spreadsheet Conversions

- **pandas**: For data manipulation
- **openpyxl**: For Excel file handling
- **xlrd**: For reading older Excel formats

## Virtual Environments

It's recommended to install FileConverter in a virtual environment, especially if you're using it for development or have conflicting Python packages:

```bash
# Create a virtual environment
python -m venv fileconverter-env

# Activate the environment
# On Windows:
fileconverter-env\Scripts\activate
# On macOS/Linux:
source fileconverter-env/bin/activate

# Install FileConverter
pip install fileconverter[gui]

# When you're done, deactivate the environment
deactivate
```

## Development Installation

For development, install from source:

```bash
# Clone the repository
git clone https://github.com/tsgfulfillment/fileconverter.git
cd fileconverter

# Install in development mode
pip install -e ".[dev,gui]"
```

This allows you to modify the code and see changes immediately without reinstalling.

## Upgrading

To upgrade FileConverter to the latest version:

```bash
pip install --upgrade fileconverter
```

To upgrade to a specific version:

```bash
pip install --upgrade fileconverter==0.2.0
```

## Troubleshooting

### Common Installation Issues

#### Missing Dependencies

If you see errors about missing libraries:

```bash
# On Windows, use pip to install Python dependencies
pip install <missing_package>

# On macOS, use Homebrew
brew install <missing_package>

# On Linux (Ubuntu/Debian)
sudo apt install <missing_package>
```

#### Permission Errors

If you encounter permission errors:

```bash
# Install with --user flag
pip install --user fileconverter

# On Linux, you might need to add ~/.local/bin to PATH
export PATH="$HOME/.local/bin:$PATH"
```

#### PyQt6 Installation Issues

If you have trouble installing PyQt6:

```bash
# On Windows, try installing from wheel
pip install PyQt6 PyQt6-QScintilla

# On Linux, use system packages
sudo apt install python3-pyqt6 python3-pyqt6.qsci
```

#### Path Issues

If the `fileconverter` command is not found:

```bash
# Find the installation location
pip show fileconverter

# Add to PATH (Windows)
set PATH=%PATH%;C:\Users\<username>\AppData\Local\Programs\Python\Python310\Scripts

# Add to PATH (macOS/Linux)
export PATH="$PATH:$HOME/.local/bin"
```

#### Desktop Shortcut Issues

If the desktop shortcut was not created:

```bash
# Manually create desktop shortcut
python -m fileconverter.gui.resources.icon_generator  # Generate icon first
```

For Windows, create a `.bat` file on your desktop with:
```bat
@echo off
python -m fileconverter.main --gui
```

For Linux, create a `.desktop` file:
```
[Desktop Entry]
Type=Application
Name=FileConverter
Comment=File conversion utility
Exec=python3 -m fileconverter.main --gui
Terminal=false
Categories=Utility;
```

#### System Registration Issues

If the application doesn't appear in system search:

- **Windows**: Check if the installation completed without errors. You may need to install with administrator privileges.
- **Linux**: Make sure the `.desktop` file was properly created in `~/.local/share/applications/`.
- **macOS**: You may need to drag the application to the Applications folder manually.

For more troubleshooting help, see the [Troubleshooting Guide](./troubleshooting.md).