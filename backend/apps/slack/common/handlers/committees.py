"""Handler for OWASP Committees Slack functionality."""

from __future__ import annotations

from django.conf import settings
from django.utils.text import Truncator

from apps.common.constants import NL
from apps.common.utils import get_absolute_url
from apps.slack.blocks import markdown
from apps.slack.common.constants import TRUNCATION_INDICATOR
from apps.slack.common.presentation import EntityPresentation
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE
from apps.slack.utils import escape


def committees_blocks(
    search_query: str = "", limit: int = 10, presentation: EntityPresentation | None = None
):
    """Committee block for both commands and app home."""
    from apps.owasp.api.search.committee import get_committees
    from apps.owasp.models.committee import Committee

    presentation = presentation or EntityPresentation()
    search_query_escaped = escape(search_query)

    attributes = ["idx_leaders", "idx_name", "idx_summary", "idx_url"]

    committees = get_committees(search_query, attributes=attributes, limit=limit)["hits"]
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
        name = Truncator(escape(committee["idx_name"])).chars(
            presentation.name_truncation, truncate=TRUNCATION_INDICATOR
        )
        summary = Truncator(committee["idx_summary"]).chars(
            presentation.summary_truncation, truncate=TRUNCATION_INDICATOR
        )

        leaders = committee.get("idx_leaders", [])
        leaders_text = (
            f"_Leader{'' if len(leaders) == 1 else 's'}: {', '.join(leaders)}_{NL}"
            if leaders and presentation.include_metadata
            else ""
        )

        blocks.append(
            markdown(
                f"{idx + 1}. <{committee['idx_url']}|*{name}*>{NL}"
                f"{leaders_text}"
                f"{escape(summary)}{NL}"
            )
        )

    if presentation.include_feedback:
        blocks.append(
            markdown(
                f"⚠️ *Extended search over {Committee.active_committees_count()} OWASP committees "
                f"is available at <{get_absolute_url('committees')}"
                f"?q={search_query}|{settings.SITE_NAME}>*{NL}"
                f"{FEEDBACK_CHANNEL_MESSAGE}"
            )
        )

    return blocks
