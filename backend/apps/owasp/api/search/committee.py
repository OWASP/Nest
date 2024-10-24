"""OWASP app committee search API."""

from algoliasearch_django import raw_search
from django.http import JsonResponse

from apps.owasp.models.committee import Committee


def get_committees(query, attributes=None, limit=25):
    """Return committees relevant to a search query."""
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
    }

    return raw_search(Committee, query, params)["hits"]


def committees(request):
    """Search committees API endpoint."""
    return JsonResponse(
        {
            "active_committees_count": Committee.active_committees_count(),
            "committees": get_committees(request.GET.get("q", "")),
        },
        safe=False,
    )
