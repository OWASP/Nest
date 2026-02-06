"""Tests for structured search utility."""

from unittest.mock import MagicMock

from apps.api.rest.v0.structured_search import apply_structured_search

FIELD_SCHEMA = {
    "name": {"type": "string", "lookup": "icontains"},
    "stars": {"type": "number", "field": "stars_count"},
}


def make_queryset():
    qs = MagicMock()
    qs.filter.return_value = qs
    return qs


def test_string_search_conversion():
    qs = make_queryset()
    apply_structured_search(qs, "name:nest", FIELD_SCHEMA)

    qs.filter.assert_called_once()
    args, _ = qs.filter.call_args
    assert "name__icontains" in str(args[0])


def test_numeric_comparison_conversion():
    qs = make_queryset()
    apply_structured_search(qs, "stars:>10", FIELD_SCHEMA)

    args, _ = qs.filter.call_args
    assert "stars_count__gt" in str(args[0])


def test_field_alias_mapping():
    qs = make_queryset()
    apply_structured_search(qs, "stars:>=50", FIELD_SCHEMA)

    args, _ = qs.filter.call_args
    assert "stars_count__gte" in str(args[0])


def test_invalid_syntax_returns_original_queryset():
    qs = make_queryset()
    apply_structured_search(qs, "stars:!!!", FIELD_SCHEMA)

    qs.filter.assert_called_once()
    args, _ = qs.filter.call_args

    assert "stars_count" not in str(args[0])


def test_unknown_field_is_ignored():
    qs = make_queryset()
    apply_structured_search(qs, "invalid_field:value", FIELD_SCHEMA)

    args, _ = qs.filter.call_args
    assert "invalid_field" not in str(args[0])
