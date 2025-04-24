import os

from django.contrib import admin
from django.utils.html import format_html

from . import models
from .actions import export_to_pdf_landscape, export_to_pdf_portrait


@admin.register(models.ExportPDFSettings)
class PdfAdmin(admin.ModelAdmin):
    list_display = ('title', 'active', 'font_name_display', 'logo_display', 'items_per_page', 'page_size',
                    'rtl_support',
                    'content_alignment', 'header_alignment', 'modified',
                    'header_background_color_preview', 'grid_line_color_preview')
    list_filter = ('active', 'show_header', 'show_logo', 'show_export_time', 'rtl_support',
                   'content_alignment', 'header_alignment', 'title_alignment', 'font_name', 'page_size')
    search_fields = ('title',)
    readonly_fields = (
        'modified', 'created', 'header_background_color_preview', 'grid_line_color_preview', 'logo_display')

    def font_name_display(self, obj):
        font_name = os.path.splitext(obj.font_name)[0]  # Remove .ttf extension
        return format_html(
            '<span style="font-family: monospace;">{}</span>',
            font_name
        )

    font_name_display.short_description = 'Font'

    def logo_display(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-height: 30px; max-width: 100px;" /> {}',
                obj.logo.url,
                os.path.basename(obj.logo.name)
            )
        return "No logo"

    logo_display.short_description = 'Logo'

    def header_background_color_preview(self, obj):
        return format_html(
            '<div style="display: inline-block; width: 20px; height: 20px; background-color: {}; border: 1px solid #000; vertical-align: middle; margin-right: 5px;"></div> {}',
            obj.header_background_color,
            obj.header_background_color
        )

    header_background_color_preview.short_description = 'Header Background'

    def grid_line_color_preview(self, obj):
        return format_html(
            '<div style="display: inline-block; width: 20px; height: 20px; background-color: {}; border: 1px solid #000; vertical-align: middle; margin-right: 5px;"></div> {}',
            obj.grid_line_color,
            obj.grid_line_color
        )

    grid_line_color_preview.short_description = 'Grid Line Color'

    fieldsets = (
        ('General', {
            'fields': ('title', 'active')
        }),
        ('Page Layout', {
            'fields': ('page_size', 'items_per_page', 'page_margin_mm')
        }),
        ('Font Settings', {
            'fields': ('font_name', 'header_font_size', 'body_font_size')
        }),
        ('Visual Settings', {
            'fields': (
                ('logo', 'logo_display'),
                ('header_background_color', 'header_background_color_preview'),
                ('grid_line_color', 'grid_line_color_preview'),
                'grid_line_width'
            )
        }),
        ('Display Options', {
            'fields': (
                'show_header', 'show_logo',
                'show_export_time', 'show_page_numbers',
                'rtl_support'
            )
        }),
        ('Alignment Settings', {
            'fields': (
                'title_alignment', 'header_alignment', 'content_alignment'
            )
        }),
        ('Table Settings', {
            'fields': ('table_spacing', 'max_chars_per_line')
        }),
        ('Metadata', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )

    actions = [export_to_pdf_landscape, export_to_pdf_portrait]

    def save_model(self, request, obj, form, change):
        # Ensure validation is called
        obj.full_clean()
        super().save_model(request, obj, form, change)

    class Media:
        css = {
            'all': ('admin/css/widgets.css',)
        }
