"""Tests for CustomPagination class."""

from unittest.mock import MagicMock

import pytest
from django.http import Http404

from apps.api.rest.v0.pagination import CustomPagination


class TestCustomPagination:
    """Test cases for CustomPagination."""

    def setup_method(self):
        """Set up test fixtures."""
        self.pagination = CustomPagination()

    def _create_mock_queryset(self, items: list, total_count: int | None = None):
        """Create a mock queryset with specified items."""
        mock_qs = MagicMock()
        mock_qs.count.return_value = total_count if total_count is not None else len(items)
        mock_qs.__getitem__ = lambda _self, s: items[s]
        return mock_qs

    def test_paginate_queryset_basic(self):
        """Test basic pagination with default parameters."""
        items = list(range(10))
        queryset = self._create_mock_queryset(items)

        pagination_input = CustomPagination.Input(page=1, page_size=10)
        result = self.pagination.paginate_queryset(queryset, pagination_input)

        assert result["current_page"] == 1
        assert result["total_count"] == 10
        assert result["total_pages"] == 1
        assert not result["has_next"]
        assert not result["has_previous"]
        assert result["items"] == items

    def test_paginate_queryset_multiple_pages(self):
        """Test pagination with multiple pages."""
        items = list(range(25))
        queryset = self._create_mock_queryset(items)

        pagination_input = CustomPagination.Input(page=2, page_size=10)
        result = self.pagination.paginate_queryset(queryset, pagination_input)

        assert result["current_page"] == 2
        assert result["total_count"] == 25
        assert result["total_pages"] == 3
        assert result["has_next"]
        assert result["has_previous"]
        assert result["items"] == items[10:20]

    def test_paginate_queryset_last_page(self):
        """Test pagination on the last page."""
        items = list(range(25))
        queryset = self._create_mock_queryset(items)

        pagination_input = CustomPagination.Input(page=3, page_size=10)
        result = self.pagination.paginate_queryset(queryset, pagination_input)

        assert result["current_page"] == 3
        assert result["total_pages"] == 3
        assert not result["has_next"]
        assert result["has_previous"]
        assert result["items"] == items[20:25]

    def test_paginate_queryset_page_exceeds_total(self):
        """Test that Http404 is raised when page exceeds total pages."""
        items = list(range(10))
        queryset = self._create_mock_queryset(items)

        pagination_input = CustomPagination.Input(page=5, page_size=10)

        with pytest.raises(Http404) as exc_info:
            self.pagination.paginate_queryset(queryset, pagination_input)

        assert "Page 5 not found" in str(exc_info.value)
        assert "Valid pages are 1 to 1" in str(exc_info.value)

    def test_paginate_queryset_empty_queryset(self):
        """Test pagination with an empty queryset returns single page."""
        queryset = self._create_mock_queryset([])

        pagination_input = CustomPagination.Input(page=1, page_size=10)
        result = self.pagination.paginate_queryset(queryset, pagination_input)

        assert result["current_page"] == 1
        assert result["total_count"] == 0
        assert result["total_pages"] == 1
        assert not result["has_next"]
        assert not result["has_previous"]
        assert result["items"] == []

    def test_paginate_queryset_empty_queryset_page_exceeds(self):
        """Test that page 2 on empty queryset raises Http404."""
        queryset = self._create_mock_queryset([])

        pagination_input = CustomPagination.Input(page=2, page_size=10)

        with pytest.raises(Http404):
            self.pagination.paginate_queryset(queryset, pagination_input)

    def test_paginate_queryset_custom_page_size(self):
        """Test pagination with custom page size."""
        items = list(range(100))
        queryset = self._create_mock_queryset(items)

        pagination_input = CustomPagination.Input(page=1, page_size=50)
        result = self.pagination.paginate_queryset(queryset, pagination_input)

        assert result["total_pages"] == 2
        assert len(result["items"]) == 50
        assert result["has_next"]


class TestPaginationInputSchema:
    """Test Pagination Input schema defaults and validation."""

    def test_input_defaults(self):
        """Test default values for pagination input."""
        input_schema = CustomPagination.Input()
        assert input_schema.page == 1
        assert input_schema.page_size == 100

    def test_input_custom_values(self):
        """Test custom values for pagination input."""
        input_schema = CustomPagination.Input(page=5, page_size=25)
        assert input_schema.page == 5
        assert input_schema.page_size == 25


class TestPaginationOutputSchema:
    """Test Pagination Output schema."""

    def test_output_schema(self):
        """Test that Output schema has expected fields."""
        output = CustomPagination.Output(
            current_page=1,
            has_next=True,
            has_previous=False,
            items=[1, 2, 3],
            total_count=100,
            total_pages=10,
        )
        assert output.current_page == 1
        assert output.has_next
        assert not output.has_previous
        assert output.items == [1, 2, 3]
        assert output.total_count == 100
        assert output.total_pages == 10
