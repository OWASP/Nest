"""Slack bot events command."""

from django.conf import settings

from apps.common.constants import NL, OWASP_WEBSITE_URL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.utils import get_events_data

COMMAND = "/events"


def events_handler(ack, command, client):
    """Slack /events command handler."""
    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    events_data = get_events_data()

    blocks = []

    blocks.append(markdown("*Upcoming OWASP Events: *"))
    blocks.append({"type": "divider"})

    for category_data in events_data:
        blocks.append(
            markdown(
                f"*{category_data['category']} Events:*{NL}{category_data['description']}{NL}"
            )
        )
        stored_events = sorted(
            category_data["events"],
            key=lambda x: x["start-date"],
        )

        for idx, events in enumerate(stored_events, 1):
            blocks.append(format_event_block(events, idx))

        blocks.append({"type": "divider"})

    blocks.append(
        markdown(
            f"🔍 For more information about upcoming events, "
            f"Please visit <{OWASP_WEBSITE_URL}/events/|OWASP Events>{NL}"
        )
    )

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(channel=conversation["channel"]["id"], blocks=blocks)


def format_event_block(event, idx):
    """Format a single event into a Slack message block."""
    block_text = f"*{idx}. {event['name']}*{NL}"
    block_text += f"{event['dates']}{NL}"

    if event.get("url"):
        block_text += f"🔗 <{event['url']}|More Information>{NL}"

    if event.get("optional-text"):
        block_text += f"_{event['optional-text']}_{NL}"

    return markdown(block_text)


if SlackConfig.app:
    events_handler = SlackConfig.app.command(COMMAND)(events_handler)
