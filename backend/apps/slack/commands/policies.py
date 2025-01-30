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

    policies = [
        (
            "Awards and Scholarships Policy",
            "Guidelines for recognizing contributions and offering scholarships.",
            "https://owasp.org/www-policy/operational/awards-and-scholarships",
        ),
        (
            "Board Code of Conduct",
            "Ethical and professional standards for OWASP board members.",
            "https://owasp.org/www-policy/operational/board-code-of-conduct",
        ),
        (
            "Branding Policy",
            "Rules for using OWASP branding, including logos and trademarks.",
            "https://owasp.org/www-policy/operational/branding",
        ),
        (
            "Chapters Policy",
            "Framework for running and managing OWASP local chapters.",
            "https://owasp.org/www-policy/operational/chapters",
        ),
        (
            "Code of Conduct Policy",
            "Expectations for behavior within the OWASP community.",
            "https://owasp.org/www-policy/operational/code-of-conduct",
        ),
        (
            "Committees Policy",
            "Structure and responsibilities of OWASP committees.",
            "https://owasp.org/www-policy/operational/committees",
        ),
        (
            "Conferences and Events Policy",
            "Rules for organizing and participating in OWASP events.",
            "https://owasp.org/www-policy/operational/conferences-events",
        ),
        (
            "Conflict Resolution Policy",
            "Procedures for resolving disputes within OWASP.",
            "https://owasp.org/www-policy/operational/conflict-resolution",
        ),
        (
            "Conflict of Interest Policy",
            "Guidelines to avoid and manage conflicts of interest.",
            "https://owasp.org/www-policy/operational/conflict-of-interest",
        ),
        (
            "Election Policy",
            "Rules governing OWASP board and leadership elections.",
            "https://owasp.org/www-policy/operational/election",
        ),
        (
            "Events Policy",
            "General policies for OWASP events, including sponsorships.",
            "https://owasp.org/www-policy/operational/events",
        ),
        (
            "Expense Reimbursement Policy",
            "Guidelines for reimbursement of OWASP-related expenses.",
            "https://owasp.org/www-policy/operational/expense-reimbursement",
        ),
        (
            "Force Majeure and Sanctions Policy",
            "Handling of extraordinary events affecting OWASP operations.",
            "https://owasp.org/www-policy/operational/force-majeure-sanctions",
        ),
        (
            "General Disclaimer Policy",
            "Legal disclaimers related to OWASP projects and content.",
            "https://owasp.org/www-policy/operational/general-disclaimer",
        ),
    ]

    formatted_policies = "\n".join(
        f"- *<{url}|{title}>*: {description}" for title, description, url in policies
    )

    blocks = [
        markdown("*Here are the key OWASP policies:*"),
        markdown(formatted_policies),
        markdown(
            f"For more, visit *<https://owasp.org/www-policy/|Official OWASP Policies>*.{NL}"
        ),
    ]

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(channel=conversation["channel"]["id"], blocks=blocks)


if SlackConfig.app:
    policies_handler = SlackConfig.app.command(COMMAND)(policies_handler)
