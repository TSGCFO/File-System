# Dependency Management in FileConverter

FileConverter includes a sophisticated dependency management system that automatically detects, installs, and configures all required dependencies. This guide explains how to use this system effectively.

## Overview

The dependency management system handles two types of dependencies:

1. **Python Packages**: Libraries that can be installed with pip
2. **External Tools**: System applications like LibreOffice, wkhtmltopdf, and ImageMagick

## Command-Line Interface

### Checking Dependencies

To check for missing dependencies:

```bash
fileconverter dependencies check
```

This will analyze your system and report any missing dependencies, categorizing them as either Python packages or external tools.

### Installing Dependencies

To install missing dependencies:

```bash
fileconverter dependencies install
```

This command will:
- Detect missing dependencies
- Automatically install Python packages using pip
- Attempt to install external tools using your system's package manager (if available)
- Provide clear instructions for manual installation when automatic installation isn't possible

### Format-Specific Dependencies

You can check or install dependencies for specific format categories:

```bash
# Check dependencies for document format conversions
fileconverter dependencies check --format=document

# Install dependencies for image format conversions
fileconverter dependencies install --format=image
```

Available format categories include:
- `document`: For document format conversions (DOC, DOCX, PDF, etc.)
- `spreadsheet`: For spreadsheet format conversions (XLS, XLSX, CSV, etc.)
- `image`: For image format conversions (PNG, JPG, TIFF, etc.)
- `archive`: For archive format conversions (ZIP, 7Z, etc.)
- `gui`: For the graphical user interface

## Offline Installation

For environments without internet access, FileConverter provides robust offline installation options:

### Creating Offline Bundles

You can create an offline installation bundle that includes all necessary Python packages:

```bash
fileconverter dependencies bundle /path/to/output/directory
```

This creates a complete offline installation bundle with:
- Python packages for offline installation
- Platform-specific installer scripts
- Documentation with installation instructions

### Using Offline Bundles

To install from an offline bundle:

1. Transfer the bundle to the target machine
2. Run the appropriate installer:
   - Windows: `installer\install.bat`
   - macOS/Linux: `installer/install.sh`

### Manual Offline Installation

You can also install manually from an offline bundle:

```bash
pip install --no-index --find-links=/path/to/bundle/vendor fileconverter[gui]
```

## External Dependencies

FileConverter requires various external tools for certain conversion types:

| Tool | Purpose | Windows | macOS | Linux |
|------|---------|---------|-------|-------|
| **LibreOffice** | DOC/DOCX/ODT conversions | `choco install libreoffice-fresh` | `brew install libreoffice` | `sudo apt install libreoffice` |
| **wkhtmltopdf** | HTML to PDF conversion | `choco install wkhtmltopdf` | `brew install wkhtmltopdf` | `sudo apt install wkhtmltopdf` |
| **ImageMagick** | Advanced image processing | `choco install imagemagick` | `brew install imagemagick` | `sudo apt install imagemagick` |

The dependency manager will automatically detect these tools and guide you through the installation process.

## Troubleshooting

### Python Package Installation Issues

If you encounter issues installing Python packages:

1. **Check your internet connection**
2. **Make sure pip is up to date**:
   ```bash
   python -m pip install --upgrade pip
   ```
3. **Try installing with verbose output**:
   ```bash
   fileconverter dependencies install --verbose
   ```

### External Tool Issues

If automatic installation of external tools fails:

1. **Install manually** using the URLs provided in the dependency report
2. **Verify installation paths** are in your system PATH
3. **Check permissions** for accessing installation directories

### Network-Restricted Environments

For environments with limited or no internet access:

1. **Create an offline bundle** on a machine with internet access
2. **Transfer the bundle** to the restricted environment
3. **Install using the offline installer**
4. **Manually install external tools** as needed

## Advanced Options

### Non-Interactive Mode

For automated installation in scripts:

```bash
fileconverter dependencies install --non-interactive
```

### Skipping Dependency Checks

For expert users who want to bypass dependency checks:

```bash
fileconverter --skip-dependency-check
```

### Debugging Dependency Issues

For detailed information about the dependency detection and installation process:

```bash
fileconverter dependencies check --verbose
fileconverter dependencies install --verbose
```

## Integration with Application Launch

The dependency management system is integrated with the application launch process:

1. When you start FileConverter, it automatically checks for critical dependencies
2. If critical dependencies are missing, it provides clear instructions for resolving the issues
3. For non-critical dependencies, it displays warnings but allows the application to continue running

This ensures a smooth user experience even for users with limited technical expertise.