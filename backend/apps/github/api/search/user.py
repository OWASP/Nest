"""OWASP app user search API."""

from __future__ import annotations

from algoliasearch_django import raw_search

from apps.github.models.user import User


def get_users(
    query: str,
    attributes: list | None = None,
    limit: int = 25,
    page: int = 1,
    searchable_attributes: list | None = None,
) -> dict:
    """Return users relevant to a search query.

    Args:
        query (str): The search query string.
        attributes (list, optional): List of attributes to retrieve.
        limit (int): Maximum number of users to return.
        page (int): The page number for pagination.
        searchable_attributes (list, optional): List of attributes to restrict the search to.

    Returns:
        dict: Search results containing users and metadata.

    """
    params = {
        "attributesToHighlight": [],
        "attributesToRetrieve": attributes
        or [
            "idx_avatar_url",
            "idx_bio",
            "idx_company",
            "idx_contributions",
            "idx_created_at",
            "idx_email",
            "idx_followers_count",
            "idx_following_count",
            "idx_issues_count",
            "idx_key",
            "idx_location",
            "idx_login",
            "idx_name",
            "idx_public_repositories_count",
            "idx_title",
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

    return raw_search(User, query, params)
