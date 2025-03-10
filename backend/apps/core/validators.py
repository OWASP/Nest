"""Validators for the search parameters of the Algolia endpoint."""

import re

from django.core.exceptions import ValidationError
from django.core.validators import validate_slug


def validate_index_name(index_name):
    """Validate index name."""
    if not index_name or not isinstance(index_name, str):
        return "indexName is required and must be a string."
    try:
        validate_slug(index_name)
    except ValidationError:
        return "IndexName must be a valid slug."
    return None


def validate_limit(limit):
    """Validate limit."""
    if not isinstance(limit, int):
        return "hitsPerPage must be an integer."

    max_limit = 100
    min_limit = 1

    if limit < min_limit or limit > max_limit:
        return "hitsPerPage value must be between 1 and 100."

    return None


def validate_page(page):
    """Validate page."""
    if not isinstance(page, int):
        return "page must be an integer."

    if page <= 0:
        return "page value must be greater than 0."

    return None


def validate_query(query):
    """Validate query."""
    if query:
        if not isinstance(query, str):
            return "query must be a string."
        if not re.match(r"^[a-zA-Z0-9-_ ]*$", query):
            return """Invalid query value provided.
                    Only alphanumeric characters, hyphens, spaces and underscores are allowed."""
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
