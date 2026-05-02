"""Tests for management commands (aligned with ``setup_fonts`` implementation)."""

import os
import shutil
import tempfile
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase
from django_pdf_actions.management.commands.setup_fonts import (
    Command as SetupFontsCommand,
)


class SetupFontsCommandTest(TestCase):
    """Regression tests for ``setup_fonts``."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_skips_download_when_default_font_exists(self):
        fonts_dir = os.path.join(self.temp_dir, "static", "assets", "fonts")
        os.makedirs(fonts_dir, exist_ok=True)
        open(os.path.join(fonts_dir, "DejaVuSans.ttf"), "wb").close()

        out = StringIO()
        with self.settings(BASE_DIR=self.temp_dir):
            with patch.object(
                SetupFontsCommand,
                "download_and_process_font",
            ) as mock_dl:
                call_command("setup_fonts", stdout=out)

        mock_dl.assert_not_called()
        self.assertIn("already exists", out.getvalue())
        self.assertIn("Font setup complete", out.getvalue())

    def test_downloads_when_font_missing(self):
        out = StringIO()
        with self.settings(BASE_DIR=self.temp_dir):
            with patch.object(
                SetupFontsCommand,
                "download_and_process_font",
            ) as mock_dl:
                call_command("setup_fonts", stdout=out)

        mock_dl.assert_called()
        args, _kwargs = mock_dl.call_args
        self.assertIn("dejavu-fonts", args[0].lower())
        self.assertIn("Font setup complete", out.getvalue())

    def test_custom_font_url_appended(self):
        out = StringIO()
        with self.settings(BASE_DIR=self.temp_dir):
            with patch.object(
                SetupFontsCommand,
                "download_and_process_font",
            ) as mock_dl:
                call_command(
                    "setup_fonts",
                    "--font-url",
                    "https://example.com/Extra.ttf",
                    "--font-name",
                    "Extra.ttf",
                    stdout=out,
                )

        self.assertEqual(mock_dl.call_count, 2)
        self.assertIn("Adding custom font", out.getvalue())

    def test_font_url_without_explicit_name(self):
        out = StringIO()
        with self.settings(BASE_DIR=self.temp_dir):
            with patch.object(
                SetupFontsCommand,
                "download_and_process_font",
            ):
                call_command(
                    "setup_fonts",
                    "--font-url",
                    "https://example.com/Roboto.ttf",
                    stdout=out,
                )

        self.assertIn("Adding custom font", out.getvalue())

    def test_download_failure_surfaces_error_message(self):
        out = StringIO()
        with self.settings(BASE_DIR=self.temp_dir):
            with patch.object(
                SetupFontsCommand,
                "download_and_process_font",
                side_effect=RuntimeError("network failed"),
            ):
                call_command("setup_fonts", stdout=out)

        self.assertIn("Error processing", out.getvalue())
        self.assertIn("Font setup complete", out.getvalue())

    def test_help_includes_arguments(self):
        cmd = SetupFontsCommand()
        parser = cmd.create_parser("setup_fonts", "setup_fonts")
        out = StringIO()
        parser.print_help(out)
        output = out.getvalue()
        self.assertIn("--font-url", output)
        self.assertIn("--font-name", output)


class ManagementCommandIntegrationTest(TestCase):
    """Light integration checks for command registration."""

    def test_setup_fonts_help_runs(self):
        cmd = SetupFontsCommand()
        parser = cmd.create_parser("setup_fonts", "setup_fonts")
        out = StringIO()
        parser.print_help(out)
        self.assertGreater(len(out.getvalue()), 0)

    def test_management_command_discovery(self):
        from django.core.management import get_commands

        commands = get_commands()
        self.assertIn("setup_fonts", commands)

    def test_management_command_help_text(self):
        self.assertIsInstance(SetupFontsCommand.help, str)
        self.assertGreater(len(SetupFontsCommand.help), 0)

    def test_management_command_options(self):
        command = SetupFontsCommand()
        parser = command.create_parser("setup_fonts", "setup_fonts")
        self.assertIsNotNone(parser)
