"""Tests for PDF export models."""

from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django_pdf_actions.models import (
    ALIGNMENT_CHOICES,
    PAGE_SIZES,
    ColorField,
    ExportPDFSettings,
    get_available_fonts,
    validate_hex_color,
)


class ExportPDFSettingsValidationTest(TestCase):
    """Test cases for ExportPDFSettings model validation."""

    def test_font_size_validation(self):
        """Test font size validation."""
        settings = ExportPDFSettings(
            title="Invalid Font Size",
            header_font_size=5,  # Too small
            body_font_size=20,  # Too large
        )
        with self.assertRaises(ValidationError) as cm:
            settings.clean_fields()

        errors = cm.exception.message_dict
        self.assertIn("header_font_size", errors)
        self.assertIn("body_font_size", errors)

    def test_page_margin_validation(self):
        """Test page margin validation."""
        settings = ExportPDFSettings(
            title="Invalid Margin", page_margin_mm=3  # Too small
        )
        with self.assertRaises(ValidationError) as cm:
            settings.clean_fields()

        errors = cm.exception.message_dict
        self.assertIn("page_margin_mm", errors)

    def test_items_per_page_validation(self):
        """Test items per page validation."""
        settings = ExportPDFSettings(
            title="Invalid Items Per Page", items_per_page=0  # Too small
        )
        with self.assertRaises(ValidationError) as cm:
            settings.clean_fields()

        errors = cm.exception.message_dict
        self.assertIn("items_per_page", errors)

    def test_grid_line_width_validation(self):
        """Test grid line width validation."""
        settings = ExportPDFSettings(
            title="Invalid Grid Line Width", grid_line_width=0.05  # Too small
        )
        with self.assertRaises(ValidationError) as cm:
            settings.clean_fields()

        errors = cm.exception.message_dict
        self.assertIn("grid_line_width", errors)

    def test_table_spacing_validation(self):
        """Test table spacing validation."""
        settings = ExportPDFSettings(
            title="Invalid Table Spacing", table_spacing=0.1  # Too small
        )
        with self.assertRaises(ValidationError) as cm:
            settings.clean_fields()

        errors = cm.exception.message_dict
        self.assertIn("table_spacing", errors)

    def test_max_chars_per_line_validation(self):
        """Test max chars per line validation."""
        settings = ExportPDFSettings(
            title="Invalid Max Chars", max_chars_per_line=10  # Too small
        )
        with self.assertRaises(ValidationError) as cm:
            settings.clean_fields()

        errors = cm.exception.message_dict
        self.assertIn("max_chars_per_line", errors)

    def test_string_representation(self):
        """Test the string representation of settings."""
        settings = ExportPDFSettings(title="Test Settings", active=True)
        self.assertEqual(str(settings), "Test Settings (Active)")

        settings.active = False
        self.assertEqual(str(settings), "Test Settings (Inactive)")

    def test_default_values(self):
        """Test default values."""
        settings = ExportPDFSettings(title="Default Settings")

        self.assertEqual(settings.header_font_size, 10)
        self.assertEqual(settings.body_font_size, 7)
        self.assertEqual(settings.page_margin_mm, 15)
        self.assertEqual(settings.items_per_page, 10)
        self.assertEqual(settings.page_size, "A4")
        self.assertEqual(settings.font_name, "DejaVuSans.ttf")
        self.assertEqual(settings.header_background_color, "#F0F0F0")
        self.assertEqual(settings.grid_line_color, "#000000")
        self.assertEqual(settings.grid_line_width, 0.25)
        self.assertEqual(settings.table_spacing, 1.0)
        self.assertEqual(settings.max_chars_per_line, 45)
        self.assertEqual(settings.content_alignment, "CENTER")
        self.assertEqual(settings.header_alignment, "CENTER")
        self.assertEqual(settings.title_alignment, "CENTER")
        self.assertTrue(settings.show_header)
        self.assertTrue(settings.show_logo)
        self.assertTrue(settings.show_export_time)
        self.assertTrue(settings.show_page_numbers)
        self.assertFalse(settings.rtl_support)
        self.assertFalse(settings.active)

    def test_active_configuration_validation(self):
        """Test that only one configuration can be active."""
        # Create first active configuration
        settings1 = ExportPDFSettings.objects.create(
            title="First Settings", active=True
        )
        self.assertTrue(settings1.pk)

        # Try to create second active configuration
        settings2 = ExportPDFSettings(title="Second Settings", active=True)

        with self.assertRaises(ValidationError) as cm:
            settings2.clean()

        self.assertIn("only be one active configuration", str(cm.exception))

    def test_active_configuration_update(self):
        """Test updating an existing active configuration."""
        # Create first active configuration
        settings1 = ExportPDFSettings.objects.create(
            title="First Settings", active=True
        )

        # Update the same configuration - should not raise error
        settings1.title = "Updated Settings"
        settings1.clean()  # Should not raise ValidationError

    def test_page_size_choices(self):
        """Test page size choices."""
        settings = ExportPDFSettings(title="Test Settings", page_size="A3")
        self.assertEqual(settings.page_size, "A3")

    def test_alignment_choices(self):
        """Test alignment choices."""
        settings = ExportPDFSettings(
            title="Test Settings",
            content_alignment="LEFT",
            header_alignment="RIGHT",
            title_alignment="CENTER",
        )
        self.assertEqual(settings.content_alignment, "LEFT")
        self.assertEqual(settings.header_alignment, "RIGHT")
        self.assertEqual(settings.title_alignment, "CENTER")

    def test_model_meta(self):
        """Test model meta configuration."""
        self.assertEqual(ExportPDFSettings._meta.verbose_name, "Export PDF Settings")
        self.assertEqual(
            ExportPDFSettings._meta.verbose_name_plural, "Export PDF Settings"
        )
        self.assertEqual(ExportPDFSettings._meta.ordering, ["-active", "-modified"])

    def test_logo_field(self):
        """Test logo field functionality."""
        # Create a temporary image file
        image_content = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06"
            b"\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
            b"\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        image_file = SimpleUploadedFile(
            "test_logo.png", image_content, content_type="image/png"
        )

        settings = ExportPDFSettings.objects.create(
            title="Test Settings", logo=image_file
        )

        self.assertTrue(settings.logo)
        self.assertTrue(settings.logo.name.startswith("export_pdf/logos/"))

    def test_rtl_support_field(self):
        """Test RTL support field."""
        settings = ExportPDFSettings(title="RTL Settings", rtl_support=True)
        self.assertTrue(settings.rtl_support)


class ColorFieldTest(TestCase):
    """Test cases for ColorField custom field."""

    def test_color_field_validation(self):
        """Test color field validation."""
        field = ColorField()

        # Test valid hex colors
        field.clean("#FFFFFF", None)
        field.clean("#000000", None)
        field.clean("#FF0000", None)
        field.clean("#abc", None)  # Short format

        # Test invalid hex colors
        with self.assertRaises(ValidationError):
            field.clean("FFFFFF", None)  # Missing #

        with self.assertRaises(ValidationError):
            field.clean("#GGGGGG", None)  # Invalid characters

        with self.assertRaises(ValidationError):
            field.clean("#FF", None)  # Too short

    def test_color_field_formfield(self):
        """Test color field form field."""
        field = ColorField()
        form_field = field.formfield()
        self.assertEqual(form_field.widget.attrs["type"], "color")


class ValidateHexColorTest(TestCase):
    """Test cases for validate_hex_color function."""

    def test_valid_hex_colors(self):
        """Test valid hex color formats."""
        valid_colors = ["#FFFFFF", "#000000", "#FF0000", "#abc", "#123"]
        for color in valid_colors:
            try:
                validate_hex_color(color)
            except ValidationError:
                self.fail(
                    f"validate_hex_color raised ValidationError for valid color: {color}"
                )

    def test_invalid_hex_colors(self):
        """Test invalid hex color formats."""
        invalid_colors = ["FFFFFF", "#GGGGGG", "#FF", "#12345", "red", ""]
        for color in invalid_colors:
            with self.assertRaises(ValidationError):
                validate_hex_color(color)


class GetAvailableFontsTest(TestCase):
    """Test cases for get_available_fonts function."""

    @patch("django_pdf_actions.models.settings.BASE_DIR", "/fake/path")
    def test_get_available_fonts_no_directory(self):
        """Test get_available_fonts when fonts directory doesn't exist."""
        fonts = get_available_fonts()
        # Should return at least the default font
        self.assertTrue(len(fonts) >= 1)
        self.assertTrue(any("DejaVuSans.ttf" in font[0] for font in fonts))

    @patch("django_pdf_actions.models.settings.BASE_DIR", "/fake/path")
    @patch("os.path.exists")
    @patch("os.listdir")
    def test_get_available_fonts_with_fonts(self, mock_listdir, mock_exists):
        """Test get_available_fonts when fonts directory exists."""
        mock_exists.return_value = True
        mock_listdir.return_value = [
            "DejaVuSans.ttf",
            "Roboto.ttf",
            "Cairo.otf",
            "readme.txt",
        ]

        fonts = get_available_fonts()

        # Should include all TTF and OTF files
        font_names = [font[0] for font in fonts]
        self.assertIn("DejaVuSans.ttf", font_names)
        self.assertIn("Roboto.ttf", font_names)
        self.assertIn("Cairo.otf", font_names)
        self.assertNotIn("readme.txt", font_names)

    @patch("django_pdf_actions.models.settings.BASE_DIR", "/fake/path")
    @patch("os.path.exists")
    @patch("os.listdir")
    def test_get_available_fonts_sorted(self, mock_listdir, mock_exists):
        """Test that fonts are sorted alphabetically."""
        mock_exists.return_value = True
        mock_listdir.return_value = ["Zebra.ttf", "Apple.ttf", "Banana.ttf"]

        fonts = get_available_fonts()
        font_names = [font[1] for font in fonts]  # Get display names

        # Should be sorted alphabetically
        self.assertEqual(font_names, sorted(font_names))


class ConstantsTest(TestCase):
    """Test cases for module constants."""

    def test_page_sizes_constant(self):
        """Test PAGE_SIZES constant."""
        self.assertIsInstance(PAGE_SIZES, list)
        self.assertTrue(len(PAGE_SIZES) > 0)

        # Check that all page sizes have proper format
        for size_code, size_description in PAGE_SIZES:
            self.assertIsInstance(size_code, str)
            self.assertIsInstance(size_description, str)
            self.assertIn("mm", size_description)

    def test_alignment_choices_constant(self):
        """Test ALIGNMENT_CHOICES constant."""
        self.assertIsInstance(ALIGNMENT_CHOICES, list)
        self.assertEqual(len(ALIGNMENT_CHOICES), 3)

        # Check that all alignment choices have proper format
        for alignment_code, alignment_description in ALIGNMENT_CHOICES:
            self.assertIsInstance(alignment_code, str)
            self.assertIsInstance(alignment_description, str)
            self.assertIn(alignment_code, ["LEFT", "CENTER", "RIGHT"])


class ExportPDFSettingsSignalTest(TestCase):
    """Test cases for ExportPDFSettings signals."""

    def test_pre_save_signal_deactivates_others(self):
        """Test that pre_save signal deactivates other configurations."""
        # Create first active configuration
        settings1 = ExportPDFSettings.objects.create(
            title="First Settings", active=True
        )

        # Create second configuration
        settings2 = ExportPDFSettings.objects.create(
            title="Second Settings", active=False
        )

        # Make second configuration active
        settings2.active = True
        settings2.save()

        # Refresh from database
        settings1.refresh_from_db()
        settings2.refresh_from_db()

        # First should be deactivated, second should be active
        self.assertFalse(settings1.active)
        self.assertTrue(settings2.active)
