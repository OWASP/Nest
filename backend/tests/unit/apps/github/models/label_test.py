from unittest.mock import Mock, patch

import pytest

from apps.github.models.label import Label


@pytest.fixture
def gh_label_mock():
    """Return a mock GitHub label object."""
    mock = Mock()
    mock.color = "000000"
    mock.description = "Description"
    mock.name = "Name"
    mock.raw_data = {"node_id": "12345"}
    return mock


class TestLabelModel:
    def test_bulk_save(self):
        mock_labels = [Mock(id=None), Mock(id=1)]
        with patch("apps.common.models.BulkSaveModel.bulk_save") as mock_bulk_save:
            Label.bulk_save(mock_labels)
            mock_bulk_save.assert_called_once_with(Label, mock_labels, fields=None)

    def test_update_data(self, mocker):
        gh_label_mock = mocker.Mock()
        gh_label_mock.raw_data = {"node_id": "12345"}

        mock_label = mocker.Mock(spec=Label)
        mock_label.node_id = "12345"
        mocker.patch("apps.github.models.label.Label.objects.get", return_value=mock_label)

        label = Label()
        label.from_github = mocker.Mock()

        updated_label = Label.update_data(gh_label_mock)

        assert updated_label.node_id == mock_label.node_id
        assert updated_label.from_github.call_count == 1

    def test_from_github(self):
        gh_label_mock = Mock()
        gh_label_mock.color = "000000"
        gh_label_mock.description = "Description"
        gh_label_mock.name = "Name"

        label = Label()
        label.from_github(gh_label_mock)

        assert label.color == gh_label_mock.color
        assert label.description == gh_label_mock.description
        assert label.name == gh_label_mock.name

    def test_str_no_description(self):
        """Test the string representation when the label has no description."""
        label = Label(name="test-label", description="")
        assert str(label) == "test-label"

    def test_from_github_with_none_values(self, gh_label_mock):
        """Test that from_github correctly handles None values from the API."""
        gh_label_mock.description = None
        label = Label(description="Existing Description")

        label.from_github(gh_label_mock)
        assert label.description == "Existing Description"
        assert label.color == "000000"
        assert label.name == "Name"

    @patch("apps.github.models.label.Label.objects.get")
    def test_update_data_creates_new_label(self, mock_get, gh_label_mock):
        """Test that update_data creates a new label if it does not exist."""
        mock_get.side_effect = Label.DoesNotExist
        with patch.object(Label, "save") as mock_save:
            label = Label.update_data(gh_label_mock)
            mock_save.assert_called_once()
            assert label.node_id == "12345"
            assert label.name == "Name"

    @patch("apps.github.models.label.Label.objects.get")
    def test_update_data_no_save(self, mock_get, gh_label_mock):
        """Test that update_data does not save the label when save=False."""
        mock_get.return_value = Label(node_id="12345")
        with patch.object(Label, "save") as mock_save:
            Label.update_data(gh_label_mock, save=False)
            mock_save.assert_not_called()
