from unittest.mock import MagicMock

import pytest
from django.http import Http404

from apps.api.rest.v0.pagination import CustomPagination


class TestCustomPagination:
    """Test cases for CustomPagination class."""

    def test_paginate_first_page(self):
        """Test pagination on the first page."""
        paginator = CustomPagination()
        
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 25
        mock_queryset.__getitem__ = MagicMock(return_value=["item1", "item2", "item3"])
        
        mock_pagination = MagicMock()
        mock_pagination.page = 1
        mock_pagination.page_size = 10
        
        result = paginator.paginate_queryset(mock_queryset, mock_pagination)
        
        assert result["current_page"] == 1
        assert result["total_count"] == 25
        assert result["total_pages"] == 3
        assert result["has_next"] is True
        assert result["has_previous"] is False
        assert result["items"] == ["item1", "item2", "item3"]
        mock_queryset.__getitem__.assert_called_once_with(slice(0, 10))

    def test_paginate_middle_page(self):
        """Test pagination on a middle page."""
        paginator = CustomPagination()
        
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 35
        mock_queryset.__getitem__ = MagicMock(return_value=["item11", "item12"])
        
        mock_pagination = MagicMock()
        mock_pagination.page = 2
        mock_pagination.page_size = 10
        
        result = paginator.paginate_queryset(mock_queryset, mock_pagination)
        
        assert result["current_page"] == 2
        assert result["total_count"] == 35
        assert result["total_pages"] == 4
        assert result["has_next"] is True
        assert result["has_previous"] is True
        assert result["items"] == ["item11", "item12"]
        mock_queryset.__getitem__.assert_called_once_with(slice(10, 20))

    def test_paginate_last_page(self):
        """Test pagination on the last page."""
        paginator = CustomPagination()
        
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 25
        mock_queryset.__getitem__ = MagicMock(return_value=["item21", "item22", "item23", "item24", "item25"])
        
        mock_pagination = MagicMock()
        mock_pagination.page = 3
        mock_pagination.page_size = 10
        
        result = paginator.paginate_queryset(mock_queryset, mock_pagination)
        
        assert result["current_page"] == 3
        assert result["total_count"] == 25
        assert result["total_pages"] == 3
        assert result["has_next"] is False
        assert result["has_previous"] is True
        assert result["items"] == ["item21", "item22", "item23", "item24", "item25"]
        mock_queryset.__getitem__.assert_called_once_with(slice(20, 30))

    def test_paginate_single_page(self):
        """Test pagination when all items fit on a single page."""
        paginator = CustomPagination()
        
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 5
        mock_queryset.__getitem__ = MagicMock(return_value=["item1", "item2", "item3", "item4", "item5"])
        
        mock_pagination = MagicMock()
        mock_pagination.page = 1
        mock_pagination.page_size = 10
        
        result = paginator.paginate_queryset(mock_queryset, mock_pagination)
        
        assert result["current_page"] == 1
        assert result["total_count"] == 5
        assert result["total_pages"] == 1
        assert result["has_next"] is False
        assert result["has_previous"] is False
        assert result["items"] == ["item1", "item2", "item3", "item4", "item5"]
        mock_queryset.__getitem__.assert_called_once_with(slice(0, 10))

    def test_paginate_empty_queryset_page_one(self):
        """Test pagination with empty queryset on page 1 (should succeed)."""
        paginator = CustomPagination()
        
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 0
        mock_queryset.__getitem__ = MagicMock(return_value=[])
        
        mock_pagination = MagicMock()
        mock_pagination.page = 1
        mock_pagination.page_size = 10
        
        result = paginator.paginate_queryset(mock_queryset, mock_pagination)
        
        assert result["current_page"] == 1
        assert result["total_count"] == 0
        assert result["total_pages"] == 1  # max(1, 0) = 1
        assert result["has_next"] is False
        assert result["has_previous"] is False
        assert result["items"] == []
        mock_queryset.__getitem__.assert_called_once_with(slice(0, 10))

    def test_paginate_empty_queryset_page_two(self):
        """Test pagination with empty queryset on page 2 (should raise Http404)."""
        paginator = CustomPagination()
        
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 0
        
        mock_pagination = MagicMock()
        mock_pagination.page = 2
        mock_pagination.page_size = 10
        
        with pytest.raises(Http404) as exc_info:
            paginator.paginate_queryset(mock_queryset, mock_pagination)
        
        assert "Page 2 not found. Valid pages are 1 to 1." in str(exc_info.value)

    def test_paginate_page_out_of_range(self):
        """Test pagination when requested page exceeds total pages."""
        paginator = CustomPagination()
        
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 25
        
        mock_pagination = MagicMock()
        mock_pagination.page = 5
        mock_pagination.page_size = 10
        
        with pytest.raises(Http404) as exc_info:
            paginator.paginate_queryset(mock_queryset, mock_pagination)
        
        assert "Page 5 not found. Valid pages are 1 to 3." in str(exc_info.value)

    def test_paginate_partial_last_page(self):
        """Test pagination when last page has fewer items than page_size."""
        paginator = CustomPagination()
        
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 23
        mock_queryset.__getitem__ = MagicMock(return_value=["item21", "item22", "item23"])
        
        mock_pagination = MagicMock()
        mock_pagination.page = 3
        mock_pagination.page_size = 10
        
        result = paginator.paginate_queryset(mock_queryset, mock_pagination)
        
        assert result["current_page"] == 3
        assert result["total_count"] == 23
        assert result["total_pages"] == 3
        assert result["has_next"] is False
        assert result["has_previous"] is True
        assert result["items"] == ["item21", "item22", "item23"]
        mock_queryset.__getitem__.assert_called_once_with(slice(20, 30))

    def test_paginate_exact_multiple_pages(self):
        """Test pagination when total items is exact multiple of page_size."""
        paginator = CustomPagination()
        
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 30
        mock_queryset.__getitem__ = MagicMock(return_value=["item21", "item22", "item23", "item24", "item25",
                                                              "item26", "item27", "item28", "item29", "item30"])
        
        mock_pagination = MagicMock()
        mock_pagination.page = 3
        mock_pagination.page_size = 10
        
        result = paginator.paginate_queryset(mock_queryset, mock_pagination)
        
        assert result["current_page"] == 3
        assert result["total_count"] == 30
        assert result["total_pages"] == 3
        assert result["has_next"] is False
        assert result["has_previous"] is True
        assert result["items"] == ["item21", "item22", "item23", "item24", "item25",
                                     "item26", "item27", "item28", "item29", "item30"]
        mock_queryset.__getitem__.assert_called_once_with(slice(20, 30))

    def test_paginate_offset_calculation(self):
        """Test that offset calculation is correct for various pages."""
        paginator = CustomPagination()
        
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 100
        mock_queryset.__getitem__ = MagicMock(return_value=[])
        
        mock_pagination = MagicMock()
        mock_pagination.page_size = 20
        
        # Page 1: offset = (1-1) * 20 = 0
        mock_pagination.page = 1
        paginator.paginate_queryset(mock_queryset, mock_pagination)
        mock_queryset.__getitem__.assert_called_with(slice(0, 20))
        mock_queryset.__getitem__.reset_mock()
        
        # Page 3: offset = (3-1) * 20 = 40
        mock_pagination.page = 3
        paginator.paginate_queryset(mock_queryset, mock_pagination)
        mock_queryset.__getitem__.assert_called_with(slice(40, 60))
        mock_queryset.__getitem__.reset_mock()
        
        # Page 5: offset = (5-1) * 20 = 80
        mock_pagination.page = 5
        paginator.paginate_queryset(mock_queryset, mock_pagination)
        mock_queryset.__getitem__.assert_called_with(slice(80, 100))

    def test_paginate_total_pages_calculation(self):
        """Test total_pages calculation for various edge cases."""
        paginator = CustomPagination()
        
        mock_queryset = MagicMock()
        mock_queryset.__getitem__ = MagicMock(return_value=[])
        
        mock_pagination = MagicMock()
        mock_pagination.page = 1
        mock_pagination.page_size = 10
        
        # 0 items: total_pages = max(1, (0 + 10 - 1) // 10) = max(1, 0) = 1
        mock_queryset.count.return_value = 0
        result = paginator.paginate_queryset(mock_queryset, mock_pagination)
        assert result["total_pages"] == 1
        
        # 1 item: total_pages = max(1, (1 + 10 - 1) // 10) = max(1, 1) = 1
        mock_queryset.count.return_value = 1
        result = paginator.paginate_queryset(mock_queryset, mock_pagination)
        assert result["total_pages"] == 1
        
        # 10 items: total_pages = max(1, (10 + 10 - 1) // 10) = max(1, 1) = 1
        mock_queryset.count.return_value = 10
        result = paginator.paginate_queryset(mock_queryset, mock_pagination)
        assert result["total_pages"] == 1
        
        # 11 items: total_pages = max(1, (11 + 10 - 1) // 10) = max(1, 2) = 2
        mock_queryset.count.return_value = 11
        result = paginator.paginate_queryset(mock_queryset, mock_pagination)
        assert result["total_pages"] == 2
        
        # 99 items: total_pages = max(1, (99 + 10 - 1) // 10) = max(1, 10) = 10
        mock_queryset.count.return_value = 99
        result = paginator.paginate_queryset(mock_queryset, mock_pagination)
        assert result["total_pages"] == 10
        
        # 100 items: total_pages = max(1, (100 + 10 - 1) // 10) = max(1, 10) = 10
        mock_queryset.count.return_value = 100
        result = paginator.paginate_queryset(mock_queryset, mock_pagination)
        assert result["total_pages"] == 10
