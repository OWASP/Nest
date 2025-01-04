"""Slack bot contribute command."""

from django.conf import settings
from django.template.defaultfilters import pluralize
from django.utils.text import Truncator

from apps.common.utils import get_absolute_url, natural_date, natural_number
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE, NL
from apps.slack.utils import escape, send_to_analytics

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
    send_to_analytics(search_query, COMMAND)
    blocks = [
        markdown(f"*No results found for `{COMMAND} {search_query_escaped}`*{NL}"),
    ]

    attributes = [
        "idx_contributors_count",
        "idx_forks_count",
        "idx_leaders",
        "idx_level",
        "idx_name",
        "idx_stars_count",
        "idx_summary",
        "idx_updated_at",
        "idx_url",
    ]
    if projects := get_projects(
        search_query,
        attributes=attributes,
        limit=10,
    )["hits"]:
        blocks = [
            markdown(
                (
                    f"{NL}*Here are top 10 most OWASP projects "
                    f"that I found for* `{search_query_escaped}` query:{NL}"
                )
                if search_query_escaped
                else (f"{NL}*Here are top 10 OWASP projects:*{NL}")
            ),
        ]

        for idx, project in enumerate(projects):
            name_truncated = Truncator(escape(project["idx_name"])).chars(
                NAME_TRUNCATION_LIMIT, truncate="..."
            )
            contributors_count = (
                f", {natural_number(project['idx_contributors_count'], unit='contributor')}"
                if project["idx_contributors_count"]
                else ""
            )
            forks_count = (
                f", {natural_number(project['idx_forks_count'], unit='fork')}"
                if project["idx_forks_count"]
                else ""
            )
            stars_count = (
                f", {natural_number(project['idx_stars_count'], unit='star')}"
                if project["idx_stars_count"]
                else ""
            )
            leaders = project["idx_leaders"]
            blocks.append(
                markdown(
                    f"{NL}*{idx + 1}.* <{project['idx_url']}|*{name_truncated}*>{NL}"
                    f"_Updated {natural_date(project['idx_updated_at'])}"
                    f"{stars_count}{forks_count}{contributors_count}_{NL}"
                    f"_{project['idx_level'].capitalize()} project. "
                    f"Leader{pluralize(len(leaders))}: {', '.join(leaders)}_{NL}"
                    f"{escape(project['idx_summary'])}{NL}"
                )
            )

        blocks.append(
            markdown(
                f"⚠️ *Extended search over {Project.active_projects_count()} OWASP projects "
                f"is available at <{get_absolute_url('projects')}"
                f"?q={search_query}|{settings.SITE_NAME}>*{NL}"
                f"{FEEDBACK_CHANNEL_MESSAGE}"
            ),
        )

    conversation = client.conversations_open(users=command["user_id"])
    client.chat_postMessage(channel=conversation["channel"]["id"], blocks=blocks)


if SlackConfig.app:
    handler = SlackConfig.app.command(COMMAND)(handler)
