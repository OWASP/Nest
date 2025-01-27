"""Handler for OWASP Sponsors Slack functionality."""

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
    """Get sponsors blocks."""
    from apps.owasp.api.search.sponsor import get_sponsors
    from apps.owasp.models.sponsor import Sponsor

    presentation = presentation or EntityPresentation()
    search_query_escaped = escape(search_query)

    attributes = [
        "idx_name",
        "idx_description",
        "idx_url",
        "idx_sponsor_level",
        "idx_is_active_sponsor",
    ]

    offset = (page - 1) * limit
    sponsors_data = get_sponsors(search_query, attributes=attributes, limit=limit, page=page)
    sponsors = sponsors_data["hits"]
    total_pages = sponsors_data["nbPages"]

    if not sponsors:
        return [
            markdown(
                f"*No sponsors found for `{search_query_escaped}`*{NL}"
                if search_query
                else f"*No sponsors found*{NL}"
            )
        ]

    blocks = [
        markdown(
            f"{NL}*OWASP sponsors that I found for* `{search_query_escaped}`:{NL}"
            if search_query_escaped
            else f"{NL}*OWASP sponsors:*{NL}"
        ),
    ]

    for idx, sponsor in enumerate(sponsors):
        name = Truncator(escape(sponsor["idx_name"])).chars(
            presentation.name_truncation, truncate=TRUNCATION_INDICATOR
        )
        description = Truncator(sponsor["idx_description"]).chars(
            presentation.summary_truncation, truncate=TRUNCATION_INDICATOR
        )

        sponsor_level = sponsor.get("idx_sponsor_level", "")
        sponsor_level_text = (
            f"_Level: {sponsor_level}_{NL}"
            if sponsor_level and presentation.include_metadata
            else ""
        )

        is_active = sponsor.get("idx_is_active_sponsor", False)
        status_text = "(Active)" if is_active else "(Inactive)"

        blocks.append(
            markdown(
                f"{offset + idx + 1}. <{sponsor['idx_url']}|*{name}*> {status_text}{NL}"
                f"{sponsor_level_text}"
                f"{escape(description)}{NL}"
            )
        )

    if presentation.include_feedback:
        blocks.append(
            markdown(
                f"⚠️ *Extended search over OWASP sponsors "
                f"is available at <{get_absolute_url('sponsors')}?q={search_query}|{settings.SITE_NAME}>*{NL}"
                f"{FEEDBACK_CHANNEL_MESSAGE}"
            )
        )
    if presentation.include_pagination and (
        pagination_block := get_pagination_buttons(
            "sponsors",
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
