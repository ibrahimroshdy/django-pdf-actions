"""Tests for Django admin integration (Export PDF settings admin)."""

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase

from django_pdf_actions.actions import export_to_pdf_landscape, export_to_pdf_portrait
from django_pdf_actions.admin import ExportPDFSettingsAdmin, PdfAdmin
from django_pdf_actions.models import ExportPDFSettings


class PdfAdminTest(TestCase):
    """Tests for PdfAdmin / ExportPDFSettingsAdmin."""

    def setUp(self):
        self.site = AdminSite()
        self.admin = PdfAdmin(ExportPDFSettings, self.site)
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123",
        )

    def test_export_pdf_settings_admin_alias(self):
        self.assertIs(ExportPDFSettingsAdmin, PdfAdmin)

    def test_admin_list_display_includes_core_fields(self):
        for field in ("title", "active", "items_per_page", "page_size", "modified"):
            self.assertIn(field, self.admin.list_display)

    def test_admin_list_filter_includes_core_filters(self):
        for f in ("active", "page_size", "rtl_support"):
            self.assertIn(f, self.admin.list_filter)

    def test_admin_search_fields(self):
        self.assertEqual(self.admin.search_fields, ("title",))

    def test_admin_readonly_fields(self):
        for field in ("modified", "created"):
            self.assertIn(field, self.admin.readonly_fields)

    def test_admin_fieldsets_sections(self):
        titles = [fs[0] for fs in self.admin.fieldsets if fs[0]]
        for section in (
            "General",
            "Page Layout",
            "Font Settings",
            "Visual Settings",
            "Display Options",
            "Alignment Settings",
            "Table Settings",
            "Metadata",
        ):
            self.assertIn(section, titles)

    def test_admin_pdf_export_actions_registered(self):
        names = [a.__name__ for a in self.admin.actions]
        self.assertIn("export_to_pdf_landscape", names)
        self.assertIn("export_to_pdf_portrait", names)

    def test_pdf_export_actions_have_human_readable_descriptions(self):
        self.assertTrue(
            getattr(export_to_pdf_landscape, "short_description", None)
            or getattr(export_to_pdf_landscape, "description", None)
        )
        self.assertTrue(
            getattr(export_to_pdf_portrait, "short_description", None)
            or getattr(export_to_pdf_portrait, "description", None)
        )

    def test_admin_save_model(self):
        request = self.factory.post("/admin/")
        request.user = self.user
        obj = ExportPDFSettings(title="Test Settings", active=True)
        self.admin.save_model(request, obj, form=None, change=False)
        self.assertTrue(obj.pk)
        self.assertEqual(obj.title, "Test Settings")

    def test_admin_get_queryset(self):
        s1 = ExportPDFSettings.objects.create(title="A", active=True)
        s2 = ExportPDFSettings.objects.create(title="B", active=False)
        request = self.factory.get("/admin/")
        request.user = self.user
        qs = self.admin.get_queryset(request)
        self.assertEqual(qs.count(), 2)
        self.assertIn(s1, qs)
        self.assertIn(s2, qs)

    def test_admin_logo_display_with_logo(self):
        image_content = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06"
            b"\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
            b"\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        image_file = SimpleUploadedFile(
            "test_logo.png", image_content, content_type="image/png"
        )
        settings = ExportPDFSettings.objects.create(title="Test", logo=image_file)
        html = self.admin.logo_display(settings)
        self.assertIsNotNone(html)

    def test_admin_logo_display_no_logo(self):
        settings = ExportPDFSettings.objects.create(title="Test")
        self.assertEqual(self.admin.logo_display(settings), "No logo")

    def test_superuser_permissions(self):
        request = self.factory.get("/admin/")
        request.user = self.user
        self.assertTrue(self.admin.has_add_permission(request))
        self.assertTrue(self.admin.has_change_permission(request))
        self.assertTrue(self.admin.has_delete_permission(request))
        self.assertTrue(self.admin.has_view_permission(request))

    def test_regular_user_no_admin_permissions(self):
        user = User.objects.create_user(
            username="regular",
            email="r@example.com",
            password="x",
        )
        request = self.factory.get("/admin/")
        request.user = user
        self.assertFalse(self.admin.has_add_permission(request))
        self.assertFalse(self.admin.has_change_permission(request))
        self.assertFalse(self.admin.has_delete_permission(request))
        self.assertFalse(self.admin.has_view_permission(request))
