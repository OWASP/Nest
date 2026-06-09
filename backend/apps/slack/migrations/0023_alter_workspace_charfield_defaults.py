from django.db import migrations, models

CHAR_FIELDS = (
    "invite_link_alert_channel_id",
    "invite_link_alert_message_ts",
    "invite_link_commit_sha",
)


def null_charfields_to_empty_string(apps, schema_editor):
    workspace_model = apps.get_model("slack", "Workspace")
    for field_name in CHAR_FIELDS:
        workspace_model.objects.filter(**{f"{field_name}__isnull": True}).update(
            **{field_name: ""}
        )


class Migration(migrations.Migration):
    dependencies = [
        ("slack", "0022_workspace_invite_link_alert_message_ts"),
    ]

    operations = [
        migrations.RunPython(
            null_charfields_to_empty_string,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="workspace",
            name="invite_link_alert_channel_id",
            field=models.CharField(
                blank=True,
                default="",
                help_text=(
                    "Slack channel ID for invite-limit alerts (e.g. C…); empty skips posting. "
                    "Used by slack_check_invite_link when posting warnings."
                ),
                max_length=32,
                verbose_name="Invite link alert channel ID",
            ),
        ),
        migrations.AlterField(
            model_name="workspace",
            name="invite_link_alert_message_ts",
            field=models.CharField(
                blank=True,
                default="",
                help_text=(
                    "Slack message timestamp (ts) of the last invite-limit alert. "
                    "Used to post a threaded resolution reply when the invite link is updated."
                ),
                max_length=32,
                verbose_name="Invite link alert message timestamp",
            ),
        ),
        migrations.AlterField(
            model_name="workspace",
            name="invite_link_commit_sha",
            field=models.CharField(
                blank=True,
                default="",
                help_text=(
                    "Full Git SHA of the latest matching commit for _includes/slack_invite.html "
                    "(used to link to the commit on GitHub)."
                ),
                max_length=40,
                verbose_name="Public invite link commit SHA",
            ),
        ),
    ]
