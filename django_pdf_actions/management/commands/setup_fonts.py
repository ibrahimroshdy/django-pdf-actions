"""Management command to set up fonts for PDF export"""

import os
import shutil
import zipfile
import tempfile
from django.core.management.base import BaseCommand
from django.conf import settings
import requests


class Command(BaseCommand):
    help = 'Downloads and sets up default fonts for PDF export'

    def add_arguments(self, parser):
        parser.add_argument(
            '--font-url',
            type=str,
            help='URL to download additional font from'
        )
        parser.add_argument(
            '--font-name',
            type=str,
            help='Name for the font file (e.g., "CustomFont.ttf")'
        )

    def download_and_process_font(self, url, target_path, font_name):
        """Download and process font file, handling both direct TTF files and zip archives."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Download the file
            response = requests.get(url, stream=True)
            response.raise_for_status()
            shutil.copyfileobj(response.raw, temp_file)
            temp_file.flush()

            # Check if it's a zip file
            if zipfile.is_zipfile(temp_file.name):
                with zipfile.ZipFile(temp_file.name) as zip_ref:
                    # List all TTF files in the zip
                    ttf_files = [f for f in zip_ref.namelist() if f.endswith('.ttf')]
                    if not ttf_files:
                        raise Exception("No TTF files found in the zip archive")
                    
                    # For DejaVu Sans, find the specific file we want
                    if font_name == 'DejaVuSans.ttf':
                        target_ttf = next(f for f in ttf_files if 'DejaVuSans.ttf' in f)
                    else:
                        # For other fonts, use the first TTF file or match the name
                        target_ttf = next((f for f in ttf_files if font_name in f), ttf_files[0])
                    
                    # Extract only the needed TTF file
                    with zip_ref.open(target_ttf) as source, open(target_path, 'wb') as target:
                        shutil.copyfileobj(source, target)
            else:
                # Direct TTF file, just move it to the target location
                shutil.move(temp_file.name, target_path)

    def handle(self, *args, **options):
        # Create fonts directory in static/assets/fonts
        fonts_dir = os.path.join(settings.BASE_DIR, 'static', 'assets', 'fonts')
        os.makedirs(fonts_dir, exist_ok=True)

        # List of default fonts to download
        fonts = [
            {
                'name': 'DejaVuSans.ttf',
                'url': 'https://github.com/dejavu-fonts/dejavu-fonts/releases/download/version_2_37/dejavu-fonts-ttf-2.37.zip'
            },
        ]

        # Add custom font if URL is provided
        if options['font_url']:
            if not options['font_name']:
                font_name = os.path.basename(options['font_url'])
                if not font_name.endswith('.ttf'):
                    font_name += '.ttf'
            else:
                font_name = options['font_name']
                if not font_name.endswith('.ttf'):
                    font_name += '.ttf'
            
            fonts.append({
                'name': font_name,
                'url': options['font_url']
            })
            self.stdout.write(
                self.style.NOTICE(f"Adding custom font: {font_name} from {options['font_url']}")
            )

        for font in fonts:
            font_path = os.path.join(fonts_dir, font['name'])
            
            # Skip if font already exists
            if os.path.exists(font_path):
                self.stdout.write(
                    self.style.SUCCESS(f"Font {font['name']} already exists at {font_path}")
                )
                continue

            try:
                # Download and process font
                self.stdout.write(f"Downloading {font['name']} to {font_path}...")
                self.download_and_process_font(font['url'], font_path, font['name'])
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully installed {font['name']} to {font_path}")
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error processing {font['name']}: {str(e)}")
                )
                self.stdout.write(
                    self.style.NOTICE(f"You can manually download the font from {font['url']} and place it in {fonts_dir}")
                )

        self.stdout.write(self.style.SUCCESS(f'Font setup complete. Fonts directory: {fonts_dir}')) 