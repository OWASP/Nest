"""Handler for OWASP Contribute Slack functionality."""

from __future__ import annotations

from django.utils.text import Truncator

from apps.common.constants import NL
from apps.slack.blocks import get_pagination_buttons, markdown
from apps.slack.common.constants import TRUNCATION_INDICATOR
from apps.slack.common.presentation import EntityPresentation
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE
from apps.slack.utils import escape


def get_blocks(
    page=1, search_query: str = "", limit: int = 10, presentation: EntityPresentation | None = None
):
    """Get contribute blocks."""
    from apps.github.models.issue import Issue
    from apps.owasp.api.search.issue import get_issues

    presentation = presentation or EntityPresentation()
    search_query_escaped = escape(search_query)

    attributes = "project_name,project_url,summary,title,url"

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
        title = Truncator(escape(issue["title"])).chars(
            presentation.name_truncation, truncate=TRUNCATION_INDICATOR
        )
        project_name = escape(issue["project_name"])
        project_url = escape(issue["project_url"])
        summary = Truncator(escape(issue["summary"])).chars(
            presentation.summary_truncation, truncate=TRUNCATION_INDICATOR
        )

        blocks.append(
            markdown(
                f"{offset + idx + 1}. <{issue['url']}|*{title}*>{NL}"
                f"<{project_url}|{project_name}>{NL}"
                f"{summary}{NL}"
            )
        )

    if presentation.include_feedback:
        blocks.append(
            markdown(
                f"Extended search over {Issue.open_issues_count()} OWASP issues"
                f"{FEEDBACK_CHANNEL_MESSAGE}"
            )
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
