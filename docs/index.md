# Django PDF Actions

<div align="center">
  <img src="assets/logo.png" alt="Django PDF Actions Logo" width="200" height="200">
  
  **A powerful Django application for generating PDF exports from the Django admin interface**
</div>

---

[![PyPI version](https://img.shields.io/pypi/v/django-pdf-actions.svg?cache=no)](https://pypi.org/project/django-pdf-actions/)
[![Python Versions](https://img.shields.io/pypi/pyversions/django-pdf-actions.svg)](https://pypi.org/project/django-pdf-actions/)
[![Django Versions](https://img.shields.io/badge/django-3.2%20%7C%204.0%20%7C%204.1%20%7C%204.2%20%7C%205.0-green.svg)](https://pypi.org/project/django-pdf-actions/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/pypi/dm/django-pdf-actions.svg)](https://pypistats.org/packages/django-pdf-actions)

## 🚀 Overview

Transform your Django admin interface into a powerful PDF export engine! Django PDF Actions seamlessly integrates professional PDF generation capabilities into your existing Django models with minimal configuration.

```mermaid
graph LR
    A[Django Admin] --> B[Select Records]
    B --> C[Choose Export Action]
    C --> D[PDF Generation]
    D --> E[Download PDF]
    
    style A fill:#e1f5fe
    style E fill:#c8e6c9
```

## ✨ Key Features

=== "🎯 Easy Integration"
    
    Add PDF export to any Django model with just 2 lines of code:
    
    ```python
    actions = [export_to_pdf_landscape, export_to_pdf_portrait]
    ```

=== "🎨 Beautiful Design"
    
    - Professional layouts with customizable styling
    - Company branding with logos and headers
    - Multiple page orientations and sizes
    - RTL language support (Arabic, Persian)

=== "⚡ Performance"
    
    - Efficient handling of large datasets
    - Optimized memory usage
    - Background processing for large exports
    - Pagination for better performance

=== "🔧 Flexible"
    
    - Custom admin methods support
    - Configurable fonts and colors  
    - Multiple export formats
    - Advanced table styling

## 🏃‍♂️ Quick Start

Get up and running in 60 seconds:

```bash
# 1. Install the package
pip install django-pdf-actions

# 2. Add to your settings
INSTALLED_APPS = [
    # ...
    'django_pdf_actions',
]

# 3. Run migrations
python manage.py migrate
```

```python
# 4. Add to your admin.py
from django_pdf_actions.actions import export_to_pdf_landscape, export_to_pdf_portrait

@admin.register(YourModel)
class YourModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    actions = [export_to_pdf_landscape, export_to_pdf_portrait]
```

!!! success "That's it!"
    Your Django admin now has professional PDF export capabilities!

## 🔄 How It Works

```mermaid
sequenceDiagram
    participant U as User
    participant A as Django Admin
    participant P as PDF Actions
    participant R as ReportLab
    participant F as File System
    
    U->>A: Select records
    U->>A: Choose PDF export action
    A->>P: Process export request
    P->>P: Get model data & settings
    P->>R: Generate PDF document
    R->>F: Create PDF file
    F->>U: Download PDF
```

## 🌍 Internationalization Support

Perfect for global applications with built-in RTL support:

```mermaid
graph TD
    A[Multi-language Content] --> B{Text Direction}
    B -->|LTR| C[English, French, German...]
    B -->|RTL| D[Arabic, Persian, ...]
    C --> E[Left-aligned Layout]
    D --> F[Right-aligned Layout]
    E --> G[Professional PDF Output]
    F --> G
    
    style A fill:#fff3e0
    style G fill:#e8f5e8
```

## 📊 Use Cases

!!! example "Real-World Applications"
    
    === "📋 Reports"
        - Employee lists
        - Sales reports  
        - Inventory management
        - Financial statements
    
    === "📄 Documents"
        - Invoices and receipts
        - Certificates
        - ID cards
        - Product catalogs
    
    === "📈 Analytics"
        - Data exports
        - Performance reports
        - Survey results
        - Customer lists

## 🎯 Perfect For

- **Businesses** needing professional document generation
- **Developers** wanting quick PDF export functionality  
- **Multi-language** applications requiring RTL support
- **Large datasets** requiring optimized performance

## 🛠️ Technical Specifications

| Feature | Specification |
|---------|--------------|
| **Python** | 3.8+ |
| **Django** | 3.2+ |
| **PDF Engine** | ReportLab |
| **Languages** | Unicode support, RTL languages |
| **File Sizes** | Optimized for large datasets |
| **Performance** | Memory-efficient processing |

## 📚 Documentation Structure

```mermaid
mindmap
  root((Documentation))
    Getting Started
      Installation
      Quick Start
      Basic Usage
    Configuration
      Settings
      Advanced Config
    Examples
      Real-world Cases
      Custom Methods
    API Reference
      Actions
      Models
      Utils
```

## 🤝 Community & Support

- 💬 [GitHub Discussions](https://github.com/ibrahimroshdy/django-pdf-actions/discussions)
- 🐛 [Issue Tracker](https://github.com/ibrahimroshdy/django-pdf-actions/issues)
- 📖 [Documentation](https://ibrahimroshdy.github.io/django-pdf-actions/)
- 📦 [PyPI Package](https://pypi.org/project/django-pdf-actions/)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/ibrahimroshdy/django-pdf-actions/blob/main/LICENSE) file for details.

---

<div align="center">
  <strong>Ready to transform your Django admin? Let's get started!</strong>
  
  [Get Started →](installation.md){ .md-button .md-button--primary }
  [View Examples →](examples.md){ .md-button }
</div>
