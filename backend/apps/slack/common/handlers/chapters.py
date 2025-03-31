"""Handler for OWASP Chapters Slack functionality."""

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
    """Get chapters blocks.

    Args:
        page (int): The current page number for pagination.
        search_query (str): The search query for filtering chapters.
        limit (int): The maximum number of chapters to retrieve per page.
        presentation (EntityPresentation | None): Configuration for entity presentation.

    Returns:
        list: A list of Slack blocks representing the chapters.

    """
    from apps.owasp.api.search.chapter import get_chapters
    from apps.owasp.models.chapter import Chapter

    presentation = presentation or EntityPresentation()
    search_query_escaped = escape(search_query)

    attributes = [
        "idx_country",
        "idx_leaders",
        "idx_name",
        "idx_region",
        "idx_suggested_location",
        "idx_summary",
        "idx_updated_at",
        "idx_url",
    ]

    offset = (page - 1) * limit
    chapters_data = get_chapters(search_query, attributes=attributes, limit=limit, page=page)
    chapters = chapters_data["hits"]
    total_pages = chapters_data["nbPages"]

    if not chapters:
        return [
            markdown(
                f"*No chapters found for `{search_query_escaped}`*{NL}"
                if search_query
                else "*No chapters found*{NL}"
            )
        ]

    blocks = [
        markdown(
            f"{NL}*OWASP chapters that I found for* `{search_query_escaped}`:{NL}"
            if search_query_escaped
            else f"{NL}*OWASP chapters:*{NL}"
        ),
    ]

    for idx, chapter in enumerate(chapters):
        location = chapter["idx_suggested_location"] or chapter["idx_country"]
        leaders = chapter.get("idx_leaders", [])
        leaders_text = (
            f"_Leader{'' if len(leaders) == 1 else 's'}: {', '.join(leaders)}_{NL}"
            if leaders and presentation.include_metadata
            else ""
        )

        name = Truncator(escape(chapter["idx_name"])).chars(
            presentation.name_truncation, truncate=TRUNCATION_INDICATOR
        )
        summary = Truncator(chapter["idx_summary"]).chars(
            presentation.summary_truncation, truncate=TRUNCATION_INDICATOR
        )

        blocks.append(
            markdown(
                f"{offset + idx + 1}. <{chapter['idx_url']}|*{name}*>{NL}"
                f"_{location}_{NL}"
                f"{leaders_text}"
                f"{escape(summary)}{NL}"
            )
        )

    if presentation.include_feedback:
        blocks.append(
            markdown(
                f"⚠️ *Extended search over {Chapter.active_chapters_count()} OWASP chapters "
                f"is available at <{get_absolute_url('chapters')}"
                f"?q={search_query}|{settings.SITE_NAME}>*{NL}"
                f"{FEEDBACK_CHANNEL_MESSAGE}"
            )
        )

    if presentation.include_pagination and (
        pagination_block := get_pagination_buttons(
            "chapters",
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
