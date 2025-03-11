"""Validators for the search parameters of the Algolia endpoint."""

import re

from django.core.exceptions import ValidationError
from django.core.validators import validate_slug


def validate_index_name(index_name):
    """Validate index name."""
    if not index_name or not isinstance(index_name, str):
        message = "indexName is required and must be a string."
        raise ValidationError(message)

    try:
        validate_slug(index_name)
    except ValidationError:
        message = (
            "Invalid indexName value provided. "
            "Only alphanumeric characters hyphens and underscores are allowed."
        )
        raise ValidationError(message) from None


def validate_limit(limit):
    """Validate limit."""
    if not isinstance(limit, int):
        message = "hitsPerPage must be an integer."
        raise ValidationError(message)

    min_limit = 1
    max_limit = 1000
    if limit < min_limit or limit > max_limit:
        message = "hitsPerPage value must be between 1 and 100."
        raise ValidationError(message)


def validate_page(page):
    """Validate page."""
    if not isinstance(page, int):
        message = "page value must be an integer."
        raise ValidationError(message)

    if page <= 0:
        message = "page value must be a positive integer."
        raise ValidationError(message)


def validate_query(query):
    """Validate query."""
    if not query:
        return

    if not isinstance(query, str):
        message = "query must be a string."
        raise ValidationError(message)

    if not re.match(r"^[a-zA-Z0-9-_ ]*$", query):
        message = (
            "Invalid query value provided. "
            "Only alphanumeric characters, hyphens, spaces and underscores are allowed."
        )
        raise ValidationError(message)


def validate_facet_filters(facet_filters):
    """Validate facet filters."""
    if not isinstance(facet_filters, list):
        message = "facetFilters must be a list."
        raise ValidationError(message)


def validate_search_params(data):
    """Validate search parameters."""
    validate_facet_filters(data.get("facetFilters", []))
    validate_index_name(data.get("indexName"))
    validate_limit(data.get("hitsPerPage", 25))
    validate_page(data.get("page", 1))
    validate_query(data.get("query", ""))
