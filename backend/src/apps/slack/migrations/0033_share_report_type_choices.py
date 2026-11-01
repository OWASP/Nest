from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("slack", "0032_contentreport_and_workspace_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contentreport",
            name="report_type",
            field=models.CharField(
                choices=[("spam", "Spam")],
                default="spam",
                help_text="Report category for the emitted content report.",
                max_length=64,
            ),
        ),
        migrations.AlterField(
            model_name="reactionrule",
            name="report_type",
            field=models.CharField(
                choices=[("spam", "Spam")],
                default="spam",
                help_text="Report category recorded when this reaction rule triggers.",
                max_length=64,
            ),
        ),
    ]
