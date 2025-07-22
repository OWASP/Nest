"""OWASP app project search API."""

from __future__ import annotations

from algoliasearch_django import raw_search

from apps.owasp.models.project import Project


def get_projects(
    query: str,
    *,
    attributes: list | None = None,
    limit: int = 25,
    page: int = 1,
    searchable_attributes: list | None = None,
) -> dict:
    """Return projects relevant to a search query.

    Args:
        query (str): The search query string.
        attributes (list, optional): List of attributes to retrieve.
        limit (int, optional): Number of results per page.
        page (int, optional): Page number for pagination.
        searchable_attributes (list, optional): Attributes to restrict the search to.

    Returns:
        dict: Search results containing projects matching the query.

    """
    params = {
        "attributesToHighlight": [],
        "attributesToRetrieve": attributes
        or [
            "idx_contributors_count",
            "idx_forks_count",
            "idx_leaders",
            "idx_level",
            "idx_name",
            "idx_stars_count",
            "idx_summary",
            "idx_top_contributors",
            "idx_topics",
            "idx_type",
            "idx_updated_at",
            "idx_url",
        ],
        "hitsPerPage": limit,
        "minProximity": 4,
        "page": page - 1,
        "typoTolerance": "min",
    }

    if searchable_attributes:
        params["restrictSearchableAttributes"] = searchable_attributes

    return raw_search(Project, query, params)
