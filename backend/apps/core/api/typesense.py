import json

from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from apps.common.typesense import Typesense
from apps.common.utils import get_geolocation, get_user_ip_address
from apps.core.utils.params_mapping_typesense import get_typesense_params_for_index

CACHE_PREFIX = "typesense_proxy"
CACHE_TTL_IN_SECONDS = 3600  # 1 hour


def get_typesense_search_results(index_name, query, page, hits_per_page, ip_address=None):
    """Return search results for the given parameters and index."""
    search_parameters = get_typesense_params_for_index(index_name)

    search_parameters.update(
        {
            "q": query,
            "page": page,
            "per_page": hits_per_page,
        }
    )

    if index_name == "chapter" and ip_address:
        user_lat, user_lng = get_geolocation("106.222.213.86")
        if user_lat and user_lng:
            search_parameters["sort_by"] = f"_geoloc({user_lat},{user_lng}):asc,updated_at:desc"

    client = Typesense.get_client()
    search_result = client.collections[index_name].documents.search(search_parameters)
    documents = [doc["document"] for doc in search_result.get("hits", [])]

    return {
        "hits": documents,
        "nbPages": (search_result.get("found", 0) + hits_per_page - 1) // hits_per_page,
        "totalHits": search_result.get("found", 0),
    }


@require_POST
def typesense_search(request):
    """Perform a generic Typesense search API endpoint."""
    try:
        data = json.loads(request.body)

        index_name = data.get("indexName")
        hits_per_page = min(int(data.get("hitsPerPage", 25)), 250)
        page = int(data.get("page", 1))
        query = data.get("query", "")
        ip_address = get_user_ip_address(request=request)

        cache_key = f"{CACHE_PREFIX}:{index_name}:{query}:{page}:{hits_per_page}"
        if "chapters" in index_name:
            cache_key = f"{cache_key}:{ip_address}"

        result = cache.get(cache_key)
        # if result is not None:
        # return JsonResponse(result)

        result = get_typesense_search_results(
            index_name,
            query,
            page,
            hits_per_page,
            ip_address=ip_address,
        )

        cache.set(cache_key, result, CACHE_TTL_IN_SECONDS)

        return JsonResponse(result)

    except Exception as e:
        return JsonResponse(
            {"error": "An internal error occurred. Please try again later. " + str(e)},
            status=500,
        )
