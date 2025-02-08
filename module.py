# Import necessary modules
import os

import django
from django.db import transaction
from faker import Faker

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dj_actions_pdf.settings')
django.setup()
from .django_pdf_actions.models import ExportPDFSettings

# Create a Faker instance
fake = Faker()


# Define a function to create fake export PDF settings
def create_fake_export_pdf_settings():
    title = fake.word()
    active = fake.boolean()
    dummy = fake.word()
    dummy1 = fake.word()
    dummy2 = fake.word()
    dummy3 = fake.word()
    dummy4 = fake.word()
    dummy5 = fake.word()
    dummy6 = fake.word()
    dummy7 = fake.word()
    dummy8 = fake.word()
    dummy9 = fake.word()
    # Create a fake image file
    image_path = os.path.join(os.path.dirname(__file__), 'media/export_pdf/logo.png')

    export_pdf_settings = ExportPDFSettings.objects.create(
        title=title,
        active=active,
        dummy=dummy,
        dummy1=dummy1,
        dummy2=dummy2,
        dummy3=dummy3,
        dummy4=dummy4,
        dummy5=dummy5,
        dummy6=dummy6,
        dummy7=dummy7,
        dummy8=dummy8,
        dummy9=dummy9

    )
    return export_pdf_settings


# Define a function to create multiple samples of export PDF settings
@transaction.atomic
def create_fake_export_pdf_settings_samples(num_samples=50):
    for _ in range(num_samples):
        create_fake_export_pdf_settings()


# Call the function to create 50 samples
create_fake_export_pdf_settings_samples()
