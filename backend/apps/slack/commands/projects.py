"""Slack bot contribute command."""

from django.conf import settings
from django.utils.text import Truncator

from apps.common.utils import get_absolute_url
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE
from apps.slack.utils import escape

COMMAND = "/projects"
NAME_TRUNCATION_LIMIT = 80


def handler(ack, command, client):
    """Slack /projects command handler."""
    from apps.owasp.api.search.project import get_projects
    from apps.owasp.models.project import Project

    ack()
    if not settings.SLACK_COMMANDS_ENABLED:
        return

    search_query = command["text"]
    search_query_escaped = escape(command["text"])
    blocks = [
        markdown(f"*No results found for `{COMMAND} {search_query_escaped}`*\n"),
    ]

    attributes = [
        "idx_name",
        "idx_summary",
        "idx_url",
    ]
    if projects := get_projects(search_query, attributes=attributes, limit=10):
        blocks = [
            markdown(
                (
                    f"\n*Here are top 10 most OWASP projects "
                    f"that I found based on *\n `{COMMAND} {search_query_escaped}`:\n"
                )
                if search_query_escaped
                else (
                    "\n*Here are top 10 OWASP projects:*\n"
                    "You can refine the results by using a more specific query, e.g.\n"
                    f"`{COMMAND} application security`"
                )
            ),
        ]

        for idx, project in enumerate(projects):
            name_truncated = Truncator(escape(project["idx_name"])).chars(
                NAME_TRUNCATION_LIMIT, truncate="..."
            )
            blocks.append(
                markdown(
                    f"\n*{idx + 1}.* <{project['idx_url']}|*{name_truncated}*>\n"
                    f"{escape(project['idx_summary'])}\n"
                ),
            )

        blocks.append(
            markdown(
                f"⚠️ *Extended search over {Project.active_projects_count()} OWASP projects "
                f"is available at <{get_absolute_url('projects')}"
                f"?q={search_query}|{settings.SITE_NAME}>*\n"
                f"{FEEDBACK_CHANNEL_MESSAGE}"
            ),
        )

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(channel=conversation["channel"]["id"], blocks=blocks)


if SlackConfig.app:
    handler = SlackConfig.app.command(COMMAND)(handler)
