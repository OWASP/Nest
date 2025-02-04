"""OWASP app project search API."""

from functools import lru_cache

from algoliasearch_django import raw_search

from apps.owasp.models.project import Project


def get_projects(query, attributes=None, limit=25, page=1, searchable_attributes=None):
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

    if searchable_attributes:
        params["restrictSearchableAttributes"] = searchable_attributes

    return raw_search(Project, query, params)


@lru_cache
def get_gsoc_projects(year, attributes=None):
    """Return GSoC projects from Algolia."""
    from apps.owasp.models.project import Project

    query = f"gsoc{year}"
    searchable_attributes = ["idx_custom_tags", "idx_topics", "idx_tags"]

    params = {
        "attributesToHighlight": [],
        "restrictSearchableAttributes": searchable_attributes,
    }

    if attributes:
        params["attributesToRetrieve"] = attributes

    results = raw_search(Project, query, params)
    return results.get("hits", [])
