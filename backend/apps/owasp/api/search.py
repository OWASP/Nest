"""OWASP app search views."""

from algoliasearch_django import raw_search
from django.http import JsonResponse

from apps.github.models import Issue


def search_project(request):
    """Search project view."""
    issues_params = {
        "attributesToRetrieve": [
            "idx_created_at",
            "idx_project_name",
            "idx_repository_languages",
            "idx_title",
            "idx_url",
        ],
        "hitsPerPage": 100,
    }

    issues = raw_search(Issue, request.GET.get("q", ""), issues_params)["hits"]

    return JsonResponse(issues, safe=False)
