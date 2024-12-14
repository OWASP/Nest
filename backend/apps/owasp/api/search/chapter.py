"""OWASP app chapter search API."""

from algoliasearch_django import raw_search
from django.http import JsonResponse

from apps.common.geocoding import get_ip_coordinates
from apps.common.utils import get_user_ip
from apps.owasp.models.chapter import Chapter


def get_chapters(query, attributes=None, limit=25, meta=None, page=0):
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
        "typoTolerance": "min",
        "page": page,
    }

    if coordinates := get_ip_coordinates(get_user_ip(meta)):
        params["aroundLatLng"] = f"{coordinates[0]},{coordinates[1]}"

    return raw_search(Chapter, query, params)


def chapters(request):
    """Search chapters API endpoint."""
    query = request.GET.get("q", "")
    page = int(request.GET.get("page", 0))
    chapters = get_chapters(query=query, page=page, meta=request.META)
    return JsonResponse(
        {
            "active_chapters_count": Chapter.active_chapters_count(),
            "chapters": chapters["hits"],
            "totalPages": chapters["nbPages"],
        },
        safe=False,
    )
