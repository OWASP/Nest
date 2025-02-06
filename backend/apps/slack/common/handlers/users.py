"""Handler for OWASP Users Slack functionality."""

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
    page: int = 1,
    search_query: str = "",
    limit: int = 10,
    presentation: EntityPresentation | None = None,
):
    """Get users blocks."""
    from apps.github.api.search.user import get_users

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
        user_name = Truncator(escape(user_name_raw)).chars(
            presentation.name_truncation, truncate=TRUNCATION_INDICATOR
        )

        bio = Truncator(escape(user.get("idx_bio", "") or "")).chars(
            presentation.summary_truncation, truncate=TRUNCATION_INDICATOR
        )

        location = escape(user.get("idx_location", ""))
        company = escape(user.get("idx_company", ""))
        email = escape(user.get("idx_email", ""))
        user_contributions = user.get("idx_contributions", 0)
        followers_count = user.get("idx_followers_count", 0)
        following_count = user.get("idx_following_count", 0)
        public_repos = user.get("idx_public_repositories_count", 0)
        issues_count = user.get("idx_issues_count", 0)

        updated_text = (
            f"_Updated {natural_date(int(user['idx_updated_at']))}_{NL}"
            if presentation.include_timestamps
            else ""
        )

        meta_info = []
        contributions_text = ""
        if presentation.include_metadata:
            if company:
                meta_info.append(f"*Company:* {company}")
            if email:
                meta_info.append(f"*Email:* {email}")
            if location:
                meta_info.append(f"*Location:* {location}")
            if followers_count:
                meta_info.append(f"*Followers:* {followers_count}")
            if following_count:
                meta_info.append(f"*Following:* {following_count}")
            if public_repos:
                meta_info.append(f"*Public Repos:* {public_repos}")
            if issues_count:
                meta_info.append(f"*Issues:* {issues_count}")
            if user_contributions:
                contributions_text += f"*Contributions*{NL}"
                for contrib_info in user_contributions:
                    repo_name = contrib_info.get("repository_name", "N/A")
                    contrib_count = contrib_info.get("contributions_count", 0)
                    contributions_text += f"*{repo_name}:* {contrib_count} contributions{NL}"

        metadata_text = f"_{' | '.join(meta_info)}_{NL}" if meta_info else ""
        metadata_text += contributions_text
        blocks.append(
            markdown(
                f"{offset + idx + 1}. <{user['idx_url']}|*{user_name}*>{NL}"
                f"{updated_text}"
                f"{bio}{NL}"
                f"{metadata_text}"
            )
        )

    if presentation.include_feedback:
        blocks.append(
            markdown(
                f"⚠️ *Extended search over GitHub users is available at "
                f"<{get_absolute_url('community/users')}?q={search_query}|{settings.SITE_NAME}>*{NL}"
                f"{FEEDBACK_CHANNEL_MESSAGE}"
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
