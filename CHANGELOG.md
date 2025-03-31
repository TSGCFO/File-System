# Changelog

All notable changes to the FileConverter project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Comprehensive configuration system with multiple layers (system, user, project)
- Cross-format conversion capability for formats without direct converters
- Enhanced documentation system with comprehensive README, API docs, and code documentation
- Detailed wiki pages with user guides and developer documentation
- Improved docstrings with parameter descriptions, return values, and examples
- Systematic inline code comments explaining complex logic and implementation decisions
- Architecture diagrams and flow charts documenting system design
- Troubleshooting guides with common issues and solutions
- Comprehensive API reference documentation
- Complete test coverage documentation

### Improved

- Enhanced delimiter selection in CSV/TSV conversions with intuitive dropdown options in GUI
- Better handling of special delimiters like tabs, pipes, and spaces in the settings dialog

### Changed

- Restructured README.md with more detailed installation and usage instructions
- Expanded contributing guidelines with clearer processes
- Improved code examples with more context and explanations

### Fixed

- Documentation typos and inconsistencies
- Missing parameter descriptions in function documentation
- Unclear error messages and warnings

## [0.1.0] - 2025-03-15

### Added

- Initial release of FileConverter
- Core conversion engine with extensible architecture
- Command-line interface for file conversion and batch processing
- Graphical user interface with intuitive design
- Support for document formats:
  - Microsoft Word (.doc, .docx)
  - PDF (.pdf)
  - Rich Text Format (.rtf)
  - OpenDocument Text (.odt)
  - Markdown (.md)
  - HTML (.html, .htm)
  - Plain Text (.txt)
- Support for spreadsheet formats:
  - Microsoft Excel (.xls, .xlsx)
  - CSV (.csv)
  - TSV (.tsv)
  - OpenDocument Spreadsheet (.ods)
- Support for image formats:
  - JPEG (.jpg, .jpeg)
  - PNG (.png)
  - BMP (.bmp)
  - GIF (.gif)
  - TIFF (.tiff, .tif)
  - WebP (.webp)
- Support for data exchange formats:
  - JSON (.json)
  - XML (.xml)
  - YAML (.yaml, .yml)
  - INI (.ini)
  - TOML (.toml)
- Support for archive formats:
  - ZIP (.zip)
  - TAR (.tar)
  - GZIP (.gz)
  - 7Z (.7z)
- Support for font formats:
  - TrueType (.ttf)
  - OpenType (.otf)
  - WOFF (.woff)
  - WOFF2 (.woff2)
- Custom conversion pipelines for multi-stage processing
- Comprehensive configuration system with multiple levels:
  - System-wide configuration
  - User-specific configuration
  - Project-specific configuration
  - Environment variable overrides
- Detailed error reporting and logging system with multiple verbosity levels
- Cross-platform compatibility tested on Windows 10/11, macOS, and major Linux distributions
- File drag-and-drop support in GUI
- Recent files tracking (last 10 conversions)
- Progress indicators for long-running conversions
- Parallel batch processing with configurable thread count
- Format detection based on file content and extension
- User-configurable default parameters per format

### Changed

- N/A (initial release)

### Deprecated

- N/A (initial release)

### Removed

- N/A (initial release)

### Fixed

- N/A (initial release)

### Security

- Input validation to prevent path traversal attacks
- Secure handling of temporary files
- Resource limits to prevent DoS via malicious files

## [0.0.1] - 2025-01-10

### Added

- Project initialization with basic structure
- Core module skeleton
- CLI framework setup
- Initial converter plugin architecture
- Basic project documentation
- Testing framework setup
- Continuous integration configuration

### Changed

- N/A (initial version)

### Fixed

- N/A (initial version)

[Unreleased]: https://github.com/tsgfulfillment/fileconverter/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/tsgfulfillment/fileconverter/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/tsgfulfillment/fileconverter/releases/tag/v0.0.1
