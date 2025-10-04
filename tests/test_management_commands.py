"""Tests for management commands."""

import os
import tempfile
from unittest.mock import patch, MagicMock, mock_open
from django.test import TestCase, override_settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.core.files.storage import default_storage
from django.conf import settings
from io import StringIO


class SetupFontsCommandTest(TestCase):
    """Test cases for setup_fonts management command."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @override_settings(BASE_DIR='/fake/path')
    @patch('django_pdf_actions.management.commands.setup_fonts.os.path.exists')
    @patch('django_pdf_actions.management.commands.setup_fonts.os.makedirs')
    def test_setup_fonts_command_basic(self, mock_makedirs, mock_exists):
        """Test basic setup_fonts command execution."""
        mock_exists.return_value = False
        
        # Capture output
        out = StringIO()
        
        # Run command
        call_command('setup_fonts', stdout=out)
        
        # Check that directories were created
        mock_makedirs.assert_called()
        
        # Check output
        output = out.getvalue()
        self.assertIn('Fonts directory created', output)

    @override_settings(BASE_DIR='/fake/path')
    @patch('django_pdf_actions.management.commands.setup_fonts.os.path.exists')
    @patch('django_pdf_actions.management.commands.setup_fonts.os.listdir')
    def test_setup_fonts_command_existing_directory(self, mock_listdir, mock_exists):
        """Test setup_fonts command with existing directory."""
        mock_exists.return_value = True
        mock_listdir.return_value = ['DejaVuSans.ttf', 'Roboto.ttf']
        
        # Capture output
        out = StringIO()
        
        # Run command
        call_command('setup_fonts', stdout=out)
        
        # Check output
        output = out.getvalue()
        self.assertIn('Found existing fonts', output)

    @override_settings(BASE_DIR='/fake/path')
    @patch('django_pdf_actions.management.commands.setup_fonts.os.path.exists')
    @patch('django_pdf_actions.management.commands.setup_fonts.requests.get')
    @patch('django_pdf_actions.management.commands.setup_fonts.open', new_callable=mock_open)
    def test_setup_fonts_command_with_font_url(self, mock_file, mock_get, mock_exists):
        """Test setup_fonts command with font URL."""
        mock_exists.return_value = True
        
        # Mock successful download
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'fake font content'
        mock_get.return_value = mock_response
        
        # Capture output
        out = StringIO()
        
        # Run command with font URL
        call_command(
            'setup_fonts',
            '--font-url', 'https://example.com/font.ttf',
            '--font-name', 'CustomFont.ttf',
            stdout=out
        )
        
        # Check that download was attempted
        mock_get.assert_called_once_with('https://example.com/font.ttf')
        
        # Check output
        output = out.getvalue()
        self.assertIn('Downloaded font', output)

    @override_settings(BASE_DIR='/fake/path')
    @patch('django_pdf_actions.management.commands.setup_fonts.os.path.exists')
    @patch('django_pdf_actions.management.commands.setup_fonts.requests.get')
    def test_setup_fonts_command_download_failure(self, mock_get, mock_exists):
        """Test setup_fonts command with download failure."""
        mock_exists.return_value = True
        
        # Mock failed download
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # Capture output
        out = StringIO()
        
        # Run command with font URL
        call_command(
            'setup_fonts',
            '--font-url', 'https://example.com/nonexistent.ttf',
            '--font-name', 'CustomFont.ttf',
            stdout=out
        )
        
        # Check output
        output = out.getvalue()
        self.assertIn('Failed to download font', output)

    @override_settings(BASE_DIR='/fake/path')
    @patch('django_pdf_actions.management.commands.setup_fonts.os.path.exists')
    @patch('django_pdf_actions.management.commands.setup_fonts.requests.get')
    def test_setup_fonts_command_network_error(self, mock_get, mock_exists):
        """Test setup_fonts command with network error."""
        mock_exists.return_value = True
        
        # Mock network error
        mock_get.side_effect = Exception('Network error')
        
        # Capture output
        out = StringIO()
        
        # Run command with font URL
        call_command(
            'setup_fonts',
            '--font-url', 'https://example.com/font.ttf',
            '--font-name', 'CustomFont.ttf',
            stdout=out
        )
        
        # Check output
        output = out.getvalue()
        self.assertIn('Error downloading font', output)

    @override_settings(BASE_DIR='/fake/path')
    @patch('django_pdf_actions.management.commands.setup_fonts.os.path.exists')
    @patch('django_pdf_actions.management.commands.setup_fonts.os.listdir')
    def test_setup_fonts_command_list_fonts(self, mock_listdir, mock_exists):
        """Test setup_fonts command list functionality."""
        mock_exists.return_value = True
        mock_listdir.return_value = ['DejaVuSans.ttf', 'Roboto.ttf', 'Cairo.otf', 'readme.txt']
        
        # Capture output
        out = StringIO()
        
        # Run command with list option
        call_command('setup_fonts', '--list', stdout=out)
        
        # Check output
        output = out.getvalue()
        self.assertIn('DejaVuSans.ttf', output)
        self.assertIn('Roboto.ttf', output)
        self.assertIn('Cairo.otf', output)
        self.assertNotIn('readme.txt', output)  # Should not list non-font files

    @override_settings(BASE_DIR='/fake/path')
    @patch('django_pdf_actions.management.commands.setup_fonts.os.path.exists')
    def test_setup_fonts_command_no_fonts_directory(self, mock_exists):
        """Test setup_fonts command when fonts directory doesn't exist."""
        mock_exists.return_value = False
        
        # Capture output
        out = StringIO()
        
        # Run command
        call_command('setup_fonts', stdout=out)
        
        # Check output
        output = out.getvalue()
        self.assertIn('Fonts directory created', output)

    @override_settings(BASE_DIR='/fake/path')
    @patch('django_pdf_actions.management.commands.setup_fonts.os.path.exists')
    @patch('django_pdf_actions.management.commands.setup_fonts.os.listdir')
    def test_setup_fonts_command_empty_directory(self, mock_listdir, mock_exists):
        """Test setup_fonts command with empty fonts directory."""
        mock_exists.return_value = True
        mock_listdir.return_value = []
        
        # Capture output
        out = StringIO()
        
        # Run command
        call_command('setup_fonts', stdout=out)
        
        # Check output
        output = out.getvalue()
        self.assertIn('No fonts found', output)

    def test_setup_fonts_command_help(self):
        """Test setup_fonts command help."""
        # Capture output
        out = StringIO()
        
        # Run command with help
        call_command('setup_fonts', '--help', stdout=out)
        
        # Check output contains help information
        output = out.getvalue()
        self.assertIn('setup_fonts', output)

    @override_settings(BASE_DIR='/fake/path')
    @patch('django_pdf_actions.management.commands.setup_fonts.os.path.exists')
    @patch('django_pdf_actions.management.commands.setup_fonts.requests.get')
    @patch('django_pdf_actions.management.commands.setup_fonts.open', new_callable=mock_open)
    def test_setup_fonts_command_multiple_fonts(self, mock_file, mock_get, mock_exists):
        """Test setup_fonts command with multiple font downloads."""
        mock_exists.return_value = True
        
        # Mock successful downloads
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'fake font content'
        mock_get.return_value = mock_response
        
        # Capture output
        out = StringIO()
        
        # Run command with multiple font URLs
        call_command(
            'setup_fonts',
            '--font-url', 'https://example.com/font1.ttf',
            '--font-name', 'Font1.ttf',
            '--font-url', 'https://example.com/font2.ttf',
            '--font-name', 'Font2.ttf',
            stdout=out
        )
        
        # Check that both downloads were attempted
        self.assertEqual(mock_get.call_count, 2)
        
        # Check output
        output = out.getvalue()
        self.assertIn('Downloaded font', output)

    @override_settings(BASE_DIR='/fake/path')
    @patch('django_pdf_actions.management.commands.setup_fonts.os.path.exists')
    @patch('django_pdf_actions.management.commands.setup_fonts.os.listdir')
    def test_setup_fonts_command_font_validation(self, mock_listdir, mock_exists):
        """Test setup_fonts command font file validation."""
        mock_exists.return_value = True
        mock_listdir.return_value = [
            'DejaVuSans.ttf',  # Valid TTF
            'Roboto.otf',      # Valid OTF
            'readme.txt',      # Invalid (not font)
            'font.woff',       # Invalid (not TTF/OTF)
            'font.eot'         # Invalid (not TTF/OTF)
        ]
        
        # Capture output
        out = StringIO()
        
        # Run command with list option
        call_command('setup_fonts', '--list', stdout=out)
        
        # Check output
        output = out.getvalue()
        self.assertIn('DejaVuSans.ttf', output)
        self.assertIn('Roboto.otf', output)
        self.assertNotIn('readme.txt', output)
        self.assertNotIn('font.woff', output)
        self.assertNotIn('font.eot', output)

    @override_settings(BASE_DIR='/fake/path')
    @patch('django_pdf_actions.management.commands.setup_fonts.os.path.exists')
    @patch('django_pdf_actions.management.commands.setup_fonts.requests.get')
    @patch('django_pdf_actions.management.commands.setup_fonts.open', new_callable=mock_open)
    def test_setup_fonts_command_file_write_error(self, mock_file, mock_get, mock_exists):
        """Test setup_fonts command with file write error."""
        mock_exists.return_value = True
        
        # Mock successful download
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'fake font content'
        mock_get.return_value = mock_response
        
        # Mock file write error
        mock_file.side_effect = IOError('Permission denied')
        
        # Capture output
        out = StringIO()
        
        # Run command with font URL
        call_command(
            'setup_fonts',
            '--font-url', 'https://example.com/font.ttf',
            '--font-name', 'CustomFont.ttf',
            stdout=out
        )
        
        # Check output
        output = out.getvalue()
        self.assertIn('Error saving font', output)

    def test_setup_fonts_command_invalid_arguments(self):
        """Test setup_fonts command with invalid arguments."""
        # Test with font-url but no font-name
        with self.assertRaises(CommandError):
            call_command('setup_fonts', '--font-url', 'https://example.com/font.ttf')
        
        # Test with font-name but no font-url
        with self.assertRaises(CommandError):
            call_command('setup_fonts', '--font-name', 'CustomFont.ttf')

    @override_settings(BASE_DIR='/fake/path')
    @patch('django_pdf_actions.management.commands.setup_fonts.os.path.exists')
    @patch('django_pdf_actions.management.commands.setup_fonts.os.listdir')
    def test_setup_fonts_command_verbose_output(self, mock_listdir, mock_exists):
        """Test setup_fonts command with verbose output."""
        mock_exists.return_value = True
        mock_listdir.return_value = ['DejaVuSans.ttf', 'Roboto.ttf']
        
        # Capture output
        out = StringIO()
        
        # Run command with verbose option
        call_command('setup_fonts', '--list', '--verbosity', '2', stdout=out)
        
        # Check output
        output = out.getvalue()
        self.assertIn('DejaVuSans.ttf', output)
        self.assertIn('Roboto.ttf', output)

    @override_settings(BASE_DIR='/fake/path')
    @patch('django_pdf_actions.management.commands.setup_fonts.os.path.exists')
    @patch('django_pdf_actions.management.commands.setup_fonts.os.makedirs')
    def test_setup_fonts_command_directory_creation_error(self, mock_makedirs, mock_exists):
        """Test setup_fonts command with directory creation error."""
        mock_exists.return_value = False
        mock_makedirs.side_effect = OSError('Permission denied')
        
        # Capture output
        out = StringIO()
        
        # Run command
        call_command('setup_fonts', stdout=out)
        
        # Check output
        output = out.getvalue()
        self.assertIn('Error creating fonts directory', output)

    @override_settings(BASE_DIR='/fake/path')
    @patch('django_pdf_actions.management.commands.setup_fonts.os.path.exists')
    @patch('django_pdf_actions.management.commands.setup_fonts.os.listdir')
    def test_setup_fonts_command_permission_error(self, mock_listdir, mock_exists):
        """Test setup_fonts command with permission error."""
        mock_exists.return_value = True
        mock_listdir.side_effect = PermissionError('Permission denied')
        
        # Capture output
        out = StringIO()
        
        # Run command
        call_command('setup_fonts', stdout=out)
        
        # Check output
        output = out.getvalue()
        self.assertIn('Error accessing fonts directory', output)


class ManagementCommandIntegrationTest(TestCase):
    """Integration tests for management commands."""

    def test_setup_fonts_command_integration(self):
        """Test setup_fonts command integration."""
        # This test would require actual file system operations
        # For now, we'll test that the command can be called without errors
        
        # Capture output
        out = StringIO()
        
        # Run command (should not raise exception)
        try:
            call_command('setup_fonts', '--help', stdout=out)
        except Exception as e:
            self.fail(f"setup_fonts command failed: {e}")
        
        # Check that help output was generated
        output = out.getvalue()
        self.assertIsInstance(output, str)
        self.assertTrue(len(output) > 0)

    def test_management_command_discovery(self):
        """Test that management commands are properly discovered."""
        from django.core.management import get_commands
        
        # Check that our command is registered
        commands = get_commands()
        self.assertIn('setup_fonts', commands)

    def test_management_command_help_text(self):
        """Test management command help text."""
        from django.core.management import get_commands
        
        # Get command class
        commands = get_commands()
        command_name = commands['setup_fonts']
        
        # Import command class
        from django.core.management.base import BaseCommand
        from django_pdf_actions.management.commands.setup_fonts import Command
        
        # Check that command has help text
        self.assertIsInstance(Command.help, str)
        self.assertTrue(len(Command.help) > 0)

    def test_management_command_options(self):
        """Test management command options."""
        from django_pdf_actions.management.commands.setup_fonts import Command
        
        # Check that command has expected options
        command = Command()
        parser = command.create_parser('setup_fonts', 'setup_fonts')
        
        # Check that parser was created successfully
        self.assertIsNotNone(parser)
