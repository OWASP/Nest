"""OWASP app project search API."""

from algoliasearch_django import raw_search
from django.core.cache import cache
from django.http import JsonResponse

from apps.common.constants import DAY_IN_SECONDS
from apps.owasp.models.project import Project

PROJECT_CACHE_PREFIX = "project:"


def get_projects(query, attributes=None, limit=25, page=1):
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
        "page": page - 1,
    }

    return raw_search(Project, query, params)


def projects(request):
    """Search projects API endpoint."""
    query = request.GET.get("q", "")
    page = int(request.GET.get("page", 1))
    cache_key = f"{PROJECT_CACHE_PREFIX}{query}_page_{page}"
    projects = cache.get(cache_key)

    if projects is None:
        projects = get_projects(query=query, page=page)
        cache.set(cache_key, projects, DAY_IN_SECONDS)

    return JsonResponse(
        {
            "active_projects_count": Project.active_projects_count(),
            "projects": projects["hits"],
            "totalPages": projects["nbPages"],
        },
        safe=False,
    )
