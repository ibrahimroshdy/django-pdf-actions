# Django PDF Export

[![PyPI version](https://img.shields.io/pypi/v/django-pdf-actions.svg?cache=no)](https://pypi.org/project/django-pdf-actions/)
[![Python Versions](https://img.shields.io/pypi/pyversions/django-pdf-actions.svg)](https://pypi.org/project/django-pdf-actions/)
[![Django Versions](https://img.shields.io/badge/django-3.2%20%7C%204.0%20%7C%204.1%20%7C%204.2-green.svg)](https://pypi.org/project/django-pdf-actions/)
[![Documentation](https://img.shields.io/badge/docs-github_pages-blue.svg)](https://ibrahimroshdy.github.io/django-pdf-actions/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful Django application that adds PDF export capabilities to your Django admin interface. Export your model data to beautifully formatted PDF documents with customizable layouts, fonts, and styling.

## Features

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
- Comprehensive documentation

## Quick Start

### 1. Installation

```bash
pip install django-pdf-actions
```

### 2. Add to INSTALLED_APPS

Add 'django_pdf_actions' to your INSTALLED_APPS setting:

```python
INSTALLED_APPS = [
    ...
    'django_pdf_actions',
]
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Set up Fonts (Optional)

Run the management command to set up default fonts:

```bash
python manage.py setup_fonts
```

### 5. Add to Your Models

Import and use the PDF export actions in your admin.py:

```python
from django.contrib import admin
from django_pdf_actions.actions import export_to_pdf_landscape, export_to_pdf_portrait
from .models import YourModel

@admin.register(YourModel)
class YourModelAdmin(admin.ModelAdmin):
    list_display = ('field1', 'field2', ...)  # Your fields here
    actions = [export_to_pdf_landscape, export_to_pdf_portrait]
```

## Configuration

### PDF Export Settings

Access the Django admin interface to configure PDF export settings:

1. Go to Admin > Django PDF > Export PDF Settings
2. Create a new configuration with your desired settings:
   - Page Layout (margins, items per page)
   - Font Settings (font family, sizes)
   - Visual Settings (colors, logo)
   - Display Options (headers, footers)
   - Table Settings (spacing, text wrapping)

Only one configuration can be active at a time. The active configuration will be used for all PDF exports.

### Available Settings

| Setting | Description | Default |
|---------|-------------|---------|
| Font Name | TTF font to use | DejaVuSans.ttf |
| Header Font Size | Font size for headers | 10pt |
| Body Font Size | Font size for content | 7pt |
| Page Margin | Page margins in mm | 15mm |
| Items Per Page | Number of rows per page | 10 |
| Table Spacing | Cell padding in mm | 1.0mm |
| Grid Line Width | Width of table lines | 0.25pt |
| Colors | Header and grid colors | Configurable |

## Customization

### Custom Fonts

1. Place your TTF fonts in:
```
your_project/django_pdf_actions/static/django_pdf_actions/fonts/
```

2. They will automatically appear in the font selection dropdown in PDF Export Settings

### Custom Styling

You can extend the default styles by subclassing the export actions:

```python
from django_pdf_actions.actions import export_to_pdf_landscape

class CustomPDFExport(export_to_pdf_landscape):
    def get_pdf_style(self):
        style = super().get_pdf_style()
        # Add your custom styling here
        return style
```

## Documentation

For full documentation, visit [ibrahimroshdy.github.io/django-pdf-actions](https://ibrahimroshdy.github.io/django-pdf-actions/).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you are having issues, please let us know by:
- Opening an issue in our [issue tracker](https://github.com/ibrahimroshdy/django-pdf-actions/issues)
- Checking our [documentation](https://ibrahimroshdy.github.io/django-pdf-actions/)
- Joining our [discussions](https://github.com/ibrahimroshdy/django-pdf-actions/discussions)
pip install django-pdf-actions
```

### 2. Add to INSTALLED_APPS

Add 'django_pdf_actions' to your INSTALLED_APPS setting:

```python
INSTALLED_APPS = [
    ...
    'django_pdf_actions',
]
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Set up Fonts (Optional)

Run the management command to set up default fonts:

```bash
python manage.py setup_fonts
```

### 5. Add to Your Models

Import and use the PDF export actions in your admin.py:

```python
from django.contrib import admin
from django_pdf_actions.actions import export_to_pdf_landscape, export_to_pdf_portrait
from .models import YourModel

@admin.register(YourModel)
class YourModelAdmin(admin.ModelAdmin):
    list_display = ('field1', 'field2', ...)  # Your fields here
    actions = [export_to_pdf_landscape, export_to_pdf_portrait]
```

## Configuration

### PDF Export Settings

Access the Django admin interface to configure PDF export settings:

1. Go to Admin > Django PDF > Export PDF Settings
2. Create a new configuration with your desired settings:
   - Page Layout (margins, items per page)
   - Font Settings (font family, sizes)
   - Visual Settings (colors, logo)
   - Display Options (headers, footers)
   - Table Settings (spacing, text wrapping)

Only one configuration can be active at a time. The active configuration will be used for all PDF exports.

### Available Settings

| Setting | Description | Default |
|---------|-------------|---------|
| Font Name | TTF font to use | DejaVuSans.ttf |
| Header Font Size | Font size for headers | 10pt |
| Body Font Size | Font size for content | 7pt |
| Page Margin | Page margins in mm | 15mm |
| Items Per Page | Number of rows per page | 10 |
| Table Spacing | Cell padding in mm | 1.0mm |
| Grid Line Width | Width of table lines | 0.25pt |
| Colors | Header and grid colors | Configurable |

## Customization

### Custom Fonts

1. Place your TTF fonts in:
```
your_project/django_pdf_actions/static/django_pdf_actions/fonts/
```

2. They will automatically appear in the font selection dropdown in PDF Export Settings

### Custom Styling

You can extend the default styles by subclassing the export actions:

```python
from django_pdf_actions.actions import export_to_pdf_landscape

class CustomPDFExport(export_to_pdf_landscape):
    def get_pdf_style(self):
        style = super().get_pdf_style()
        # Add your custom styling here
        return style
```

## Documentation

For full documentation, visit [ibrahimroshdy.github.io/django-pdf-actions](https://ibrahimroshdy.github.io/django-pdf-actions/).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you are having issues, please let us know by:
- Opening an issue in our [issue tracker](https://github.com/ibrahimroshdy/django-pdf-actions/issues)
- Checking our [documentation](https://ibrahimroshdy.github.io/django-pdf-actions/)
