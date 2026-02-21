"""Tests for structured search utility."""

from unittest.mock import MagicMock, patch

from apps.api.rest.v0.structured_search import QueryParserError, apply_structured_search

FIELD_SCHEMA = {
    "name": {"type": "string", "lookup": "icontains"},
    "stars": {"type": "number", "field": "stars_count"},
}


def make_queryset():
    qs = MagicMock()
    qs.filter.return_value = qs
    return qs


class TestApplyStructuredSearch:
    def test_string_search_conversion(self):
        qs = make_queryset()
        apply_structured_search(qs, "name:nest", FIELD_SCHEMA)

        qs.filter.assert_called_once()
        args, _ = qs.filter.call_args
        assert "name__icontains" in str(args[0])

    def test_numeric_comparison_conversion(self):
        qs = make_queryset()
        apply_structured_search(qs, "stars:>10", FIELD_SCHEMA)

        args, _ = qs.filter.call_args
        assert "stars_count__gt" in str(args[0])

    def test_field_alias_mapping(self):
        qs = make_queryset()
        apply_structured_search(qs, "stars:>=50", FIELD_SCHEMA)

        args, _ = qs.filter.call_args
        assert "stars_count__gte" in str(args[0])

    def test_invalid_syntax_skips_condition_and_applies_empty_filter(self):
        qs = make_queryset()
        result = apply_structured_search(qs, "stars:!!!", FIELD_SCHEMA)

        qs.filter.assert_called_once()
        args, _ = qs.filter.call_args
        assert "stars_count" not in str(args[0])
        assert result == qs.filter.return_value

    def test_unknown_field_is_ignored(self):
        qs = make_queryset()
        apply_structured_search(qs, "invalid_field:value", FIELD_SCHEMA)

        args, _ = qs.filter.call_args
        assert "invalid_field" not in str(args[0])

    def test_empty_query_returns_original_queryset(self):
        """Test that empty query returns original queryset."""
        qs = make_queryset()
        result = apply_structured_search(qs, "", FIELD_SCHEMA)

        assert result == qs
        qs.filter.assert_not_called()

    def test_none_query_returns_original_queryset(self):
        """Test that None query returns original queryset."""
        qs = make_queryset()
        result = apply_structured_search(qs, None, FIELD_SCHEMA)

        assert result == qs
        qs.filter.assert_not_called()

    def test_invalid_number_value_is_skipped(self):
        """Test that invalid number value is skipped."""
        qs = make_queryset()
        apply_structured_search(qs, "stars:not_a_number", FIELD_SCHEMA)

        qs.filter.assert_called_once()
        args, _ = qs.filter.call_args
        assert "stars_count" not in str(args[0])

    def test_less_than_operator(self):
        """Test less than operator for numeric fields."""
        qs = make_queryset()
        apply_structured_search(qs, "stars:<5", FIELD_SCHEMA)

        args, _ = qs.filter.call_args
        assert "stars_count__lt" in str(args[0])

    def test_string_field_with_exact_lookup(self):
        """Test string field with exact lookup."""
        schema_with_exact = {
            "name": {"type": "string", "lookup": "exact"},
        }
        qs = make_queryset()
        apply_structured_search(qs, "name:test", schema_with_exact)

        qs.filter.assert_called_once()
        args, _ = qs.filter.call_args
        assert "name__icontains" not in str(args[0])

    def test_less_than_equal_operator(self):
        """Test less than or equal operator for numeric fields."""
        qs = make_queryset()
        apply_structured_search(qs, "stars:<=100", FIELD_SCHEMA)

        args, _ = qs.filter.call_args
        assert "stars_count__lte" in str(args[0])

    def test_equal_operator_numeric(self):
        """Test equals operator for numeric fields."""
        qs = make_queryset()
        apply_structured_search(qs, "stars:=42", FIELD_SCHEMA)

        args, _ = qs.filter.call_args
        assert "stars_count" in str(args[0])

    def test_multiple_conditions(self):
        """Test query with multiple field conditions."""
        qs = make_queryset()
        apply_structured_search(qs, "name:nest stars:>10", FIELD_SCHEMA)

        qs.filter.assert_called_once()
        args, _ = qs.filter.call_args
        filter_str = str(args[0])
        assert "name__icontains" in filter_str
        assert "stars_count__gt" in filter_str

    def test_query_parser_error_returns_original_queryset(self):
        """Test that QueryParserError returns original queryset."""
        qs = make_queryset()
        with patch("apps.api.rest.v0.structured_search.QueryParser") as mock_parser_class:
            mock_parser_class.side_effect = QueryParserError("Test error")
            result = apply_structured_search(qs, "name:test", FIELD_SCHEMA)

        assert result == qs
        qs.filter.assert_not_called()

    def test_condition_field_not_in_schema_is_skipped(self):
        """Test that condition with field not in field_schema is skipped."""
        qs = make_queryset()
        with patch("apps.api.rest.v0.structured_search.QueryParser") as mock_parser_class:
            mock_parser = MagicMock()
            mock_parser_class.return_value = mock_parser
            mock_parser.parse.return_value = [
                {"field": "query", "type": "string", "value": "test"}
            ]
            apply_structured_search(qs, "test", FIELD_SCHEMA)

        qs.filter.assert_called_once()

    def test_boolean_field_uses_no_lookup_suffix(self):
        """Test boolean field uses empty lookup suffix."""
        schema_with_boolean = {
            "active": {"type": "boolean", "field": "is_active"},
        }
        qs = make_queryset()
        with patch("apps.api.rest.v0.structured_search.QueryParser") as mock_parser_class:
            mock_parser = MagicMock()
            mock_parser_class.return_value = mock_parser
            mock_parser.parse.return_value = [
                {"field": "active", "type": "boolean", "value": True}
            ]
            apply_structured_search(qs, "active:true", schema_with_boolean)

        qs.filter.assert_called_once()
        args, _ = qs.filter.call_args
        assert "is_active" in str(args[0])

    def test_number_field_with_none_value_is_skipped(self):
        """Test that number field with None value is skipped."""
        qs = make_queryset()
        with patch("apps.api.rest.v0.structured_search.QueryParser") as mock_parser_class:
            mock_parser = MagicMock()
            mock_parser_class.return_value = mock_parser
            mock_parser.parse.return_value = [{"field": "stars", "type": "number", "value": None}]
            apply_structured_search(qs, "stars:", FIELD_SCHEMA)

        qs.filter.assert_called_once()
        args, _ = qs.filter.call_args
        assert "stars" not in str(args[0])


def test_location_search_conversion():
    """Test that location searches map correctly to icontains."""
    qs = make_queryset()
    schema = {"location": {"type": "string", "lookup": "icontains"}}
    apply_structured_search(qs, "location:London", schema)

    args, _ = qs.filter.call_args
    assert "location__icontains" in str(args[0])


def test_company_search_conversion():
    """Test that company searches map correctly to icontains."""
    qs = make_queryset()
    schema = {"company": {"type": "string", "lookup": "icontains"}}
    apply_structured_search(qs, "company:OWASP", schema)

    args, _ = qs.filter.call_args
    assert "company__icontains" in str(args[0])


def test_followers_count_mapping():
    """Test that followers numeric search maps to followers_count."""
    qs = make_queryset()
    schema = {"followers": {"type": "number", "field": "followers_count"}}
    apply_structured_search(qs, "followers:>50", schema)

    args, _ = qs.filter.call_args
    assert "followers_count__gt" in str(args[0])


def test_forks_count_mapping():
    """Test that forks numeric search maps to forks_count."""
    qs = make_queryset()
    schema = {"forks": {"type": "number", "field": "forks_count"}}
    apply_structured_search(qs, "forks:<5", schema)

    args, _ = qs.filter.call_args
    assert "forks_count__lt" in str(args[0])

