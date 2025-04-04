"""OWASP app project search API."""

from apps.common.typesense import Typesense
from apps.core.utils.params_mapping_typesense import get_typesense_params_for_index



def get_projects(query, attributes=None, limit=25, page=1, searchable_attributes=None):
    """Return projects relevant to a search query.

    Args:
        query (str): The search query string.
        attributes (list, optional): List of attributes to retrieve.
        limit (int, optional): Number of results per page.
        page (int, optional): Page number for pagination.
        searchable_attributes (list, optional): Attributes to restrict the search to.

    Returns:
        dict: Search results containing projects matching the query.

    """
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
        search_parameters["query_by"] = searchable_attributes
        search_parameters["query_by_weights"] = searchable_attributes_weights

    client = Typesense.get_client()
    search_result = client.collections["project"].documents.search(search_parameters)
    documents = [doc["document"] for doc in search_result.get("hits", [])]

    return {
        "hits": documents,
        "nbPages": (search_result.get("found", 0) + limit - 1) // limit,
        "totalHits": search_result.get("found", 0),
    }
