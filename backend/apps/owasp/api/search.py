"""OWASP app search views."""

from algoliasearch_django import raw_search
from django.http import JsonResponse

from apps.github.models import Issue


def search_project(_request):
    """Search project view."""
    issues_params = {
        "attributesToRetrieve": [
            "idx_created_at",
            "idx_project_name",
            "idx_repository_languages",
            "idx_title",
            "idx_url",
        ],
        # "filters": "idx_labels:issue",
        "hitsPerPage": 100,
    }

    term = "python first issue"
    issues = raw_search(Issue, term, issues_params)["hits"]

    return JsonResponse(issues, safe=False)
