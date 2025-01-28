"""OWASP app sponsor search API."""

from algoliasearch_django import raw_search

from apps.owasp.models.sponsor import Sponsor


def get_sponsors(query, attributes=None, limit=25, page=1):
    """Return sponsors relevant to a search query."""
    params = {
        "attributesToHighlight": [],
        "attributesToRetrieve": attributes
        or [
            "idx_name",
            "idx_sort_name",
            "idx_description",
            "idx_url",
            "idx_job_url",
            "idx_image_path",
            "idx_member_type",
            "idx_sponsor_type",
            "idx_is_member",
        ],
        "hitsPerPage": limit,
        "minProximity": 4,
        "page": page - 1,
        "typoTolerance": "min",
        "facetFilters": [],
    }

    return raw_search(Sponsor, query, params)
