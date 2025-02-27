"""Slack bot sponsors command."""

import logging

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction

from apps.common.constants import NL
from apps.slack.apps import SlackConfig
from apps.slack.utils import (
    get_or_create_issue,
    get_text,
    validate_deadline,
    validate_github_issue_link,
    validate_price,
)

logger = logging.getLogger(__name__)

COMMAND = "/sponsor"

COMMAND_FORMAT_ERROR = (
    "Invalid command format. Usage: `/sponsor task add <issue_link> <price_usd> [deadline]`"
)
DATE_INDEX = 4
MIN_PARTS_LENGTH = 4
TIME_INDEX = 5


def sponsor_handler(ack, command, client):
    """Slack /sponsor command handler."""
    from apps.nest.models.sponsorship import Sponsorship

    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    def validate_command_format(parts):
        if len(parts) < MIN_PARTS_LENGTH:
            raise ValidationError(COMMAND_FORMAT_ERROR)

    text = command.get("text", "")
    if text.startswith("task add"):
        try:
            parts = text.split()
            validate_command_format(parts)

            issue_link = parts[2]
            price = parts[3]

            deadline_str = None
            if len(parts) > DATE_INDEX:
                deadline_str = parts[DATE_INDEX]
                if len(parts) > TIME_INDEX:
                    deadline_str += " " + parts[TIME_INDEX]

            validate_github_issue_link(issue_link)
            validated_price = validate_price(price)
            deadline = validate_deadline(deadline_str) if deadline_str else None

            with transaction.atomic():
                issue = get_or_create_issue(issue_link)
                sponsorship, created = Sponsorship.objects.get_or_create(
                    issue=issue,
                    defaults={
                        "price_usd": validated_price,
                        "slack_user_id": command["user_id"],
                        "deadline_at": deadline,
                    },
                )

                if not created:
                    sponsorship.price_usd = validated_price
                    sponsorship.slack_user_id = command["user_id"]
                    sponsorship.deadline_at = deadline
                    sponsorship.save()

            blocks = get_sponsorship_blocks(sponsorship)
        except ValidationError as e:
            logger.exception("Validation error")
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"❌ *Error:* {e!s}{NL}",
                    },
                }
            ]
        except Exception:
            logger.exception("Validation error")
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            f"❌ *Error:* An error occurred while processing your request.{NL}"
                        ),
                    },
                }
            ]
    else:
        usage_text = (
            f"*Usage:* `/sponsor task add <issue_link> <price_usd> [deadline]`{NL}"
            f"Example: `/sponsor task add https://github.com/ORG/Repo/issues/XYZ"
            f"100 2025-12-31`{NL}"
            f"Example with time: `/sponsor task add https://github.com/ORG/Repo/"
            f"issues/XYZ 100 2025-12-31 23:59`"
        )
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": usage_text,
                },
            }
        ]

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(
        blocks=blocks,
        channel=conversation["channel"]["id"],
        text=get_text(blocks),
    )


if SlackConfig.app:
    sponsor_handler = SlackConfig.app.command(COMMAND)(sponsor_handler)


def get_sponsorship_blocks(sponsorship):
    """Generate Slack blocks for the sponsorship confirmation message."""
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"🎉 *Sponsorship created successfully!* 🎉{NL}"
                f"*Issue:* {sponsorship.issue.title}{NL}"
                f"*Price:* ${sponsorship.price_usd}{NL}"
                f"*Created by:* <@{sponsorship.slack_user_id}>{NL}",
            },
        }
    ]
    if sponsorship.deadline_at:
        blocks[0]["text"]["text"] += (
            f"*Deadline:* {sponsorship.deadline_at.strftime('%Y-%m-%d %H:%M')}{NL}"
        )
    return blocks
