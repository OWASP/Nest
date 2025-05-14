"""OWASP app committee search API."""

from __future__ import annotations

from algoliasearch_django import raw_search

from apps.owasp.models.committee import Committee


def get_committees(
    query: str,
    *,
    attributes: list | None = None,
    limit: int = 25,
    page: int = 1,
) -> dict:
    """Return committees relevant to a search query.

    Args:
        query (str): The search query string.
        attributes (list, optional): List of attributes to retrieve.
        limit (int, optional): Number of results per page.
        page (int, optional): Page number for pagination.

    Returns:
        dict: Search results containing committees matching the query.

    """
    params = {
        "attributesToHighlight": [],
        "attributesToRetrieve": attributes
        or [
            "idx_created_at",
            "idx_leaders",
            "idx_name",
            "idx_related_urls",
            "idx_summary",
            "idx_top_contributors",
            "idx_updated_at",
            "idx_url",
        ],
        "hitsPerPage": limit,
        "minProximity": 4,
        "page": page - 1,
        "typoTolerance": "min",
    }

    return raw_search(Committee, query, params)
