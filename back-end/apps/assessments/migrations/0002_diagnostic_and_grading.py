import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0001_initial'),
        ('careers', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='evaluation_mode',
            field=models.CharField(
                choices=[('rules', 'Rule-based'), ('ai', 'AI-assisted')],
                default='rules',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='assessment',
            name='grading_config',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text=(
                    "Private server-side grading configuration. For quizzes, use "
                    "{'answer_key': {'question_id': 'answer'}}. Never expose this field publicly."
                ),
            ),
        ),
        migrations.CreateModel(
            name='DiagnosticQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('prompt', models.TextField()),
                ('options', models.JSONField(default=list, help_text='Public answer choices, preferably a list of {value, label} objects.')),
                ('correct_answer', models.CharField(max_length=255)),
                ('explanation', models.TextField(blank=True, default='')),
                ('order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('career_track', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='diagnostic_questions', to='careers.careertrack')),
                ('skill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='diagnostic_questions', to='skills.skill')),
            ],
            options={
                'db_table': 'diagnostic_questions',
                'ordering': ['order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='DiagnosticAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('answers', models.JSONField(default=dict)),
                ('skill_scores', models.JSONField(default=list)),
                ('weak_skill_ids', models.JSONField(default=list)),
                ('overall_score', models.FloatField(default=0.0)),
                ('completed_at', models.DateTimeField()),
                ('career_track', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='diagnostic_attempts', to='careers.careertrack')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='diagnostic_attempts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'diagnostic_attempts',
                'ordering': ['-completed_at', '-created_at'],
            },
        ),
    ]
