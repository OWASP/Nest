from unittest.mock import Mock, patch

import pytest

from apps.github.models.repository import Repository
from apps.owasp.models.event import Event


class TestEventModel:
    @pytest.mark.parametrize(
        ("name", "key", "expected_str"),
        [
            ("event1", "", "event1"),
            ("", "key1", "key1"),
            ("", "", ""),
        ],
    )
    def test_event_str(self, name, key, expected_str):
        event = Event(name=name, key=key)
        assert str(event) == expected_str

    def test_from_github(self):
        repository_mock = Repository()
        repository_mock.name = "Test Repo"
        repository_mock.created_at = "2024-01-01"
        repository_mock.updated_at = "2024-12-24"
        repository_mock.title = "Nest"
        repository_mock.pitch = "Nest Pitch"
        repository_mock.tags = ["react", "python"]

        event = Event()

        with patch(
            "apps.owasp.models.event.RepositoryBasedEntityModel.from_github"
        ) as mock_from_github:
            mock_from_github.side_effect = lambda instance, _, repo: setattr(
                instance, "name", repo.title
            )

            event.from_github(repository_mock)

        assert event.owasp_repository == repository_mock

        mock_from_github.assert_called_once_with(
            event,
            {
                "description": "pitch",
                "level": "level",
                "name": "title",
                "tags": "tags",
            },
            repository_mock,
        )

        assert event.name == repository_mock.title

    def test_bulk_save(self):
        mock_event = [Mock(id=None), Mock(id=1)]
        with patch("apps.owasp.models.event.BulkSaveModel.bulk_save") as mock_bulk_save:
            Event.bulk_save(mock_event, fields=["name"])
            mock_bulk_save.assert_called_once_with(Event, mock_event, fields=["name"])

    @patch("apps.owasp.models.event.Event.objects.get")
    def test_update_data_event_does_not_exist(self, mock_get):
        mock_get.side_effect = Event.DoesNotExist
        gh_repository_mock = Mock()
        gh_repository_mock.name = "new_repo"
        repository_mock = Repository()

        with patch.object(Event, "save", return_value=None) as mock_save:
            event = Event.update_data(gh_repository_mock, repository_mock, save=True)
            mock_save.assert_called_once()
            assert event.key == "new_repo"
            assert event.owasp_repository == repository_mock
