"""OWASP app user search API."""

from __future__ import annotations

from typing import Any

from algoliasearch_django import raw_search as algolia_raw_search

from apps.github.models.user import User


def raw_search(model_class, query: str, params: dict[str, Any]) -> dict[str, Any]:
    """Perform a raw search on Algolia indices.

    Args:
    ----
        model_class: Django model class mapped to Algolia index
        query: Search query string
        params: Search parameters for Algolia

    Returns:
    -------
        Dictionary containing the search results with hits and pagination info

    """
    return algolia_raw_search(model_class, query, params)


def get_users(
    query: str | None = None,
    attributes: list[str] | None = None,
    limit: int = 25,
    page: int = 1,
    searchable_attributes: list[str] | None = None,
) -> dict[str, Any]:
    """Search for GitHub users with the given query parameters.

    Args:
    ----
        query: Optional search query string
        attributes: Optional list of attributes to retrieve
        limit: Maximum number of hits per page
        page: Page number (1-based)
        searchable_attributes: Optional list of attributes to search in

    Returns:
    -------
        Dictionary containing the search results with hits and pagination info

    """
    default_attributes = [
        "idx_avatar_url",
        "idx_created_at",
        "idx_email",
        "idx_followers_count",
        "idx_key",
        "idx_login",
        "idx_name",
        "idx_public_repositories_count",
        "idx_title",
        "idx_updated_at",
        "idx_url",
    ]

    params = {
        "attributesToHighlight": [],
        "attributesToRetrieve": attributes or default_attributes,
        "hitsPerPage": limit,
        "minProximity": 4,
        "page": page - 1,  # Algolia uses 0-based pagination
        "typoTolerance": "min",
    }

    if searchable_attributes:
        params["restrictSearchableAttributes"] = searchable_attributes

    return raw_search(User, query or "", params)
