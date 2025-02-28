"""Tests for PDF export utility functions."""

from django.test import SimpleTestCase
from reportlab.lib import colors
from reportlab.platypus import TableStyle
from django_pdf_actions.actions.utils import (
    hex_to_rgb, setup_font, get_logo_path,
    create_table_style, create_header_style,
    calculate_column_widths
)


class PDFUtilsTest(SimpleTestCase):
    """Test cases for PDF utilities."""

    def setUp(self):
        """Set up test environment."""
        self.settings = type('MockSettings', (), {
            'title': 'Test Settings',
            'active': True,
            'header_font_size': 12,
            'body_font_size': 10,
            'page_margin_mm': 15,
            'items_per_page': 10,
            'header_background_color': '#F0F0F0',
            'grid_line_color': '#000000',
            'grid_line_width': 0.25,
            'font_name': 'DejaVuSans',
            'logo': None,
            'show_logo': True,
            'show_header': True,
            'show_export_time': True,
            'show_page_numbers': True,
            'max_chars_per_line': 50,
            'table_spacing': 1.5,
            'header_height_mm': 20,
            'footer_height_mm': 15,
            'table_line_height': 1.2,
            'table_header_height': 30,
            'page_size': 'A4'
        })()

    def test_hex_to_rgb(self):
        """Test hex color to RGB conversion."""
        # Test white
        self.assertEqual(
            hex_to_rgb('#FFFFFF'),
            (1.0, 1.0, 1.0)
        )
        # Test black
        self.assertEqual(
            hex_to_rgb('#000000'),
            (0.0, 0.0, 0.0)
        )
        # Test gray
        self.assertEqual(
            hex_to_rgb('#808080'),
            (0.5019607843137255, 0.5019607843137255, 0.5019607843137255)
        )

    def test_setup_font(self):
        """Test font setup."""
        font_name = setup_font(self.settings)
        self.assertIsInstance(font_name, str)
        self.assertTrue(len(font_name) > 0)

    def test_get_logo_path(self):
        """Test logo path retrieval."""
        path = get_logo_path(self.settings)
        self.assertTrue('export_pdf/logo.png' in path)

    def test_create_table_style(self):
        """Test table style creation."""
        style = create_table_style(
            self.settings,
            'Helvetica',
            colors.lightgrey,
            colors.black
        )
        self.assertIsInstance(style, TableStyle)
        self.assertTrue(hasattr(style, '_cmds'))
        self.assertTrue(len(style._cmds) > 0)

    def test_create_header_style(self):
        """Test header style creation."""
        style = create_header_style(self.settings, 'Helvetica', True)
        self.assertEqual(style.fontSize, self.settings.header_font_size)
        self.assertEqual(style.fontName, 'Helvetica')

    def test_calculate_column_widths(self):
        """Test column width calculation."""
        data = [
            ['Short', 'Medium Column', 'Very Long Column Header'],
            ['Data1', 'Data2', 'Data3'],
        ]
        table_width = 500
        widths = calculate_column_widths(
            data, table_width, 'Helvetica', 10
        )
        
        self.assertEqual(len(widths), 3)
        self.assertTrue(all(w > 0 for w in widths))
        self.assertAlmostEqual(sum(widths), table_width, places=2) 