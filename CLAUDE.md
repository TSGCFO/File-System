# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Important Environment Setup
- Before starting any task in this project and before attempting to read or write any files activate the virtual enviroment. Never do anything if you are not in a virtual environmnet.

## Build Commands
- Install: `pip install -e .` (dev mode) or `python setup.py install`
- Run GUI: `python -m fileconverter.main --gui`
- Run CLI: `python -m fileconverter.cli <command>`

## Test Commands
- All tests: `python run_tests.py`
- Unit tests only: `python run_tests.py --unit`
- Integration tests only: `python run_tests.py --integration`
- Skip GUI tests: `python run_tests.py --no-gui`
- Single test file: `python -m pytest tests/test_converters/test_cross_domain.py`

## Lint/Format Tools
- Code formatting: `black fileconverter/`
- Import sorting: `isort fileconverter/`
- Type checking: `mypy fileconverter/`
- Linting: `flake8 fileconverter/`

## Code Style Guidelines
- Python ≥3.10 required
- Use type hints for all functions and methods
- snake_case for functions/variables, PascalCase for classes
- Use consistent import order: standard library → third-party → local
- Follow error handling patterns in utils/error_handling.py
- Group imports alphabetically within each section
- Every line of code, function, method etc. must be accompanied with comments or docstrings. You must always write self-documenting code.

## Special Tools
- Read the `.cursorrules` file which contains a tool for you too use. The tool provides you with a team of AI agents who can assist you in your tasks.