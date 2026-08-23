from django.db import migrations, models


def replace_null_channel_ids(apps, schema_editor):
    """Replace NULL content_report_alert_channel_id values with empty strings."""
    workspace = apps.get_model("slack", "Workspace")
    workspace.objects.filter(content_report_alert_channel_id__isnull=True).update(
        content_report_alert_channel_id="",
    )


class Migration(migrations.Migration):
    dependencies = [
        ("slack", "0035_expand_report_type_choices"),
    ]

    operations = [
        migrations.RunPython(replace_null_channel_ids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="workspace",
            name="content_report_alert_channel_id",
            field=models.CharField(
                blank=True,
                default="",
                help_text=(
                    "Slack channel ID for content reports (e.g. C..., without #); "
                    "empty disables content reporting."
                ),
                max_length=32,
                verbose_name="Content report alert channel ID",
            ),
        ),
    ]
