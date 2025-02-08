"""Test configuration for pytest."""

import os
import pytest
from django.conf import settings


def pytest_configure():
    """Configure Django for tests."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
    try:
        import django
        django.setup()
    except Exception as e:
        print(f"Error setting up Django: {e}")
        raise


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Set up the test database."""
    with django_db_blocker.unblock():
        try:
            from django.core.management import call_command
            # Run migrations
            call_command('migrate', verbosity=0, interactive=False)
        except Exception as e:
            print(f"Error running migrations: {e}")
            raise


@pytest.fixture
def admin_user(django_db_setup, django_db_blocker):
    """Create and return a superuser for testing."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    with django_db_blocker.unblock():
        return User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password'
        )


@pytest.fixture
def admin_client(admin_user, client):
    """Create and return an admin client for testing."""
    from django.test import Client
    client = Client()
    client.force_login(admin_user)
    return client


@pytest.fixture
def pdf_settings(django_db_setup, django_db_blocker):
    """Create and return PDF export settings for testing."""
    from django_pdf_actions.models import ExportPDFSettings
    
    with django_db_blocker.unblock():
        return ExportPDFSettings.objects.create(
            title='Test Settings',
            active=True,
            header_font_size=12,
            body_font_size=10,
            page_margin_mm=15,
            items_per_page=10,
            header_background_color='#F0F0F0',
            grid_line_color='#000000'
        ) 