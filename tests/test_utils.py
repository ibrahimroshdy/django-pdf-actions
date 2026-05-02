"""Tests for PDF export utility functions."""

import hashlib
import os
import tempfile
from unittest.mock import patch, MagicMock, mock_open
from django.test import TestCase, override_settings
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A3, A2, A1
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import TableStyle
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
        # Short #RGB form expands to #RRGGBB
        self.assertEqual(hex_to_rgb('#abc'), hex_to_rgb('#aabbcc'))
        self.assertEqual(hex_to_rgb('#f00'), (1.0, 0.0, 0.0))

    @patch('django_pdf_actions.actions.utils.TTFont')
    @patch('django_pdf_actions.actions.utils.pdfmetrics.getRegisteredFontNames', return_value=[])
    @patch('django_pdf_actions.actions.utils.resolve_font_path')
    def test_setup_font_with_custom_font(self, mock_resolve, _mock_registered, _mock_tt):
        """Test font setup with custom font."""
        mock_resolve.return_value = '/fake/fonts/DejaVuSans.ttf'

        with patch('django_pdf_actions.actions.utils.pdfmetrics.registerFont') as mock_register:
            font_name = setup_font(self.settings)
            self.assertTrue(font_name.startswith('PdfAct_'))
            mock_register.assert_called_once()

    @patch('django_pdf_actions.actions.utils.TTFont')
    @patch('django_pdf_actions.actions.utils.pdfmetrics.getRegisteredFontNames', return_value=[])
    @patch('django_pdf_actions.actions.utils.resolve_font_path')
    def test_setup_font_with_default_font(self, mock_resolve, _mock_registered, _mock_tt):
        """Test font setup when configured font is missing but bundle default resolves."""
        mock_resolve.side_effect = [None, '/fake/fonts/DejaVuSans.ttf']

        with patch('django_pdf_actions.actions.utils.pdfmetrics.registerFont') as mock_register:
            font_name = setup_font(self.settings)
            self.assertTrue(font_name.startswith('PdfAct_'))
            mock_register.assert_called_once()

    @patch('django_pdf_actions.actions.utils.resolve_font_path', return_value=None)
    def test_setup_font_fallback_to_helvetica(self, mock_resolve):
        """Test font setup fallback to Helvetica."""
        font_name = setup_font(self.settings)
        self.assertEqual(font_name, 'Helvetica')

    @patch('django_pdf_actions.actions.utils.resolve_font_path', return_value=None)
    def test_setup_font_with_none_settings(self, mock_resolve):
        """Test font setup with None settings."""
        font_name = setup_font(None)
        self.assertEqual(font_name, 'Helvetica')

    @patch('django_pdf_actions.actions.utils.pdfmetrics.getRegisteredFontNames')
    @patch('django_pdf_actions.actions.utils.resolve_font_path')
    def test_setup_font_skips_register_when_already_registered(
        self, mock_resolve, mock_registered_names
    ):
        """Same resolved path does not call registerFont again if already registered."""
        font_path = '/fake/fonts/DejaVuSans.ttf'
        mock_resolve.return_value = font_path
        internal = (
            'PdfAct_'
            + hashlib.sha256(os.path.abspath(font_path).encode()).hexdigest()[:12]
        )
        mock_registered_names.return_value = [internal]
        with patch('django_pdf_actions.actions.utils.pdfmetrics.registerFont') as mock_register:
            self.assertEqual(setup_font(self.settings), internal)
            mock_register.assert_not_called()

    @patch('django_pdf_actions.actions.utils.os.path.isfile')
    def test_get_logo_path_with_logo(self, mock_isfile):
        """Test logo path retrieval with a locally stored logo file."""
        mock_isfile.return_value = True
        mock_logo = MagicMock()
        mock_logo.path = '/path/to/logo.png'
        mock_logo.name = 'export_pdf/logos/x.png'
        self.settings.logo = mock_logo
        self.settings.show_logo = True

        path = get_logo_path(self.settings)
        self.assertEqual(path, '/path/to/logo.png')

    def test_get_logo_path_without_logo(self):
        """Test logo path when no image is configured."""
        self.settings.logo = None
        self.assertIsNone(get_logo_path(self.settings))

    def test_get_logo_path_show_logo_disabled(self):
        """When show_logo is off, do not resolve a path even if a file exists."""
        mock_logo = MagicMock()
        mock_logo.path = '/path/to/logo.png'
        mock_logo.name = 'x.png'
        self.settings.logo = mock_logo
        self.settings.show_logo = False
        self.assertIsNone(get_logo_path(self.settings))

    def test_get_logo_path_with_none_settings(self):
        """Test logo path retrieval with None settings."""
        self.assertIsNone(get_logo_path(None))

    @patch('django_pdf_actions.actions.utils.os.path.isfile')
    def test_get_logo_path_remote_storage_uses_image_reader(self, mock_isfile):
        """Remote backends without local path fall back to ImageReader."""
        mock_isfile.return_value = False

        mock_storage = MagicMock()
        mock_storage.path.side_effect = NotImplementedError()
        inner = MagicMock()
        inner.read.return_value = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\xfa'
            b'\x0f\x00\x00\x01\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        mgr = MagicMock()
        mgr.__enter__.return_value = inner
        mgr.__exit__.return_value = None
        mock_storage.open.return_value = mgr

        mock_logo = MagicMock()
        mock_logo.path = '/nope'
        mock_logo.name = 'logos/remote.png'
        mock_logo.storage = mock_storage
        self.settings.logo = mock_logo
        self.settings.show_logo = True

        from reportlab.lib.utils import ImageReader

        result = get_logo_path(self.settings)
        self.assertIsInstance(result, ImageReader)

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
        """Test header style creation with RTL support (no explicit L/R alignment)."""
        rtl_only = type('RTLSettings', (), {
            'header_font_size': 12,
            'body_font_size': 10,
            'rtl_support': True,
        })()
        style = create_header_style(rtl_only, 'Helvetica', False)
        self.assertEqual(style.alignment, 2)  # RIGHT for RTL body when not overridden

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

    @patch('os.path.isfile')
    def test_draw_logo_exists(self, mock_isfile):
        """Test drawing logo when file exists."""
        mock_isfile.return_value = True

        mock_canvas = MagicMock()

        with patch('reportlab.platypus.Image') as mock_image:
            mock_image_instance = MagicMock()
            mock_image.return_value = mock_image_instance

            draw_logo(mock_canvas, '/path/to/logo.png', 600, 800)

            mock_image.assert_called_once_with('/path/to/logo.png', width=100, height=50)
            mock_image_instance.drawOn.assert_called_once()

    @patch('os.path.isfile')
    def test_draw_logo_not_exists(self, mock_isfile):
        """Test drawing logo when file doesn't exist."""
        mock_isfile.return_value = False

        mock_canvas = MagicMock()

        draw_logo(mock_canvas, '/path/to/logo.png', 600, 800)

        mock_canvas.assert_not_called()

    def test_draw_logo_none_source(self):
        """No logo source should not touch the canvas."""
        mock_canvas = MagicMock()
        draw_logo(mock_canvas, None, 600, 800)
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