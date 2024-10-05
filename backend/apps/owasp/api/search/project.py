"""OWASP app project search API."""

from algoliasearch_django import raw_search
from django.http import JsonResponse
from django.core.cache import cache
from apps.owasp.constants import DAY_IN_SECONDS
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

    project_cache_key = f"Project:{query}"
    project_cache_result = cache.get(project_cache_key)

    # check if cache exists

    if project_cache_result is None:
        search_result = raw_search(Project, query, params)["hits"]
        # save to cache, empty queries excluded
        if query != "":
            cache.set(project_cache_key,search_result,DAY_IN_SECONDS)

    else:
        search_result=project_cache_result
    
    return search_result


def projects(request):
    """Search projects API endpoint."""
    return JsonResponse(get_projects(request.GET.get("q", "")), safe=False)
