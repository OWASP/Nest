"""Slack bot sponsors command."""

import logging
from urllib.parse import urlparse

from dateutil.parser import parse as date_parse
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.common.constants import NL
from apps.slack.apps import SlackConfig
from apps.slack.utils import get_text

logger = logging.getLogger(__name__)

COMMAND = "/sponsor"

COMMAND_FORMAT_ERROR = (
    "Invalid command format. Usage: `/sponsor task add <issue_link> <amount>[EUR|USD] [deadline]`"
)
DEADLINE_FORMAT_ERROR = "Invalid deadline format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM."
INVALID_ISSUE_LINK_FORMAT = "Invalid GitHub issue link format."
DATE_INDEX = 4
MIN_PARTS_LENGTH = 4
TIME_INDEX = 5


def sponsor_handler(ack, command, client):
    """Slack /sponsor command handler."""
    from apps.github.common import sync_issue
    from apps.nest.models.sponsorship import Sponsorship

    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    text = command.get("text", "")
    if text.startswith("task add"):
        try:
            parts = text.split()
            if len(parts) < MIN_PARTS_LENGTH:
                logger.error(COMMAND_FORMAT_ERROR)
                return

            issue_link = parts[2]
            price_input = parts[3]

            currency = Sponsorship.CurrencyType.USD
            price = price_input

            if price_input.endswith("EUR"):
                currency = "EUR"
                price = price_input[:-3]
            elif price_input.endswith("USD"):
                currency = "USD"
                price = price_input[:-3]

            parsed_url = urlparse(issue_link)
            path_parts = parsed_url.path.strip("/").split("/")
            if len(path_parts) < MIN_PARTS_LENGTH or path_parts[2] != "issues":
                logger.error("Invalid GitHub issue link format")
                return

            deadline = None
            if len(parts) > DATE_INDEX:
                deadline_str = " ".join(parts[DATE_INDEX:])
                try:
                    deadline = date_parse(deadline_str).replace(
                        tzinfo=timezone.get_current_timezone()
                    )
                except ValueError as e:
                    raise ValidationError(DEADLINE_FORMAT_ERROR) from e

            with transaction.atomic():
                issue = sync_issue(issue_link)
                sponsorship, created = Sponsorship.objects.get_or_create(
                    issue=issue,
                    defaults={
                        "amount": price,
                        "currency": currency,
                        "deadline_at": deadline,
                        "slack_user_id": command["user_id"],
                    },
                )

                if not created:
                    sponsorship.amount = price
                    sponsorship.currency = currency
                    sponsorship.deadline_at = deadline
                    sponsorship.slack_user_id = command["user_id"]
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
            f"*Usage:* `/sponsor task add <issue_link> <amount>[EUR|USD] [deadline]`{NL}"
            f"Example: `/sponsor task add https://github.com/ORG/Repo/issues/XYZ "
            f"100USD 2025-12-31`{NL}"
            f"Example with EUR: `/sponsor task add https://github.com/ORG/Repo/issues/XYZ "
            f"100EUR 2025-12-31`{NL}"
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
    currency_symbol = "€" if sponsorship.currency == "EUR" else "$"
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"🎉 *Sponsorship created successfully!* 🎉{NL}"
                f"*Issue:* {sponsorship.issue.title}{NL}"
                f"*Price:* {currency_symbol}{sponsorship.amount} ({sponsorship.currency}){NL}"
                f"*Created by:* <@{sponsorship.slack_user_id}>{NL}",
            },
        }
    ]
    if sponsorship.deadline_at:
        blocks[0]["text"]["text"] += (
            f"*Deadline:* {sponsorship.deadline_at.strftime('%Y-%m-%d %H:%M')}{NL}"
        )
    return blocks
