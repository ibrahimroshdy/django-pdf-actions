from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('django_pdf_actions', '0003_exportpdfsettings_rtl_support_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='exportpdfsettings',
            name='content_alignment',
            field=models.CharField(choices=[('LEFT', 'Left'), ('CENTER', 'Center'), ('RIGHT', 'Right')],
                                   default='CENTER', help_text='Text alignment for table content', max_length=10),
        ),
        migrations.AddField(
            model_name='exportpdfsettings',
            name='header_alignment',
            field=models.CharField(choices=[('LEFT', 'Left'), ('CENTER', 'Center'), ('RIGHT', 'Right')],
                                   default='CENTER', help_text='Text alignment for table headers', max_length=10),
        ),
        migrations.AddField(
            model_name='exportpdfsettings',
            name='title_alignment',
            field=models.CharField(choices=[('LEFT', 'Left'), ('CENTER', 'Center'), ('RIGHT', 'Right')],
                                   default='CENTER', help_text='Text alignment for the title', max_length=10),
        ),
    ]
