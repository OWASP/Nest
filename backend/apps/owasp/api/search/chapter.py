"""OWASP app chapter search API."""

from algoliasearch_django import raw_search

from apps.owasp.models.chapter import Chapter


def get_chapters(query, attributes=None, limit=25, page=1, searchable_attributes=None):
    """Return chapters relevant to a search query.

    Args:
        query (str): The search query string.
        attributes (list, optional): List of attributes to retrieve. Defaults to None.
        limit (int, optional): Number of results per page. Defaults to 25.
        page (int, optional): Page number for pagination. Defaults to 1.
        searchable_attributes (list, optional): Attributes to restrict the search to. Defaults to None.

    Returns:
        dict: Search results containing chapters matching the query.
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

    if searchable_attributes:
        params["restrictSearchableAttributes"] = searchable_attributes

    return raw_search(Chapter, query, params)
