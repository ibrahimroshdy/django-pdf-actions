"""Landscape PDF export action"""

import io
import os
from datetime import datetime

import arabic_reshaper
from bidi.algorithm import get_display
from django.http import HttpResponse
from django.utils.text import capfirst
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table

from .utils import (
    get_active_settings, hex_to_rgb, setup_font, get_logo_path,
    create_table_style, create_header_style, calculate_column_widths,
    draw_model_name, draw_exported_at, draw_page_number, draw_logo,
    get_page_size
)


def reshape_to_arabic(columns, font_name, font_size, queryset, max_chars_per_line, pdf_settings=None):
    """Process and reshape Arabic text if present"""
    # Create header style with larger font and bold for column headers
    header_style = create_header_style(pdf_settings, font_name, is_header=True)
    body_style = create_header_style(pdf_settings, font_name, is_header=False)

    # Get RTL setting
    rtl_enabled = pdf_settings and pdf_settings.rtl_support

    # Process column headers - capitalize and format
    headers = []
    for column in columns:
        # Get verbose name if available, otherwise capitalize the field name
        if hasattr(queryset.model, column):
            field = queryset.model._meta.get_field(column)
            header = capfirst(field.verbose_name) if hasattr(field, 'verbose_name') else capfirst(column)
        else:
            header = capfirst(column.replace('_', ' '))
        
        # Apply RTL processing to headers if enabled
        if rtl_enabled and isinstance(header, str):
            header = arabic_reshaper.reshape(header)
            header = get_display(header)
            
        headers.append(Paragraph(str(header), header_style))

    data = [headers]

    for obj in queryset:
        row = []
        for column in columns:
            value = str(getattr(obj, column))
            if isinstance(value, str):
                # Only reshape if RTL is enabled and the string contains text
                if rtl_enabled:
                    value = arabic_reshaper.reshape(value)
                    value = get_display(value)
                
                # Handle line wrapping for long text
                if len(value) > max_chars_per_line:
                    lines = [value[i:i + max_chars_per_line] for i in range(0, len(value), max_chars_per_line)]
                    value = "<br/>".join(lines)
            row.append(Paragraph(str(value), body_style))
        data.append(row)
    return data


def export_to_pdf_landscape(modeladmin, request, queryset):
    """Export data to PDF in landscape orientation"""
    # Get active settings
    pdf_settings = get_active_settings()

    # Get page size from settings and rotate for landscape
    pagesize = get_page_size(pdf_settings)
    pagesize = pagesize[1], pagesize[0]  # Swap width and height for landscape

    # Create the response object with content type as PDF
    response = HttpResponse(content_type='application/pdf')
    response[
        'Content-Disposition'] = f'attachment; filename="{modeladmin.model.__name__}_export_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.pdf"'
    buffer = io.BytesIO()

    # Initialize canvas with landscape orientation
    p = canvas.Canvas(buffer, pagesize=pagesize)
    canvas_width, canvas_height = pagesize

    # Use settings or defaults - optimized for landscape
    ROWS_PER_PAGE = pdf_settings.items_per_page if pdf_settings else 15  # Fewer rows in landscape due to less height
    max_chars_per_line = pdf_settings.max_chars_per_line if pdf_settings else 60  # More chars per line in landscape
    page_margin = (pdf_settings.page_margin_mm if pdf_settings else 15) * mm

    # Setup font and colors
    font_name = setup_font(pdf_settings)
    logo_file = get_logo_path(pdf_settings)
    header_bg_color = hex_to_rgb(pdf_settings.header_background_color) if pdf_settings else colors.lightgrey
    grid_color = hex_to_rgb(pdf_settings.grid_line_color) if pdf_settings else colors.black

    # Create table style optimized for landscape
    table_style = create_table_style(pdf_settings, font_name, header_bg_color, grid_color)

    # Calculate available space for table
    table_width = canvas_width - (2 * page_margin)
    table_height = canvas_height - (3 * page_margin)  # Leave space for header and footer

    # Prepare data
    valid_fields = [field for field in modeladmin.list_display if hasattr(modeladmin.model, field)]
    data = reshape_to_arabic(valid_fields, font_name,
                             pdf_settings.body_font_size if pdf_settings else 7,
                             queryset, max_chars_per_line, pdf_settings)

    # Calculate column widths and pages
    col_widths = calculate_column_widths(data, table_width, font_name,
                                         pdf_settings.body_font_size if pdf_settings else 7)
    total_rows = len(data) - 1
    total_pages = int((total_rows + ROWS_PER_PAGE - 1) / ROWS_PER_PAGE)

    # Define margins - optimized for landscape
    header_margin = page_margin + (10 * mm)  # Space for title
    table_top_margin = header_margin + (8 * mm)  # Start table below header
    footer_margin = page_margin + (5 * mm)

    # Draw pages
    for page in range(total_pages):
        if not pdf_settings or pdf_settings.show_header:
            draw_model_name(p, modeladmin, font_name,
                            pdf_settings.header_font_size if pdf_settings else 12,
                            canvas_width, canvas_height, header_margin)

        # Draw the table with adjusted positioning - centered
        start_row = page * ROWS_PER_PAGE
        end_row = min((page + 1) * ROWS_PER_PAGE, len(data))
        page_data = data[0:1] + data[start_row + 1:end_row]  # Include header row

        table = Table(page_data, colWidths=col_widths, style=table_style)
        table.wrapOn(p, table_width, table_height)
        table_x = (canvas_width - table_width) / 2  # Center the table
        table_y = canvas_height - table_top_margin - table._height
        table.drawOn(p, table_x, table_y)

        # Draw footer elements
        if not pdf_settings or pdf_settings.show_export_time:
            draw_exported_at(p, font_name,
                             pdf_settings.body_font_size if pdf_settings else 7,
                             canvas_width, footer_margin)

        if not pdf_settings or pdf_settings.show_page_numbers:
            draw_page_number(p, page, total_pages, font_name,
                             pdf_settings.body_font_size if pdf_settings else 7,
                             canvas_width, footer_margin)

        if (not pdf_settings or pdf_settings.show_logo) and os.path.exists(logo_file):
            draw_logo(p, logo_file, canvas_width, canvas_height)

        p.showPage()

    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response
