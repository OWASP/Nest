"""Tests for structured search utility."""

from unittest.mock import MagicMock

from apps.api.rest.v0.structured_search import apply_structured_search

FIELD_SCHEMA = {
    "name": {
        "type": "string",
        "lookup": "icontains",
    },
    "stars_count": {
        "type": "number",
        "field": "stars_count",
    },
}


def make_queryset():
    qs = MagicMock()
    qs.filter.return_value = qs
    return qs


def test_invalid_query_fails_safely():
    qs = make_queryset()

    apply_structured_search(qs, "stars>>>", FIELD_SCHEMA)

    qs.filter.assert_called_once()


def test_string_search_applied():
    qs = make_queryset()

    apply_structured_search(qs, "name:nest", FIELD_SCHEMA)

    qs.filter.assert_called_once()


def test_number_search_applied():
    qs = make_queryset()

    apply_structured_search(qs, "stars_count>10", FIELD_SCHEMA)

    qs.filter.assert_called_once()


def test_unknown_field_is_ignored():
    qs = make_queryset()

    apply_structured_search(qs, "unknown:abc", FIELD_SCHEMA)

    qs.filter.assert_called_once()
