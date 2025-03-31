# Setting Up Documentation with MkDocs

This guide provides instructions for setting up a documentation site using MkDocs with the markdown files in the `docs/` directory.

## Table of Contents

- [Introduction](#introduction)
- [Setting Up MkDocs](#setting-up-mkdocs)
- [Configuring MkDocs](#configuring-mkdocs)
- [Building and Deploying](#building-and-deploying)
- [Customization](#customization)
- [ReadTheDocs Alternative](#readthedocs-alternative)

## Introduction

MkDocs is a fast, simple static site generator that's geared towards building project documentation. Documentation source files are written in Markdown, and configured with a single YAML configuration file.

## Setting Up MkDocs

### Step 1: Install MkDocs

```bash
# Install MkDocs
pip install mkdocs

# Install the Material theme (recommended)
pip install mkdocs-material
```

### Step 2: Create Project Structure

MkDocs is already compatible with our existing structure, but we need to create a configuration file:

```bash
# Navigate to your project root
cd /path/to/fileconverter

# Create a new MkDocs configuration file
touch mkdocs.yml
```

## Configuring MkDocs

### Step 3: Edit the Configuration File

Open `mkdocs.yml` and add the following configuration:

```yaml
# Project information
site_name: FileConverter Documentation
site_description: Documentation for the FileConverter utility
site_author: TSG Fulfillment
site_url: https://tsgfulfillment.github.io/fileconverter/

# Repository
repo_name: tsgfulfillment/fileconverter
repo_url: https://github.com/tsgfulfillment/fileconverter
edit_uri: edit/main/docs/

# Copyright
copyright: Copyright &copy; 2023 - 2025 TSG Fulfillment

# Theme configuration
theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.top
    - search.highlight
    - search.share
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/toggle-switch-off-outline
        name: Switch to dark mode
    - scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/toggle-switch
        name: Switch to light mode

# Extensions
markdown_extensions:
  - admonition
  - codehilite
  - footnotes
  - meta
  - pymdownx.highlight
  - pymdownx.superfences
  - pymdownx.tabbed
  - pymdownx.tasklist:
      custom_checkbox: true
  - toc:
      permalink: true

# Navigation structure
nav:
  - Home: index.md
  - User Guide:
    - Installation: installation.md
    - Usage: usage.md
    - Supported Formats: formats.md
    - Troubleshooting: troubleshooting.md
  - Developer Guide:
    - Architecture: architecture.md
    - API Reference: api.md
    - Adding Converters: adding_converters.md
  - Project:
    - Changelog: ../CHANGELOG.md
    - Contributing: ../CONTRIBUTING.md
    - License: ../LICENSE.md
```

### Step 4: Adjust the Documentation Files

Our existing documentation files should work with MkDocs, but you may need to make a few adjustments:

1. Ensure all internal links use the correct relative paths for MkDocs
2. Check that image paths are properly referenced
3. Make sure the frontmatter is compatible with MkDocs if you use any

## Building and Deploying

### Step 5: Preview the Documentation Locally

```bash
# Run the local development server
mkdocs serve
```

This will start a local server at http://127.0.0.1:8000/ where you can preview the documentation.

### Step 6: Build the Documentation

```bash
# Build the static site
mkdocs build
```

This will create a `site` directory with the compiled HTML documentation.

### Step 7: Deploy to GitHub Pages

MkDocs provides a simple command to deploy your documentation to GitHub Pages:

```bash
# Deploy to GitHub Pages
mkdocs gh-deploy
```

This will:
1. Build your documentation
2. Create or update a `gh-pages` branch in your repository
3. Push the built site to this branch

After this, your documentation will be available at `https://[username].github.io/fileconverter/`.

## Customization

### Adding Additional Pages

To add a new page:

1. Create a new markdown file in the `docs/` directory
2. Add the page to the `nav` section in `mkdocs.yml`

### Customizing the Theme

The Material theme provides extensive customization options. See the [Material for MkDocs documentation](https://squidfunk.github.io/mkdocs-material/customization/) for details.

### Adding Extensions

MkDocs supports various extensions for enhanced functionality:

```bash
# Install the Mermaid diagram extension
pip install mkdocs-mermaid2-plugin

# Then add to mkdocs.yml under plugins:
# plugins:
#   - mermaid2
```

## ReadTheDocs Alternative

If you prefer to use ReadTheDocs instead of MkDocs, follow these steps:

### Step 1: Create a `readthedocs.yml` File

Create a file named `.readthedocs.yml` in your project root:

```yaml
# .readthedocs.yml
version: 2

# Build documentation in the docs/ directory with Sphinx
sphinx:
  configuration: docs/conf.py

# Optionally set the version of Python and requirements required
python:
  version: 3.8
  install:
    - requirements: docs/requirements.txt

# Build PDF & ePub
formats:
  - pdf
  - epub
```

### Step 2: Create a Sphinx Configuration

Create a `conf.py` file in the `docs/` directory:

```python
# docs/conf.py
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'FileConverter'
copyright = '2023-2025, TSG Fulfillment'
author = 'TSG Fulfillment'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'recommonmark',
    'sphinx_markdown_tables',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Support for Markdown
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}
```

### Step 3: Create a Requirements File

Create a `requirements.txt` file in the `docs/` directory:

```
# docs/requirements.txt
sphinx>=4.0.0
sphinx_rtd_theme>=0.5.2
recommonmark>=0.7.1
sphinx-markdown-tables>=0.0.15
```

### Step 4: Create an Index File

Create an `index.rst` file in the `docs/` directory:

```rst
FileConverter Documentation
==========================

.. toctree::
   :maxdepth: 2
   :caption: User Guide:

   installation
   usage
   formats
   troubleshooting

.. toctree::
   :maxdepth: 2
   :caption: Developer Guide:

   architecture
   api
   adding_converters

.. toctree::
   :maxdepth: 1
   :caption: Project:

   ../CHANGELOG
   ../CONTRIBUTING
   ../LICENSE
```

### Step 5: Connect to ReadTheDocs

1. Create an account on [ReadTheDocs](https://readthedocs.org/)
2. Import your GitHub repository
3. Configure the settings as needed
4. Trigger a build

Your documentation will then be available at `https://fileconverter.readthedocs.io/`.