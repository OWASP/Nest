from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("slack", "0034_contentreport_source_command"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contentreport",
            name="report_type",
            field=models.CharField(
                choices=[
                    ("harassment", "Harassment"),
                    ("off_topic", "Off-topic"),
                    ("other", "Other"),
                    ("spam", "Spam"),
                ],
                default="spam",
                help_text="Report category for the emitted content report.",
                max_length=64,
            ),
        ),
        migrations.AlterField(
            model_name="contentreport",
            name="source",
            field=models.CharField(
                choices=[
                    ("command", "Command"),
                    ("emoji", "Emoji"),
                    ("shortcut", "Shortcut"),
                ],
                help_text="Whether this report came from emoji, a message shortcut, or /report.",
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="reactionrule",
            name="report_type",
            field=models.CharField(
                choices=[
                    ("harassment", "Harassment"),
                    ("off_topic", "Off-topic"),
                    ("other", "Other"),
                    ("spam", "Spam"),
                ],
                default="spam",
                help_text="Report category recorded when this reaction rule triggers.",
                max_length=64,
            ),
        ),
    ]
