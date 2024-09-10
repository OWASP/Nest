# Generated by Django 5.1.1 on 2024-09-07 02:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("github", "0040_alter_issue_options_alter_issue_url"),
    ]

    operations = [
        migrations.AlterField(
            model_name="issue",
            name="repository",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="issues",
                to="github.repository",
            ),
        ),
    ]