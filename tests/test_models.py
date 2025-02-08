"""Tests for PDF export models."""

from django.test import SimpleTestCase
from django.core.exceptions import ValidationError
from django_pdf_actions.models import ExportPDFSettings


class ExportPDFSettingsValidationTest(SimpleTestCase):
    """Test cases for ExportPDFSettings model validation."""

    def test_font_size_validation(self):
        """Test font size validation."""
        settings = ExportPDFSettings(
            title='Invalid Font Size',
            header_font_size=5,  # Too small
            body_font_size=20    # Too large
        )
        with self.assertRaises(ValidationError) as cm:
            settings.clean_fields()
            settings.clean()
        
        errors = cm.exception.message_dict
        self.assertIn('header_font_size', errors)
        self.assertIn('body_font_size', errors)

    def test_page_margin_validation(self):
        """Test page margin validation."""
        settings = ExportPDFSettings(
            title='Invalid Margin',
            page_margin_mm=3  # Too small
        )
        with self.assertRaises(ValidationError) as cm:
            settings.clean_fields()
            settings.clean()
        
        errors = cm.exception.message_dict
        self.assertIn('page_margin_mm', errors)

    def test_string_representation(self):
        """Test the string representation of settings."""
        settings = ExportPDFSettings(
            title='Test Settings',
            active=True
        )
        self.assertEqual(
            str(settings),
            'Test Settings (Active)'
        )

    def test_default_values(self):
        """Test default values."""
        settings = ExportPDFSettings(
            title='Default Settings'
        )

        self.assertEqual(settings.header_font_size, 10)
        self.assertEqual(settings.body_font_size, 7)
        self.assertEqual(settings.page_margin_mm, 15)
        self.assertEqual(settings.items_per_page, 10)
        self.assertTrue(settings.show_header)
        self.assertTrue(settings.show_logo)
        self.assertTrue(settings.show_export_time)
        self.assertTrue(settings.show_page_numbers) 