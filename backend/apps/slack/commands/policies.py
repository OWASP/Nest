"""Slack bot policies command."""

from django.conf import settings

from apps.common.constants import NL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown

COMMAND = "/policies"


def policies_handler(ack, command, client):
    """Slack /policies command handler."""
    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    blocks = [
        markdown(
            "- <https://owasp.org/www-policy/operational/awards-and-scholarships|"
            "Awards and Scholarships Policy>\n"
        ),
        markdown(
            "- <https://owasp.org/www-policy/operational/board-code-of-conduct|"
            "Board Code of Conduct>\n"
        ),
        markdown("- <https://owasp.org/www-policy/operational/branding|Branding Policy>\n"),
        markdown("- <https://owasp.org/www-policy/operational/chapters|Chapters Policy>\n"),
        markdown(
            "- <https://owasp.org/www-policy/operational/code-of-conduct|"
            "Code of Conduct Policy>\n"
        ),
        markdown("- <https://owasp.org/www-policy/operational/committees|Committees Policy>\n"),
        markdown(
            "- <https://owasp.org/www-policy/operational/community-review-process|"
            "Community Review Process Policy>\n"
        ),
        markdown(
            "- <https://owasp.org/www-policy/operational/conferences-events|"
            "Conferences and Events Policy>\n"
        ),
        markdown(
            "- <https://owasp.org/www-policy/operational/conflict-resolution|"
            "Conflict Resolution Policy>\n"
        ),
        markdown(
            "- <https://owasp.org/www-policy/operational/conflict-of-interest|"
            "Conflict of Interest Policy>\n"
        ),
        markdown("- <https://owasp.org/www-policy/operational/election|Election Policy>\n"),
        markdown("- <https://owasp.org/www-policy/operational/events|Events Policy>\n"),
        markdown(
            "- <https://owasp.org/www-policy/operational/expense-reimbursement|"
            "Expense Reimbursement Policy>\n"
        ),
        markdown(
            "- <https://owasp.org/www-policy/operational/force-majeure-sanctions|"
            "Force Majeure and Sanctions Policy>\n"
        ),
        markdown(
            "- <https://owasp.org/www-policy/operational/general-disclaimer|"
            "General Disclaimer Policy>\n"
        ),
        markdown(f"Please visit <https://owasp.org/www-policy/|OWASP policies> page{NL}"),
    ]

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(channel=conversation["channel"]["id"], blocks=blocks)


if SlackConfig.app:
    policies_handler = SlackConfig.app.command(COMMAND)(policies_handler)
