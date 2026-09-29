from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('assessments', '0005_diagnosticquestion_source_id')]
    operations = [
        migrations.AddField(model_name='submission', name='request_id', field=models.UUIDField(blank=True, null=True)),
        migrations.AddField(model_name='submission', name='evaluation', field=models.JSONField(blank=True, default=dict)),
        migrations.AddConstraint(model_name='submission', constraint=models.UniqueConstraint(fields=('user', 'request_id'), name='unique_submission_request')),
    ]
