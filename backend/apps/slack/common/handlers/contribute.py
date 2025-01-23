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
    page=1, search_query: str = "", limit: int = 10, presentation: EntityPresentation | None = None
):
    """Get contribute blocks."""
    from apps.owasp.api.search.issue import get_issues
    from apps.owasp.models.contribute import Contribute

    presentation = presentation or EntityPresentation()
    search_query_escaped = escape(search_query)

    attributes = [
        "idx_title",
        "idx_project_name",
        "idx_project_url",
        "idx_summary",
        "idx_url",
    ]

    offset = (page - 1) * limit
    contribute_data = get_issues(search_query, attributes=attributes, limit=limit, page=page)
    contribute_items = contribute_data["hits"]
    total_pages = contribute_data["nbPages"]

    if not contribute_items:
        return [
            markdown(
                f"*No contributions found for `{search_query_escaped}`*{NL}"
                if search_query
                else "*No contributions found*{NL}"
            )
        ]

    blocks = [
        markdown(
            f"{NL}*OWASP contributions found for* `{search_query_escaped}`:{NL}"
            if search_query_escaped
            else f"{NL}*OWASP contributions:*{NL}"
        ),
    ]

    for idx, contribution in enumerate(contribute_items):
        title = Truncator(escape(contribution["idx_title"])).chars(
            presentation.name_truncation, truncate=TRUNCATION_INDICATOR
        )
        project = escape(contribution["idx_project_name"])
        project_url = escape(contribution["idx_project_url"])
        summary = Truncator(escape(contribution["idx_summary"])).chars(
            presentation.summary_truncation, truncate=TRUNCATION_INDICATOR
        )

        blocks.append(
            markdown(
                f"{offset + idx + 1}. <{contribution['idx_url']}|*{title}*>{NL}"
                f"*Project:* <{project_url}|{project}>{NL}"
                f"*Summary:* {summary}{NL}"
            )
        )

    if presentation.include_feedback:
        blocks.append(
            markdown(
                f"Extended search over {Contribute.active_contribute_count()} OWASP contributions"
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
