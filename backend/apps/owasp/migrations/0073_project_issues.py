# Generated migration to add issues M2M field to Project

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("github", "0040_merge_20251117_0136"),
        ("owasp", "0072_project_project_name_gin_idx_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="issues",
            field=models.ManyToManyField(
                blank=True,
                to="github.Issue",
                verbose_name="Issues",
            ),
        ),
    ]
