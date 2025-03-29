"""Slack bot news command."""

from django.conf import settings

from apps.common.constants import NL, OWASP_NEWS_URL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import divider, markdown
from apps.slack.utils import get_news_data, get_text

COMMAND = "/news"


def news_handler(ack, command, client):
    """Handle the Slack /news command.

    Args:
    ----
        ack (function): Acknowledge the Slack command request.
        command (dict): The Slack command payload.
        client (slack_sdk.WebClient): The Slack WebClient instance for API calls.

    """
    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    items = get_news_data()
    if items:
        blocks = [markdown(f"*:newspaper: Latest OWASP news:*{NL}")]
        blocks += [
            markdown(f"  • *<{item['url']}|{item['title']}>* by {item['author']}")
            for item in items
        ]
        blocks += [
            divider(),
            markdown(f"Please visit <{OWASP_NEWS_URL}|OWASP news> page for more information.{NL}"),
        ]
    else:
        blocks = [markdown(":warning: *Failed to fetch OWASP news. Please try again later.*")]

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(
        blocks=blocks,
        channel=conversation["channel"]["id"],
        text=get_text(blocks),
    )


if SlackConfig.app:
    news_handler = SlackConfig.app.command(COMMAND)(news_handler)
