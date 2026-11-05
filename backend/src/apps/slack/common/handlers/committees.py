"""Handler for OWASP Committees Slack functionality."""

from __future__ import annotations

from django.conf import settings
from django.template.defaultfilters import pluralize

from apps.common.constants import NL
from apps.common.utils import get_absolute_url, truncate
from apps.slack.blocks import get_pagination_buttons, markdown
from apps.slack.common.presentation import EntityPresentation
from apps.slack.constants import FEEDBACK_SHARING_INVITE
from apps.slack.utils import escape


def get_blocks(
    limit: int = 10,
    page: int = 1,
    presentation: EntityPresentation | None = None,
    search_query: str = "",
) -> list:
    """Get committees blocks.

    Args:
        limit (int): The maximum number of committees to retrieve per page.
        page (int): The current page number for pagination.
        presentation (EntityPresentation | None): Configuration for entity presentation.
        search_query (str): The search query for filtering committees.

    Returns:
        list: A list of Slack blocks representing the committees.

    """
    from apps.owasp.index.search.committee import get_committees
    from apps.owasp.models.committee import Committee

    presentation = presentation or EntityPresentation()
    search_query_escaped = escape(search_query)

    attributes = [
        "idx_leaders",
        "idx_name",
        "idx_summary",
        "idx_url",
    ]

    offset = (page - 1) * limit
    committees_data = get_committees(search_query, attributes=attributes, limit=limit, page=page)
    committees = committees_data["hits"]
    total_pages = committees_data["nbPages"]

    if not committees:
        return [
            markdown(
                f"*No committees found for `{search_query_escaped}`*{NL}"
                if search_query
                else "*No committees found*{NL}"
            )
        ]

    blocks = [
        markdown(
            f"{NL}*OWASP committees that I found for* `{search_query_escaped}`:{NL}"
            if search_query_escaped
            else f"{NL}*OWASP committees:*{NL}"
        ),
    ]

    for idx, committee in enumerate(committees):
        name = truncate(escape(committee["idx_name"]), presentation.name_truncation)
        summary = truncate(escape(committee["idx_summary"]), presentation.summary_truncation)

        leaders = committee.get("idx_leaders", [])
        leaders_text = (
            f"_Leader{pluralize(len(leaders))}: {', '.join(leaders)}_{NL}"
            if leaders and presentation.include_metadata
            else ""
        )

        blocks.append(
            markdown(
                f"{offset + idx + 1}. <{committee['idx_url']}|*{name}*>{NL}"
                f"{leaders_text}"
                f"{summary}{NL}"
            )
        )

    if presentation.include_feedback:
        blocks.append(
            markdown(
                f"⚠️ *Extended search over {Committee.active_committees_count()} OWASP committees "
                f"is available at <{get_absolute_url('/committees')}"
                f"?q={search_query}|{settings.SITE_NAME}>*{NL}"
                f"{FEEDBACK_SHARING_INVITE}"
            )
        )
    if presentation.include_pagination and (
        pagination_block := get_pagination_buttons(
            "committees",
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
