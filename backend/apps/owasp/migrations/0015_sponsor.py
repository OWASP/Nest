# Generated by Django 5.1.5 on 2025-01-28 11:40

from django.db import migrations, models

import apps.owasp.models.mixins.sponsor


class Migration(migrations.Migration):
    dependencies = [
        ("owasp", "0014_project_custom_tags"),
    ]

    operations = [
        migrations.CreateModel(
            name="Sponsor",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("nest_created_at", models.DateTimeField(auto_now_add=True)),
                ("nest_updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255, verbose_name="Name")),
                ("sort_name", models.CharField(max_length=255, verbose_name="Sort Name")),
                ("description", models.TextField(blank=True, verbose_name="Description")),
                ("url", models.URLField(blank=True, verbose_name="Website URL")),
                ("job_url", models.URLField(blank=True, verbose_name="Job URL")),
                (
                    "image_path",
                    models.CharField(blank=True, max_length=255, verbose_name="Image Path"),
                ),
                (
                    "is_member",
                    models.BooleanField(default=False, verbose_name="Is Corporate Sponsor"),
                ),
                (
                    "member_type",
                    models.CharField(
                        blank=True,
                        choices=[("2", "Platinum"), ("3", "Gold"), ("4", "Silver")],
                        default="4",
                        max_length=2,
                        verbose_name="Member Type",
                    ),
                ),
                (
                    "sponsor_type",
                    models.CharField(
                        choices=[
                            ("1", "Diamond"),
                            ("2", "Platinum"),
                            ("3", "Gold"),
                            ("4", "Silver"),
                            ("5", "Supporter"),
                            ("-1", "Not a Sponsor"),
                        ],
                        default="-1",
                        max_length=2,
                        verbose_name="Sponsor Type",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Sponsors",
                "db_table": "owasp_sponsors",
            },
            bases=(apps.owasp.models.mixins.sponsor.SponsorIndexMixin, models.Model),
        ),
    ]
