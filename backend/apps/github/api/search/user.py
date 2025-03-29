"""OWASP app user search API."""

from algoliasearch_django import raw_search

from apps.github.models.user import User


def get_users(query, attributes=None, limit=25, page=1, searchable_attributes=None):
    """Return users relevant to a search query.

    Args:
        query (str): The search query string.
        attributes (list, optional): List of attributes to retrieve. Defaults to None.
        limit (int): Maximum number of users to return. Defaults to 25.
        page (int): The page number for pagination. Defaults to 1.
        searchable_attributes (list, optional): List of attributes to restrict the search to. Defaults to None.

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
