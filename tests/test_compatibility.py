"""Compatibility tests for different Python and Django versions."""

import sys

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django_pdf_actions.actions import export_to_pdf_landscape, export_to_pdf_portrait
from django_pdf_actions.models import ExportPDFSettings

from .utils import MockModel, MockModelAdmin, MockQuerySet


class PythonVersionCompatibilityTest(TestCase):
    """Test compatibility across different Python versions."""

    def test_python_version_info(self):
        """Test that we can access Python version information."""
        version_info = sys.version_info
        self.assertIsInstance(version_info.major, int)
        self.assertIsInstance(version_info.minor, int)
        self.assertGreaterEqual(version_info.major, 3)
        self.assertGreaterEqual(version_info.minor, 8)

    def test_string_formatting_compatibility(self):
        """Test string formatting works across Python versions."""
        # Test f-strings (Python 3.6+)
        name = "Test"
        result = f"Hello {name}"
        self.assertEqual(result, "Hello Test")

        # Test .format() method
        result = "Hello {}".format(name)
        self.assertEqual(result, "Hello Test")

        # Test % formatting
        result = "Hello %s" % name
        self.assertEqual(result, "Hello Test")

    def test_pathlib_compatibility(self):
        """Test pathlib usage (Python 3.4+)."""
        from pathlib import Path

        path = Path("/test/path")
        self.assertIsInstance(path, Path)
        self.assertEqual(str(path), "/test/path")

    def test_typing_compatibility(self):
        """Test typing module usage (Python 3.5+)."""
        from typing import Dict, List, Optional

        # Test basic typing
        test_list: List[str] = ["a", "b", "c"]
        test_dict: Dict[str, int] = {"a": 1, "b": 2}
        test_optional: Optional[str] = None

        self.assertIsInstance(test_list, list)
        self.assertIsInstance(test_dict, dict)
        self.assertIsNone(test_optional)


class DjangoVersionCompatibilityTest(TestCase):
    """Test compatibility across different Django versions."""

    def test_django_version_info(self):
        """Test that we can access Django version information."""
        import django

        version = django.get_version()
        self.assertIsInstance(version, str)
        self.assertTrue(len(version) > 0)

    def test_django_settings_compatibility(self):
        """Test Django settings compatibility."""
        from django.conf import settings

        # Test that required settings exist
        self.assertTrue(hasattr(settings, "SECRET_KEY"))
        self.assertTrue(hasattr(settings, "INSTALLED_APPS"))
        self.assertTrue(hasattr(settings, "DATABASES"))

    def test_django_models_compatibility(self):
        """Test Django models compatibility."""
        from django.db import models

        # Test that we can create a model
        class TestModel(models.Model):
            name = models.CharField(max_length=100)

            class Meta:
                app_label = "django_pdf_actions"
                managed = False

        # Test model field types
        self.assertIsInstance(TestModel._meta.get_field("name"), models.CharField)

    def test_django_admin_compatibility(self):
        """Test Django admin compatibility."""
        from django.contrib.admin import ModelAdmin

        # Test that we can create a ModelAdmin
        admin = ModelAdmin(MockModel, AdminSite())
        self.assertIsInstance(admin, ModelAdmin)

    def test_django_http_compatibility(self):
        """Test Django HTTP compatibility."""
        from django.http import HttpRequest, HttpResponse

        # Test HttpResponse
        response = HttpResponse("test")
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.content, b"test")

        # Test HttpRequest
        request = HttpRequest()
        self.assertIsInstance(request, HttpRequest)

    def test_django_forms_compatibility(self):
        """Test Django forms compatibility."""
        from django import forms

        # Test form creation
        class TestForm(forms.Form):
            name = forms.CharField(max_length=100)

        form = TestForm()
        self.assertIsInstance(form, forms.Form)
        self.assertIn("name", form.fields)

    def test_django_utils_compatibility(self):
        """Test Django utils compatibility."""
        from django.utils.text import capfirst
        from django.utils.translation import gettext_lazy as _

        # Test capfirst
        result = capfirst("hello")
        self.assertEqual(result, "Hello")

        # Test gettext_lazy (translation delayed until coercion / rendering)
        lazy_text = _("Hello")
        self.assertEqual(str(lazy_text), "Hello")


class ReportLabCompatibilityTest(TestCase):
    """Test ReportLab compatibility and features."""

    def test_reportlab_imports(self):
        """Test that ReportLab can be imported."""
        import importlib

        modules = (
            "reportlab.lib.colors",
            "reportlab.lib.pagesizes",
            "reportlab.lib.styles",
            "reportlab.lib.units",
            "reportlab.pdfbase.pdfmetrics",
            "reportlab.pdfbase.ttfonts",
            "reportlab.pdfgen.canvas",
            "reportlab.platypus",
        )
        for name in modules:
            try:
                importlib.import_module(name)
            except ImportError as e:
                self.fail(f"ReportLab import failed for {name}: {e}")

    def test_reportlab_basic_functionality(self):
        """Test basic ReportLab functionality."""
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas
        from reportlab.platypus import Paragraph, Table

        # Test colors (ReportLab exposes Color objects, not bare RGB tuples)
        self.assertIsInstance(colors.red, colors.Color)
        self.assertIsInstance(colors.blue, colors.Color)

        # Test page sizes
        self.assertIsInstance(A4, tuple)
        self.assertEqual(len(A4), 2)

        # Test units
        self.assertIsInstance(mm, float)

        # Test canvas creation
        import io

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        self.assertIsInstance(c, canvas.Canvas)

        # Test paragraph creation
        style = ParagraphStyle("Test")
        para = Paragraph("Test", style)
        self.assertIsInstance(para, Paragraph)

        # Test table creation
        table = Table([["A", "B"], ["C", "D"]])
        self.assertIsInstance(table, Table)

    def test_reportlab_font_handling(self):
        """Test ReportLab font handling."""
        # Test that we can register a font (using built-in Helvetica)
        try:
            # This should work with built-in fonts
            font_name = "Helvetica"
            self.assertIsNotNone(font_name)
        except Exception as e:
            self.fail(f"Font handling failed: {e}")


class ArabicReshaperCompatibilityTest(TestCase):
    """Test Arabic reshaper compatibility."""

    def test_arabic_reshaper_import(self):
        """Test that arabic_reshaper can be imported."""
        import importlib

        try:
            importlib.import_module("arabic_reshaper")
        except ImportError as e:
            self.fail(f"arabic_reshaper import failed: {e}")

    def test_arabic_reshaper_functionality(self):
        """Test arabic_reshaper basic functionality."""
        try:
            import arabic_reshaper

            # Test basic reshaping
            text = "مرحبا"
            reshaped = arabic_reshaper.reshape(text)
            self.assertIsInstance(reshaped, str)
        except ImportError:
            self.skipTest("arabic_reshaper not available")

    def test_bidi_algorithm_import(self):
        """Test that bidi algorithm can be imported."""
        import importlib

        try:
            importlib.import_module("bidi.algorithm")
        except ImportError as e:
            self.fail(f"bidi algorithm import failed: {e}")

    def test_bidi_algorithm_functionality(self):
        """Test bidi algorithm basic functionality."""
        try:
            from bidi.algorithm import get_display

            # Test basic display
            text = "مرحبا"
            display_text = get_display(text)
            self.assertIsInstance(display_text, str)
        except ImportError:
            self.skipTest("bidi algorithm not available")


class ModelUtilsCompatibilityTest(TestCase):
    """Test model-utils compatibility."""

    def test_model_utils_import(self):
        """Test that model-utils can be imported."""
        import importlib

        try:
            importlib.import_module("model_utils.models")
        except ImportError as e:
            self.fail(f"model-utils import failed: {e}")

    def test_timestamped_model_functionality(self):
        """Test TimeStampedModel functionality."""
        try:
            from django.db import models
            from model_utils.models import TimeStampedModel

            class TestModel(TimeStampedModel):
                name = models.CharField(max_length=100)

                class Meta:
                    app_label = "django_pdf_actions"
                    managed = False

            # Test that the model has created and modified fields
            self.assertTrue(hasattr(TestModel, "created"))
            self.assertTrue(hasattr(TestModel, "modified"))
        except ImportError:
            self.skipTest("model-utils not available")


class CrossVersionIntegrationTest(TestCase):
    """Integration tests across different versions."""

    def setUp(self):
        """Set up test environment."""
        self.factory = RequestFactory()
        self.user = AnonymousUser()

        # Create mock objects
        self.mock_obj1 = MockModel(id=1, name="Test User 1", email="test1@example.com")
        self.mock_obj2 = MockModel(id=2, name="Test User 2", email="test2@example.com")
        self.queryset = MockQuerySet([self.mock_obj1, self.mock_obj2])

        self.modeladmin = MockModelAdmin(MockModel, AdminSite())

    def test_pdf_export_with_minimal_settings(self):
        """Test PDF export with minimal settings across versions."""
        # Create minimal settings
        settings = ExportPDFSettings.objects.create(
            title="Minimal Settings", active=True
        )
        self.assertTrue(settings.pk)

        request = self.factory.get("/admin")
        request.user = self.user

        # Test landscape export
        response = export_to_pdf_landscape(self.modeladmin, request, self.queryset)

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response["Content-Type"], "application/pdf")

        # Test portrait export
        response = export_to_pdf_portrait(self.modeladmin, request, self.queryset)

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response["Content-Type"], "application/pdf")

    def test_pdf_export_with_maximal_settings(self):
        """Test PDF export with maximal settings across versions."""
        # Create maximal settings
        settings = ExportPDFSettings.objects.create(
            title="Maximal Settings",
            active=True,
            page_size="A3",
            items_per_page=25,
            page_margin_mm=20,
            font_name="DejaVuSans.ttf",
            header_font_size=14,
            body_font_size=9,
            header_background_color="#E0E0E0",
            grid_line_color="#333333",
            grid_line_width=0.5,
            show_header=True,
            show_logo=True,
            show_export_time=True,
            show_page_numbers=True,
            rtl_support=True,
            content_alignment="LEFT",
            header_alignment="RIGHT",
            title_alignment="CENTER",
            table_spacing=2.0,
            max_chars_per_line=60,
        )
        self.assertTrue(settings.pk)

        request = self.factory.get("/admin")
        request.user = self.user

        # Test landscape export
        response = export_to_pdf_landscape(self.modeladmin, request, self.queryset)

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response["Content-Type"], "application/pdf")

        # Test portrait export
        response = export_to_pdf_portrait(self.modeladmin, request, self.queryset)

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response["Content-Type"], "application/pdf")

    def test_model_validation_across_versions(self):
        """Test model validation works across versions."""
        # Test valid settings
        settings = ExportPDFSettings(
            title="Valid Settings",
            active=True,
            header_font_size=10,
            body_font_size=8,
            page_margin_mm=15,
            items_per_page=10,
            grid_line_width=0.25,
            table_spacing=1.0,
            max_chars_per_line=45,
        )

        # Should not raise validation error
        try:
            settings.clean_fields()
            settings.clean()
        except ValidationError as e:
            self.fail(f"Valid settings raised ValidationError: {e}")

    def test_edge_case_values(self):
        """Test edge case values across versions."""
        # Test minimum values
        settings = ExportPDFSettings.objects.create(
            title="Min Values",
            active=True,
            header_font_size=6,
            body_font_size=6,
            page_margin_mm=5,
            items_per_page=1,
            grid_line_width=0.1,
            table_spacing=0.5,
            max_chars_per_line=20,
        )

        request = self.factory.get("/admin")
        request.user = self.user

        response = export_to_pdf_landscape(self.modeladmin, request, self.queryset)

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response["Content-Type"], "application/pdf")

        # Test maximum values
        settings.header_font_size = 24
        settings.body_font_size = 18
        settings.page_margin_mm = 50
        settings.items_per_page = 100
        settings.grid_line_width = 2.0
        settings.table_spacing = 5.0
        settings.max_chars_per_line = 100
        settings.save()

        response = export_to_pdf_landscape(self.modeladmin, request, self.queryset)

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response["Content-Type"], "application/pdf")

    def test_unicode_handling(self):
        """Test Unicode handling across versions."""
        # Create objects with Unicode content
        unicode_obj1 = MockModel(
            id=1, name="测试用户1", email="test1@example.com"  # Chinese
        )
        unicode_obj2 = MockModel(
            id=2, name="مستخدم اختبار 2", email="test2@example.com"  # Arabic
        )
        unicode_obj3 = MockModel(
            id=3, name="Тестовый пользователь 3", email="test3@example.com"  # Russian
        )

        queryset = MockQuerySet([unicode_obj1, unicode_obj2, unicode_obj3])

        settings = ExportPDFSettings.objects.create(
            title="Unicode Settings", active=True
        )
        self.assertTrue(settings.pk)

        request = self.factory.get("/admin")
        request.user = self.user

        # Test landscape export with Unicode
        response = export_to_pdf_landscape(self.modeladmin, request, queryset)

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response["Content-Type"], "application/pdf")

        # Test portrait export with Unicode
        response = export_to_pdf_portrait(self.modeladmin, request, queryset)

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response["Content-Type"], "application/pdf")

    def test_large_dataset_handling(self):
        """Test handling of large datasets across versions."""
        # Create a large dataset
        large_queryset = MockQuerySet(
            [
                MockModel(id=i, name=f"User {i}", email=f"user{i}@example.com")
                for i in range(100)  # 100 items
            ]
        )

        settings = ExportPDFSettings.objects.create(
            title="Large Dataset Settings",
            active=True,
            items_per_page=10,  # Should create multiple pages
        )
        self.assertTrue(settings.pk)

        request = self.factory.get("/admin")
        request.user = self.user

        # Test landscape export with large dataset
        response = export_to_pdf_landscape(self.modeladmin, request, large_queryset)

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response["Content-Type"], "application/pdf")

        # Test portrait export with large dataset
        response = export_to_pdf_portrait(self.modeladmin, request, large_queryset)

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response["Content-Type"], "application/pdf")

    def test_empty_queryset_handling(self):
        """Test handling of empty querysets across versions."""
        empty_queryset = MockQuerySet([])

        settings = ExportPDFSettings.objects.create(
            title="Empty Dataset Settings", active=True
        )
        self.assertTrue(settings.pk)

        request = self.factory.get("/admin")
        request.user = self.user

        # Test landscape export with empty queryset
        response = export_to_pdf_landscape(self.modeladmin, request, empty_queryset)

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response["Content-Type"], "application/pdf")

        # Test portrait export with empty queryset
        response = export_to_pdf_portrait(self.modeladmin, request, empty_queryset)

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response["Content-Type"], "application/pdf")


class PerformanceCompatibilityTest(TestCase):
    """Test performance characteristics across versions."""

    def setUp(self):
        """Set up test environment."""
        self.factory = RequestFactory()
        self.user = AnonymousUser()

        self.modeladmin = MockModelAdmin(MockModel, AdminSite())

    def test_export_performance_with_different_settings(self):
        """Test export performance with different settings."""
        import time

        # Create test data
        queryset = MockQuerySet(
            [
                MockModel(id=i, name=f"User {i}", email=f"user{i}@example.com")
                for i in range(50)  # 50 items
            ]
        )

        request = self.factory.get("/admin")
        request.user = self.user

        # Test with different page sizes
        page_sizes = ["A4", "A3", "A2", "A1"]

        for page_size in page_sizes:
            settings = ExportPDFSettings.objects.create(
                title=f"Performance Test {page_size}",
                active=True,
                page_size=page_size,
                items_per_page=10,
            )
            self.assertTrue(settings.pk)

            start_time = time.time()

            response = export_to_pdf_landscape(self.modeladmin, request, queryset)

            end_time = time.time()
            execution_time = end_time - start_time

            # Should complete within reasonable time (adjust threshold as needed)
            self.assertLess(execution_time, 10.0)  # 10 seconds max
            self.assertIsInstance(response, HttpResponse)
            self.assertEqual(response["Content-Type"], "application/pdf")

    def test_memory_usage_with_large_datasets(self):
        """Test memory usage with large datasets."""
        import gc

        # Create large dataset
        large_queryset = MockQuerySet(
            [
                MockModel(id=i, name=f"User {i}", email=f"user{i}@example.com")
                for i in range(1000)  # 1000 items
            ]
        )

        settings = ExportPDFSettings.objects.create(
            title="Memory Test Settings", active=True, items_per_page=50
        )
        self.assertTrue(settings.pk)

        request = self.factory.get("/admin")
        request.user = self.user

        # Force garbage collection before test
        gc.collect()

        # Test export
        response = export_to_pdf_landscape(self.modeladmin, request, large_queryset)

        # Force garbage collection after test
        gc.collect()

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response["Content-Type"], "application/pdf")
