"""Validators for the search parameters of the Algolia endpoint."""

import re

from django.core.exceptions import ValidationError
from django.core.validators import validate_slug
from django.http import JsonResponse


def validate_index_name(index_name):
    """Validate index name."""
    if not index_name or not isinstance(index_name, str):
        return JsonResponse({"error": "indexName is required."}, status=400)
    try:
        validate_slug(index_name)
    except ValidationError:
        return JsonResponse({"error": "indexName must be a valid string (slug)."}, status=400)
    return None


def validate_limit(limit):
    """Validate limit."""
    if not isinstance(limit, int):
        return JsonResponse({"error": "hitsPerPage must be an integer."}, status=400)

    max_limit = 100
    min_limit = 1

    if limit < min_limit or limit > max_limit:
        return JsonResponse({"error": "hitsPerPage value must be between 1 and 100."}, status=400)

    return None


def validate_page(page):
    """Validate page."""
    if not isinstance(page, int):
        return JsonResponse({"error": "page must be an integer."}, status=400)

    if page <= 0:
        return JsonResponse({"error": "page value must be greater than 0."}, status=400)

    return None


def validate_query(query):
    """Validate query."""
    if query:
        if not isinstance(query, str):
            return JsonResponse({"error": "query must be a string."}, status=400)
        if not re.match(r"^[a-zA-Z0-9-_ ]*$", query):
            return JsonResponse(
                {
                    "error": """Invalid query value provided.
                    Only alphanumeric characters, hyphens, spaces and underscores are allowed."""
                },
                status=400,
            )
    return None


def validate_search_params(data):
    """Validate search parameters."""
    index_name = data.get("indexName")
    limit = data.get("hitsPerPage", 25)
    page = data.get("page", 1)
    query = data.get("query", "")

    if index_validation_error := validate_index_name(index_name):
        return index_validation_error

    if limit_validation_error := validate_limit(limit):
        return limit_validation_error

    if page_validation_error := validate_page(page):
        return page_validation_error

    if query_validation_error := validate_query(query):
        return query_validation_error

    return None
