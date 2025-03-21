# Generated by Django 5.1.7 on 2025-03-18 14:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("owasp", "0029_alter_project_custom_tags"),
    ]

    operations = [
        migrations.AddField(
            model_name="chapter",
            name="is_leaders_policy_compliant",
            field=models.BooleanField(default=True, verbose_name="Is leaders policy compliant"),
        ),
        migrations.AddField(
            model_name="committee",
            name="is_leaders_policy_compliant",
            field=models.BooleanField(default=True, verbose_name="Is leaders policy compliant"),
        ),
        migrations.AddField(
            model_name="project",
            name="is_leaders_policy_compliant",
            field=models.BooleanField(default=True, verbose_name="Is leaders policy compliant"),
        ),
    ]
