"""OWASP app project search API."""

from algoliasearch_django import raw_search

from apps.owasp.models.project import Project

PROJECT_CACHE_PREFIX = "project:"


def get_projects(query, attributes=None, limit=25, page=1, restrict_attributes=None):
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
        "page": page - 1,
        "typoTolerance": "min",
    }

    if restrict_attributes:
        params["restrictSearchableAttributes"] = restrict_attributes

    return raw_search(Project, query, params)
