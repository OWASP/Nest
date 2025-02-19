"""OWASP app Algolia search proxy API."""

import json

import requests
from algoliasearch.http.exceptions import AlgoliaException
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse

from apps.common.index import IndexBase
from apps.common.utils import get_user_ip_address
from apps.core.utils.params_mapping import get_params_for_index

CACHE_DURATION = 3600  # 1hr
CACHE_PREFIX = "algolia_proxy:"


def get_search_results(index_name, query, page, hits_per_page, ip_address=None):
    """Return search results for the given parameters."""
    search_params = get_params_for_index(index_name.split("_")[0])
    search_params.update(
        {
            "hitsPerPage": hits_per_page,
            "indexName": f"{settings.ENVIRONMENT.lower()}_{index_name}",
            "page": page - 1,
            "query": query,
        }
    )

    # Perform search
    client = IndexBase.get_client(ip_address=ip_address)
    response = client.search(search_method_params={"requests": [search_params]})
    search_result = response.results[0].to_dict()

    return {
        "hits": search_result.get("hits", []),
        "nbPages": search_result.get("nbPages", 0),
    }


def algolia_search(request):
    """Search Algolia API endpoint."""
    if request.method != "POST":
        return JsonResponse(
            {"error": f"Method {request.method} is not allowed"},
            status=requests.codes.method_not_allowed,
        )

    try:
        data = json.loads(request.body)

        index_name = data.get("indexName")
        limit = int(data.get("hitsPerPage", 25))
        page = int(data.get("page", 1))
        query = data.get("query", "")

        cache_key = f"{CACHE_PREFIX}{index_name}:{query}:{page}:{limit}"

        result = cache.get(cache_key)
        if result is not None:
            return JsonResponse(result)

        result = get_search_results(
            index_name,
            query,
            page,
            limit,
            ip_address=get_user_ip_address(request),
        )
        cache.set(cache_key, result, CACHE_DURATION)

        return JsonResponse(result)
    except (AlgoliaException, json.JSONDecodeError):
        return JsonResponse(
            {"error": "An internal error occurred. Please try again later."},
            status=500,
        )
