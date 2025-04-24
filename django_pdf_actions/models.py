import os
import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.forms import TextInput
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel

# Page size choices with dimensions in points (1 point = 1/72 inch)
PAGE_SIZES = [
    ('A4', 'A4 (210mm × 297mm)'),
    ('A3', 'A3 (297mm × 420mm)'),
    ('A2', 'A2 (420mm × 594mm)'),
    ('A1', 'A1 (594mm × 841mm)'),
]

# Define alignment choices
ALIGNMENT_CHOICES = [
    ('LEFT', 'Left'),
    ('CENTER', 'Center'),
    ('RIGHT', 'Right'),
]


def validate_hex_color(value):
    """Validate hex color format"""
    if not re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', value):
        raise ValidationError(
            _('%(value)s is not a valid hex color. Format should be #RRGGBB or #RGB'),
            params={'value': value},
        )


def get_available_fonts():
    """Get list of available fonts from the static/assets/fonts directory"""
    fonts_dir = os.path.join(settings.BASE_DIR, 'static', 'assets', 'fonts')
    fonts = []

    if os.path.exists(fonts_dir):
        for file in os.listdir(fonts_dir):
            if file.lower().endswith(('.ttf', '.otf')):
                # Store just the filename as the value, but show name without extension as label
                name = os.path.splitext(file)[0]
                fonts.append((file, name))

    # Always include the default font
    if not fonts or 'DejaVuSans.ttf' not in [f[0] for f in fonts]:
        fonts.append(('DejaVuSans.ttf', 'DejaVu Sans (Default)'))

    return sorted(fonts, key=lambda x: x[1])


class ColorField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 7
        kwargs['validators'] = [validate_hex_color]
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs['widget'] = TextInput(attrs={'type': 'color'})
        return super().formfield(**kwargs)


# Define the ExportPDFSettings model
class ExportPDFSettings(TimeStampedModel):
    title = models.CharField(
        max_length=100,
        help_text=_("Name of this configuration")
    )
    active = models.BooleanField(
        default=False,
        help_text=_("Only one configuration can be active at a time")
    )

    # Page Layout Settings
    page_size = models.CharField(
        max_length=2,
        choices=PAGE_SIZES,
        default='A4',
        help_text=_("Select the page size for the PDF")
    )
    items_per_page = models.PositiveIntegerField(
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text=_("Number of items to display per page")
    )
    page_margin_mm = models.PositiveIntegerField(
        default=15,
        validators=[MinValueValidator(5), MaxValueValidator(50)],
        help_text=_("Page margin in millimeters")
    )

    # Font Settings
    font_name = models.CharField(
        max_length=100,
        choices=get_available_fonts(),
        default='DejaVuSans.ttf',
        help_text=_("Select font from available system fonts")
    )
    header_font_size = models.PositiveIntegerField(
        default=10,
        validators=[MinValueValidator(6), MaxValueValidator(24)],
        help_text=_("Font size for headers")
    )
    body_font_size = models.PositiveIntegerField(
        default=7,
        validators=[MinValueValidator(6), MaxValueValidator(18)],
        help_text=_("Font size for table content")
    )

    # Visual Settings
    logo = models.ImageField(
        upload_to='export_pdf/logos/',
        help_text=_("Logo to display on PDF"),
        null=True,
        blank=True
    )
    header_background_color = ColorField(
        default='#F0F0F0',
        help_text=_("Header background color (hex format, e.g. #F0F0F0)")
    )
    grid_line_color = ColorField(
        default='#000000',
        help_text=_("Grid line color (hex format, e.g. #000000)")
    )
    grid_line_width = models.FloatField(
        default=0.25,
        validators=[MinValueValidator(0.1), MaxValueValidator(2.0)],
        help_text=_("Grid line width in points")
    )

    # Display Options
    show_header = models.BooleanField(
        default=True,
        help_text=_("Display the header with model name")
    )
    show_logo = models.BooleanField(
        default=True,
        help_text=_("Display the logo in the PDF")
    )
    show_export_time = models.BooleanField(
        default=True,
        help_text=_("Display export timestamp")
    )
    show_page_numbers = models.BooleanField(
        default=True,
        help_text=_("Display page numbers")
    )
    rtl_support = models.BooleanField(
        default=False,
        help_text=_("Enable right-to-left (RTL) text support for Arabic and other RTL languages")
    )
    content_alignment = models.CharField(
        max_length=10,
        choices=ALIGNMENT_CHOICES,
        default='CENTER',
        help_text=_("Text alignment for table content")
    )
    header_alignment = models.CharField(
        max_length=10,
        choices=ALIGNMENT_CHOICES,
        default='CENTER',
        help_text=_("Text alignment for table headers")
    )
    title_alignment = models.CharField(
        max_length=10,
        choices=ALIGNMENT_CHOICES,
        default='CENTER',
        help_text=_("Text alignment for the title")
    )

    # Table Settings
    table_spacing = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.5), MaxValueValidator(5.0)],
        help_text=_("Spacing between table cells in millimeters")
    )
    max_chars_per_line = models.PositiveIntegerField(
        default=45,
        validators=[MinValueValidator(20), MaxValueValidator(100)],
        help_text=_("Maximum characters per line before wrapping")
    )

    def __str__(self):
        return f"{self.title} ({'Active' if self.active else 'Inactive'})"

    def clean(self):
        if self.active:
            # Check if there's already an active configuration
            active_configs = ExportPDFSettings.objects.filter(active=True)
            if self.pk:
                active_configs = active_configs.exclude(pk=self.pk)
            if active_configs.exists():
                raise ValidationError(
                    _("There can only be one active configuration. Please deactivate the current active configuration first.")
                )

    class Meta:
        verbose_name = _('Export PDF Settings')
        verbose_name_plural = _('Export PDF Settings')
        ordering = ['-active', '-modified']


@receiver(pre_save, sender=ExportPDFSettings)
def deactivate_other_settings(sender, instance, **kwargs):
    if instance.active:
        # Deactivate all other configurations
        ExportPDFSettings.objects.exclude(pk=instance.pk).update(active=False)
