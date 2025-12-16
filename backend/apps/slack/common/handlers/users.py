"""Handler for OWASP Users Slack functionality."""

from __future__ import annotations

from django.conf import settings

from apps.common.constants import NL
from apps.common.utils import get_absolute_url, truncate
from apps.slack.blocks import get_pagination_buttons, markdown
from apps.slack.common.presentation import EntityPresentation
from apps.slack.constants import FEEDBACK_SHARING_INVITE
from apps.slack.utils import escape


def get_blocks(
    page: int = 1,
    search_query: str = "",
    limit: int = 10,
    presentation: EntityPresentation | None = None,
):
    """Get users blocks.

    Args:
        page (int): The current page number for pagination.
        search_query (str): The search query for filtering users.
        limit (int): The maximum number of users to retrieve per page.
        presentation (EntityPresentation | None): Configuration for entity presentation.

    Returns:
        list: A list of Slack blocks representing the users.

    """
    from apps.github.index.search.user import get_users

    presentation = presentation or EntityPresentation()
    search_query_escaped = escape(search_query)

    attributes = [
        "idx_bio",
        "idx_company",
        "idx_contributions",
        "idx_email",
        "idx_followers_count",
        "idx_following_count",
        "idx_issues_count",
        "idx_location",
        "idx_login",
        "idx_name",
        "idx_public_repositories_count",
        "idx_updated_at",
        "idx_url",
    ]

    users_data = get_users(search_query, attributes=attributes, limit=limit, page=page)
    users = users_data["hits"]
    total_pages = users_data["nbPages"]
    offset = (page - 1) * limit

    if not users:
        no_result_text = (
            f"*No users found for `{search_query_escaped}`*{NL}"
            if search_query_escaped
            else f"*No users found*{NL}"
        )
        return [markdown(no_result_text)]

    blocks = [
        markdown(
            f"{NL}*OWASP users that I found for* `{search_query_escaped}`:{NL}"
            if search_query_escaped
            else f"{NL}*OWASP users:*{NL}"
        ),
    ]

    for idx, user in enumerate(users):
        user_name_raw = user.get("idx_name") or user.get("idx_login", "")
        user_name = truncate(escape(user_name_raw), presentation.name_truncation)

        bio = truncate(escape(user.get("idx_bio", "") or ""), presentation.summary_truncation)

        location = escape(user.get("idx_location", ""))
        company = escape(user.get("idx_company", ""))
        followers_count = user.get("idx_followers_count", 0)
        following_count = user.get("idx_following_count", 0)
        public_repositories = user.get("idx_public_repositories_count", 0)

        metadata = []
        if presentation.include_metadata:
            if company:
                metadata.append(f"Company: {company}")
            if location:
                metadata.append(f"Location: {location}")
            if followers_count:
                metadata.append(f"Followers: {followers_count}")
            if following_count:
                metadata.append(f"Following: {following_count}")
            if public_repositories:
                metadata.append(f"Repositories: {public_repositories}")

        blocks.append(
            markdown(
                f"{offset + idx + 1}. <{user['idx_url']}|*{user_name}*>{NL}"
                f"_{' | '.join(metadata)}_{NL}"
                f"{bio}{NL}"
            )
        )

    if presentation.include_feedback:
        blocks.append(
            markdown(
                f"⚠️ *Extended search over OWASP community users is available at "
                f"<{get_absolute_url('/members')}?q={search_query}|{settings.SITE_NAME}>*{NL}"
                f"{FEEDBACK_SHARING_INVITE}"
            )
        )

    if presentation.include_pagination and (
        pagination_block := get_pagination_buttons(
            "users",
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
