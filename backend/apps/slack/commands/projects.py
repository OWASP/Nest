"""Slack bot contribute command."""

from django.conf import settings
from django.utils.text import Truncator

from apps.common.utils import get_absolute_url
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE
from apps.slack.utils import escape

COMMAND = "/projects"
TEXT_TRUNCATION_LIMIT = 260


def handler(ack, say, command):
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

    projects = get_projects(search_query, limit=10)
    if projects:
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
            description_truncated = Truncator(project["idx_description"]).chars(
                TEXT_TRUNCATION_LIMIT, truncate="..."
            )
            blocks.append(
                markdown(
                    f"\n*{idx + 1}.* <{project['idx_url']}|*{escape(project['idx_name'])}*>\n"
                    f"{escape(description_truncated)}\n"
                ),
            )

        blocks.append(
            markdown(
                f"⚠️ *Extended search over {Project.active_projects_count()} OWASP projects "
                f"is available at <{get_absolute_url('projects')}|{settings.SITE_NAME}>*\n"
                f"{FEEDBACK_CHANNEL_MESSAGE}"
            ),
        )

    say(blocks=blocks)


if SlackConfig.app:
    handler = SlackConfig.app.command(COMMAND)(handler)
