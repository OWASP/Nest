from unittest.mock import MagicMock, patch

import pytest

from apps.api.rest.v0.label import LabelDetail, list_label


class TestLabelSchema:
    @pytest.mark.parametrize(
        "label_data",
        [
            {
                "color": "f29513",
                "description": "Indicates a bug in the project",
                "name": "bug",
            },
            {
                "color": "a2eeef",
                "description": "Indicates a new feature or enhancement",
                "name": "enhancement",
            },
        ],
    )
    def test_label_schema(self, label_data):
        label = LabelDetail(**label_data)

        assert label.color == label_data["color"]
        assert label.description == label_data["description"]
        assert label.name == label_data["name"]


class TestListLabel:
    """Test cases for list_label endpoint."""

    @patch("apps.api.rest.v0.label.LabelModel.objects")
    def test_list_label_with_ordering(self, mock_objects):
        """Test listing labels with custom ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_all = MagicMock()
        mock_filtered = MagicMock()
        mock_ordered = MagicMock()

        mock_objects.all.return_value = mock_all
        mock_filters.filter.return_value = mock_filtered
        mock_filtered.order_by.return_value = mock_ordered

        result = list_label(mock_request, filters=mock_filters, ordering="nest_created_at")

        mock_objects.all.assert_called_once()
        mock_filters.filter.assert_called_once_with(mock_all)
        mock_filtered.order_by.assert_called_once_with("nest_created_at")
        assert result == mock_ordered

    @patch("apps.api.rest.v0.label.LabelModel.objects")
    def test_list_label_without_ordering(self, mock_objects):
        """Test listing labels without ordering (ordering=None)."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_all = MagicMock()
        mock_filtered = MagicMock()

        mock_objects.all.return_value = mock_all
        mock_filters.filter.return_value = mock_filtered

        result = list_label(mock_request, filters=mock_filters, ordering=None)

        mock_objects.all.assert_called_once()
        mock_filters.filter.assert_called_once_with(mock_all)
        mock_filtered.order_by.assert_not_called()
        assert result == mock_filtered
