# Django PDF Actions

<p align="center">
  <img src="assets/logo.png" alt="Django PDF Actions Logo" width="200" height="200">
</p>

A powerful Django application for generating PDF exports from the Django admin interface with advanced customization options.

[![PyPI version](https://img.shields.io/pypi/v/django-pdf-actions.svg?cache=no)](https://pypi.org/project/django-pdf-actions/)
[![Python Versions](https://img.shields.io/pypi/pyversions/django-pdf-actions.svg)](https://pypi.org/project/django-pdf-actions/)
[![Django Versions](https://img.shields.io/badge/django-3.2%20%7C%204.0%20%7C%204.1%20%7C%204.2-green.svg)](https://pypi.org/project/django-pdf-actions/)
[![Documentation](https://img.shields.io/badge/docs-github_pages-blue.svg)](https://ibrahimroshdy.github.io/django-pdf-actions/)
[![Documentation Status](https://readthedocs.org/projects/django-pdf-actions/badge/?version=latest)](https://django-pdf-actions.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Development Status](https://img.shields.io/badge/status-beta-yellow.svg)](https://pypi.org/project/django-pdf-actions/)
[![GitHub last commit](https://img.shields.io/github/last-commit/ibrahimroshdy/django-pdf-actions.svg)](https://github.com/ibrahimroshdy/django-pdf-actions/commits/main)
[![PyPI Downloads](https://img.shields.io/pypi/dm/django-pdf-actions.svg)](https://pypistats.org/packages/django-pdf-actions)
[![Total Downloads](https://static.pepy.tech/badge/django-pdf-actions)](https://pepy.tech/project/django-pdf-actions)

## Overview

Django PDF Actions seamlessly integrates PDF export functionality into your Django admin interface. With just a few lines of code, you can add professional PDF export capabilities to any model in your Django application.

### Key Features

- **Easy Integration**: Add PDF export actions to any model with minimal configuration
- **Customizable Layout**: Control margins, fonts, colors, and page settings
- **Multiple Orientations**: Export in both portrait and landscape formats
- **Advanced Styling**: Custom headers, footers, watermarks, and company branding
- **Performance Optimized**: Efficient handling of large datasets with pagination
- **Security Features**: Access control, encryption, and secure file handling
- **Internationalization**: Support for multiple languages and Unicode fonts
- **Responsive Design**: Automatic column sizing and content wrapping

## Quick Example

```python
from django.contrib import admin
from django_pdf_actions.actions import export_to_pdf_landscape, export_to_pdf_portrait
from .models import YourModel

@admin.register(YourModel)
class YourModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'date_joined')
    actions = [export_to_pdf_landscape, export_to_pdf_portrait]
```

## Documentation

### Getting Started
1. [Installation Guide](installation.md)
2. [Quick Start Guide](quickstart.md)
3. [Settings Reference](settings.md)

## Requirements

- Python 3.8+
- Django 3.2+
- WeasyPrint dependencies

## Support

- [GitHub Issues](https://github.com/ibrahimroshdy/django-pdf-actions/issues)
- [Documentation](https://ibrahimroshdy.github.io/django-pdf-actions/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
