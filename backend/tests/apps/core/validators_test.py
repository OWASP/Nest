import pytest
from django.core.exceptions import ValidationError

from apps.core.validators import (
    validate_facet_filters,
    validate_index_name,
    validate_limit,
    validate_page,
    validate_query,
)


class TestAlgoliaValidators:
    # Index name tests
    @pytest.mark.parametrize(
        ("index_name", "error_message"),
        [
            (5, "indexName is required and must be a string."),
            ("", "indexName is required and must be a string."),
            (
                "index!name",
                (
                    "Invalid indexName value provided. "
                    "Only alphanumeric characters hyphens and underscores are allowed."
                ),
            ),
            (
                "index name",
                (
                    "Invalid indexName value provided. "
                    "Only alphanumeric characters hyphens and underscores are allowed."
                ),
            ),
        ],
    )
    def test_invalid_index_name(self, index_name, error_message):
        with pytest.raises(ValidationError) as exc_info:
            validate_index_name(index_name)
        assert str(exc_info.value.messages[0]) == error_message

    def test_valid_index_name(self):
        validate_index_name("index_name")

    # hitsPerPage tests
    @pytest.mark.parametrize(
        ("limit", "error_message"),
        [
            (0, "hitsPerPage value must be between 1 and 1000."),
            (1001, "hitsPerPage value must be between 1 and 1000."),
            ("5", "hitsPerPage must be an integer."),
        ],
    )
    def test_invalid_limit(self, limit, error_message):
        with pytest.raises(ValidationError) as exc_info:
            validate_limit(limit)
        assert str(exc_info.value.messages[0]) == error_message

    def test_valid_limit(self):
        validate_limit(5)

    # Page tests
    @pytest.mark.parametrize(
        ("page", "error_message"),
        [
            (0, "page value must be a positive integer."),
            ("5", "page value must be an integer."),
        ],
    )
    def test_invalid_page(self, page, error_message):
        with pytest.raises(ValidationError) as exc_info:
            validate_page(page)
        assert str(exc_info.value.messages[0]) == error_message

    def test_valid_page(self):
        validate_page(5)

    # Query tests
    @pytest.mark.parametrize(
        ("query", "error_message"),
        [
            (5, "query must be a string."),
            (
                "query!name",
                (
                    "Invalid query value provided. "
                    "Only alphanumeric characters, hyphens, spaces, and underscores are allowed."
                ),
            ),
        ],
    )
    def test_invalid_query(self, query, error_message):
        with pytest.raises(ValidationError) as exc_info:
            validate_query(query)
        assert str(exc_info.value.messages[0]) == error_message

    @pytest.mark.parametrize(
        ("query"),
        ["query_name", "query-name", "query name", "ç_query.valid"],
    )
    def test_valid_query(self, query):
        validate_query(query)

    # Facet filters tests
    @pytest.mark.parametrize(
        ("facet_filters", "error_message"),
        [
            (5, "facetFilters must be a list."),
        ],
    )
    def test_invalid_facet_filters(self, facet_filters, error_message):
        with pytest.raises(ValidationError) as exc_info:
            validate_facet_filters(facet_filters)
        assert str(exc_info.value.messages[0]) == error_message

    def test_valid_facet_filters(self):
        validate_facet_filters([])

    def test_empty_query(self):
        """Test that empty query doesn't raise ValidationError."""
        validate_query("")  # Should not raise
        validate_query(None)  # Should not raise
