# Generated migration

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("owasp", "0060_membersnapshot_chapter_project_contributions"),
    ]

    operations = [
        migrations.AddField(
            model_name="membersnapshot",
            name="repository_contributions",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="Top 5 repositories by commit count (repo_name -> count mapping)",
                verbose_name="Repository Contributions",
            ),
        ),
    ]
