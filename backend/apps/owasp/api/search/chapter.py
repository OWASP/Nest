"""OWASP app chapter search API."""

from apps.common.typesense import Typesense
from apps.core.utils.params_mapping_typesense import get_typesense_params_for_index


def get_chapters(
    query,
    attributes=None,
    limit=25,
    page=1,
    searchable_attributes=None,
    searchable_attributes_weights=None,
):
    """Return chapters relevant to a search query."""
    search_parameters = get_typesense_params_for_index("chapter")
    search_parameters.update(
        {
            "q": query,
            "page": page,
            "per_page": limit,
        }
    )

    if attributes:
        search_parameters["include_fields"] = attributes

    if searchable_attributes:
        search_parameters["query_by"] = searchable_attributes
        search_parameters["query_by_weights"] = searchable_attributes_weights

    client = Typesense.get_client()
    search_result = client.collections["chapter"].documents.search(search_parameters)
    documents = [doc["document"] for doc in search_result.get("hits", [])]

    return {
        "hits": documents,
        "nbPages": (search_result.get("found", 0) + limit - 1) // limit,
        "totalHits": search_result.get("found", 0),
    }
