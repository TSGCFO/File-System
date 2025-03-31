# Setting Up a GitHub Wiki for FileConverter

This guide provides instructions for setting up a GitHub Wiki using the markdown files we've created in the `docs/` directory.

## Table of Contents

- [Introduction](#introduction)
- [Enabling GitHub Wiki](#enabling-github-wiki)
- [Creating Wiki Pages](#creating-wiki-pages)
- [Setting Up Navigation](#setting-up-navigation)
- [Adding Images and Assets](#adding-images-and-assets)
- [Maintaining the Wiki](#maintaining-the-wiki)
- [Best Practices](#best-practices)

## Introduction

GitHub Wiki is a built-in documentation system for GitHub repositories. It provides a simple way to create and organize documentation pages directly within your project repository. The wiki itself is a separate Git repository that can be cloned and edited locally.

## Enabling GitHub Wiki

### Step 1: Enable Wiki for Your Repository

1. Navigate to your repository on GitHub (e.g., `https://github.com/tsgfulfillment/fileconverter`)
2. Click on "Settings" in the top navigation bar
3. Scroll down to the "Features" section
4. Make sure the "Wikis" checkbox is enabled
5. Click "Save" if you made any changes

### Step 2: Access Your Wiki

1. Go back to your repository's main page
2. Click on the "Wiki" tab in the top navigation bar
3. You'll be taken to your repository's wiki homepage

## Creating Wiki Pages

### Step 3: Create the Home Page

1. If this is your first time accessing the wiki, you'll be prompted to create a home page
2. Otherwise, click on "Create the first page" button
3. For the home page, use the content from our `index.md` file:
   ```markdown
   # FileConverter Documentation

   Welcome to the FileConverter documentation. This comprehensive guide provides detailed information about the FileConverter system, its features, usage, and development.

   (... rest of index.md content ...)
   ```
4. In the "Edit message" field, enter a commit message like "Initial wiki home page"
5. Click "Save Page"

### Step 4: Add Additional Pages

For each of our documentation files, create a corresponding wiki page:

1. From your wiki home page, click "New Page" in the upper-right corner
2. Enter a page title that matches the document (e.g., "Installation Guide" for `installation.md`)
3. Copy the content from the corresponding file in the `docs/` directory
4. Optionally adjust links to work with the wiki structure
5. Add a commit message
6. Click "Save Page"

Repeat this process for all documentation files:
- Installation Guide (`installation.md`)
- Usage Guide (`usage.md`)
- API Reference (`api.md`)
- Architecture (`architecture.md`)
- Troubleshooting (`troubleshooting.md`)
- Supported Formats (`formats.md`)
- Adding Converters (`adding_converters.md`)

### Step 5: Clone and Add Pages Locally (Alternative Method)

For more efficient page creation, you can clone the wiki repository and add pages locally:

1. Clone the wiki repository:
   ```bash
   git clone https://github.com/tsgfulfillment/fileconverter.wiki.git
   cd fileconverter.wiki
   ```

2. Copy and rename the markdown files from your `docs/` directory:
   ```bash
   # Example for copying installation.md
   cp ../docs/installation.md "Installation-Guide.md"
   # Repeat for other files
   ```
   
   **Note**: In GitHub Wiki, page filenames determine the URL. Use hyphens for spaces in the filename (e.g., `Installation-Guide.md` becomes "Installation Guide" in the wiki).

3. Edit the files to adjust any links or paths as needed

4. Commit and push the changes:
   ```bash
   git add .
   git commit -m "Add documentation pages to wiki"
   git push origin master
   ```

## Setting Up Navigation

### Step 6: Create a Sidebar Navigation

GitHub Wiki allows you to create a sidebar navigation by creating a special page named `_Sidebar`:

1. Create a new page named `_Sidebar`
2. Add the following content:
   ```markdown
   ### Documentation

   #### User Guide
   * [Home](Home)
   * [Installation Guide](Installation-Guide)
   * [Usage Guide](Usage-Guide)
   * [Supported Formats](Supported-Formats)
   * [Troubleshooting](Troubleshooting)

   #### Developer Guide
   * [Architecture](Architecture)
   * [API Reference](API-Reference)
   * [Adding Converters](Adding-Converters)

   #### Project
   * [GitHub Repository](https://github.com/tsgfulfillment/fileconverter)
   * [Changelog](https://github.com/tsgfulfillment/fileconverter/blob/main/CHANGELOG.md)
   * [License](https://github.com/tsgfulfillment/fileconverter/blob/main/LICENSE)
   ```
3. Commit the sidebar page

### Step 7: Create a Footer

You can also create a footer that appears on all wiki pages:

1. Create a new page named `_Footer`
2. Add the following content:
   ```markdown
   ---
   © 2023-2025 TSG Fulfillment | [Website](https://tsgfulfillment.com) | [GitHub](https://github.com/tsgfulfillment)
   ```
3. Commit the footer page

## Adding Images and Assets

### Step 8: Add Images to Your Wiki

For diagrams and screenshots referenced in the documentation:

1. In the wiki interface, click "Clone this wiki locally" to get the clone URL
2. Clone the wiki repository if you haven't already
3. Create an `images` directory in the wiki repository
4. Add your images to this directory
5. Update your markdown files to reference these images:
   ```markdown
   ![Architecture Diagram](images/architecture-diagram.png)
   ```
6. Commit and push the changes

## Maintaining the Wiki

### Step 9: Regular Updates

Keep your wiki in sync with code changes:

1. Update documentation files in the main repository's `docs/` directory
2. Copy the updated content to the corresponding wiki pages
3. For automated synchronization, consider using GitHub Actions (see Best Practices below)

### Step 10: Versioning (Optional)

For major releases, you may want to version your documentation:

1. Create pages with version prefixes:
   ```
   v1.0-Home
   v1.0-Installation-Guide
   ```
2. Update links between pages to point to the versioned pages
3. Maintain a version selector in your sidebar

## Best Practices

### Automated Wiki Updates

You can use GitHub Actions to automatically sync your `docs/` directory with your GitHub Wiki:

1. Create a `.github/workflows/wiki-sync.yml` file:
   ```yaml
   name: Sync Docs to Wiki

   on:
     push:
       paths:
         - 'docs/**'
       branches:
         - main

   jobs:
     sync-wiki:
       runs-on: ubuntu-latest
       steps:
         - name: Checkout source
           uses: actions/checkout@v3

         - name: Sync docs to wiki
           uses: SwiftDocOrg/github-wiki-publish-action@v1
           with:
             path: "docs"
           env:
             GITHUB_PERSONAL_ACCESS_TOKEN: ${{ secrets.GH_PERSONAL_ACCESS_TOKEN }}
   ```

2. Set up a `GH_PERSONAL_ACCESS_TOKEN` secret in your repository settings with a token that has wiki write access

### Wiki Organization Tips

1. **Use consistent naming**: Follow a clear naming convention for all pages
2. **Keep headings consistent**: Use the same heading structure across pages
3. **Update the sidebar**: When adding new pages, remember to update the sidebar
4. **Check links regularly**: Ensure all internal links between wiki pages work
5. **Add tags**: Use tags at the bottom of pages to help with categorization
6. **Include edit dates**: Consider adding "Last updated" information

### Content Structure Best Practices

1. **Start with a clear introduction**: Each page should begin with a brief introduction
2. **Use a table of contents**: For longer pages, include a table of contents
3. **Follow a logical flow**: Organize information from basic to advanced
4. **Include examples**: Provide concrete examples where applicable
5. **Link to related pages**: Create connections between related content
6. **Keep content up to date**: Regularly review and update documentation

By following these instructions, you'll create a comprehensive GitHub Wiki that leverages your existing documentation files and provides a user-friendly interface for accessing project documentation.