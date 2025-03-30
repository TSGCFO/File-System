#!/usr/bin/env python3
from setuptools import setup, find_packages
import os
from fileconverter.version import __version__

# Read the long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

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
    install_requires=[
        line.strip() for line in open("requirements.txt", "r") 
        if line.strip() and not line.startswith("#")
    ],
    entry_points={
        "console_scripts": [
            "fileconverter=fileconverter.cli:main",
        ],
        "gui_scripts": [
            "fileconverter-gui=fileconverter.__main__:launch_gui",
        ],
    },
    zip_safe=False,
)
