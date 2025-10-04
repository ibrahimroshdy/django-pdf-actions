"""Tests for PDF export utility functions."""

import os
import tempfile
from unittest.mock import patch, MagicMock, mock_open
from django.test import TestCase, override_settings
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A3, A2, A1
from reportlab.platypus import TableStyle, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from django_pdf_actions.actions.utils import (
    hex_to_rgb, setup_font, get_logo_path, get_page_size, get_active_settings,
    create_table_style, create_header_style, calculate_column_widths,
    draw_model_name, draw_exported_at, draw_page_number, draw_logo,
    PAGE_SIZE_MAP
)
from django_pdf_actions.models import ExportPDFSettings


class PDFUtilsTest(TestCase):
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
            'font_name': 'DejaVuSans.ttf',
            'logo': None,
            'show_logo': True,
            'show_header': True,
            'show_export_time': True,
            'show_page_numbers': True,
            'rtl_support': False,
            'max_chars_per_line': 50,
            'table_spacing': 1.5,
            'content_alignment': 'CENTER',
            'header_alignment': 'CENTER',
            'title_alignment': 'CENTER',
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
        # Test red
        self.assertEqual(
            hex_to_rgb('#FF0000'),
            (1.0, 0.0, 0.0)
        )
        # Test green
        self.assertEqual(
            hex_to_rgb('#00FF00'),
            (0.0, 1.0, 0.0)
        )
        # Test blue
        self.assertEqual(
            hex_to_rgb('#0000FF'),
            (0.0, 0.0, 1.0)
        )

    @patch('django_pdf_actions.actions.utils.settings.BASE_DIR', '/fake/path')
    @patch('os.path.exists')
    def test_setup_font_with_custom_font(self, mock_exists):
        """Test font setup with custom font."""
        mock_exists.return_value = True
        
        with patch('django_pdf_actions.actions.utils.pdfmetrics.registerFont') as mock_register:
            font_name = setup_font(self.settings)
            self.assertEqual(font_name, 'PDF_Font')
            mock_register.assert_called_once()

    @patch('django_pdf_actions.actions.utils.settings.BASE_DIR', '/fake/path')
    @patch('os.path.exists')
    def test_setup_font_with_default_font(self, mock_exists):
        """Test font setup with default font."""
        # First call returns False (custom font doesn't exist)
        # Second call returns True (default font exists)
        mock_exists.side_effect = [False, True]
        
        with patch('django_pdf_actions.actions.utils.pdfmetrics.registerFont') as mock_register:
            font_name = setup_font(self.settings)
            self.assertEqual(font_name, 'PDF_Font')
            mock_register.assert_called_once()

    @patch('django_pdf_actions.actions.utils.settings.BASE_DIR', '/fake/path')
    @patch('os.path.exists')
    def test_setup_font_fallback_to_helvetica(self, mock_exists):
        """Test font setup fallback to Helvetica."""
        mock_exists.return_value = False
        
        font_name = setup_font(self.settings)
        self.assertEqual(font_name, 'Helvetica')

    @patch('django_pdf_actions.actions.utils.settings.BASE_DIR', '/fake/path')
    @patch('os.path.exists')
    def test_setup_font_with_none_settings(self, mock_exists):
        """Test font setup with None settings."""
        mock_exists.return_value = False
        
        font_name = setup_font(None)
        self.assertEqual(font_name, 'Helvetica')

    def test_get_logo_path_with_logo(self):
        """Test logo path retrieval with logo."""
        mock_logo = MagicMock()
        mock_logo.path = '/path/to/logo.png'
        self.settings.logo = mock_logo
        
        path = get_logo_path(self.settings)
        self.assertEqual(path, '/path/to/logo.png')

    def test_get_logo_path_without_logo(self):
        """Test logo path retrieval without logo."""
        self.settings.logo = None
        
        with patch('django_pdf_actions.actions.utils.settings.MEDIA_ROOT', '/media'):
            path = get_logo_path(self.settings)
            self.assertEqual(path, '/media/export_pdf/logo.png')

    def test_get_logo_path_with_none_settings(self):
        """Test logo path retrieval with None settings."""
        with patch('django_pdf_actions.actions.utils.settings.MEDIA_ROOT', '/media'):
            path = get_logo_path(None)
            self.assertEqual(path, '/media/export_pdf/logo.png')

    def test_get_page_size_with_settings(self):
        """Test page size retrieval with settings."""
        self.settings.page_size = 'A3'
        size = get_page_size(self.settings)
        self.assertEqual(size, A3)

    def test_get_page_size_without_settings(self):
        """Test page size retrieval without settings."""
        size = get_page_size(None)
        self.assertEqual(size, A4)

    def test_get_page_size_invalid_size(self):
        """Test page size retrieval with invalid size."""
        self.settings.page_size = 'INVALID'
        size = get_page_size(self.settings)
        self.assertEqual(size, A4)  # Should fallback to A4

    def test_get_active_settings_with_active(self):
        """Test getting active settings when one exists."""
        settings_obj = ExportPDFSettings.objects.create(
            title='Test Settings',
            active=True
        )
        
        result = get_active_settings()
        self.assertEqual(result, settings_obj)

    def test_get_active_settings_without_active(self):
        """Test getting active settings when none exists."""
        result = get_active_settings()
        self.assertIsNone(result)

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

    def test_create_table_style_with_rtl(self):
        """Test table style creation with RTL support."""
        self.settings.rtl_support = True
        style = create_table_style(
            self.settings,
            'Helvetica',
            colors.lightgrey,
            colors.black
        )
        self.assertIsInstance(style, TableStyle)

    def test_create_table_style_with_alignment(self):
        """Test table style creation with custom alignment."""
        self.settings.content_alignment = 'LEFT'
        self.settings.header_alignment = 'RIGHT'
        style = create_table_style(
            self.settings,
            'Helvetica',
            colors.lightgrey,
            colors.black
        )
        self.assertIsInstance(style, TableStyle)

    def test_create_table_style_with_none_settings(self):
        """Test table style creation with None settings."""
        style = create_table_style(
            None,
            'Helvetica',
            colors.lightgrey,
            colors.black
        )
        self.assertIsInstance(style, TableStyle)

    def test_create_header_style_header(self):
        """Test header style creation for headers."""
        style = create_header_style(self.settings, 'Helvetica', True)
        self.assertIsInstance(style, ParagraphStyle)
        self.assertEqual(style.fontSize, self.settings.header_font_size)
        self.assertEqual(style.fontName, 'Helvetica')
        self.assertEqual(style.fontWeight, 'bold')

    def test_create_header_style_body(self):
        """Test header style creation for body text."""
        style = create_header_style(self.settings, 'Helvetica', False)
        self.assertIsInstance(style, ParagraphStyle)
        self.assertEqual(style.fontSize, self.settings.body_font_size)
        self.assertEqual(style.fontName, 'Helvetica')
        self.assertEqual(style.fontWeight, 'normal')

    def test_create_header_style_with_alignment(self):
        """Test header style creation with custom alignment."""
        self.settings.header_alignment = 'LEFT'
        self.settings.content_alignment = 'RIGHT'
        
        # Test header alignment
        style = create_header_style(self.settings, 'Helvetica', True)
        self.assertEqual(style.alignment, 0)  # LEFT
        
        # Test content alignment
        style = create_header_style(self.settings, 'Helvetica', False)
        self.assertEqual(style.alignment, 2)  # RIGHT

    def test_create_header_style_with_rtl(self):
        """Test header style creation with RTL support."""
        self.settings.rtl_support = True
        style = create_header_style(self.settings, 'Helvetica', False)
        self.assertEqual(style.alignment, 2)  # RIGHT for RTL

    def test_create_header_style_with_none_settings(self):
        """Test header style creation with None settings."""
        style = create_header_style(None, 'Helvetica', True)
        self.assertIsInstance(style, ParagraphStyle)
        self.assertEqual(style.fontSize, 12)  # Default header size

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

    def test_calculate_column_widths_empty_data(self):
        """Test column width calculation with empty data."""
        data = []
        table_width = 500
        widths = calculate_column_widths(
            data, table_width, 'Helvetica', 10
        )
        
        self.assertEqual(len(widths), 0)

    def test_calculate_column_widths_single_column(self):
        """Test column width calculation with single column."""
        data = [
            ['Header'],
            ['Data'],
        ]
        table_width = 500
        widths = calculate_column_widths(
            data, table_width, 'Helvetica', 10
        )
        
        self.assertEqual(len(widths), 1)
        self.assertAlmostEqual(widths[0], table_width, places=2)

    def test_calculate_column_widths_minimum_width(self):
        """Test column width calculation respects minimum width."""
        data = [
            ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'],  # 10 columns
        ]
        table_width = 100  # Very small width
        widths = calculate_column_widths(
            data, table_width, 'Helvetica', 10
        )
        
        # Each column should have at least 5% of table width
        min_width = table_width * 0.05
        for width in widths:
            self.assertGreaterEqual(width, min_width)

    @patch('django_pdf_actions.actions.utils.get_active_settings')
    def test_draw_model_name(self, mock_get_settings):
        """Test drawing model name."""
        mock_get_settings.return_value = self.settings
        
        # Create mock canvas
        mock_canvas = MagicMock()
        mock_canvas.stringWidth.return_value = 100
        
        # Create mock model admin
        mock_model = MagicMock()
        mock_model._meta.verbose_name_plural = 'Test Models'
        mock_modeladmin = MagicMock()
        mock_modeladmin.model = mock_model
        
        draw_model_name(
            mock_canvas, mock_modeladmin, 'Helvetica', 12, 600, 800, 50
        )
        
        mock_canvas.setFont.assert_called_with('Helvetica', 12)
        mock_canvas.stringWidth.assert_called_once()
        mock_canvas.drawCentredString.assert_called_once()

    @patch('django_pdf_actions.actions.utils.get_active_settings')
    def test_draw_model_name_with_rtl(self, mock_get_settings):
        """Test drawing model name with RTL support."""
        self.settings.rtl_support = True
        mock_get_settings.return_value = self.settings
        
        # Create mock canvas
        mock_canvas = MagicMock()
        mock_canvas.stringWidth.return_value = 100
        
        # Create mock model admin
        mock_model = MagicMock()
        mock_model._meta.verbose_name_plural = 'Test Models'
        mock_modeladmin = MagicMock()
        mock_modeladmin.model = mock_model
        
        with patch('django_pdf_actions.actions.utils.arabic_reshaper') as mock_arabic:
            with patch('django_pdf_actions.actions.utils.get_display') as mock_display:
                mock_arabic.reshape.return_value = 'reshaped_text'
                mock_display.return_value = 'display_text'
                
                draw_model_name(
                    mock_canvas, mock_modeladmin, 'Helvetica', 12, 600, 800, 50
                )
                
                mock_arabic.reshape.assert_called_once()
                mock_display.assert_called_once()

    @patch('django_pdf_actions.actions.utils.get_active_settings')
    def test_draw_exported_at(self, mock_get_settings):
        """Test drawing export timestamp."""
        mock_get_settings.return_value = self.settings
        
        # Create mock canvas
        mock_canvas = MagicMock()
        mock_canvas.stringWidth.return_value = 100
        
        draw_exported_at(mock_canvas, 'Helvetica', 10, 600, 50)
        
        mock_canvas.setFont.assert_called_with('Helvetica', 10)
        mock_canvas.stringWidth.assert_called_once()
        mock_canvas.drawString.assert_called_once()

    @patch('django_pdf_actions.actions.utils.get_active_settings')
    def test_draw_exported_at_with_rtl(self, mock_get_settings):
        """Test drawing export timestamp with RTL support."""
        self.settings.rtl_support = True
        mock_get_settings.return_value = self.settings
        
        # Create mock canvas
        mock_canvas = MagicMock()
        mock_canvas.stringWidth.return_value = 100
        
        with patch('django_pdf_actions.actions.utils.arabic_reshaper') as mock_arabic:
            with patch('django_pdf_actions.actions.utils.get_display') as mock_display:
                mock_arabic.reshape.return_value = 'reshaped_text'
                mock_display.return_value = 'display_text'
                
                draw_exported_at(mock_canvas, 'Helvetica', 10, 600, 50)
                
                mock_arabic.reshape.assert_called_once()
                mock_display.assert_called_once()

    @patch('django_pdf_actions.actions.utils.get_active_settings')
    def test_draw_page_number(self, mock_get_settings):
        """Test drawing page numbers."""
        mock_get_settings.return_value = self.settings
        
        # Create mock canvas
        mock_canvas = MagicMock()
        mock_canvas.stringWidth.return_value = 100
        
        draw_page_number(mock_canvas, 0, 3, 'Helvetica', 10, 600, 50)
        
        mock_canvas.setFont.assert_called_with('Helvetica', 10)
        mock_canvas.stringWidth.assert_called_once()
        mock_canvas.drawCentredString.assert_called_once()

    @patch('django_pdf_actions.actions.utils.get_active_settings')
    def test_draw_page_number_with_rtl(self, mock_get_settings):
        """Test drawing page numbers with RTL support."""
        self.settings.rtl_support = True
        mock_get_settings.return_value = self.settings
        
        # Create mock canvas
        mock_canvas = MagicMock()
        mock_canvas.stringWidth.return_value = 100
        
        with patch('django_pdf_actions.actions.utils.arabic_reshaper') as mock_arabic:
            with patch('django_pdf_actions.actions.utils.get_display') as mock_display:
                mock_arabic.reshape.return_value = 'reshaped_text'
                mock_display.return_value = 'display_text'
                
                draw_page_number(mock_canvas, 0, 3, 'Helvetica', 10, 600, 50)
                
                mock_arabic.reshape.assert_called_once()
                mock_display.assert_called_once()

    @patch('os.path.exists')
    def test_draw_logo_exists(self, mock_exists):
        """Test drawing logo when file exists."""
        mock_exists.return_value = True
        
        # Create mock canvas
        mock_canvas = MagicMock()
        
        with patch('django_pdf_actions.actions.utils.Image') as mock_image:
            mock_image_instance = MagicMock()
            mock_image.return_value = mock_image_instance
            
            draw_logo(mock_canvas, '/path/to/logo.png', 600, 800)
            
            mock_image.assert_called_once_with('/path/to/logo.png', width=100, height=50)
            mock_image_instance.drawOn.assert_called_once()

    @patch('os.path.exists')
    def test_draw_logo_not_exists(self, mock_exists):
        """Test drawing logo when file doesn't exist."""
        mock_exists.return_value = False
        
        # Create mock canvas
        mock_canvas = MagicMock()
        
        draw_logo(mock_canvas, '/path/to/logo.png', 600, 800)
        
        # Should not call any drawing methods
        mock_canvas.assert_not_called()


class PageSizeMapTest(TestCase):
    """Test cases for PAGE_SIZE_MAP constant."""

    def test_page_size_map_contains_all_sizes(self):
        """Test that PAGE_SIZE_MAP contains all expected page sizes."""
        expected_sizes = ['A4', 'A3', 'A2', 'A1']
        for size in expected_sizes:
            self.assertIn(size, PAGE_SIZE_MAP)

    def test_page_size_map_values(self):
        """Test that PAGE_SIZE_MAP values are correct."""
        self.assertEqual(PAGE_SIZE_MAP['A4'], A4)
        self.assertEqual(PAGE_SIZE_MAP['A3'], A3)
        self.assertEqual(PAGE_SIZE_MAP['A2'], A2)
        self.assertEqual(PAGE_SIZE_MAP['A1'], A1) 