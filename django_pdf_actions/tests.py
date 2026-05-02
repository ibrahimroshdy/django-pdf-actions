"""
Django PDF Actions Test Suite

This module provides a comprehensive test suite for the Django PDF Actions package.
It includes tests for models, actions, utilities, admin integration, and management commands.
"""

import unittest

from django.test import TestCase, TestLoader
from django.test.runner import DiscoverRunner


class DjangoPDFActionsTestSuite(TestCase):
    """
    Main test suite for Django PDF Actions.

    This class serves as a central point for running all tests
    and provides utilities for test discovery and execution.
    """

    def test_package_imports(self):
        """Test that all package modules can be imported successfully."""
        try:
            from django_pdf_actions import actions, admin, apps, models
            from django_pdf_actions.actions import landscape, portrait, utils
        except ImportError as e:
            self.fail(f"Failed to import package modules: {e}")
        self.assertTrue(actions)
        self.assertTrue(admin)
        self.assertTrue(apps)
        self.assertTrue(models)
        self.assertTrue(landscape)
        self.assertTrue(portrait)
        self.assertTrue(utils)

    def test_package_version(self):
        """Test that package version is accessible."""
        try:
            from django_pdf_actions import __version__

            self.assertIsNotNone(__version__)
            self.assertIsInstance(__version__, str)
        except ImportError:
            # Version might not be defined in __init__.py
            pass

    def test_package_metadata(self):
        """Test that package metadata is accessible."""
        try:
            from django_pdf_actions.apps import ExportPDFConfig

            self.assertIsNotNone(ExportPDFConfig.name)
            self.assertIsNotNone(ExportPDFConfig.verbose_name)
        except ImportError as e:
            self.fail(f"Failed to import app config: {e}")


class TestDiscovery:
    """
    Utility class for test discovery and organization.
    """

    @staticmethod
    def get_all_tests():
        """
        Get all test classes and methods in the package.

        Returns:
            list: List of test classes and methods
        """
        loader = TestLoader()
        suite = loader.discover("tests", pattern="test_*.py")
        return suite

    @staticmethod
    def get_test_categories():
        """
        Get tests organized by category.

        Returns:
            dict: Dictionary with test categories as keys and test lists as values
        """
        categories = {
            "models": ["test_models.py"],
            "actions": ["test_actions.py"],
            "utils": ["test_utils.py"],
            "admin": ["test_admin.py"],
            "management": ["test_management_commands.py"],
            "compatibility": ["test_compatibility.py"],
        }
        return categories

    @staticmethod
    def run_specific_category(category):
        """
        Run tests for a specific category.

        Args:
            category (str): Test category to run

        Returns:
            unittest.TestResult: Test results
        """
        categories = TestDiscovery.get_test_categories()
        if category not in categories:
            raise ValueError(f"Unknown test category: {category}")

        loader = TestLoader()
        suite = unittest.TestSuite()

        for test_file in categories[category]:
            try:
                module_suite = loader.loadTestsFromName(f"tests.{test_file[:-3]}")
                suite.addTest(module_suite)
            except Exception as e:
                print(f"Warning: Could not load {test_file}: {e}")

        runner = unittest.TextTestRunner(verbosity=2)
        return runner.run(suite)


class TestRunner(DiscoverRunner):
    """
    Custom test runner for Django PDF Actions.

    This runner provides additional functionality for test discovery,
    categorization, and reporting.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.test_categories = TestDiscovery.get_test_categories()

    def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
        """
        Build test suite with custom logic.

        Args:
            test_labels (list): List of test labels to run
            extra_tests (list): Additional tests to include
            **kwargs: Additional keyword arguments

        Returns:
            unittest.TestSuite: Built test suite
        """
        suite = super().build_suite(test_labels, extra_tests, **kwargs)

        # Add custom test organization if needed
        if test_labels:
            for label in test_labels:
                if label in self.test_categories:
                    # Add category-specific tests
                    category_suite = TestDiscovery.run_specific_category(label)
                    suite.addTest(category_suite)

        return suite

    def run_tests(self, test_labels=None, extra_tests=None, **kwargs):
        """
        Run tests with custom reporting.

        Args:
            test_labels (list): List of test labels to run
            extra_tests (list): Additional tests to include
            **kwargs: Additional keyword arguments

        Returns:
            int: Exit code
        """
        # Add custom setup if needed
        self.setup_test_environment()

        # Run tests
        result = super().run_tests(test_labels, extra_tests, **kwargs)

        # Add custom teardown if needed
        self.teardown_test_environment()

        return result

    def setup_test_environment(self):
        """Setup test environment."""
        # Add any custom setup logic here
        pass

    def teardown_test_environment(self):
        """Teardown test environment."""
        # Add any custom teardown logic here
        pass


# Test utilities and helpers
class TestHelpers:
    """
    Utility functions for testing.
    """

    @staticmethod
    def create_test_settings(**kwargs):
        """
        Create test PDF settings with default values.

        Args:
            **kwargs: Override default values

        Returns:
            ExportPDFSettings: Test settings instance
        """
        from django_pdf_actions.models import ExportPDFSettings

        defaults = {
            "title": "Test Settings",
            "active": True,
            "page_size": "A4",
            "items_per_page": 10,
            "page_margin_mm": 15,
            "font_name": "DejaVuSans.ttf",
            "header_font_size": 10,
            "body_font_size": 7,
            "header_background_color": "#F0F0F0",
            "grid_line_color": "#000000",
            "grid_line_width": 0.25,
            "show_header": True,
            "show_logo": True,
            "show_export_time": True,
            "show_page_numbers": True,
            "rtl_support": False,
            "content_alignment": "CENTER",
            "header_alignment": "CENTER",
            "title_alignment": "CENTER",
            "table_spacing": 1.0,
            "max_chars_per_line": 45,
        }

        defaults.update(kwargs)
        return ExportPDFSettings(**defaults)

    @staticmethod
    def create_test_model_admin():
        """
        Create test model admin for testing.

        Returns:
            MockModelAdmin: Test model admin instance
        """
        from django.contrib.admin.sites import AdminSite

        from tests.utils import MockModel, MockModelAdmin

        return MockModelAdmin(MockModel, AdminSite())

    @staticmethod
    def create_test_queryset(count=5):
        """
        Create test queryset for testing.

        Args:
            count (int): Number of test objects to create

        Returns:
            MockQuerySet: Test queryset
        """
        from tests.utils import MockModel, MockQuerySet

        objects = [
            MockModel(id=i, name=f"Test User {i}", email=f"test{i}@example.com")
            for i in range(1, count + 1)
        ]

        return MockQuerySet(objects)


# Test configuration and constants
TEST_CONFIG = {
    "COVERAGE_THRESHOLD": 85,
    "MAX_TEST_DURATION": 30,  # seconds
    "TEST_DATA_SIZE": {"small": 10, "medium": 100, "large": 1000},
    "SUPPORTED_PYTHON_VERSIONS": ["3.8", "3.9", "3.10", "3.11", "3.12"],
    "SUPPORTED_DJANGO_VERSIONS": ["3.2", "4.0", "4.1", "4.2", "5.0"],
    "REQUIRED_DEPENDENCIES": [
        "django",
        "reportlab",
        "django-model-utils",
        "arabic-reshaper",
        "python-bidi",
        "Pillow",
    ],
}


# Test markers and decorators
def slow_test(func):
    """Decorator for marking slow tests."""
    func._slow_test = True
    return func


def integration_test(func):
    """Decorator for marking integration tests."""
    func._integration_test = True
    return func


def performance_test(func):
    """Decorator for marking performance tests."""
    func._performance_test = True
    return func


def compatibility_test(func):
    """Decorator for marking compatibility tests."""
    func._compatibility_test = True
    return func


# Export test utilities
__all__ = [
    "DjangoPDFActionsTestSuite",
    "TestDiscovery",
    "TestRunner",
    "TestHelpers",
    "TEST_CONFIG",
    "slow_test",
    "integration_test",
    "performance_test",
    "compatibility_test",
]
