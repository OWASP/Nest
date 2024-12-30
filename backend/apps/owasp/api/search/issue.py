"""OWASP app issue search API."""

from algoliasearch_django import raw_search

from apps.github.models.issue import Issue

ISSUE_CACHE_PREFIX = "issue:"


def get_issues(query, attributes=None, distinct=False, limit=25, page=1):
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
        "page": page - 1,
    }

    if distinct:
        params["distinct"] = 1

    return raw_search(Issue, query, params)
