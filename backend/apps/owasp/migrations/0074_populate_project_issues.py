"""Backfill Project.issues M2M field for existing projects."""

from django.db import migrations


def populate_project_issues(apps, schema_editor):
    """Populate issues M2M field for all projects."""
    db_alias = schema_editor.connection.alias
    Project = apps.get_model("owasp", "Project")
    Issue = apps.get_model("github", "Issue")

    for project in Project.objects.using(db_alias).iterator():
        repository_ids = project.repositories.values_list("id", flat=True)
        issues = Issue.objects.using(db_alias).filter(repository_id__in=list(repository_ids))
        project.issues.set(issues)


def reverse_populate_project_issues(apps, schema_editor):
    """Clear issues M2M field for all projects."""
    db_alias = schema_editor.connection.alias
    Project = apps.get_model("owasp", "Project")

    for project in Project.objects.using(db_alias).iterator():
        project.issues.clear()


class Migration(migrations.Migration):
    dependencies = [
        ("owasp", "0073_project_issues"),
    ]

    operations = [
        migrations.RunPython(
            populate_project_issues,
            reverse_populate_project_issues,
        ),
    ]
