"""Test utilities."""

from django.contrib.admin import ModelAdmin
from django.db import models


class MockModel(models.Model):
    """Mock model for testing."""
    name = models.CharField(max_length=100)
    email = models.EmailField()

    class Meta:
        app_label = 'django_pdf_actions'
        managed = False


class MockQuerySet:
    """Mock queryset for testing."""
    def __init__(self, items):
        self.items = items
        self.model = MockModel

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)


class MockModelAdmin(ModelAdmin):
    """Mock model admin for testing."""
    list_display = ('id', 'name', 'email')
    model = MockModel 