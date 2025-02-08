"""Management command to set up fonts for PDF export"""

import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
import requests


class Command(BaseCommand):
    help = 'Downloads and sets up default fonts for PDF export'

    def handle(self, *args, **options):
        # Create fonts directory if it doesn't exist
        fonts_dir = os.path.join(settings.BASE_DIR, 'django_pdf_actions/static/django_pdf_actions/fonts')
        os.makedirs(fonts_dir, exist_ok=True)

        # List of fonts to download
        fonts = [
            {
                'name': 'DejaVuSans.ttf',
                'url': 'https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf'
            },
            # Add more fonts here as needed
        ]

        for font in fonts:
            font_path = os.path.join(fonts_dir, font['name'])
            
            # Skip if font already exists
            if os.path.exists(font_path):
                self.stdout.write(
                    self.style.SUCCESS(f"Font {font['name']} already exists")
                )
                continue

            try:
                # Download font
                self.stdout.write(f"Downloading {font['name']}...")
                response = requests.get(font['url'], stream=True)
                response.raise_for_status()

                # Save font file
                with open(font_path, 'wb') as f:
                    shutil.copyfileobj(response.raw, f)

                self.stdout.write(
                    self.style.SUCCESS(f"Successfully downloaded {font['name']}")
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error downloading {font['name']}: {str(e)}")
                )

        self.stdout.write(self.style.SUCCESS('Font setup complete')) 