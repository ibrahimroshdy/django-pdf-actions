# Settings Reference

<p align="center">
  <img src="assets/logo.svg" alt="Django PDF Actions Logo" width="200" height="200">
</p>

## PDF Export Settings

Django PDF Export provides a comprehensive set of settings that can be configured through the Django admin interface.

## Page Layout Settings

| Setting | Description | Default | Range |
|---------|-------------|---------|--------|
| `items_per_page` | Number of rows per page | 10 | 1-50 |
| `page_margin_mm` | Page margins in millimeters | 15 | 5-50 |
| `header_height_mm` | Header height in millimeters | 20 | 10-50 |
| `footer_height_mm` | Footer height in millimeters | 15 | 10-50 |

## Font Settings

| Setting | Description | Default | Range |
|---------|-------------|---------|--------|
| `font_name` | TTF font file name | DejaVuSans.ttf | Any TTF |
| `header_font_size` | Header text size | 10 | 6-24 |
| `body_font_size` | Body text size | 7 | 6-18 |

## Table Settings

| Setting | Description | Default | Range |
|---------|-------------|---------|--------|
| `table_spacing` | Cell padding in millimeters | 1.5 | 0.5-5.0 |
| `table_line_height` | Row height multiplier | 1.2 | 1.0-2.0 |
| `table_header_height` | Header row height | 30 | 20-50 |
| `max_chars_per_line` | Maximum characters per line | 50 | 30-100 |

## Visual Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `header_background_color` | Header background color | #F0F0F0 |
| `grid_line_color` | Table grid line color | #000000 |
| `grid_line_width` | Grid line thickness | 0.25 |

## Display Options

| Setting | Description | Default |
|---------|-------------|---------|
| `show_header` | Display page header | True |
| `show_logo` | Display company logo | True |
| `show_export_time` | Show export timestamp | True |
| `show_page_numbers` | Show page numbers | True |

## Configuration Example

Here's an example of how to configure the settings through the Django admin interface:

1. Navigate to Admin > Django PDF > Export PDF Settings
2. Click "Add Export PDF Settings"
3. Configure your settings:
   ```python
   {
       'title': 'Default Export Settings',
       'active': True,
       'header_font_size': 12,
       'body_font_size': 8,
       'page_margin_mm': 20,
       'items_per_page': 15,
       'table_spacing': 2.0,
       'show_logo': True,
       'show_page_numbers': True
   }
   ```
4. Save your settings

## Notes

- Only one configuration can be active at a time
- Changes take effect immediately
- Font files must be in the correct directory
- Colors should be in hexadecimal format (#RRGGBB) 