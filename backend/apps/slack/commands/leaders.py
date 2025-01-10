"""Slack bot owasp command."""

from django.conf import settings

from apps.common.constants import NL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.utils import escape

COMMAND = "/leaders"


def handler(ack, command, client):
    """Slack /leaders command handler."""
    from apps.owasp.api.search.chapter import get_chapters
    from apps.owasp.api.search.project import get_projects

    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    search_query_escaped = escape(command["text"])

    blocks = [markdown(f"*No results found for `{COMMAND} {search_query_escaped}`*{NL}")]
    attributes = [
        "idx_leaders",
        "idx_name",
    ]
    restrict_attributes = ["idx_leaders", "idx_name"]
    chapters = get_chapters(
        query=search_query_escaped,
        attributes=attributes,
        limit=10,
        page=1,
        restrict_attributes=restrict_attributes,
    )["hits"]

    projects = get_projects(
        query=search_query_escaped,
        attributes=attributes,
        limit=10,
        page=1,
        restrict_attributes=restrict_attributes,
    )["hits"]

    if chapters or projects:
        blocks = [markdown(f"{NL}Here are the results for `{search_query_escaped}`:{NL}")]

        if chapters:
            blocks.append(markdown("*Chapter Leaders:*"))
            for chapter in chapters[:10]:
                chapter_leaders = chapter["idx_leaders"]
                if isinstance(chapter_leaders, list):
                    chapter_leaders = ", ".join(chapter_leaders)

                blocks.append(
                    markdown(f"• *{escape(chapter['idx_name'])}*: {escape(chapter_leaders)}{NL}")
                )

        if projects:
            blocks.append(markdown("*Project Leaders:*"))
            for project in projects[:10]:
                project_leaders = project["idx_leaders"]
                if isinstance(project_leaders, list):
                    project_leaders = ", ".join(project_leaders)

                blocks.append(
                    markdown(f"• *{escape(project['idx_name'])}*: {escape(project_leaders)}{NL}")
                )

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(channel=conversation["channel"]["id"], blocks=blocks)


if SlackConfig.app:
    handler = SlackConfig.app.command(COMMAND)(handler)
