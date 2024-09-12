"""OWASP app project search API."""

from algoliasearch_django import raw_search
from django.http import JsonResponse

from apps.owasp.models import Project


def projects(request):
    """Search projects view."""
    params = {
        "attributesToRetrieve": [
            "idx_name",
            "idx_topics",
            "idx_url",
        ],
        "typoTolerance": "min",
        "hitsPerPage": 25,
        "minProximity": 4,
    }

    return JsonResponse(
        raw_search(Project, request.GET.get("q", ""), params)["hits"],
        safe=False,
    )
