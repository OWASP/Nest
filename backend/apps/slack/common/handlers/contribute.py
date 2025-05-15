"""Handler for OWASP Contribute Slack functionality."""

from __future__ import annotations

from django.conf import settings
from django.utils.text import Truncator

from apps.common.constants import NL
from apps.common.utils import get_absolute_url
from apps.slack.blocks import get_pagination_buttons, markdown
from apps.slack.common.constants import TRUNCATION_INDICATOR
from apps.slack.common.presentation import EntityPresentation
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE
from apps.slack.utils import escape


def get_blocks(
    limit: int = 10,
    page: int = 1,
    presentation: EntityPresentation | None = None,
    search_query: str = "",
) -> list:
    """Get contribute blocks.

    Args:
        limit (int): The maximum number of issues to retrieve per page.
        page (int): The current page number for pagination.
        presentation (EntityPresentation | None): Configuration for entity presentation.
        search_query (str): The search query for filtering issues.

    Returns:
        list: A list of Slack blocks representing the contribution issues.

    """
    from apps.github.models.issue import Issue
    from apps.owasp.api.search.issue import get_issues

    presentation = presentation or EntityPresentation()
    search_query_escaped = escape(search_query)

    attributes = [
        "idx_project_name",
        "idx_project_url",
        "idx_summary",
        "idx_title",
        "idx_url",
    ]

    offset = (page - 1) * limit
    contribute_data = get_issues(search_query, attributes=attributes, limit=limit, page=page)
    issues = contribute_data["hits"]
    total_pages = contribute_data["nbPages"]

    if not issues:
        return [
            markdown(
                f"*No issues found for `{search_query_escaped}`*{NL}"
                if search_query
                else "*No issues found*{NL}"
            )
        ]

    blocks = []
    for idx, issue in enumerate(issues):
        title = Truncator(escape(issue["idx_title"])).chars(
            presentation.name_truncation, truncate=TRUNCATION_INDICATOR
        )
        project_name = escape(issue["idx_project_name"])
        project_url = escape(issue["idx_project_url"])
        summary = Truncator(escape(issue["idx_summary"])).chars(
            presentation.summary_truncation, truncate=TRUNCATION_INDICATOR
        )

        blocks.append(
            markdown(
                f"{offset + idx + 1}. <{issue['idx_url']}|*{title}*>{NL}"
                f"<{project_url}|{project_name}>{NL}"
                f"{summary}{NL}"
            )
        )

    if presentation.include_feedback:
        blocks.append(
            markdown(
                f"⚠️ *Extended search over {Issue.open_issues_count()} open issues "
                f"is available at <{get_absolute_url('contribute')}"
                f"?q={search_query}|{settings.SITE_NAME}>*{NL}"
                f"{FEEDBACK_CHANNEL_MESSAGE}"
            ),
        )
    if presentation.include_pagination and (
        pagination_block := get_pagination_buttons(
            "contribute",
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
