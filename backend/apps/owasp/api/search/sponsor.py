"""OWASP app sponsor search API."""

from algoliasearch_django import raw_search
from apps.owasp.models.sponsor import Sponsor

def get_sponsors(query, attributes=None, limit=25, page=1):
    params = {
        "attributesToHighlight": [],
        "attributesToRetrieve": attributes
        or [
            "idx_name",
            "idx_sort_name",
            "idx_description",
            "idx_url",
            "idx_job_url",
            "idx_image",
            "idx_member_type",
            "idx_sponsor_type",
            "idx_member_level",
            "idx_sponsor_level",
            "idx_is_member",
            "idx_is_active_sponsor"
        ],
        "hitsPerPage": limit,
        "minProximity": 4,
        "page": page - 1,
        "typoTolerance": "min"
    }
    return raw_search(Sponsor, query, params)
