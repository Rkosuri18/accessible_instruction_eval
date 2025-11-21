

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InstructionDoc',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('file', models.FileField(upload_to='instructions/')),
                ('version', models.CharField(blank=True, max_length=20)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(choices=[('sensory_conversion', 'Sensory Conversion'), ('procedural_structure', 'Procedural Structure'), ('action_specificity', 'Action Specificity'), ('verification_recovery', 'Verification Feedback & Recovery'), ('reference_clarity', 'Reference Clarity'), ('personalization', 'Personalization'), ('cognitive_load', 'Cognitive Load')], max_length=64, unique=True)),
                ('text', models.TextField()),
                ('order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='ResponseSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_token', models.CharField(blank=True, max_length=64)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('consented', models.BooleanField(default=False)),
                ('doc', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='surveys.instructiondoc')),
            ],
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating_int', models.IntegerField()),
                ('reason_text', models.TextField(blank=True)),
                ('improvement_text', models.TextField(blank=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='surveys.question')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='surveys.responsesession')),
            ],
            options={
                'unique_together': {('session', 'question')},
            },
        ),
    ]
