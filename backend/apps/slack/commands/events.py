"""Slack bot events command."""

from django.conf import settings

from apps.common.constants import NL, OWASP_WEBSITE_URL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.utils import get_events_data, get_text

COMMAND = "/events"


def events_handler(ack, command, client):
    """Slack /events command handler."""
    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    events_data = get_events_data()

    valid_events = [event for event in events_data if event.get("startDate")]
    sorted_events = sorted(valid_events, key=lambda x: x["startDate"])

    categorized_events = {}
    for event in sorted_events:
        category = event.get("category") or "Other"
        if category not in categorized_events:
            categorized_events[category] = {
                "description": event.get("categoryDescription", ""),
                "events": [],
            }
        categorized_events[category]["events"].append(event)

    blocks = []
    blocks.append(markdown("*Upcoming OWASP Events:*"))
    blocks.append({"type": "divider"})

    for category, category_data in categorized_events.items():
        blocks.append(markdown(f"*{category} Events:*{NL}{category_data['description']}{NL}"))

        for idx, event in enumerate(category_data["events"], 1):
            if event.get("url"):
                block_text = f"*{idx}. <{event['url']}|{event['name']}>*{NL}"
            else:
                block_text = f"*{idx}. {event['name']}*{NL}"

            if event.get("startDate"):
                block_text += f" Start Date: {event['startDate']}{NL}"

            if event.get("endDate"):
                block_text += f" End Date: {event['endDate']}{NL}"

            if event.get("description"):
                block_text += f"_{event['description']}_{NL}"

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
