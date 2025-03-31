#!/usr/bin/env python3
"""
Main entry point for the FileConverter package.

This module is executed when the package is run directly with 'python -m fileconverter'.
"""

import sys
from fileconverter.main import main

if __name__ == "__main__":
    sys.exit(main())
