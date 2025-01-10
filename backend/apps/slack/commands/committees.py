"""Slack bot committees command."""

from django.conf import settings

from apps.common.constants import NL
from apps.common.utils import get_absolute_url
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.commands.constants import COMMAND_START
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE
from apps.slack.utils import escape

COMMAND = "/committees"


def handler(ack, command, client):
    """Slack /committees command handler."""
    from apps.owasp.api.search.committee import get_committees
    from apps.owasp.models.committee import Committee

    ack()
    if not settings.SLACK_COMMANDS_ENABLED:
        return

    command_text = command["text"].strip()
    search_query = "" if command_text in COMMAND_START else command_text
    search_query_escaped = escape(search_query)
    blocks = [
        markdown(f"*No results found for `{COMMAND} {search_query_escaped}`*{NL}"),
    ]

    attributes = [
        "idx_name",
        "idx_summary",
        "idx_url",
        "idx_leaders"
    ]
    
    if committees := get_committees(
        search_query,
        attributes=attributes,
        limit=10,
    )["hits"]:
        blocks = [
            markdown(
                f"{NL}*Here are top available committees "
                f"that I found for* `{search_query_escaped}`:{NL}"
                if search_query_escaped
                else f"{NL}*Here are top available OWASP committees:*{NL}"
            ),
        ]

        for idx, committee in enumerate(committees):
            leaders = committee.get("idx_leaders", [])
            blocks.append(
                markdown(
                    f"{NL}*{idx + 1}.* <{committee['idx_url']}|*{escape(committee['idx_name'])}*>{NL}"
                    f"Leader{'' if len(leaders) == 1 else 's'}: {', '.join(leaders)}{NL}"
                    f"{escape(committee['idx_summary'])}{NL}"
                )
            )

        blocks.append(
            markdown(
                f"⚠️ *Extended search over {Committee.active_committees_count()} OWASP committees"
                f"is available at <{get_absolute_url('committees')}"
                f"?q={search_query}|{settings.SITE_NAME}>*{NL}"
                f"{FEEDBACK_CHANNEL_MESSAGE}"
            ),
        )

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(channel=conversation["channel"]["id"], blocks=blocks)


if SlackConfig.app:
    handler = SlackConfig.app.command(COMMAND)(handler)