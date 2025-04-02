"""Slack bot policies command."""

from django.conf import settings

from apps.common.constants import NL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.template_system.loader import env
from apps.slack.utils import get_text

COMMAND = "/policies"


def policies_handler(ack, command, client):
    """Handle the Slack /policies command.

    Args:
        ack (function): Acknowledge the Slack command request.
        command (dict): The Slack command payload.
        client (slack_sdk.WebClient): The Slack WebClient instance for API calls.

    """
    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    policies_list = [
        ("Chapters Policy", "https://owasp.org/www-policy/operational/chapters"),
        ("Code of Conduct", "https://owasp.org/www-policy/operational/code-of-conduct"),
        ("Committees Policy", "https://owasp.org/www-policy/operational/committees"),
        (
            "Conflict Resolution Policy",
            "https://owasp.org/www-policy/operational/conflict-resolution",
        ),
        (
            "Conflict of Interest Policy",
            "https://owasp.org/www-policy/operational/conflict-of-interest",
        ),
        ("Donations Policy", "https://owasp.org/www-policy/operational/donations"),
        ("Elections Policy", "https://owasp.org/www-policy/operational/election"),
        ("Events Policy", "https://owasp.org/www-policy/operational/events"),
        ("Expense Policy", "https://owasp.org/www-policy/operational/expense-reimbursement"),
        ("Grant Policy", "https://owasp.org/www-policy/operational/grants"),
        ("Membership Policy", "https://owasp.org/www-policy/operational/membership"),
        ("Project Policy", "https://owasp.org/www-policy/operational/projects"),
        (
            "Whistleblower & Anti-Retaliation Policy",
            "https://owasp.org/www-policy/operational/whistleblower",
        ),
    ]

    template = env.get_template("policies.txt")
    rendered_text = template.render(
        policies=policies_list,
        NL=NL,
        SECTION_BREAK="{{ SECTION_BREAK }}",
        DIVIDER="{{ DIVIDER }}",
    )

    blocks = []
    for section in rendered_text.split("{{ SECTION_BREAK }}"):
        section = section.strip()
        if section == "{{ DIVIDER }}":
            blocks.append({"type": "divider"})
        elif section:
            blocks.append(markdown(section))

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(
        blocks=blocks,
        channel=conversation["channel"]["id"],
        text=get_text(blocks),
    )


if SlackConfig.app:
    policies_handler = SlackConfig.app.command(COMMAND)(policies_handler)
