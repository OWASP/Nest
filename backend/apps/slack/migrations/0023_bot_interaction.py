# Generated migration for BotInteraction model

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("slack", "0022_workspace_invite_link_last_alert_message_ts_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="BotInteraction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nest_created_at", models.DateTimeField(auto_now_add=True)),
                ("nest_updated_at", models.DateTimeField(auto_now=True)),
                (
                    "channel_id",
                    models.CharField(max_length=64, verbose_name="Channel ID"),
                ),
                (
                    "user_id",
                    models.CharField(max_length=64, verbose_name="User ID"),
                ),
                ("user_message", models.TextField(verbose_name="User message")),
                ("bot_response", models.TextField(verbose_name="Bot response")),
                (
                    "intent_category",
                    models.CharField(
                        blank=True,
                        default="",
                        max_length=64,
                        verbose_name="Intent category",
                    ),
                ),
                (
                    "confidence_score",
                    models.FloatField(
                        blank=True, null=True, verbose_name="Confidence score"
                    ),
                ),
                (
                    "thumbs_up",
                    models.BooleanField(
                        blank=True,
                        help_text="True = 👍, False = 👎, None = no reaction yet.",
                        null=True,
                        verbose_name="Thumbs up",
                    ),
                ),
                (
                    "tokens_used",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Tokens used"
                    ),
                ),
                (
                    "slack_reply_ts",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Slack message ts of the bot reply. Used to match reaction_added events.",
                        max_length=32,
                        verbose_name="Slack reply timestamp",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Bot Interactions",
                "db_table": "slack_bot_interactions",
            },
        ),
    ]