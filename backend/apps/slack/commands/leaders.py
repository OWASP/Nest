"""Slack bot leaders command."""

from django.conf import settings

from apps.common.constants import NL
from apps.common.utils import get_absolute_url
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.utils import escape, get_text

COMMAND = "/leaders"


def leaders_handler(ack, command, client):
    """Slack /leaders command handler."""
    from apps.owasp.api.search.chapter import get_chapters
    from apps.owasp.api.search.project import get_projects

    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    search_query = command["text"].strip()
    search_query_escaped = escape(search_query)

    attributes = [
        "idx_key",
        "idx_leaders",
        "idx_name",
    ]
    searchable_attributes = ["idx_leaders", "idx_name"]
    limit = 5
    chapters = get_chapters(
        query=search_query_escaped,
        attributes=attributes,
        limit=limit,
        page=1,
        searchable_attributes=searchable_attributes,
    )["hits"]

    projects = get_projects(
        query=search_query_escaped,
        attributes=attributes,
        limit=limit,
        page=1,
        searchable_attributes=searchable_attributes,
    )["hits"]

    blocks = []
    indent = "    •"
    if chapters or projects:
        if chapters:
            blocks.append(markdown("*Chapters*"))
            for chapter in chapters:
                if chapter_leaders := chapter["idx_leaders"]:
                    chapter_url = get_absolute_url(f"chapters/{chapter['idx_key']}")
                    leaders = "".join(
                        f"{indent} `{leader}`{NL}"
                        if search_query and search_query.lower() in leader.lower()
                        else f"{indent} {leader}{NL}"
                        for leader in chapter_leaders
                    )
                    blocks.append(markdown(f"<{chapter_url}|{chapter['idx_name']}>:{NL}{leaders}"))

        if projects:
            blocks.append(markdown("*Projects*"))
            for project in projects:
                if project_leaders := project["idx_leaders"]:
                    project_url = get_absolute_url(f"projects/{project['idx_key']}")
                    leaders = "".join(
                        f"{indent} `{leader}`{NL}"
                        if search_query and search_query.lower() in leader.lower()
                        else f"{indent} {leader}{NL}"
                        for leader in project_leaders
                    )

                    blocks.append(markdown(f"<{project_url}|{project['idx_name']}>:{NL}{leaders}"))
    else:
        blocks.append(markdown(f"*No results found for `{COMMAND} {search_query_escaped}`*{NL}"))

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(
        blocks=blocks,
        channel=conversation["channel"]["id"],
        text=get_text(blocks),
    )


if SlackConfig.app:
    leaders_handler = SlackConfig.app.command(COMMAND)(leaders_handler)
