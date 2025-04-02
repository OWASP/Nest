"""Slack bot events command."""

from django.conf import settings

from apps.common.constants import NL, OWASP_WEBSITE_URL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.template_system.loader import env
from apps.slack.utils import get_events_data, get_text

COMMAND = "/events"


def events_handler(ack, command, client):
    """Slack /events command handler.

    Args:
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
            categorized_events[category] = {"events": []}
        categorized_events[category]["events"].append(
            {
                "name": event.name,
                "url": event.url,
                "start_date": event.start_date,
                "end_date": event.end_date,
                "description": event.description,
            }
        )

    frame_template = env.get_template("events_frame.txt")
    event_item_template = env.get_template("event_item.txt")

    blocks = []

    rendered_main_header = frame_template.render(render_type="main")
    blocks.append(markdown(rendered_main_header.strip()))
    blocks.append({"type": "divider"})

    for category, category_data in categorized_events.items():
        rendered_category_header = frame_template.render(render_type="category", category=category)
        blocks.append(markdown(rendered_category_header.strip()))

        for idx, event in enumerate(category_data["events"], 1):
            rendered_text = event_item_template.render(idx=idx, event=event, NL=NL)
            blocks.append(markdown(rendered_text.strip()))

        blocks.append({"type": "divider"})

    rendered_footer = frame_template.render(
        render_type="footer", website_url=OWASP_WEBSITE_URL, NL=NL
    )
    blocks.append(markdown(rendered_footer.strip()))

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(
        blocks=blocks,
        channel=conversation["channel"]["id"],
        text=get_text(blocks),
    )


if SlackConfig.app:
    events_handler = SlackConfig.app.command(COMMAND)(events_handler)
