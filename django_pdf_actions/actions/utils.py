"""Utility functions for PDF export actions"""

import hashlib
import logging
import os
from io import BytesIO
from typing import Optional

import arabic_reshaper
from bidi.algorithm import get_display
from django.conf import settings
from django.core.exceptions import FieldDoesNotExist, MultipleObjectsReturned
from django.utils.text import capfirst
from reportlab.platypus import Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A3, A2, A1
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle

from ..models import ExportPDFSettings

logger = logging.getLogger(__name__)

# Page size mapping
PAGE_SIZE_MAP = {
    'A4': A4,
    'A3': A3,
    'A2': A2,
    'A1': A1,
}


def get_page_size(pdf_settings):
    """Get the page size from settings or default to A4"""
    if pdf_settings and pdf_settings.page_size:
        return PAGE_SIZE_MAP.get(pdf_settings.page_size, A4)
    return A4


def get_active_settings():
    """Get the active PDF export settings or return default values"""
    try:
        return ExportPDFSettings.objects.get(active=True)
    except ExportPDFSettings.DoesNotExist:
        return None
    except MultipleObjectsReturned:
        logger.warning(
            'Multiple ExportPDFSettings rows have active=True; using the first by primary key.'
        )
        return ExportPDFSettings.objects.filter(active=True).order_by('pk').first()


def resolve_font_path(filename: str) -> Optional[str]:
    """Resolve a font file to an absolute path.

    Order:
    1. ``<BASE_DIR>/static/assets/fonts/<filename>`` (common project layout)
    2. Django staticfiles finders: ``assets/fonts/``, ``django_pdf_actions/fonts/``, or bare name
    """
    if not filename:
        return None

    project_path = os.path.join(
        settings.BASE_DIR, 'static', 'assets', 'fonts', filename
    )
    if os.path.isfile(project_path):
        return project_path

    try:
        from django.contrib.staticfiles import finders

        for rel in (
            os.path.join('assets', 'fonts', filename),
            os.path.join('django_pdf_actions', 'fonts', filename),
            filename,
        ):
            found = finders.find(rel)
            if found and os.path.isfile(found):
                return found
    except Exception as exc:
        logger.debug('Staticfiles font lookup skipped: %s', exc)

    return None


def hex_to_rgb(hex_color):
    """Convert hex color (#RGB or #RRGGBB) to an RGB tuple of floats in 0..1."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join(c * 2 for c in hex_color)
    return tuple(int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4))


def setup_font(pdf_settings):
    """Register a TTF for PDF export; idempotent per resolved path within the process."""
    candidates = []
    if pdf_settings and pdf_settings.font_name:
        path = resolve_font_path(pdf_settings.font_name)
        if path:
            candidates.append((pdf_settings.font_name, path))
    default_path = resolve_font_path('DejaVuSans.ttf')
    if default_path and all(p != default_path for _, p in candidates):
        candidates.append(('DejaVuSans.ttf', default_path))

    for label, font_path in candidates:
        digest = hashlib.sha256(os.path.abspath(font_path).encode()).hexdigest()[:12]
        internal_name = f'PdfAct_{digest}'
        if internal_name in pdfmetrics.getRegisteredFontNames():
            return internal_name
        try:
            pdfmetrics.registerFont(TTFont(internal_name, font_path, 'utf-8'))
            return internal_name
        except Exception as exc:
            logger.warning(
                'Error loading font %s from %s: %s',
                label,
                font_path,
                exc,
            )

    logger.info('Falling back to built-in Helvetica (no TTF resolved)')
    return 'Helvetica'


def get_logo_path(pdf_settings):
    """Resolve logo for ReportLab: local filesystem path, or ImageReader for remote storage.

    Returns ``None`` when the logo should not be drawn (disabled, missing file, or no settings).
    """
    if not pdf_settings or not getattr(pdf_settings, 'show_logo', True):
        return None
    logo = getattr(pdf_settings, 'logo', None)
    if not logo:
        return None
    name = getattr(logo, 'name', '') or ''
    if not name:
        return None

    if hasattr(logo, 'path'):
        try:
            path = logo.path
            if path and os.path.isfile(path):
                return path
        except (ValueError, NotImplementedError):
            pass

    storage = logo.storage
    try:
        if hasattr(storage, 'path'):
            path = storage.path(name)
            if path and os.path.isfile(path):
                return path
    except NotImplementedError:
        pass

    from reportlab.lib.utils import ImageReader

    with storage.open(name, 'rb') as fh:
        return ImageReader(BytesIO(fh.read()))


def create_table_style(pdf_settings, font_name, header_bg_color, grid_color):
    """Create table style based on settings"""
    # Get font sizes from settings
    header_font_size = pdf_settings.header_font_size if pdf_settings else 12
    body_font_size = pdf_settings.body_font_size if pdf_settings else 8
    grid_line_width = pdf_settings.grid_line_width if pdf_settings else 0.25
    table_spacing = pdf_settings.table_spacing if pdf_settings else 1.5

    # Cell / header alignment: explicit LEFT/RIGHT wins; CENTER + RTL uses RIGHT for body cells.
    cell_alignment = 'CENTER'
    header_alignment = 'CENTER'
    if pdf_settings:
        cell_alignment = getattr(
            pdf_settings, 'content_alignment', 'CENTER'
        ) or 'CENTER'
        header_alignment = getattr(
            pdf_settings, 'header_alignment', 'CENTER'
        ) or 'CENTER'
        if pdf_settings.rtl_support and cell_alignment == 'CENTER':
            cell_alignment = 'RIGHT'

    # Build table style
    style = [
        ('FONT', (0, 0), (-1, -1), font_name, body_font_size),  # Body font
        ('FONT', (0, 0), (-1, 0), font_name, header_font_size),  # Header font
        ('FONTWEIGHT', (0, 0), (-1, 0), 'bold'),  # Make header row bold
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), header_bg_color),
        ('GRID', (0, 0), (-1, -1), grid_line_width, grid_color),
        ('ALIGN', (0, 1), (-1, -1), cell_alignment),  # Content alignment
        ('ALIGN', (0, 0), (-1, 0), header_alignment),  # Header alignment
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), grid_line_width, grid_color),
        ('INNERGRID', (0, 0), (-1, -1), grid_line_width, grid_color),
        ('TOPPADDING', (0, 0), (-1, -1), table_spacing * mm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), table_spacing * mm),
        ('LEFTPADDING', (0, 0), (-1, -1), table_spacing * 2 * mm),
        ('RIGHTPADDING', (0, 0), (-1, -1), table_spacing * 2 * mm),
    ]

    return TableStyle(style)


def create_header_style(pdf_settings, font_name, is_header=False):
    """Create style for column headers and body text"""
    styles = getSampleStyleSheet()

    # Use proper font sizes from settings
    if pdf_settings:
        font_size = pdf_settings.header_font_size if is_header else pdf_settings.body_font_size
    else:
        font_size = 12 if is_header else 8

    # 0 = left, 1 = center, 2 = right. RTL: treat CENTER content as RIGHT for body paragraphs.
    alignment = 1
    if pdf_settings:
        if is_header:
            ha = getattr(pdf_settings, 'header_alignment', 'CENTER') or 'CENTER'
            if ha == 'LEFT':
                alignment = 0
            elif ha == 'RIGHT':
                alignment = 2
            else:
                alignment = 1
        else:
            ca = getattr(pdf_settings, 'content_alignment', 'CENTER') or 'CENTER'
            if ca == 'LEFT':
                alignment = 0
            elif ca == 'RIGHT':
                alignment = 2
            else:
                alignment = 1
        if getattr(pdf_settings, 'rtl_support', False) and not is_header:
            if (getattr(pdf_settings, 'content_alignment', 'CENTER') or 'CENTER') == 'CENTER':
                alignment = 2

    style = ParagraphStyle(
        'CustomHeader' if is_header else 'CustomBody',
        parent=styles['Normal'],
        fontSize=font_size,
        fontName=font_name,
        alignment=alignment,
        spaceAfter=2 * mm,
        leading=font_size * 1.2,  # Line height
        textColor=colors.black,
        fontWeight='bold' if is_header else 'normal'  # Make headers bold
    )
    
    # ReportLab doesn't support direct CSS for RTL
    # The text direction is handled by the arabic_reshaper and get_display functions
    
    return style


def reshape_to_arabic(
    columns,
    font_name,
    font_size,
    queryset,
    max_chars_per_line,
    pdf_settings=None,
    modeladmin=None,
):
    """Build ReportLab table rows from ``list_display`` columns (fields + admin methods)."""
    header_style = create_header_style(pdf_settings, font_name, is_header=True)
    body_style = create_header_style(pdf_settings, font_name, is_header=False)

    rtl_enabled = pdf_settings and getattr(pdf_settings, 'rtl_support', False)

    if rtl_enabled:
        columns = list(reversed(columns))

    headers = []
    for column in columns:
        header = None

        if hasattr(queryset.model, column):
            try:
                field = queryset.model._meta.get_field(column)
                header = (
                    capfirst(field.verbose_name)
                    if hasattr(field, 'verbose_name')
                    else capfirst(column)
                )
            except FieldDoesNotExist:
                header = capfirst(column.replace('_', ' '))
        elif modeladmin and hasattr(modeladmin, column):
            method = getattr(modeladmin, column)
            if hasattr(method, 'short_description'):
                header = str(method.short_description)
            else:
                header = capfirst(column.replace('_', ' '))
        else:
            header = capfirst(column.replace('_', ' '))

        if rtl_enabled and isinstance(header, str):
            header = arabic_reshaper.reshape(header)
            header = get_display(header)

        headers.append(Paragraph(str(header), header_style))

    data = [headers]

    for obj in queryset:
        row = []
        for column in columns:
            value = None
            if hasattr(obj, column):
                value = getattr(obj, column)
            elif modeladmin and hasattr(modeladmin, column):
                try:
                    method = getattr(modeladmin, column)
                    if callable(method):
                        value = method(obj)
                    else:
                        value = method
                except Exception as exc:
                    logger.debug(
                        'Admin list_display value for %r failed: %s',
                        column,
                        exc,
                        exc_info=True,
                    )
                    value = f'Error: {column}'
            else:
                value = f'Missing: {column}'

            value = str(value) if value is not None else ''

            if isinstance(value, str):
                if rtl_enabled:
                    value = arabic_reshaper.reshape(value)
                    value = get_display(value)

                if len(value) > max_chars_per_line:
                    lines = [
                        value[i : i + max_chars_per_line]
                        for i in range(0, len(value), max_chars_per_line)
                    ]
                    if rtl_enabled:
                        lines.reverse()
                    value = '<br/>'.join(lines)
            row.append(Paragraph(str(value), body_style))
        data.append(row)
    return data


def calculate_column_widths(data, table_width, font_name, font_size):
    """Calculate optimal column widths based on content"""
    if not data:
        return []
    num_cols = len(data[0])
    max_widths = [0] * num_cols

    # Find maximum content width for each column
    for row in data:
        for i, cell in enumerate(row):
            content = str(cell)
            # Headers get more weight in width calculation
            multiplier = 1.2 if row == data[0] else 1.0
            width = len(content) * font_size * 0.6 * multiplier
            max_widths[i] = max(max_widths[i], width)

    # Ensure minimum width for each column
    min_width = table_width * 0.05  # 5% of table width
    max_widths = [max(width, min_width) for width in max_widths]

    # Normalize widths to fit table_width
    total_width = sum(max_widths)
    return [width / total_width * table_width for width in max_widths]


def draw_table_data(p, page, rows_per_page, total_rows, col_widths, table_style, canvas_height, table_top_margin, data):
    """Draw table data for current page"""
    start_row = page * rows_per_page + 1
    end_row = min((page + 1) * rows_per_page + 1, total_rows + 1)
    page_data = data[start_row:end_row]
    table = Table(page_data, colWidths=col_widths, style=table_style)
    table.wrapOn(p, 100, 100)
    table_height = table._height
    y = canvas_height - table_top_margin - table_height
    table.drawOn(p, 100, y)


def draw_model_name(
    p,
    modeladmin,
    font_name,
    font_size,
    canvas_width,
    canvas_height,
    page_margin,
    pdf_settings=None,
):
    """Draw model name header"""
    # Try to get verbose_name_plural, then verbose_name, then fall back to __name__
    model = modeladmin.model

    if hasattr(model._meta, 'verbose_name_plural') and model._meta.verbose_name_plural:
        model_name = str(capfirst(model._meta.verbose_name_plural))
    elif hasattr(model._meta, 'verbose_name') and model._meta.verbose_name:
        model_name = str(capfirst(model._meta.verbose_name))
    else:
        model_name = model.__name__

    if pdf_settings is None:
        pdf_settings = get_active_settings()

    # Apply Arabic reshaping and bidirectional algorithm if RTL support is enabled
    if pdf_settings and hasattr(pdf_settings, 'rtl_support') and pdf_settings.rtl_support:
        model_name = arabic_reshaper.reshape(model_name)
        model_name = get_display(model_name)

    p.setFont(font_name, font_size)
    model_name_string_width = p.stringWidth(model_name, font_name, font_size)

    # Use title_alignment if available
    if pdf_settings and hasattr(pdf_settings, 'title_alignment'):
        alignment = pdf_settings.title_alignment
        if alignment == 'LEFT':
            x = page_margin + 10  # Left aligned with margin
        elif alignment == 'RIGHT':
            x = canvas_width - model_name_string_width - page_margin - 10  # Right aligned with margin
        else:  # CENTER is default
            x = canvas_width / 2
    else:
        # Default center alignment
        x = canvas_width / 2

    if pdf_settings is None:
        use_centred_string = True
    elif getattr(pdf_settings, 'title_alignment', 'CENTER') == 'CENTER':
        use_centred_string = True
    else:
        use_centred_string = False

    if use_centred_string:
        p.drawCentredString(x, canvas_height - page_margin, model_name)
    else:
        p.drawString(x, canvas_height - page_margin, model_name)


def draw_exported_at(
    p, font_name, font_size, canvas_width, footer_margin, pdf_settings=None
):
    """Draw export timestamp"""
    from datetime import datetime
    export_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if pdf_settings is None:
        pdf_settings = get_active_settings()

    exported_at_string = f"Exported at: {export_date_time}"

    # Apply Arabic reshaping and bidirectional algorithm if RTL support is enabled
    if pdf_settings and hasattr(pdf_settings, 'rtl_support') and pdf_settings.rtl_support:
        exported_at_string = arabic_reshaper.reshape(exported_at_string)
        exported_at_string = get_display(exported_at_string)

    p.setFont(font_name, font_size)
    exported_at_string_width = p.stringWidth(exported_at_string, font_name, font_size)

    # Position string appropriately based on RTL setting
    if pdf_settings and hasattr(pdf_settings, 'rtl_support') and pdf_settings.rtl_support:
        x = 100  # For RTL, align to the left side with margin
    else:
        x = canvas_width - exported_at_string_width - 100  # For LTR, align to the right side with margin

    p.drawString(x, footer_margin, exported_at_string)


def draw_page_number(
    p,
    page,
    total_pages,
    font_name,
    font_size,
    canvas_width,
    footer_margin,
    pdf_settings=None,
):
    """Draw page numbers"""
    if pdf_settings is None:
        pdf_settings = get_active_settings()

    page_string = f"Page {page + 1} of {total_pages}"

    # Apply Arabic reshaping and bidirectional algorithm if RTL support is enabled
    if pdf_settings and hasattr(pdf_settings, 'rtl_support') and pdf_settings.rtl_support:
        page_string = arabic_reshaper.reshape(page_string)
        page_string = get_display(page_string)

    p.setFont(font_name, font_size)
    page_string_width = p.stringWidth(page_string, font_name, font_size)
    x = canvas_width / 2
    p.drawCentredString(x, footer_margin, page_string)


def draw_logo(p, logo_source, canvas_width, canvas_height):
    """Draw logo from a filesystem path or a ReportLab ``ImageReader`` (remote storage)."""
    if logo_source is None:
        return
    if isinstance(logo_source, str) and not os.path.isfile(logo_source):
        return
    from reportlab.platypus import Image

    logo_width = 100
    logo_height = 50
    logo_offset = 20
    logo_x = canvas_width - logo_width - logo_offset
    logo_y = canvas_height - logo_height - logo_offset
    logo = Image(logo_source, width=logo_width, height=logo_height)
    logo.drawOn(p, logo_x, logo_y)
