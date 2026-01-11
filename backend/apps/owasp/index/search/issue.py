"""OWASP app issue search API."""

from __future__ import annotations

from algoliasearch_django import raw_search

from apps.github.models.issue import Issue

ISSUE_CACHE_PREFIX = "issue:"


def get_issues(
    query: str,
    *,
    attributes: list | None = None,
    distinct: bool = False,
    limit: int = 25,
    page: int = 1,
) -> dict:
    """Return issues relevant to a search query.

    Args:
        query (str): The search query string.
        attributes (list, optional): List of attributes to retrieve.
        distinct (bool, optional): Whether to enable distinct mode.
        limit (int, optional): Number of results per page.
        page (int, optional): Page number for pagination.

    Returns:
        dict: Search results containing issues matching the query.

    """
    params = {
        "attributesToHighlight": [],
        "attributesToRetrieve": attributes
        or [
            "idx_comments_count",
            "idx_created_at",
            "idx_hint",
            "idx_labels",
            "idx_project_name",
            "idx_project_url",
            "idx_repository_languages",
            "idx_summary",
            "idx_tags",
            "idx_title",
            "idx_updated_at",
            "idx_url",
        ],
        "hitsPerPage": limit,
        "page": page - 1,
    }

    if distinct:
        params["distinct"] = 1

    return raw_search(Issue, query, params)
