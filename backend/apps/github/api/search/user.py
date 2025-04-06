"""OWASP app user search API."""

from __future__ import annotations

from apps.github.constants import default_attributes
from apps.github.models.user import User
from apps.github.utils import raw_search


def get_users(query, attributes=None, limit=25, page=1, searchable_attributes=None):
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
        "attributesToRetrieve": attributes or default_attributes,
        "hitsPerPage": limit,
        "minProximity": 4,
        "page": page - 1,  # Algolia uses 0-based pagination
        "typoTolerance": "min",
    }

    if searchable_attributes:
        params["restrictSearchableAttributes"] = searchable_attributes

    return raw_search(User, query or "", params)
