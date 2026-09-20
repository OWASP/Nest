from django.db import migrations, models
from django.db.models import Count, Min


def remove_duplicate_content_reports(apps, schema_editor):
    """Keep one ContentReport per conversation/message_ts before unique constraint."""
    content_report = apps.get_model("slack", "ContentReport")
    duplicates = (
        content_report.objects.values("conversation_id", "message_ts")
        .annotate(row_count=Count("id"), keep_id=Min("id"))
        .filter(row_count__gt=1)
    )
    for row in duplicates:
        content_report.objects.filter(
            conversation_id=row["conversation_id"],
            message_ts=row["message_ts"],
        ).exclude(id=row["keep_id"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("slack", "0031_reactionrule_unique_conversation_report_type"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="ReactionAlert",
            new_name="ContentReport",
        ),
        migrations.AlterModelTable(
            name="contentreport",
            table="slack_content_reports",
        ),
        migrations.AlterUniqueTogether(
            name="contentreport",
            unique_together=set(),
        ),
        migrations.AddField(
            model_name="contentreport",
            name="source",
            field=models.CharField(
                choices=[("emoji", "Emoji"), ("shortcut", "Shortcut")],
                default="emoji",
                help_text="Whether this report came from emoji reactions or a message shortcut.",
                max_length=32,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="contentreport",
            name="message",
            field=models.ForeignKey(
                blank=True,
                help_text="Stored Slack message when available (required for shortcut reports).",
                null=True,
                on_delete=models.deletion.SET_NULL,
                related_name="content_reports",
                to="slack.message",
            ),
        ),
        migrations.AlterField(
            model_name="contentreport",
            name="alert_message_ts",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Slack timestamp of the posted moderation alert message.",
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="contentreport",
            name="message_ts",
            field=models.CharField(
                help_text="Slack timestamp of the reported message.",
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="contentreport",
            name="reaction_count",
            field=models.PositiveSmallIntegerField(
                blank=True,
                help_text="Unique emoji reporters at alert time; null for shortcut reports.",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="contentreport",
            name="report_type",
            field=models.CharField(
                help_text="Report category for the emitted content report.",
                max_length=64,
            ),
        ),
        migrations.AlterField(
            model_name="contentreport",
            name="reporter_user_ids",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="Slack user IDs that triggered this content report.",
            ),
        ),
        migrations.RunPython(remove_duplicate_content_reports, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="contentreport",
            constraint=models.UniqueConstraint(
                fields=("conversation", "message_ts"),
                name="unique_contentreport_conversation_message_ts",
                violation_error_message=(
                    "A content report already exists for this conversation and message."
                ),
            ),
        ),
        migrations.AddField(
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
                null=True,
                verbose_name="Content report alert channel ID",
            ),
        ),
        migrations.AddField(
            model_name="workspace",
            name="content_report_alert_user_ids",
            field=models.JSONField(
                blank=True,
                default=None,
                help_text=(
                    'Optional JSON list of Slack user IDs (e.g. ["U01ABC..."]) '
                    "mentioned on content-report alerts."
                ),
                null=True,
                verbose_name="Content report Slack user IDs to mention",
            ),
        ),
    ]
