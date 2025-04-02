"""Slack bot news command."""

from django.conf import settings

from apps.common.constants import NL, OWASP_NEWS_URL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.template_system.loader import env
from apps.slack.utils import get_news_data, get_text

COMMAND = "/news"


def news_handler(ack, command, client):
    """Handle the Slack /news command.

    Args:
        ack (function): Acknowledge the Slack command request.
        command (dict): The Slack command payload.
        client (slack_sdk.WebClient): The Slack WebClient instance for API calls.

    """
    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    template = env.get_template("news.txt")
    items = get_news_data()
    if items:
        rendered_text = template.render(
            has_news=True,
            news_items=items,
            news_url=OWASP_NEWS_URL,
            SECTION_BREAK="{{ SECTION_BREAK }}",
            DIVIDER="{{ DIVIDER }}",
            NL=NL,
        )
        blocks = []
        for section in rendered_text.split("{{ SECTION_BREAK }}"):
            cleaned_section = section.strip()
            if cleaned_section == "{{ DIVIDER }}":
                blocks.append({"type": "divider"})
            elif cleaned_section:
                blocks.append(markdown(cleaned_section))
    else:
        rendered_text = template.render(has_news=False, NL=NL)
        blocks = [markdown(rendered_text.strip())]

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(
        blocks=blocks,
        channel=conversation["channel"]["id"],
        text=get_text(blocks),
    )


if SlackConfig.app:
    news_handler = SlackConfig.app.command(COMMAND)(news_handler)
