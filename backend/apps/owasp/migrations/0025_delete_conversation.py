# Generated by Django 5.1.7 on 2025-03-08 19:24

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("owasp", "0024_remove_conversation_updated_at_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Conversation",
        ),
    ]
