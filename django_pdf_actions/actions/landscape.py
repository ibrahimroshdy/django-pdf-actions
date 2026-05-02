"""Landscape PDF export action."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .pdf_response import build_pdf_export_response
from .utils import reshape_to_arabic

__all__ = ["export_to_pdf_landscape", "reshape_to_arabic"]


@admin.action(description=_("Export selected records to PDF (landscape)"))
def export_to_pdf_landscape(modeladmin, request, queryset):
    """Export data to PDF in landscape orientation."""
    return build_pdf_export_response(modeladmin, queryset, landscape=True)
