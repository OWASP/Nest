"""OWASP app Algolia search proxy API."""

from django.http import JsonResponse
from django.core.cache import cache
import json
from django.conf import settings
from apps.common.index import IndexBase
from apps.owasp.api.search.params_mapping import get_params_for_index

CACHE_DURATION = 3600 #1hr
CACHE_PREFIX = "algolia_proxy:"


def get_search_results(index_name, query, page, hits_per_page):
    """Return search results for the given parameters."""
    env = settings.ENVIRONMENT.lower()
    full_index_name = f"{env}_{index_name}"

    search_params = get_params_for_index(index_name.split("_")[0])
    search_params.update({
        "indexName": full_index_name,
        "query": query,
        "page": page - 1,
        "hitsPerPage": hits_per_page,
    })

    # Perform search
    client = IndexBase.get_client()
    response = client.search(search_method_params={"requests": [search_params]})
    search_result = response.results[0].to_dict()

    return {
        "hits": search_result.get("hits", []),
        "nbPages": search_result.get("nbPages", 0),
    }


def algolia_search(request):
    """Search Algolia API endpoint."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            index_name = data.get("indexName")
            query = data.get("query", "")
            current_page = data.get("page", 1)
            hits_per_page = data.get("hitsPerPage")

            cache_key = f"{CACHE_PREFIX}{index_name}:{query}:{current_page}:{hits_per_page}"

            cached_result = cache.get(cache_key)
            if cached_result:
                return JsonResponse(cached_result)

            search_results = get_search_results(index_name, query, current_page, hits_per_page)

            # Cache the result
            cache.set(cache_key, search_results, CACHE_DURATION)

            return JsonResponse(search_results)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)