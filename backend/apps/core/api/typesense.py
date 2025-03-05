"""OWASP app Typesense search API."""

import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from apps.common.typesense import Typesense
from apps.common.utils import get_geolocation


@require_POST
def typesense_search(request):
    """Return Typesense chapter search results."""
    try:
        data = json.loads(request.body)
        query = data.get("query", "")
        page = int(data.get("page", 1))
        hits_per_page = min(int(data.get("hitsPerPage", 25)), 250)
        # ip_address = get_user_ip_address(request)
        # random ip (for now)
        user_lat, user_lng = get_geolocation("136.63.36.183")
        search_parameters = {
            "q": query,
            "query_by": "name,country,region",
            "query_by_weights": "5,3,2",  # Prioritize name > country > region
            "page": page,
            "per_page": hits_per_page,
            "sort_by": f"location({user_lat},{user_lng}):asc,updated_at:desc,created_at:asc",
            "num_typos": 2,  # Allow typo tolerance like Algolia
            "prioritize_exact_match": True,  # Rank exact matches higher
        }
        client = Typesense.get_client()
        search_result = client.collections["chapter"].documents.search(search_parameters)

        return JsonResponse(
            {
                "hits": search_result["hits"],
                "nbPages": search_result["found"] // hits_per_page + 1,
                "totalHits": search_result["found"],
            }
        )
    except (client.exceptions.TypesenseClientError, json.JSONDecodeError):
        return JsonResponse(
            {"error": "An internal error occurred. Please try again later."},
            status=500,
        )
