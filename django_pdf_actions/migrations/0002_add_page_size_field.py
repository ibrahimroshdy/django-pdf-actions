from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('django_pdf_actions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='exportpdfsettings',
            name='page_size',
            field=models.CharField(
                choices=[
                    ('A4', 'A4 (210mm × 297mm)'),
                    ('A3', 'A3 (297mm × 420mm)'),
                    ('A2', 'A2 (420mm × 594mm)'),
                    ('A1', 'A1 (594mm × 841mm)')
                ],
                default='A4',
                help_text='Select the page size for the PDF',
                max_length=2
            ),
        ),
    ]
