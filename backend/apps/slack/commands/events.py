"""Slack bot events command."""

from django.conf import settings

from apps.common.constants import NL, OWASP_WEBSITE_URL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.utils import get_events_data, get_text

COMMAND = "/events"


def events_handler(ack, command, client):
    """Slack /events command handler.

    Args:
    ----
        ack (function): Function to acknowledge the Slack command.
        command (dict): The Slack command payload.
        client (SlackClient): The Slack client instance for sending messages.

    """
    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    events_data = get_events_data()

    valid_events = [event for event in events_data if event.start_date]
    sorted_events = sorted(valid_events, key=lambda x: x.start_date)

    categorized_events = {}
    for event in sorted_events:
        category = event.category or "Other"
        if category not in categorized_events:
            categorized_events[category] = {
                "events": [],
            }
        categorized_events[category]["events"].append(event)

    blocks = []
    blocks.append(markdown("*Upcoming OWASP Events:*"))
    blocks.append({"type": "divider"})

    for category, category_data in categorized_events.items():
        blocks.append(markdown(f"*Category: {category.replace('_', ' ').title()}*"))

        for idx, event in enumerate(category_data["events"], 1):
            if event.url:
                block_text = f"*{idx}. <{event.url}|{event.name}>*{NL}"
            else:
                block_text = f"*{idx}. {event.name}*{NL}"

            block_text += f" Start Date: {event.start_date}{NL}"

            if event.end_date:
                block_text += f" End Date: {event.end_date}{NL}"

            if event.description:
                block_text += f"_{event.description}_{NL}"

            blocks.append(markdown(block_text))

        blocks.append({"type": "divider"})

    blocks.append(
        markdown(
            f"🔍 For more information about upcoming events, "
            f"please visit <{OWASP_WEBSITE_URL}/events/|OWASP Events>{NL}"
        )
    )

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(
        blocks=blocks,
        channel=conversation["channel"]["id"],
        text=get_text(blocks),
    )


if SlackConfig.app:
    events_handler = SlackConfig.app.command(COMMAND)(events_handler)
