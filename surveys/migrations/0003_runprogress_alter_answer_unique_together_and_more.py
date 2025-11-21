

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0002_instructiondoc_alt_html_instructiondoc_file_ocr_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='RunProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_token', models.CharField(db_index=True, max_length=64)),
                ('resp_session_ids', models.JSONField()),
                ('current_step', models.PositiveIntegerField()),
                ('total_steps', models.PositiveIntegerField()),
                ('is_finished', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='answer',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='instructiondoc',
            name='alt_html',
        ),
        migrations.RemoveField(
            model_name='instructiondoc',
            name='file_ocr',
        ),
        migrations.RemoveField(
            model_name='instructiondoc',
            name='has_text_layer',
        ),
        migrations.RemoveField(
            model_name='instructiondoc',
            name='ocr_notes',
        ),
        migrations.RemoveField(
            model_name='instructiondoc',
            name='ocr_status',
        ),
        migrations.AlterField(
            model_name='instructiondoc',
            name='file',
            field=models.FileField(upload_to='instructions/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=('pdf', 'mp4', 'webm', 'ogg'))]),
        ),
        migrations.AlterField(
            model_name='instructiondoc',
            name='version',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddConstraint(
            model_name='answer',
            constraint=models.UniqueConstraint(fields=('session', 'question'), name='unique_answer_per_session_question'),
        ),
    ]
