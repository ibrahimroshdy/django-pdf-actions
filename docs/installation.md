# Installation Guide

## Prerequisites

Before installing Django PDF Export, ensure you have:

- Python 3.8 or higher
- Django 3.2 or higher
- pip (Python package installer)

## Installation Methods

### Using pip (Recommended)

The easiest way to install Django PDF Export is using pip:

```bash
pip install django-pdf-actions
```

### From Source

If you want to install the latest development version:

```bash
git clone https://github.com/ibrahimroshdy/django-pdf-actions.git
cd django-pdf-actions
pip install -e .
```

## Configuration

### 1. Add to INSTALLED_APPS

Add 'django_pdf_actions' to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'django_pdf_actions',
]
```

### 2. Run Migrations

Apply the database migrations:

```bash
python manage.py migrate
```

### 3. Set up Fonts (Optional)

Set up the default fonts:

```bash
python manage.py setup_fonts
```

## Verify Installation

To verify the installation:

1. Start your Django development server
2. Navigate to the Django admin interface
3. Select any model with list view
4. You should see "Export to PDF (Portrait)" and "Export to PDF (Landscape)" in the actions dropdown

## Next Steps

- Check out the [Quick Start Guide](quickstart.md) to begin using the package
- Configure your [PDF Export Settings](settings.md) 