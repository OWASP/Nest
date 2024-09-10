"""OWASP app issue search API."""

from algoliasearch_django import raw_search
from django.http import JsonResponse

from apps.github.models import Issue


def project_issues(request):
    """Search project issues view."""
    issues_params = {
        "attributesToRetrieve": [
            "idx_created_at",
            "idx_project_name",
            "idx_repository_languages",
            "idx_title",
            "idx_url",
        ],
        "hitsPerPage": 25,
    }

    return JsonResponse(
        raw_search(Issue, request.GET.get("q", ""), issues_params)["hits"],
        safe=False,
    )
