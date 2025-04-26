# Django PDF Actions

<p align="center"> 
  <img src="docs/assets/logo.png" alt="Django PDF Actions Logo" width="200" height="200">
</p>

[![PyPI version](https://img.shields.io/pypi/v/django-pdf-actions.svg?cache=no)](https://pypi.org/project/django-pdf-actions/)
[![Python Versions](https://img.shields.io/pypi/pyversions/django-pdf-actions.svg)](https://pypi.org/project/django-pdf-actions/)
[![Django Versions](https://img.shields.io/badge/django-3.2%20%7C%204.0%20%7C%204.1%20%7C%204.2%20%7C%205.0-green.svg)](https://pypi.org/project/django-pdf-actions/)
[![Documentation](https://img.shields.io/badge/docs-github_pages-blue.svg)](https://ibrahimroshdy.github.io/django-pdf-actions/)
[![Documentation Status](https://readthedocs.org/projects/django-pdf-actions/badge/?version=latest)](https://django-pdf-actions.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Development Status](https://img.shields.io/badge/status-stable-green.svg)](https://pypi.org/project/django-pdf-actions/)
[![GitHub last commit](https://img.shields.io/github/last-commit/ibrahimroshdy/django-pdf-actions.svg)](https://github.com/ibrahimroshdy/django-pdf-actions/commits/main)
[![PyPI Downloads](https://img.shields.io/pypi/dm/django-pdf-actions.svg)](https://pypistats.org/packages/django-pdf-actions)
[![Total Downloads](https://static.pepy.tech/badge/django-pdf-actions)](https://pepy.tech/project/django-pdf-actions)
[![Published on Django Packages](https://img.shields.io/badge/Published%20on-Django%20Packages-0c3c26)](https://djangopackages.org/packages/p/django-pdf-actions/)

A Django application that adds PDF export capabilities to your Django admin interface. Export your model data to PDF documents with customizable layouts and styling.

## Prerequisites

Before installing Django PDF Export, ensure you have:
- Python 3.8 or higher
- Django 3.2 or higher
- pip (Python package installer)

## Features

### 📊 Export Capabilities
- Export any Django model data to PDF directly from the admin interface
- Support for both portrait and landscape orientations
- Automatic pagination with configurable items per page
- Smart table layouts with automatic column width adjustment
- Support for Django model fields from list_display
- Batch export multiple records at once
- Professional table styling with grid lines and backgrounds

### 🎨 Design & Customization
Through the ExportPDFSettings model, you can configure:
- Page Layout:
  - Items per page (1-50)
  - Page margins (5-50mm)
  - Automatic column width calculation
  - Smart pagination handling
- Font Settings:
  - Custom font support (TTF files)
  - Configurable header and body font sizes
  - Default DejaVu Sans font included
- Visual Settings:
  - Company logo integration with flexible positioning
  - Header background color customization
  - Grid line color and width control
  - Professional table styling
- Display Options:
  - Toggle header visibility
  - Toggle logo visibility
  - Toggle export timestamp
  - Toggle page numbers
  - Customizable header and footer information
- Alignment Options:
  - Customizable title alignment (left, center, right)
  - Customizable header alignment (left, center, right)
  - Customizable content alignment (left, center, right)
  - Automatic RTL alignment for right-to-left languages
- Table Settings:
  - Cell spacing and padding control
  - Text wrapping with configurable character limits
  - Grid line customization
  - Header row styling

### 🌍 International Support
- Complete Unicode compatibility for all languages
- Arabic text support with automatic reshaping
- Bidirectional text handling
- Multi-language content support in the same document
- RTL (Right-to-Left) text support
- Enhanced RTL support with proper text alignment and bidirectional text handling
- Configurable RTL support that can be enabled/disabled as needed
- Column order reversal for proper RTL table display
- Uses model verbose_name for proper localized headings
- Customizable alignment options for RTL content

## Quick Start

### 1. Installation

#### Using pip (Recommended)
```bash
pip install django-pdf-actions
```

#### From Source
If you want to install the latest development version:
```bash
git clone https://github.com/ibrahimroshdy/django-pdf-actions.git
cd django-pdf-actions
pip install -e .
```

### 2. Add to INSTALLED_APPS

Add 'django_pdf_actions' to your INSTALLED_APPS setting:

```python
INSTALLED_APPS = [
    ...
    'django_pdf_actions'
]
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Set up Fonts

The package uses fonts from your project's `static/assets/fonts` directory. The default font is DejaVu Sans, which provides excellent Unicode support.

To use custom fonts:
1. Create the fonts directory if it doesn't exist:
   ```bash
   mkdir -p static/assets/fonts
   ```
2. Install the default font (DejaVu Sans):
```bash
python manage.py setup_fonts
```
3. Add custom fonts (optional):
   ```bash
   # Example: Installing Roboto font
   python manage.py setup_fonts --font-url "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf" --font-name "Roboto-Regular.ttf"

   # Example: Installing Cairo font for Arabic support
   python manage.py setup_fonts --font-url "https://github.com/google/fonts/raw/main/ofl/cairo/Cairo-Regular.ttf" --font-name "Cairo-Regular.ttf"
   ```

#### Font Directory Structure
After setup, your project should have this structure:
```
your_project/
├── static/
│   └── assets/
│       └── fonts/
│           ├── DejaVuSans.ttf
│           ├── Roboto-Regular.ttf (optional)
│           └── Cairo-Regular.ttf (optional)
```

### 5. Verify Installation

To verify the installation:
1. Start your Django development server
2. Navigate to the Django admin interface
3. Select any model with list view
4. You should see "Export to PDF (Portrait)" and "Export to PDF (Landscape)" in the actions dropdown

### 6. Add to Your Models

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
2. Create a new configuration with your desired settings
3. Mark it as active (only one configuration can be active at a time)

The active configuration will be used for all PDF exports across your admin interface.

### Available Settings

| Setting | Description | Default | Range |
|---------|-------------|---------|--------|
| Page Size | PDF page size | A4 | A4, A3, A2, A1 |
| Items Per Page | Rows per page | 10 | 1-50 |
| Page Margin | Page margins | 15mm | 5-50mm |
| Font Name | TTF font to use | DejaVuSans.ttf | Any installed TTF |
| Header Font Size | Header text size | 10 | 6-24 |
| Body Font Size | Content text size | 7 | 6-18 |
| Logo | Company logo | Optional | Image file |
| Header Background | Header color | #F0F0F0 | Hex color |
| Grid Line Color | Table lines color | #000000 | Hex color |
| Grid Line Width | Table line width | 0.25 | 0.1-2.0 |
| Table Spacing | Cell padding | 1.0mm | 0.5-5.0mm |
| Max Chars Per Line | Text wrapping | 45 | 20-100 |
| RTL Support | Right-to-left text | Disabled | Enabled/Disabled |
| Title Alignment | Title text alignment | Center | Left/Center/Right |
| Header Alignment | Column headers alignment | Center | Left/Center/Right |
| Content Alignment | Table content alignment | Center | Left/Center/Right |

### Page Sizes

The package supports multiple standard page sizes:
- **A4**: 210mm × 297mm (default)
- **A3**: 297mm × 420mm
- **A2**: 420mm × 594mm
- **A1**: 594mm × 841mm

The page size affects:
- Available space for content
- Number of rows per page
- Table column widths
- Overall document dimensions

### Technical Details

- **Python Compatibility**: Python 3.8 or higher
- **Django Compatibility**: Django 3.2, 4.0, 4.1, 4.2, 5.0
- **Dependencies**: Automatically handled by pip
- **PDF Engine**: ReportLab
- **Character Encoding**: UTF-8
- **Paper Size**: A4 (default)

## Development

### Setting Up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/ibrahimroshdy/django-pdf-actions.git
cd django-pdf-actions
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

4. Run tests:
```bash
pytest
```

## Documentation

For more detailed information, check out our documentation:
- [Installation Guide](https://ibrahimroshdy.github.io/django-pdf-actions/installation/)
- [Quick Start Guide](https://ibrahimroshdy.github.io/django-pdf-actions/quickstart/)
- [Configuration Guide](https://ibrahimroshdy.github.io/django-pdf-actions/settings/)

## License 

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you are having issues, please let us know by:
- Opening an issue in our [issue tracker](https://github.com/ibrahimroshdy/django-pdf-actions/issues)
- Checking our [documentation](https://ibrahimroshdy.github.io/django-pdf-actions/)

### Common Issues

1. Font Installation
   - Ensure your fonts directory exists at `static/assets/fonts/`
   - Verify font files are in TTF format
   - Check file permissions

2. PDF Generation
   - Ensure your model fields are properly defined in list_display
   - Check that an active PDF Export Settings configuration exists
   - Verify logo file paths if using custom logos
   - Check for any errors in the Django admin console

3. RTL Text Support
   - For Arabic, Persian, or other RTL languages, enable the RTL Support option
   - Use a font that supports the language (e.g., Cairo for Arabic)
   - Install appropriate fonts using the `setup_fonts` command
   - Text alignment and directionality will automatically adjust when RTL is enabled

