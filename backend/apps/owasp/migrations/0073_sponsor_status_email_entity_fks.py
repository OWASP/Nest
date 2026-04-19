# Generated manually for sponsor status, email, and entity FK fields.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("owasp", "0072_project_project_name_gin_idx_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="sponsor",
            name="status",
            field=models.CharField(
                choices=[
                    ("draft", "Draft"),
                    ("active", "Active"),
                    ("archived", "Archived"),
                ],
                default="active",
                max_length=20,
                verbose_name="Status",
            ),
        ),
        migrations.AddField(
            model_name="sponsor",
            name="contact_email",
            field=models.EmailField(
                blank=True,
                default="",
                max_length=254,
                verbose_name="Contact Email",
            ),
        ),
        migrations.AddField(
            model_name="sponsor",
            name="chapter",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="sponsors",
                to="owasp.chapter",
                verbose_name="Chapter",
            ),
        ),
        migrations.AddField(
            model_name="sponsor",
            name="project",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="sponsors",
                to="owasp.project",
                verbose_name="Project",
            ),
        ),
    ]
