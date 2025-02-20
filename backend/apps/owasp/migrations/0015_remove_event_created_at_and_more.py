# Generated by Django 5.1.5 on 2025-02-20 16:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("owasp", "0014_project_custom_tags"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="event",
            name="created_at",
        ),
        migrations.RemoveField(
            model_name="event",
            name="has_active_repositories",
        ),
        migrations.RemoveField(
            model_name="event",
            name="is_active",
        ),
        migrations.RemoveField(
            model_name="event",
            name="level",
        ),
        migrations.RemoveField(
            model_name="event",
            name="owasp_repository",
        ),
        migrations.RemoveField(
            model_name="event",
            name="summary",
        ),
        migrations.RemoveField(
            model_name="event",
            name="tags",
        ),
        migrations.RemoveField(
            model_name="event",
            name="topics",
        ),
        migrations.RemoveField(
            model_name="event",
            name="updated_at",
        ),
        migrations.AddField(
            model_name="event",
            name="category",
            field=models.CharField(
                choices=[
                    ("global", "Global"),
                    ("appsec_days", "AppSec Days"),
                    ("partner", "Partner"),
                    ("other", "Other"),
                ],
                default="other",
                max_length=20,
                verbose_name="Category",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="category_description",
            field=models.TextField(blank=True, default="", verbose_name="Category Description"),
        ),
        migrations.AddField(
            model_name="event",
            name="end_date",
            field=models.DateField(blank=True, null=True, verbose_name="End Date"),
        ),
        migrations.AddField(
            model_name="event",
            name="start_date",
            field=models.DateField(blank=True, default="2025-01-01", verbose_name="Start Date"),
        ),
        migrations.AlterField(
            model_name="event",
            name="description",
            field=models.TextField(blank=True, default="", verbose_name="Description"),
        ),
    ]
