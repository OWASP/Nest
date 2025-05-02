from unittest.mock import MagicMock, patch

import pytest

from apps.github.models.label import Label


class TestLabel:
    LABEL_GET_NODE_ID_PATH = "apps.github.models.label.Label.get_node_id"

    @pytest.fixture
    def label(self):
        return Label()

    @pytest.fixture
    def gh_label(self):
        label = MagicMock()
        label.color = "ff0000"
        label.description = "Bug report"
        label.name = "bug"
        label.raw_data = {"node_id": "test_node_id"}
        return label

    def test_str_with_description(self, label):
        label.name = "bug"
        label.description = "Bug report"
        assert str(label) == "bug (Bug report)"

    def test_str_without_description(self, label):
        label.name = "bug"
        label.description = ""
        assert str(label) == "bug"

    def test_from_github(self, label, gh_label):
        label.from_github(gh_label)

        assert label.color == gh_label.color
        assert label.description == gh_label.description
        assert label.name == gh_label.name

    def test_bulk_save(self):
        labels = [MagicMock(), MagicMock()]

        with patch("apps.common.models.BulkSaveModel.bulk_save") as mock_bulk_save:
            Label.bulk_save(labels)
            mock_bulk_save.assert_called_once_with(Label, labels)

    @patch("apps.github.models.label.Label.objects.get")
    def test_update_data_existing_label(self, mock_get, gh_label):
        mock_label = MagicMock()
        mock_get.return_value = mock_label

        with patch(self.LABEL_GET_NODE_ID_PATH, return_value="test_node_id"):
            result = Label.update_data(gh_label)

            mock_get.assert_called_once_with(node_id="test_node_id")
            mock_label.from_github.assert_called_once_with(gh_label)
            mock_label.save.assert_called_once()
            assert result == mock_label

    @patch(LABEL_GET_NODE_ID_PATH, return_value="test_node_id")
    @patch("apps.github.models.label.Label", autospec=True)
    def test_update_data_new_label(self, mock_label_class, mock_get_node_id, gh_label):
        mock_get = MagicMock(side_effect=Label.DoesNotExist)
        mock_label_class.objects.get = mock_get
        mock_new_label = MagicMock()
        mock_label_class.return_value = mock_new_label
        mock_label_class.DoesNotExist = Label.DoesNotExist

        result = Label.update_data(gh_label)

        mock_get.assert_called_once_with(node_id="test_node_id")
        assert mock_label_class.call_args.kwargs == {"node_id": "test_node_id"}
        mock_new_label.from_github.assert_called_once_with(gh_label)
        mock_new_label.save.assert_called_once()
        assert result == mock_new_label

    @patch("apps.github.models.label.Label.objects.get")
    def test_update_data_without_save(self, mock_get, gh_label):
        mock_label = MagicMock()
        mock_get.return_value = mock_label

        with patch(self.LABEL_GET_NODE_ID_PATH, return_value="test_node_id"):
            result = Label.update_data(gh_label, save=False)

            mock_get.assert_called_once_with(node_id="test_node_id")
            mock_label.from_github.assert_called_once_with(gh_label)
            mock_label.save.assert_not_called()
            assert result == mock_label
