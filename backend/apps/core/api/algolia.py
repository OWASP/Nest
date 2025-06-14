"""OWASP app Algolia search proxy API."""

from __future__ import annotations

import json
from http import HTTPStatus
from typing import Any

from algoliasearch.http.exceptions import AlgoliaException
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponseNotAllowed, JsonResponse

from apps.common.index import IndexBase
from apps.common.utils import get_user_ip_address
from apps.core.utils.index import deep_camelize, get_params_for_index
from apps.core.validators import validate_search_params

CACHE_PREFIX = "algolia_proxy"
CACHE_TTL_IN_SECONDS = 3600  # 1 hour


def get_search_results(
    index_name: str,
    query: str,
    page: int,
    hits_per_page: int,
    facet_filters: list,
    ip_address=None,
) -> dict[str, Any]:
    """Return search results for the given parameters.

    Args:
        index_name (str): The name of the index.
        query (str): The search query.
        page (int): The page number.
        hits_per_page (int): The number of hits per page.
        facet_filters (list): The list of facet filters.
        ip_address (str, optional): The IP address of the user.

    Returns:
        dict: The search results containing hits and number of pages.

    """
    search_params = get_params_for_index(index_name.split("_")[0])
    search_params.update(
        {
            "hitsPerPage": hits_per_page,
            "indexName": f"{settings.ENVIRONMENT.lower()}_{index_name}",
            "page": page - 1,
            "query": query,
            "facetFilters": facet_filters,
        }
    )

    client = IndexBase.get_client(ip_address=ip_address)
    response = client.search(search_method_params={"requests": [search_params]})
    search_result = response.results[0].to_dict()

    return {
        "hits": deep_camelize(search_result["hits"]),
        "nbPages": search_result.get("nbPages", 0),
    }


def algolia_search(request: HttpRequest) -> JsonResponse | HttpResponseNotAllowed:
    """Search Algolia API endpoint.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: The search results or an error message.

    """
    if request.method != "POST":
        return JsonResponse(
            {"error": f"Method {request.method} is not allowed"},
            status=HTTPStatus.METHOD_NOT_ALLOWED,
        )

    try:
        data = json.loads(request.body)

        try:
            validate_search_params(data)
        except ValidationError as error:
            return JsonResponse({"error": error.message}, status=400)

        facet_filters = data.get("facetFilters", [])
        index_name = data.get("indexName")
        ip_address = get_user_ip_address(request)
        limit = data.get("hitsPerPage", 25)
        page = data.get("page", 1)
        query = data.get("query", "")

        cache_key = f"{CACHE_PREFIX}:{index_name}:{query}:{page}:{limit}"
        if index_name == "chapters":
            cache_key = f"{cache_key}:{ip_address}"

        result = cache.get(cache_key)
        if result is not None:
            return JsonResponse(result)

        result = get_search_results(
            index_name,
            query,
            page,
            limit,
            facet_filters,
            ip_address=ip_address,
        )
        cache.set(cache_key, result, CACHE_TTL_IN_SECONDS)

        return JsonResponse(result)
    except (AlgoliaException, json.JSONDecodeError):
        return JsonResponse(
            {"error": "An internal error occurred. Please try again later."},
            status=500,
        )
