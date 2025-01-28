"""Handler for OWASP Sponsors Slack functionality."""

from __future__ import annotations

from django.utils.text import Truncator

from apps.common.constants import NL, OWASP_WEBSITE_URL
from apps.slack.blocks import markdown
from apps.slack.common.constants import TRUNCATION_INDICATOR
from apps.slack.common.presentation import EntityPresentation
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE
from apps.slack.utils import escape


def get_blocks(
    page=1, search_query: str = "", limit: int = 10, presentation: EntityPresentation | None = None
):
    """Get sponsors blocks."""
    from apps.owasp.api.search.sponsor import get_sponsors

    presentation = presentation or EntityPresentation()
    search_query_escaped = escape(search_query)

    attributes = [
        "idx_name",
        "idx_sort_name",
        "idx_description",
        "idx_url",
        "idx_member_type",
        "idx_sponsor_type",
        "idx_is_member",
    ]

    offset = (page - 1) * limit
    sponsors_data = get_sponsors(search_query, attributes=attributes, limit=limit, page=page)
    sponsors = sponsors_data["hits"]

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

        member_type = sponsor.get("idx_member_type", "")
        sponsor_type = sponsor.get("idx_sponsor_type", "")
        is_member = sponsor.get("idx_is_member", False)

        metadata_text = []
        if member_type and presentation.include_metadata:
            metadata_text.append(f"Member Type: {member_type}")
        if sponsor_type and presentation.include_metadata:
            metadata_text.append(f"Sponsor Type: {sponsor_type}")

        metadata_line = (
            f"_{' | '.join(metadata_text)}_{NL}"
            if metadata_text and presentation.include_metadata
            else ""
        )

        blocks.append(
            markdown(
                f"{offset + idx + 1}. <{sponsor['idx_url']}|*{name}*>"
                f"{' (Corporate Sponsor)' if is_member else ''}{NL}"
                f"{metadata_line}"
                f"{escape(description)}{NL}"
            )
        )

    if presentation.include_feedback:
        blocks.append(
            markdown(
                f"*Please visit the <{OWASP_WEBSITE_URL}/supporters|OWASP supporters>"
                f" for more information about the sponsors*{NL}"
                f"{FEEDBACK_CHANNEL_MESSAGE}"
            )
        )

    return blocks
