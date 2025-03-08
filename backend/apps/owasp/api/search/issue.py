"""OWASP app issue search API."""

from apps.common.typesense import Typesense
from apps.core.utils.params_mapping_typesense import get_typesense_params_for_index

ISSUE_CACHE_PREFIX = "issue:"


def get_issues(query, attributes=None, distinct=False, limit=25, page=1):
    """Return issues relevant to a search query."""
    search_parameters = get_typesense_params_for_index("issue")
    search_parameters.update(
        {
            "q": query,
            "page": page,
            "per_page": limit,
        }
    )

    if attributes:
        search_parameters["include_fields"] = attributes

    if distinct:
        search_parameters["group_by"] = "project_name"
        search_parameters["group_limit"] = 1

    client = Typesense.get_client()
    search_result = client.collections["issue"].documents.search(search_parameters)
    documents = [doc["document"] for doc in search_result.get("hits", [])]

    return {
        "hits": documents,
        "nbPages": (search_result.get("found", 0) + limit - 1) // limit,
        "totalHits": search_result.get("found", 0),
    }
