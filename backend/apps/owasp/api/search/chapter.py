"""OWASP app chapter search API."""

from algoliasearch_django import raw_search

from apps.common.geocoding import get_ip_coordinates
from apps.common.utils import get_user_ip
from apps.owasp.models.chapter import Chapter


def get_chapters(query, attributes=None, limit=25, meta=None, page=1):
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
        "page": page - 1,
        "typoTolerance": "min",
    }

    if coordinates := get_ip_coordinates(get_user_ip(meta)):
        params["aroundLatLng"] = f"{coordinates[0]},{coordinates[1]}"

    return raw_search(Chapter, query, params)
