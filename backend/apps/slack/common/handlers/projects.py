"""Handler for OWASP Projects Slack functionality."""

from __future__ import annotations

from django.conf import settings
from django.utils.text import Truncator

from apps.common.constants import NL
from apps.common.utils import get_absolute_url, natural_date
from apps.slack.blocks import get_pagination_buttons, markdown
from apps.slack.common.constants import TRUNCATION_INDICATOR
from apps.slack.common.presentation import EntityPresentation
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE
from apps.slack.utils import escape


def get_blocks(
    page=1, search_query: str = "", limit: int = 10, presentation: EntityPresentation | None = None
):
    """Get projects blocks."""
    from apps.owasp.api.search.project import get_projects
    from apps.owasp.models.project import Project

    presentation = presentation or EntityPresentation()
    search_query_escaped = escape(search_query)

    attributes = (
        "contributors_count,forks_count,leaders,level,name,stars_count,summary,updated_at,url"
    )

    offset = (page - 1) * limit
    projects_data = get_projects(search_query, attributes=attributes, limit=limit, page=page)
    projects = projects_data["hits"]
    total_pages = projects_data["nbPages"]

    if not projects:
        return [
            markdown(
                f"*No projects found for `{search_query_escaped}`*{NL}"
                if search_query
                else "*No projects found*{NL}"
            )
        ]

    blocks = [
        markdown(
            f"{NL}*OWASP projects that I found for* `{search_query_escaped}`:{NL}"
            if search_query_escaped
            else f"{NL}*OWASP projects:*{NL}"
        ),
    ]

    for idx, project in enumerate(projects):
        name = Truncator(escape(project["name"])).chars(
            presentation.name_truncation, truncate=TRUNCATION_INDICATOR
        )
        summary = Truncator(project["summary"]).chars(
            presentation.summary_truncation, truncate=TRUNCATION_INDICATOR
        )

        metadata = []
        if presentation.include_metadata:
            if project["contributors_count"]:
                metadata.append(f"Contributors: {project['contributors_count']}")
            if project["forks_count"]:
                metadata.append(f"Forks: {project['forks_count']}")
            if project["stars_count"]:
                metadata.append(f"Stars: {project['stars_count']}")

        metadata_text = f"_{' | '.join(metadata)}_{NL}" if metadata else ""

        leaders = project["leaders"]
        leader_text = (
            f"_Leaders: {', '.join(leaders)}_{NL}"
            if leaders and presentation.include_metadata
            else ""
        )

        updated_text = (
            f"_Updated {natural_date(int(project['updated_at']))}_{NL}"
            if presentation.include_timestamps
            else ""
        )

        blocks.append(
            markdown(
                f"{offset + idx + 1}. <{project['url']}|*{name}*>{NL}"
                f"{updated_text}"
                f"{metadata_text}"
                f"{leader_text}"
                f"{escape(summary)}{NL}"
            )
        )

    if presentation.include_feedback:
        blocks.append(
            markdown(
                f"⚠️ *Extended search over {Project.active_projects_count()} OWASP projects "
                f"is available at <{get_absolute_url('projects')}"
                f"?q={search_query}|{settings.SITE_NAME}>*{NL}"
                f"{FEEDBACK_CHANNEL_MESSAGE}"
            )
        )

    if presentation.include_pagination and (
        pagination_block := get_pagination_buttons(
            "projects",
            page,
            total_pages - 1,
        )
    ):
        blocks.append(
            {
                "type": "actions",
                "elements": pagination_block,
            }
        )

    return blocks
