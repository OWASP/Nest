"""OWASP app committee search API."""

from algoliasearch_django import raw_search
from django.http import JsonResponse

from apps.common.index import IndexSynonymsMixin
from apps.owasp.models.committee import Committee


def get_committees(query, attributes=None, limit=25, page=1):
    """Return committees relevant to a search query."""
    params = {
        "attributesToHighlight": [],
        "attributesToRetrieve": attributes
        or [
            "idx_created_at",
            "idx_leaders",
            "idx_name",
            "idx_related_urls",
            "idx_summary",
            "idx_top_contributors",
            "idx_updated_at",
            "idx_url",
        ],
        "hitsPerPage": limit,
        "minProximity": 4,
        "page": page - 1,
        "typoTolerance": "min",
    }

    return raw_search(Committee, query, params)


def committees(request):
    """Search committees API endpoint."""
    page = int(request.GET.get("page", 1))
    query = request.GET.get("q", "")
    active_committees_count = IndexSynonymsMixin.get_algolia_index_count("local_committees")
    committees = get_committees(query=query, page=page)
    return JsonResponse(
        {
            "active_committees_count": active_committees_count,
            "committees": committees["hits"],
            "total_pages": committees["nbPages"],
        },
        safe=False,
    )
