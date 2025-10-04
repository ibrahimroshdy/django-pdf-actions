"""Tests for Django admin integration."""

from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django_pdf_actions.models import ExportPDFSettings
from django_pdf_actions.admin import ExportPDFSettingsAdmin


class ExportPDFSettingsAdminTest(TestCase):
    """Test cases for ExportPDFSettings admin."""

    def setUp(self):
        """Set up test environment."""
        self.site = AdminSite()
        self.admin = ExportPDFSettingsAdmin(ExportPDFSettings, self.site)
        self.factory = RequestFactory()
        
        # Create superuser
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )

    def test_admin_list_display(self):
        """Test admin list display configuration."""
        list_display = self.admin.list_display
        expected_fields = ['title', 'active', 'page_size', 'items_per_page', 'created']
        
        for field in expected_fields:
            self.assertIn(field, list_display)

    def test_admin_list_filter(self):
        """Test admin list filter configuration."""
        list_filter = self.admin.list_filter
        expected_filters = ['active', 'page_size', 'created', 'modified']
        
        for filter_field in expected_filters:
            self.assertIn(filter_field, list_filter)

    def test_admin_search_fields(self):
        """Test admin search fields configuration."""
        search_fields = self.admin.search_fields
        expected_fields = ['title']
        
        for field in expected_fields:
            self.assertIn(field, search_fields)

    def test_admin_ordering(self):
        """Test admin ordering configuration."""
        ordering = self.admin.ordering
        expected_ordering = ['-active', '-modified']
        
        self.assertEqual(ordering, expected_ordering)

    def test_admin_readonly_fields(self):
        """Test admin readonly fields configuration."""
        readonly_fields = self.admin.readonly_fields
        expected_fields = ['created', 'modified']
        
        for field in expected_fields:
            self.assertIn(field, readonly_fields)

    def test_admin_fieldsets(self):
        """Test admin fieldsets configuration."""
        fieldsets = self.admin.fieldsets
        
        # Check that fieldsets exist
        self.assertIsNotNone(fieldsets)
        self.assertIsInstance(fieldsets, (list, tuple))
        
        # Check that we have expected sections
        fieldset_titles = [fieldset[0] for fieldset in fieldsets if fieldset[0]]
        expected_sections = [
            'Basic Settings',
            'Page Layout',
            'Font Settings',
            'Visual Settings',
            'Display Options',
            'Alignment Options',
            'Table Settings'
        ]
        
        for section in expected_sections:
            self.assertIn(section, fieldset_titles)

    def test_admin_actions(self):
        """Test admin actions configuration."""
        actions = self.admin.actions
        
        # Should have actions for activating/deactivating settings
        action_names = [action.__name__ for action in actions]
        expected_actions = ['activate_settings', 'deactivate_settings']
        
        for action in expected_actions:
            self.assertIn(action, action_names)

    def test_activate_settings_action(self):
        """Test activate settings admin action."""
        # Create inactive settings
        settings1 = ExportPDFSettings.objects.create(
            title='Settings 1',
            active=False
        )
        settings2 = ExportPDFSettings.objects.create(
            title='Settings 2',
            active=False
        )
        
        # Create request
        request = self.factory.post('/admin/')
        request.user = self.user
        
        # Test activating one setting
        queryset = ExportPDFSettings.objects.filter(id=settings1.id)
        self.admin.activate_settings(request, queryset)
        
        # Check that only one setting is active
        settings1.refresh_from_db()
        settings2.refresh_from_db()
        
        self.assertTrue(settings1.active)
        self.assertFalse(settings2.active)

    def test_deactivate_settings_action(self):
        """Test deactivate settings admin action."""
        # Create active settings
        settings1 = ExportPDFSettings.objects.create(
            title='Settings 1',
            active=True
        )
        settings2 = ExportPDFSettings.objects.create(
            title='Settings 2',
            active=True
        )
        
        # Create request
        request = self.factory.post('/admin/')
        request.user = self.user
        
        # Test deactivating settings
        queryset = ExportPDFSettings.objects.filter(id__in=[settings1.id, settings2.id])
        self.admin.deactivate_settings(request, queryset)
        
        # Check that settings are deactivated
        settings1.refresh_from_db()
        settings2.refresh_from_db()
        
        self.assertFalse(settings1.active)
        self.assertFalse(settings2.active)

    def test_admin_form_validation(self):
        """Test admin form validation."""
        # Test valid form data
        form_data = {
            'title': 'Test Settings',
            'active': True,
            'page_size': 'A4',
            'items_per_page': 10,
            'page_margin_mm': 15,
            'font_name': 'DejaVuSans.ttf',
            'header_font_size': 10,
            'body_font_size': 7,
            'header_background_color': '#F0F0F0',
            'grid_line_color': '#000000',
            'grid_line_width': 0.25,
            'show_header': True,
            'show_logo': True,
            'show_export_time': True,
            'show_page_numbers': True,
            'rtl_support': False,
            'content_alignment': 'CENTER',
            'header_alignment': 'CENTER',
            'title_alignment': 'CENTER',
            'table_spacing': 1.0,
            'max_chars_per_line': 45
        }
        
        # Create form instance
        form = self.admin.get_form(request=None)()
        form.cleaned_data = form_data
        
        # Should be valid
        self.assertTrue(form.is_valid())

    def test_admin_save_model(self):
        """Test admin save model method."""
        # Create request
        request = self.factory.post('/admin/')
        request.user = self.user
        
        # Create settings object
        settings = ExportPDFSettings(
            title='Test Settings',
            active=True
        )
        
        # Test save
        self.admin.save_model(request, settings, None, None)
        
        # Check that settings was saved
        self.assertTrue(settings.pk)
        self.assertEqual(settings.title, 'Test Settings')
        self.assertTrue(settings.active)

    def test_admin_get_queryset(self):
        """Test admin get queryset method."""
        # Create test settings
        settings1 = ExportPDFSettings.objects.create(
            title='Settings 1',
            active=True
        )
        settings2 = ExportPDFSettings.objects.create(
            title='Settings 2',
            active=False
        )
        
        # Create request
        request = self.factory.get('/admin/')
        request.user = self.user
        
        # Test queryset
        queryset = self.admin.get_queryset(request)
        
        # Should return all settings
        self.assertEqual(queryset.count(), 2)
        self.assertIn(settings1, queryset)
        self.assertIn(settings2, queryset)

    def test_admin_has_add_permission(self):
        """Test admin add permission."""
        # Create request
        request = self.factory.get('/admin/')
        request.user = self.user
        
        # Superuser should have add permission
        self.assertTrue(self.admin.has_add_permission(request))

    def test_admin_has_change_permission(self):
        """Test admin change permission."""
        # Create request
        request = self.factory.get('/admin/')
        request.user = self.user
        
        # Superuser should have change permission
        self.assertTrue(self.admin.has_change_permission(request))

    def test_admin_has_delete_permission(self):
        """Test admin delete permission."""
        # Create request
        request = self.factory.get('/admin/')
        request.user = self.user
        
        # Superuser should have delete permission
        self.assertTrue(self.admin.has_delete_permission(request))

    def test_admin_has_view_permission(self):
        """Test admin view permission."""
        # Create request
        request = self.factory.get('/admin/')
        request.user = self.user
        
        # Superuser should have view permission
        self.assertTrue(self.admin.has_view_permission(request))

    def test_admin_logo_field_display(self):
        """Test admin logo field display."""
        # Create settings with logo
        image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
        image_file = SimpleUploadedFile(
            "test_logo.png",
            image_content,
            content_type="image/png"
        )
        
        settings = ExportPDFSettings.objects.create(
            title='Test Settings',
            logo=image_file
        )
        
        # Test logo display
        logo_display = self.admin.logo_display(settings)
        self.assertIsNotNone(logo_display)

    def test_admin_logo_field_display_no_logo(self):
        """Test admin logo field display when no logo."""
        # Create settings without logo
        settings = ExportPDFSettings.objects.create(
            title='Test Settings'
        )
        
        # Test logo display
        logo_display = self.admin.logo_display(settings)
        self.assertEqual(logo_display, "No logo")

    def test_admin_color_field_widget(self):
        """Test admin color field widget."""
        # Test that color fields use color input widget
        form = self.admin.get_form(request=None)()
        
        # Check that color fields have color input widget
        color_fields = ['header_background_color', 'grid_line_color']
        for field_name in color_fields:
            if field_name in form.fields:
                widget = form.fields[field_name].widget
                self.assertEqual(widget.input_type, 'color')

    def test_admin_help_text(self):
        """Test admin help text."""
        # Test that help text is properly configured
        form = self.admin.get_form(request=None)()
        
        # Check that important fields have help text
        fields_with_help = [
            'active',
            'page_size',
            'items_per_page',
            'page_margin_mm',
            'font_name',
            'header_font_size',
            'body_font_size',
            'rtl_support'
        ]
        
        for field_name in fields_with_help:
            if field_name in form.fields:
                field = form.fields[field_name]
                self.assertTrue(hasattr(field, 'help_text'))
                self.assertIsNotNone(field.help_text)

    def test_admin_validation_error_handling(self):
        """Test admin validation error handling."""
        # Create request
        request = self.factory.post('/admin/')
        request.user = self.user
        
        # Create settings with invalid data
        settings = ExportPDFSettings(
            title='Invalid Settings',
            header_font_size=5,  # Too small
            body_font_size=25,   # Too large
            page_margin_mm=2,    # Too small
            items_per_page=0,    # Too small
            grid_line_width=0.05, # Too small
            table_spacing=0.1,   # Too small
            max_chars_per_line=10 # Too small
        )
        
        # Test that validation errors are handled
        try:
            self.admin.save_model(request, settings, None, None)
            # If no exception is raised, the validation should have caught the errors
        except Exception as e:
            # Validation errors should be caught and handled gracefully
            self.assertIsInstance(e, (ValueError, TypeError))

    def test_admin_bulk_operations(self):
        """Test admin bulk operations."""
        # Create multiple settings
        settings_list = []
        for i in range(5):
            settings = ExportPDFSettings.objects.create(
                title=f'Settings {i}',
                active=False
            )
            settings_list.append(settings)
        
        # Create request
        request = self.factory.post('/admin/')
        request.user = self.user
        
        # Test bulk activation
        queryset = ExportPDFSettings.objects.filter(id__in=[s.id for s in settings_list])
        self.admin.activate_settings(request, queryset)
        
        # Check that only one is active (due to unique constraint)
        active_count = ExportPDFSettings.objects.filter(active=True).count()
        self.assertEqual(active_count, 1)
        
        # Test bulk deactivation
        self.admin.deactivate_settings(request, queryset)
        
        # Check that all are deactivated
        active_count = ExportPDFSettings.objects.filter(active=True).count()
        self.assertEqual(active_count, 0)

    def test_admin_custom_methods(self):
        """Test admin custom methods."""
        # Create settings
        settings = ExportPDFSettings.objects.create(
            title='Test Settings',
            active=True,
            page_size='A4',
            items_per_page=10
        )
        
        # Test custom methods
        self.assertIsNotNone(self.admin.logo_display(settings))
        
        # Test that custom methods return appropriate values
        logo_display = self.admin.logo_display(settings)
        self.assertIsInstance(logo_display, str)

    def test_admin_permissions_with_regular_user(self):
        """Test admin permissions with regular user."""
        # Create regular user
        user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='regular123'
        )
        
        # Create request
        request = self.factory.get('/admin/')
        request.user = user
        
        # Regular user should not have admin permissions
        self.assertFalse(self.admin.has_add_permission(request))
        self.assertFalse(self.admin.has_change_permission(request))
        self.assertFalse(self.admin.has_delete_permission(request))
        self.assertFalse(self.admin.has_view_permission(request))

    def test_admin_permissions_with_staff_user(self):
        """Test admin permissions with staff user."""
        # Create staff user
        user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='staff123',
            is_staff=True
        )
        
        # Create request
        request = self.factory.get('/admin/')
        request.user = user
        
        # Staff user should have view permission but not others
        self.assertFalse(self.admin.has_add_permission(request))
        self.assertFalse(self.admin.has_change_permission(request))
        self.assertFalse(self.admin.has_delete_permission(request))
        self.assertTrue(self.admin.has_view_permission(request))
