# Django PDF Export

A powerful Django application that adds PDF export capabilities to your Django admin interface. Export your model data to beautifully formatted PDF documents with customizable layouts, fonts, and styling.

## Overview

Django PDF Export adds PDF export capabilities to your Django admin interface with support for:

- Multiple orientations (portrait and landscape)
- Customizable fonts and styling
- Configurable layouts
- Unicode text support (including Arabic)
- Header and footer customization
- Logo integration
- Table styling and formatting
- And much more...

## Key Features

### 📊 Export Capabilities
- Export any Django model data to PDF directly from the admin interface
- Support for both portrait and landscape orientations
- Batch export multiple records at once
- Smart pagination and table layouts

### 🎨 Design & Customization
- Full control over fonts, colors, margins, and spacing
- Customizable headers and footers
- Company logo integration
- Professional table styling with grid lines and backgrounds

### 🌍 International Support
- Complete Unicode compatibility
- Right-to-left (RTL) text support
- Arabic text rendering
- Multi-language content in the same document

### ⚡ Developer Experience
- Zero-configuration default settings
- Simple one-line integration with Django admin
- Extensible architecture for custom requirements
- Comprehensive documentation and examples

## Requirements

- Python 3.8+
- Django 3.2+
- ReportLab 4.0+
- django-model-utils 5.0+

## Quick Installation

```bash
pip install django-pdf-actions
```

Add to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'django_pdf_actions',
]
```

Run migrations:

```bash
python manage.py migrate
```

## Basic Usage

Add PDF export actions to your admin class:

```python
from django.contrib import admin
from django_pdf_actions.actions import export_to_pdf_landscape, export_to_pdf_portrait

@admin.register(YourModel)
class YourModelAdmin(admin.ModelAdmin):
    actions = [export_to_pdf_landscape, export_to_pdf_portrait]
```

## Support

- [GitHub Issues](https://github.com/ibrahimroshdy/django-pdf-actions/issues)
- [Documentation](https://ibrahimroshdy.github.io/django-pdf-actions/)

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/ibrahimroshdy/django-pdf-actions/blob/main/LICENSE) file for details.