"""OWASP app chapter search API."""

from algoliasearch_django import raw_search

from apps.owasp.models.chapter import Chapter


def get_chapters(query, page=1, attributes=None, limit=25, searchable_attributes=None):
    """Return chapters relevant to a search query."""
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
        "page": page,
        "typoTolerance": "min",
    }

    if searchable_attributes:
        params["restrictSearchableAttributes"] = searchable_attributes

    return raw_search(Chapter, query, params)
