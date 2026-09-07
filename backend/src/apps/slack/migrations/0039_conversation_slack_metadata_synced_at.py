from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("slack", "0038_report_type_spam_only"),
    ]

    operations = [
        migrations.AddField(
            model_name="conversation",
            name="slack_metadata_synced_at",
            field=models.DateTimeField(
                blank=True,
                help_text="When privacy and channel flags were last loaded from Slack.",
                null=True,
                verbose_name="Slack metadata synced at",
            ),
        ),
    ]
