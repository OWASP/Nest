"""OWASP app issue search API."""

from algoliasearch_django import raw_search
from django.core.cache import cache
from django.http import JsonResponse

from apps.common.constants import DAY_IN_SECONDS
from apps.github.models.issue import Issue

ISSUE_CACHE_PREFIX = "issue:"


def get_issues(query, attributes=None, distinct=False, limit=25):
    """Return issues relevant to a search query."""
    params = {
        "attributesToHighlight": [],
        "attributesToRetrieve": attributes
        or [
            "idx_comments_count",
            "idx_created_at",
            "idx_hint",
            "idx_labels",
            "idx_project_name",
            "idx_project_url",
            "idx_repository_languages",
            "idx_summary",
            "idx_title",
            "idx_updated_at",
            "idx_url",
        ],
        "hitsPerPage": limit,
    }

    if distinct:
        params["distinct"] = 1

    return raw_search(Issue, query, params)["hits"]


def project_issues(request):
    """Search project issues API endpoint."""
    query = request.GET.get("q", "")
    cache_key = f"{ISSUE_CACHE_PREFIX}{query}"
    issues = cache.get(cache_key)

    if issues is None:
        issues = get_issues(query)
        cache.set(cache_key, issues, DAY_IN_SECONDS)

    return JsonResponse(
        {
            "open_issues_count":Issue.open_issues_count(),
            "issues": issues,
        },
        safe=False
    )
