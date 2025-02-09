# GitHub Actions Workflows

This directory contains the GitHub Actions workflows for the django-pdf-actions package. Here's what each workflow does:

> **Note**: This package is distributed via [PyPI](https://pypi.org/project/django-pdf-actions/). While the source code is hosted on GitHub, package installation should be done via pip: `pip install django-pdf-actions`

## Version Management (`gitversion.yml`)
Handles automatic version management for the package:
- Runs on pushes to `main`, `develop`, `releases/*`, and `hotfix/*` branches
- Automatically increments the patch version in `pyproject.toml` on pushes to main
- Respects manually set versions (if you manually set a higher version)
- Creates git tags for each new version
- Skips version bump if the version was manually updated

## Documentation Pages (`pages.yml`)
Handles the documentation site deployment:
- Builds and deploys the documentation to GitHub Pages
- Uses MkDocs for documentation generation
- Runs when documentation-related files are changed
- Deploys to the gh-pages branch

## Tests (`tests.yml`)
Runs the test suite:
- Executes on pull requests and pushes to main/develop
- Runs tests across different Python versions
- Checks code quality and test coverage
- Ensures compatibility across Python versions

## Package Publishing (`publish.yml`)
Handles package publishing to PyPI:
- Triggered when a new release is created
- Builds the package using Poetry
- Publishes the package to PyPI
- Ensures the package is properly distributed

## Workflow Dependencies
Some workflows may depend on others:
1. `gitversion.yml` runs independently to manage versions
2. When a new version is tagged, it can trigger `publish.yml`
3. Documentation updates via `pages.yml` run independently
4. Tests run on PRs and pushes to ensure quality
