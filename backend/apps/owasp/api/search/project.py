"""OWASP app project search API."""

from algoliasearch_django import raw_search
from django.http import JsonResponse

from apps.owasp.models.project import Project


def get_projects(query, attributes=None, limit=25):
    """Return projects relevant to a search query."""
    params = {
        "attributesToHighlight": [],
        "attributesToRetrieve": attributes
        or [
            "idx_contributors_count",
            "idx_forks_count",
            "idx_leaders",
            "idx_level",
            "idx_name",
            "idx_stars_count",
            "idx_summary",
            "idx_top_contributors",
            "idx_topics",
            "idx_type",
            "idx_updated_at",
            "idx_url",
        ],
        "hitsPerPage": limit,
        "minProximity": 4,
        "typoTolerance": "min",
    }

    return raw_search(Project, query, params)["hits"]


def projects(request):
    """Search projects API endpoint."""
    return JsonResponse(
        {
            "active_projects_count": Project.active_projects_count(),
            "projects": get_projects(request.GET.get("q", "")),
        },
        safe=False,
    )
