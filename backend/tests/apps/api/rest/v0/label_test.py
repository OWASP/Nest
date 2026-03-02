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


class TestListLabels:
    """Tests for list_label endpoint."""

    @patch("apps.api.rest.v0.label.LabelModel")
    def test_list_labels_no_ordering(self, mock_label_model):
        """Test list labels without ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_queryset = MagicMock()
        mock_filters.filter.return_value = mock_queryset

        result = list_label(mock_request, mock_filters, ordering=None)

        assert result == mock_queryset
        mock_queryset.order_by.assert_not_called()

    @patch("apps.api.rest.v0.label.LabelModel")
    def test_list_labels_with_ordering(self, mock_label_model):
        """Test list labels with ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_queryset = MagicMock()
        mock_ordered_queryset = MagicMock()
        mock_filters.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_ordered_queryset

        result = list_label(mock_request, mock_filters, ordering="nest_created_at")

        mock_queryset.order_by.assert_called_with("nest_created_at")
        assert result == mock_ordered_queryset

    @patch("apps.api.rest.v0.label.LabelModel")
    def test_list_labels_with_desc_ordering(self, mock_label_model):
        """Test list labels with descending ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_queryset = MagicMock()
        mock_ordered_queryset = MagicMock()
        mock_filters.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_ordered_queryset

        result = list_label(mock_request, mock_filters, ordering="-nest_updated_at")

        mock_queryset.order_by.assert_called_with("-nest_updated_at")
        assert result == mock_ordered_queryset
