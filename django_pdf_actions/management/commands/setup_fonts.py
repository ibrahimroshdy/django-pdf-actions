"""Management command to set up fonts for PDF export"""

import os
import shutil
import tempfile
import zipfile

import requests
from django.conf import settings
from django.core.management.base import BaseCommand


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
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

        with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as temp_file:
            # Download the file with browser headers
            response = requests.get(url, stream=True, headers=headers)
            response.raise_for_status()

            # Check content type for zip
            content_type = response.headers.get('content-type', '').lower()
            is_zip = 'zip' in content_type or url.lower().endswith('.zip')

            # Save the downloaded content
            shutil.copyfileobj(response.raw, temp_file)
            temp_file.flush()

            try:
                # Try to open as zip even if not detected as zip (some servers don't set content-type)
                if is_zip or zipfile.is_zipfile(temp_file.name):
                    with zipfile.ZipFile(temp_file.name) as zip_ref:
                        # List all TTF files in the zip
                        ttf_files = [f for f in zip_ref.namelist() if f.lower().endswith('.ttf')]
                        if not ttf_files:
                            raise Exception("No TTF files found in the zip archive")

                        # For DejaVu Sans, find the specific file we want
                        if font_name.lower() == 'dejavusans.ttf':
                            target_ttf = next(f for f in ttf_files if 'DejaVuSans.ttf' in f)
                        else:
                            # For other fonts, try to match the name or use the first TTF
                            target_ttf = next(
                                (f for f in ttf_files if font_name.lower() in f.lower()),
                                ttf_files[0]
                            )

                        # Extract only the needed TTF file
                        with zip_ref.open(target_ttf) as source, open(target_path, 'wb') as target:
                            shutil.copyfileobj(source, target)
                            self.stdout.write(f"Extracted {target_ttf} from zip to {target_path}")
                else:
                    # Direct TTF file, just move it to the target location
                    shutil.move(temp_file.name, target_path)
            except zipfile.BadZipFile:
                # If not a valid zip, assume it's a direct TTF
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
                    self.style.NOTICE(
                        f"You can manually download the font from {font['url']} and place it in {fonts_dir}")
                )

        self.stdout.write(self.style.SUCCESS(f'Font setup complete. Fonts directory: {fonts_dir}'))
