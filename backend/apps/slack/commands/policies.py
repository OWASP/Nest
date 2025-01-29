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
        ),
        ("Board Code of Conduct", "Ethical and professional standards for OWASP board members."),
        ("Branding Policy", "Rules for using OWASP branding, including logos and trademarks."),
        ("Chapters Policy", "Framework for running and managing OWASP local chapters."),
        ("Code of Conduct Policy", "Expectations for behavior within the OWASP community."),
        ("Committees Policy", "Structure and responsibilities of OWASP committees."),
        (
            "Community Review Process Policy",
            "Process for community-driven review of policies and decisions.",
        ),
        (
            "Conferences and Events Policy",
            "Rules for organizing and participating in OWASP events.",
        ),
        ("Conflict Resolution Policy", "Procedures for resolving disputes within OWASP."),
        ("Conflict of Interest Policy", "Guidelines to avoid and manage conflicts of interest."),
        ("Election Policy", "Rules governing OWASP board and leadership elections."),
        ("Events Policy", "General policies for OWASP events, including sponsorships."),
        (
            "Expense Reimbursement Policy",
            "Guidelines for reimbursement of OWASP-related expenses.",
        ),
        (
            "Force Majeure and Sanctions Policy",
            "Handling of extraordinary events affecting OWASP operations.",
        ),
        ("General Disclaimer Policy", "Legal disclaimers related to OWASP projects and content."),
    ]

    formatted_policies = "\n".join(
        f"- *<{url}|{title}>*: {description}"
        for title, description, url in [
            (
                p[0],
                p[1],
                f"https://owasp.org/www-policy/operational/{p[0].lower().replace(' ', '-')}",
            )
            for p in policies
        ]
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
