"""Utility functions for PDF export actions"""

import os

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A3, A2, A1
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle

from ..models import ExportPDFSettings


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


def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def setup_font(pdf_settings):
    """Setup and register font"""
    font_name = 'PDF_Font'

    # Try to get font from settings
    if pdf_settings and pdf_settings.font_name:
        font_path = os.path.join(settings.BASE_DIR, 'static', 'assets', 'fonts', pdf_settings.font_name)
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path, 'utf-8'))
                return font_name
            except Exception as e:
                print(f"Error loading font {pdf_settings.font_name}: {str(e)}")

    # Try default font
    default_font = os.path.join(settings.BASE_DIR, 'static', 'assets', 'fonts', 'DejaVuSans.ttf')
    if os.path.exists(default_font):
        try:
            pdfmetrics.registerFont(TTFont(font_name, default_font, 'utf-8'))
            return font_name
        except Exception as e:
            print(f"Error loading default font: {str(e)}")

    # If all else fails, use Helvetica (built into ReportLab)
    return 'Helvetica'


def get_logo_path(pdf_settings):
    """Get logo file path"""
    if pdf_settings and pdf_settings.logo and pdf_settings.show_logo:
        return pdf_settings.logo.path
    return os.path.join(settings.MEDIA_ROOT, 'export_pdf/logo.png')


def create_table_style(pdf_settings, font_name, header_bg_color, grid_color):
    """Create table style based on settings"""
    # Get font sizes from settings
    header_font_size = pdf_settings.header_font_size if pdf_settings else 12
    body_font_size = pdf_settings.body_font_size if pdf_settings else 8
    grid_line_width = pdf_settings.grid_line_width if pdf_settings else 0.25
    table_spacing = pdf_settings.table_spacing if pdf_settings else 1.5
    
    # Determine cell alignment based on RTL setting
    # 'LEFT', 'CENTER', 'RIGHT'
    cell_alignment = 'CENTER'  # Default is center
    if pdf_settings and pdf_settings.rtl_support:
        cell_alignment = 'RIGHT'  # For RTL languages, default to right alignment

    return TableStyle([
        ('FONT', (0, 0), (-1, -1), font_name, body_font_size),  # Body font
        ('FONT', (0, 0), (-1, 0), font_name, header_font_size),  # Header font
        ('FONTWEIGHT', (0, 0), (-1, 0), 'bold'),  # Make header row bold
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), header_bg_color),
        ('GRID', (0, 0), (-1, -1), grid_line_width, grid_color),
        ('ALIGN', (0, 0), (-1, -1), cell_alignment),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), grid_line_width, grid_color),
        ('INNERGRID', (0, 0), (-1, -1), grid_line_width, grid_color),
        ('TOPPADDING', (0, 0), (-1, -1), table_spacing * mm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), table_spacing * mm),
        ('LEFTPADDING', (0, 0), (-1, -1), table_spacing * 2 * mm),
        ('RIGHTPADDING', (0, 0), (-1, -1), table_spacing * 2 * mm),
    ])


def create_header_style(pdf_settings, font_name, is_header=False):
    """Create style for column headers and body text"""
    styles = getSampleStyleSheet()

    # Use proper font sizes from settings
    if pdf_settings:
        font_size = pdf_settings.header_font_size if is_header else pdf_settings.body_font_size
    else:
        font_size = 12 if is_header else 8
    
    # Determine text alignment based on RTL setting
    # 0 = left, 1 = center, 2 = right
    alignment = 1  # Default is center
    if pdf_settings and pdf_settings.rtl_support:
        # For RTL languages, reverse the alignment
        alignment = 2 if not is_header else 1  # Right-align for body text in RTL mode, center for headers

    return ParagraphStyle(
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


def calculate_column_widths(data, table_width, font_name, font_size):
    """Calculate optimal column widths based on content"""
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


def draw_model_name(p, modeladmin, font_name, font_size, canvas_width, canvas_height, page_margin):
    """Draw model name header"""
    model_name = modeladmin.model.__name__
    
    # Get settings to check if RTL is enabled
    pdf_settings = get_active_settings()
    
    # Apply Arabic reshaping and bidirectional algorithm if RTL support is enabled
    if pdf_settings and pdf_settings.rtl_support:
        import arabic_reshaper
        from bidi.algorithm import get_display
        model_name = arabic_reshaper.reshape(model_name)
        model_name = get_display(model_name)
    
    p.setFont(font_name, font_size)
    model_name_string_width = p.stringWidth(model_name, font_name, font_size)
    x = canvas_width / 2
    p.drawCentredString(x, canvas_height - page_margin, model_name)


def draw_exported_at(p, font_name, font_size, canvas_width, footer_margin):
    """Draw export timestamp"""
    from datetime import datetime
    export_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Get settings to check if RTL is enabled
    pdf_settings = get_active_settings()
    
    exported_at_string = f"Exported at: {export_date_time}"
    
    # Apply Arabic reshaping and bidirectional algorithm if RTL support is enabled
    if pdf_settings and pdf_settings.rtl_support:
        import arabic_reshaper
        from bidi.algorithm import get_display
        exported_at_string = arabic_reshaper.reshape(exported_at_string)
        exported_at_string = get_display(exported_at_string)
    
    p.setFont(font_name, font_size)
    exported_at_string_width = p.stringWidth(exported_at_string, font_name, font_size)
    
    # Position string appropriately based on RTL setting
    if pdf_settings and pdf_settings.rtl_support:
        x = 100  # For RTL, align to the left side with margin
    else:
        x = canvas_width - exported_at_string_width - 100  # For LTR, align to the right side with margin
    
    p.drawString(x, footer_margin, exported_at_string)


def draw_page_number(p, page, total_pages, font_name, font_size, canvas_width, footer_margin):
    """Draw page numbers"""
    # Get settings to check if RTL is enabled
    pdf_settings = get_active_settings()
    
    page_string = f"Page {page + 1} of {total_pages}"
    
    # Apply Arabic reshaping and bidirectional algorithm if RTL support is enabled
    if pdf_settings and pdf_settings.rtl_support:
        import arabic_reshaper
        from bidi.algorithm import get_display
        page_string = arabic_reshaper.reshape(page_string)
        page_string = get_display(page_string)
    
    p.setFont(font_name, font_size)
    page_string_width = p.stringWidth(page_string, font_name, font_size)
    x = canvas_width / 2
    p.drawCentredString(x, footer_margin, page_string)


def draw_logo(p, logo_file, canvas_width, canvas_height):
    """Draw logo if it exists"""
    if os.path.exists(logo_file):
        from reportlab.platypus import Image
        logo_width = 100
        logo_height = 50
        logo_offset = 20
        logo_x = canvas_width - logo_width - logo_offset
        logo_y = canvas_height - logo_height - logo_offset
        logo = Image(logo_file, width=logo_width, height=logo_height)
        logo.drawOn(p, logo_x, logo_y)
