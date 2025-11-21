

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0003_runprogress_alter_answer_unique_together_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='EvaluationRun',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_token', models.CharField(blank=True, db_index=True, help_text='Anonymous cookie-based id for the participant.', max_length=64)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('total_steps', models.PositiveSmallIntegerField(default=0)),
            ],
        ),
        migrations.AlterField(
            model_name='responsesession',
            name='doc',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='surveys.instructiondoc'),
        ),
        migrations.AlterField(
            model_name='runprogress',
            name='current_step',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='runprogress',
            name='total_steps',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='responsesession',
            name='run',
            field=models.ForeignKey(blank=True, help_text='Which evaluation run this session belongs to.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to='surveys.evaluationrun'),
        ),
        migrations.AddField(
            model_name='runprogress',
            name='run',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='progress_rows', to='surveys.evaluationrun'),
        ),
    ]
