# Generated by Django 5.1.1 on 2024-10-05 21:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("owasp", "0008_chapter_description_chapter_has_active_repositories_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="chapter",
            name="created_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Created at"),
        ),
        migrations.AddField(
            model_name="chapter",
            name="updated_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Updated at"),
        ),
        migrations.AddField(
            model_name="committee",
            name="created_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Created at"),
        ),
        migrations.AddField(
            model_name="committee",
            name="updated_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Updated at"),
        ),
        migrations.AddField(
            model_name="event",
            name="created_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Created at"),
        ),
        migrations.AddField(
            model_name="event",
            name="updated_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Updated at"),
        ),
    ]
