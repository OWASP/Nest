"""Slack bot contribute command."""

from django.conf import settings
from django.utils.text import Truncator

from apps.common.constants import NL
from apps.common.utils import get_absolute_url
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.commands.constants import COMMAND_START
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE
from apps.slack.utils import escape

COMMAND = "/contribute"
SUMMARY_TRUNCATION_LIMIT = 255
TITLE_TRUNCATION_LIMIT = 80


def handler(ack, command, client):
    """Slack /contribute command handler."""
    from apps.github.models.issue import Issue
    from apps.owasp.api.search.issue import get_issues
    from apps.slack.common.contribute import CONTRIBUTE_GENERAL_INFORMATION_BLOCKS

    ack()
    if not settings.SLACK_COMMANDS_ENABLED:
        return

    command_text = command["text"].strip()
    if command_text in COMMAND_START:
        blocks = [
            *CONTRIBUTE_GENERAL_INFORMATION_BLOCKS,
            markdown(f"{FEEDBACK_CHANNEL_MESSAGE}"),
        ]
    else:
        search_query_escaped = escape(command_text)
        blocks = [
            markdown(f"*No results found for `{COMMAND} {search_query_escaped}`*{NL}"),
        ]

        attributes = [
            "idx_project_name",
            "idx_summary",
            "idx_title",
            "idx_url",
        ]
        if issues := get_issues(
            command_text,
            attributes=attributes,
            distinct=not command_text,
            limit=10,
        )["hits"]:
            blocks = [
                markdown(
                    (
                        f"{NL}*Here are top 10 most relevant issues "
                        f"that I found based on *{NL} `{COMMAND} {search_query_escaped}`:{NL}"
                    )
                    if search_query_escaped
                    else (f"{NL}*Here are top 10 most recent issues:*{NL}")
                ),
            ]

            for idx, issue in enumerate(issues):
                title_truncated = Truncator(escape(issue["idx_title"])).chars(
                    TITLE_TRUNCATION_LIMIT, truncate="..."
                )
                summary_truncated = Truncator(issue["idx_summary"]).chars(
                    SUMMARY_TRUNCATION_LIMIT, truncate="..."
                )
                blocks.append(
                    markdown(
                        f"{NL}*{idx + 1}.* <{issue['idx_url']}|*{title_truncated}*>{NL}"
                        f"{escape(issue['idx_project_name'])}{NL}"
                        f"{escape(summary_truncated)}{NL}"
                    ),
                )

            blocks.append(
                markdown(
                    f"⚠️ *Extended search over {Issue.open_issues_count()} open issues "
                    f"is available at <{get_absolute_url('projects/issues')}"
                    f"?q={command_text}|{settings.SITE_NAME}>*\n"
                    f"{FEEDBACK_CHANNEL_MESSAGE}"
                ),
            )

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(channel=conversation["channel"]["id"], blocks=blocks)


if SlackConfig.app:
    handler = SlackConfig.app.command(COMMAND)(handler)
