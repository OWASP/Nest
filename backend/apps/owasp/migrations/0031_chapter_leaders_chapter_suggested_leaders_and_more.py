# Generated by Django 5.1.7 on 2025-03-23 13:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("github", "0018_alter_issue_managers_alter_pullrequest_managers"),
        ("owasp", "0030_chapter_is_leaders_policy_compliant_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="chapter",
            name="leaders",
            field=models.ManyToManyField(
                blank=True,
                related_name="assigned_%(class)s",
                to="github.user",
                verbose_name="Assigned leaders",
            ),
        ),
        migrations.AddField(
            model_name="chapter",
            name="suggested_leaders",
            field=models.ManyToManyField(
                blank=True,
                related_name="matched_%(class)s",
                to="github.user",
                verbose_name="Matched Users",
            ),
        ),
        migrations.AddField(
            model_name="committee",
            name="leaders",
            field=models.ManyToManyField(
                blank=True,
                related_name="assigned_%(class)s",
                to="github.user",
                verbose_name="Assigned leaders",
            ),
        ),
        migrations.AddField(
            model_name="committee",
            name="suggested_leaders",
            field=models.ManyToManyField(
                blank=True,
                related_name="matched_%(class)s",
                to="github.user",
                verbose_name="Matched Users",
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="leaders",
            field=models.ManyToManyField(
                blank=True,
                related_name="assigned_%(class)s",
                to="github.user",
                verbose_name="Assigned leaders",
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="suggested_leaders",
            field=models.ManyToManyField(
                blank=True,
                related_name="matched_%(class)s",
                to="github.user",
                verbose_name="Matched Users",
            ),
        ),
    ]
