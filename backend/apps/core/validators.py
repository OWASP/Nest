"""Validators for the search parameters of the Algolia endpoint."""

from django.core.exceptions import ValidationError
from django.core.validators import validate_slug
from django.http import JsonResponse


def validate_string_slug(value):
    """Validate a string value as a slug."""
    if not value or not isinstance(value, str):
        return lambda field_name: JsonResponse(
            {"error": f"Missing or invalid {field_name}."}, status=400
        )
    try:
        validate_slug(value)
    except ValidationError:
        return lambda field_name: JsonResponse(
            {"error": f"Invalid {field_name} provided."}, status=400
        )
    return None


def validate_index_name(index_name):
    """Validate index name."""
    validation_error = validate_string_slug(index_name)
    if validation_error:
        return validation_error("indexName")

    return None


def validate_limit(limit):
    """Validate limit."""
    try:
        limit = int(limit)
        max_limit = 100
        min_limit = 1
        if limit < min_limit or limit > max_limit:
            return JsonResponse(
                {"error": "hitsPerPage value must be between 1 and 100."}, status=400
            )

    except ValueError:
        return JsonResponse({"error": "Invalid hitsPerPage value provided."}, status=400)

    return None


def validate_page(page):
    """Validate page."""
    try:
        page = int(page)
        if page <= 0:
            return JsonResponse({"error": "page value must be greater than 0."}, status=400)

    except ValueError:
        return JsonResponse({"error": "Invalid page value provided."}, status=400)

    return None


def validate_query(query):
    """Validate query."""
    if query:
        validation_error = validate_string_slug(query)
        if validation_error:
            return validation_error("query")
    return None


def validate_search_params(data):
    """Validate search parameters."""
    index_name = data.get("indexName")
    limit = data.get("hitsPerPage", 25)
    page = data.get("page", 1)
    query = data.get("query", "")

    index_validation_error = validate_index_name(index_name)

    if index_validation_error:
        return index_validation_error

    limit_validation_error = validate_limit(limit)
    if limit_validation_error:
        return limit_validation_error

    page_validation_error = validate_page(page)
    if page_validation_error:
        return page_validation_error

    query_validation_error = validate_query(query)
    if query_validation_error:
        return query_validation_error

    return None
