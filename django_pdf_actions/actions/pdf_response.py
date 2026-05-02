"""
Shared PDF HTTP response for admin export actions.

Request trace (landscape example)
---------------------------------
1. Admin POST runs ``export_to_pdf_landscape(modeladmin, request, queryset)`` (``landscape.py``).
2. That delegates here to ``build_pdf_export_response(..., landscape=True)``.
3. ``get_active_settings()`` (``utils``) returns the active row, ``None`` if none exist, or the
   first by primary key if multiple rows are marked active (with a warning).
4. Page size from ``get_page_size(pdf_settings)``; if *landscape*, width/height are swapped.
5. ``setup_font`` → ``resolve_font_path`` (project ``static/assets/fonts`` then staticfiles finders).
6. ``reshape_to_arabic`` builds the table matrix from ``modeladmin.list_display`` + queryset rows
   (headers from field verbose names or admin ``short_description``; cells from attributes or
   admin callables).
7. ``calculate_column_widths`` / ReportLab ``Table`` + draw helpers lay out each page slice;
   ``HttpResponse`` is returned with PDF bytes attached.
"""

import io
from datetime import datetime

from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table

from .utils import (
    calculate_column_widths,
    create_table_style,
    draw_exported_at,
    draw_logo,
    draw_model_name,
    draw_page_number,
    get_active_settings,
    get_logo_path,
    get_page_size,
    hex_to_rgb,
    reshape_to_arabic,
    setup_font,
)


def build_pdf_export_response(modeladmin, queryset, *, landscape: bool) -> HttpResponse:
    """Generate a PDF download for the given admin queryset (shared portrait/landscape)."""
    pdf_settings = get_active_settings()

    pagesize = get_page_size(pdf_settings)
    if landscape:
        pagesize = pagesize[1], pagesize[0]

    if landscape:
        rows_per_page = pdf_settings.items_per_page if pdf_settings else 15
        max_chars = pdf_settings.max_chars_per_line if pdf_settings else 60
    else:
        rows_per_page = pdf_settings.items_per_page if pdf_settings else 20
        max_chars = pdf_settings.max_chars_per_line if pdf_settings else 40

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="{modeladmin.model.__name__}_export_'
        f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.pdf"'
    )
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=pagesize)
    canvas_width, canvas_height = pagesize
    page_margin = (pdf_settings.page_margin_mm if pdf_settings else 15) * mm

    font_name = setup_font(pdf_settings)
    logo_source = get_logo_path(pdf_settings)
    header_bg_color = (
        hex_to_rgb(pdf_settings.header_background_color) if pdf_settings else colors.lightgrey
    )
    grid_color = hex_to_rgb(pdf_settings.grid_line_color) if pdf_settings else colors.black
    table_style = create_table_style(pdf_settings, font_name, header_bg_color, grid_color)

    table_width = canvas_width - (2 * page_margin)
    table_height = canvas_height - (3 * page_margin)

    valid_fields = list(modeladmin.list_display)
    data = reshape_to_arabic(
        valid_fields,
        font_name,
        pdf_settings.body_font_size if pdf_settings else 7,
        queryset,
        max_chars,
        pdf_settings,
        modeladmin,
    )

    col_widths = calculate_column_widths(
        data,
        table_width,
        font_name,
        pdf_settings.body_font_size if pdf_settings else 7,
    )
    total_rows = len(data) - 1
    total_pages = max(
        1, int((total_rows + rows_per_page - 1) // rows_per_page)
    )

    header_margin = page_margin + (10 * mm)
    table_top_margin = header_margin + (8 * mm)
    footer_margin = page_margin + (5 * mm)

    for page in range(total_pages):
        if not pdf_settings or pdf_settings.show_header:
            draw_model_name(
                p,
                modeladmin,
                font_name,
                pdf_settings.header_font_size if pdf_settings else 12,
                canvas_width,
                canvas_height,
                header_margin,
                pdf_settings=pdf_settings,
            )

        start_row = page * rows_per_page
        end_row = min((page + 1) * rows_per_page + 1, len(data))
        page_data = data[0:1] + data[start_row + 1 : end_row]

        table = Table(page_data, colWidths=col_widths, style=table_style)
        table.wrapOn(p, table_width, table_height)
        table_x = (canvas_width - table_width) / 2
        table_y = canvas_height - table_top_margin - table._height
        table.drawOn(p, table_x, table_y)

        if not pdf_settings or pdf_settings.show_export_time:
            draw_exported_at(
                p,
                font_name,
                pdf_settings.body_font_size if pdf_settings else 7,
                canvas_width,
                footer_margin,
                pdf_settings=pdf_settings,
            )

        if not pdf_settings or pdf_settings.show_page_numbers:
            draw_page_number(
                p,
                page,
                total_pages,
                font_name,
                pdf_settings.body_font_size if pdf_settings else 7,
                canvas_width,
                footer_margin,
                pdf_settings=pdf_settings,
            )

        if logo_source is not None:
            draw_logo(p, logo_source, canvas_width, canvas_height)

        p.showPage()

    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response
