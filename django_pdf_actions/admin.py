from django.contrib import admin
from .actions import export_to_pdf_landscape, export_to_pdf_portrait
from . import models


@admin.register(models.ExportPDFSettings)
class PdfAdmin(admin.ModelAdmin):
    list_display = ('title', 'active', 'items_per_page', 'modified')
    list_filter = ('active', 'show_header', 'show_logo', 'show_export_time')
    search_fields = ('title',)
    readonly_fields = ('modified', 'created')
    
    fieldsets = (
        ('General', {
            'fields': ('title', 'active')
        }),
        ('Page Layout', {
            'fields': ('items_per_page', 'page_margin_mm')
        }),
        ('Font Settings', {
            'fields': ('font_name', 'header_font_size', 'body_font_size')
        }),
        ('Visual Settings', {
            'fields': (
                'logo', 'header_background_color', 
                'grid_line_color', 'grid_line_width'
            )
        }),
        ('Display Options', {
            'fields': (
                'show_header', 'show_logo',
                'show_export_time', 'show_page_numbers'
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
