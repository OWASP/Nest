"""OWASP app issue search API."""

from algoliasearch_django import raw_search
from django.http import JsonResponse

from apps.github.models.issue import Issue


def get_issues(query, distinct=False, limit=25):
    """Return issues relevant to a search query."""
    params = {
        "attributesToRetrieve": [
            "idx_created_at",
            "idx_project_name",
            "idx_repository_languages",
            "idx_summary",
            "idx_title",
            "idx_url",
        ],
        "hitsPerPage": limit,
    }

    if distinct:
        params["distinct"] = 1

    return raw_search(Issue, query, params)["hits"]


def project_issues(request):
    """Search project issues view."""
    return JsonResponse(get_issues(request.GET.get("q", "")), safe=False)
