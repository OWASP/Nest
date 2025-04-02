"""Slack bot leaders command."""

from django.conf import settings

from apps.common.constants import NL
from apps.common.utils import get_absolute_url
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.template_system.loader import env
from apps.slack.utils import escape, get_text

COMMAND = "/leaders"


def leaders_handler(ack, command, client):
    """Handle the Slack /leaders command.

    Args:
        ack (function): Acknowledge the Slack command request.
        command (dict): The Slack command payload.
        client (slack_sdk.WebClient): The Slack WebClient instance for API calls.

    """
    from apps.owasp.api.search.chapter import get_chapters
    from apps.owasp.api.search.project import get_projects

    ack()

    if not settings.SLACK_COMMANDS_ENABLED:
        return

    search_query = command["text"].strip()
    search_query_escaped = escape(search_query)

    attributes = ["idx_key", "idx_leaders", "idx_name"]
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

    chapters_with_urls = [
        {
            "idx_key": chapter["idx_key"],
            "idx_name": chapter["idx_name"],
            "idx_leaders": chapter["idx_leaders"],
            "url": get_absolute_url(f"chapters/{chapter['idx_key']}"),
        }
        for chapter in chapters
    ]
    projects_with_urls = [
        {
            "idx_key": project["idx_key"],
            "idx_name": project["idx_name"],
            "idx_leaders": project["idx_leaders"],
            "url": get_absolute_url(f"projects/{project['idx_key']}"),
        }
        for project in projects
    ]

    template = env.get_template("leaders.txt")
    rendered_text = template.render(
        chapters=chapters_with_urls,
        projects=projects_with_urls,
        search_query=search_query_escaped,
        command=COMMAND,
        has_results=bool(chapters or projects),
        NL=NL,
    )
    sections = [
        section.strip()
        for section in rendered_text.split("===SECTION_BREAK===")
        if section.strip()
    ]
    blocks = [markdown(section) for section in sections]

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(
        blocks=blocks,
        channel=conversation["channel"]["id"],
        text=get_text(blocks),
    )


if SlackConfig.app:
    leaders_handler = SlackConfig.app.command(COMMAND)(leaders_handler)
