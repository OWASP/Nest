# Generated by Django 5.1.6 on 2025-02-22 18:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("github", "0015_alter_release_author"),
        ("owasp", "0014_project_custom_tags"),
    ]

    operations = [
        migrations.CreateModel(
            name="Snapshot",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("start_at", models.DateTimeField()),
                ("end_at", models.DateTimeField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("processing", "Processing"),
                            ("completed", "Completed"),
                            ("error", "Error"),
                        ],
                        default="pending",
                        max_length=10,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("error_message", models.TextField(blank=True, default="")),
                (
                    "new_chapters",
                    models.ManyToManyField(
                        blank=True, related_name="snapshots", to="owasp.chapter"
                    ),
                ),
                (
                    "new_issues",
                    models.ManyToManyField(
                        blank=True, related_name="snapshots", to="github.issue"
                    ),
                ),
                (
                    "new_projects",
                    models.ManyToManyField(
                        blank=True, related_name="snapshots", to="owasp.project"
                    ),
                ),
                (
                    "new_releases",
                    models.ManyToManyField(
                        blank=True, related_name="snapshots", to="github.release"
                    ),
                ),
                (
                    "new_users",
                    models.ManyToManyField(blank=True, related_name="snapshots", to="github.user"),
                ),
            ],
            options={
                "verbose_name_plural": "Snapshots",
                "db_table": "owasp_snapshots",
            },
        ),
    ]
