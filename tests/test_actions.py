"""Tests for PDF export actions."""

from unittest.mock import patch
from django.test import SimpleTestCase, RequestFactory
from django.http import HttpResponse
from django.contrib.auth.models import AnonymousUser
from reportlab.lib.pagesizes import A4, landscape
from django_pdf_actions.actions import export_to_pdf_landscape, export_to_pdf_portrait
from django_pdf_actions.models import ExportPDFSettings
from .utils import MockModel, MockQuerySet, MockModelAdmin


class PDFExportActionsTest(SimpleTestCase):
    """Test cases for PDF export actions."""

    def setUp(self):
        """Set up test environment."""
        self.factory = RequestFactory()
        self.user = AnonymousUser()
        
        # Create mock objects
        self.mock_obj1 = MockModel(id=1, name='Test User 1', email='test1@example.com')
        self.mock_obj2 = MockModel(id=2, name='Test User 2', email='test2@example.com')
        self.queryset = MockQuerySet([self.mock_obj1, self.mock_obj2])
        
        # Initialize ModelAdmin with proper site
        from django.contrib.admin.sites import AdminSite
        self.modeladmin = MockModelAdmin(MockModel, AdminSite())

        # Create test settings with all required attributes
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

    @patch('django_pdf_actions.actions.landscape.get_active_settings')
    def test_landscape_export(self, mock_get_settings):
        """Test landscape PDF export."""
        mock_get_settings.return_value = self.settings
        request = self.factory.get('/admin')
        request.user = self.user

        response = export_to_pdf_landscape(
            self.modeladmin, request, self.queryset
        )

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response['Content-Disposition'].startswith(
            'attachment; filename="MockModel_export_'
        ))

    @patch('django_pdf_actions.actions.portrait.get_active_settings')
    def test_portrait_export(self, mock_get_settings):
        """Test portrait PDF export."""
        mock_get_settings.return_value = self.settings
        request = self.factory.get('/admin')
        request.user = self.user

        response = export_to_pdf_portrait(
            self.modeladmin, request, self.queryset
        )

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response['Content-Disposition'].startswith(
            'attachment; filename="MockModel_export_'
        ))

    @patch('django_pdf_actions.actions.landscape.get_active_settings')
    def test_export_with_no_settings(self, mock_get_settings):
        """Test PDF export with no active settings."""
        mock_get_settings.return_value = None
        request = self.factory.get('/admin')
        request.user = self.user

        response = export_to_pdf_landscape(
            self.modeladmin, request, self.queryset
        )

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response['Content-Type'], 'application/pdf') 