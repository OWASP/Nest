"""Slack bot donate command."""

from django.conf import settings

from apps.common.constants import NL, OWASP_WEBSITE_URL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.utils import get_text

COMMAND = "/donate"


def donate_handler(ack, command, client):
    """Slack /donate command handler."""
    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    blocks = [
        markdown(
            "The OWASP Foundation, a U.S. 501(c)(3) nonprofit organization, accepts donations to "
            "support its mission of improving software security. Donations can be made through "
            "the official OWASP website or via postal mail. Online donations are processed "
            "through a form that attributes contributions to specific chapters or projects "
            "based on the referring page title. The form supports multiple currencies: "
            f"USD, GBP, and EUR.{NL}"
            "Donations can be unrestricted, allowing OWASP to allocate funds where needed, or "
            "restricted, where contributions of $1,000 or more can be designated for a specific "
            "project or chapter with a 10% administrative fee. Donors may be publicly "
            "acknowledged, though OWASP remains vendor-neutral and does not endorse any "
            "supporters. For substantial contributions, OWASP welcomes major foundation and "
            "corporate grants, and interested parties are encouraged to reach out. For detailed "
            "information on donation policies and procedures, please refer to the "
            f"<https://{OWASP_WEBSITE_URL}/www-policy/operational/donations|OWASP Donations "
            "Policy>."
        ),
        {"type": "divider"},
        markdown(f"Please Visit <{OWASP_WEBSITE_URL}/donate/| OWASP Foundation> page to donate."),
    ]

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(
        blocks=blocks,
        channel=conversation["channel"]["id"],
        text=get_text(blocks),
    )


if SlackConfig.app:
    donate_handler = SlackConfig.app.command(COMMAND)(donate_handler)
