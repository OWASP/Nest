from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("slack", "0033_share_report_type_choices"),
    ]

    operations = [
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
    ]
