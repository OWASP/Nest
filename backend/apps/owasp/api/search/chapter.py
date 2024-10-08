"""OWASP app chapter search API."""

from algoliasearch_django import raw_search
from django.http import JsonResponse

from apps.common.geocoding import get_ip_coordinates
from apps.common.utils import get_user_ip
from apps.owasp.models.chapter import Chapter


def get_chapters(query, attributes=None, limit=25, meta=None):
    """Return chapters relevant to a search query."""
    params = {
        "attributesToHighlight": [],
        "attributesToRetrieve": attributes
        or [
            "idx_name",
            "idx_related_urls",
            "idx_suggested_location",
            "idx_summary",
        ],
        "hitsPerPage": limit,
        "minProximity": 4,
        "typoTolerance": "min",
    }

    if coordinates := get_ip_coordinates(get_user_ip(meta)):
        params["aroundLatLng"] = f"{coordinates[0]},{coordinates[1]}"

    return raw_search(Chapter, query, params)["hits"]


def chapters(request):
    """Search chapters API endpoint."""
    return JsonResponse(get_chapters(request.GET.get("q", ""), meta=request.META), safe=False)
