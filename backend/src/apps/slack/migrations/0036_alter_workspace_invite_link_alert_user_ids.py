from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("slack", "0035_expand_report_type_choices"),
    ]

    operations = [
        migrations.AlterField(
            model_name="workspace",
            name="invite_link_alert_user_ids",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text=(
                    'Optional JSON list of Slack user IDs (e.g. ["U01ABC..."]). '
                    "A trailing cc: line with <@mentions> is added to invite-limit alerts."
                ),
                null=True,
                verbose_name="Invite alert Slack user IDs to mention",
            ),
        ),
    ]
