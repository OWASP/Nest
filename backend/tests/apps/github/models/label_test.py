from unittest.mock import Mock, patch

from apps.github.models.label import Label


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
