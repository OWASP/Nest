"""OWASP app issue search API."""

from algoliasearch_django import raw_search
from django.http import JsonResponse
from django.core.cache import cache
from apps.github.models.issue import Issue


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

    issue_cache_key=f"algolia_search_{query}"
    issue_cache_result = cache.get(issue_cache_key)
    
    #check if cache exists
    
    if issue_cache_result:
        return issue_cache_result
    
    search_result = raw_search(Issue,query,params)["hits"]
    
    #save to cache
    
    cache.set(issue_cache_key,search_result,86400)
    return search_result


def project_issues(request):
    """Search project issues API endpoint."""
    return JsonResponse(get_issues(request.GET.get("q", "")), safe=False)
