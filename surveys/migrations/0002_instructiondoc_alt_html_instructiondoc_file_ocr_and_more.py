

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='instructiondoc',
            name='alt_html',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='instructiondoc',
            name='file_ocr',
            field=models.FileField(blank=True, null=True, upload_to='docs_ocr/'),
        ),
        migrations.AddField(
            model_name='instructiondoc',
            name='has_text_layer',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='instructiondoc',
            name='ocr_notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='instructiondoc',
            name='ocr_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('done', 'Done'), ('failed', 'Failed')], default='pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='instructiondoc',
            name='version',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
