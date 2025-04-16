# Generated by Django 5.2 on 2025-04-14 07:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("github", "0020_repositorycontributor_user_contrib_idx"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="release",
            index=models.Index(fields=["-published_at"], name="release_published_at_desc_idx"),
        ),
    ]
