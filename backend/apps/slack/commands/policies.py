"""Slack bot policies command."""

from django.conf import settings

from apps.common.constants import NL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import divider, markdown
from apps.slack.utils import get_text

COMMAND = "/policies"


def policies_handler(ack, command, client):
    """Slack /policies command handler."""
    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    policies = [
        (
            "Chapters Policy",
            "https://owasp.org/www-policy/operational/chapters",
        ),
        (
            "Code of Conduct",
            "https://owasp.org/www-policy/operational/code-of-conduct",
        ),
        (
            "Committees Policy",
            "https://owasp.org/www-policy/operational/committees",
        ),
        (
            "Conflict Resolution Policy",
            "https://owasp.org/www-policy/operational/conflict-resolution",
        ),
        (
            "Conflict of Interest Policy",
            "https://owasp.org/www-policy/operational/conflict-of-interest",
        ),
        (
            "Donations Policy",
            "https://owasp.org/www-policy/operational/donations",
        ),
        (
            "Elections Policy",
            "https://owasp.org/www-policy/operational/election",
        ),
        (
            "Events Policy",
            "https://owasp.org/www-policy/operational/events",
        ),
        (
            "Expense Policy",
            "https://owasp.org/www-policy/operational/expense-reimbursement",
        ),
        (
            "Grant Policy",
            "https://owasp.org/www-policy/operational/grants",
        ),
        (
            "Membership Policy",
            "https://owasp.org/www-policy/operational/membership",
        ),
        (
            "Project Policy",
            "https://owasp.org/www-policy/operational/projects",
        ),
        (
            "Whistleblower & Anti-Retaliation Policy",
            "https://owasp.org/www-policy/operational/whistleblower",
        ),
    ]

    policies = NL.join(f"  • <{url}|{title}>" for title, url in policies)
    blocks = [
        markdown(f"Important OWASP policies:{NL}{policies}"),
        divider(),
        markdown(
            "Please visit <https://owasp.org/www-policy/|OWASP policies> page for more "
            f"information{NL}"
        ),
    ]

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(
        blocks=blocks,
        channel=conversation["channel"]["id"],
        text=get_text(blocks),
    )


if SlackConfig.app:
    policies_handler = SlackConfig.app.command(COMMAND)(policies_handler)
