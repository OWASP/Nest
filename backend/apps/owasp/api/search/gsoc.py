"""OWASP app project gsoc search API """

from functools import lru_cache

from algoliasearch_django import raw_search

@lru_cache
def get_gsoc_projects(year, attributes=None):
    """Return GSoC projects from Algolia."""
    from apps.owasp.models.project import Project
    query = f"gsoc{year}"
    searchable_attributes = ["idx_custom_tags"]

    params = {
        "attributesToHighlight": [],
        "restrictSearchableAttributes": searchable_attributes,
    }
    
    if attributes:
        params["attributesToRetrieve"] = attributes

    results = raw_search(Project, query, params)
    projects = results.get('hits', [])

    return projects
