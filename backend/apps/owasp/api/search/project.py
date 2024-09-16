"""OWASP app project search API."""

from algoliasearch_django import raw_search
from django.http import JsonResponse

from apps.owasp.models.project import Project


def get_projects(query, limit=25):
    """Return projects relevant to a search query."""
    params = {
        "attributesToRetrieve": [
            "idx_description",
            "idx_name",
            "idx_topics",
            "idx_url",
        ],
        "hitsPerPage": limit,
        "typoTolerance": "min",
        "minProximity": 4,
    }

    return raw_search(Project, query, params)["hits"]


def projects(request):
    """Search projects API endpoint."""
    return JsonResponse(get_projects(request.GET.get("q", "")), safe=False)
