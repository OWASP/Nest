from unittest.mock import Mock

from apps.github.models.release import Release
from apps.github.models.user import User
from apps.github.models.repository import Repository


class TestReleaseModel:
    def test_bulk_save(self, mocker):
        mock_releases = [mocker.Mock(id=None), mocker.Mock(id=1)]
        mock_bulk_save = mocker.patch("apps.common.models.BulkSaveModel.bulk_save")
        Release.bulk_save(mock_releases)
        mock_bulk_save.assert_called_once_with(Release, mock_releases, fields=None)

    def test_update_data(self, mocker):
        gh_release_mock = mocker.Mock()
        gh_release_mock.raw_data = {"node_id": "12345"}

        mock_release = mocker.Mock(spec=Release)
        mock_release.node_id = "12345"
        mocker.patch("apps.github.models.release.Release.objects.get", return_value=mock_release)

        release = Release()
        release.from_github = mocker.Mock()

        updated_release = Release.update_data(gh_release_mock)

        assert updated_release.node_id == mock_release.node_id
        assert updated_release.from_github.call_count == 1

    def test_update_data_creates_new(self, mocker):
        """Tests that update_data creates a new instance if one doesn't exist."""
        gh_release_mock = mocker.Mock()
        gh_release_mock.raw_data = {"node_id": "54321"}

        mocker.patch("apps.github.models.release.Release.objects.get", side_effect=Release.DoesNotExist)
        mock_from_github = mocker.patch("apps.github.models.release.Release.from_github")
        mock_release_save = mocker.patch("apps.github.models.release.Release.save")

        release = Release.update_data(gh_release_mock)

        assert release.node_id == "54321"
        mock_from_github.assert_called_once()
        mock_release_save.assert_called_once()

    def test_from_github(self):
        gh_release_mock = Mock()
        gh_release_mock.created_at = "2021-01-01T00:00:00Z"
        gh_release_mock.body = "Description"
        gh_release_mock.title = "Name"
        gh_release_mock.tag_name = "v1.0.0"

        release = Release()
        release.from_github(gh_release_mock)

        assert release.created_at == gh_release_mock.created_at
        assert release.description == gh_release_mock.body
        assert release.name == gh_release_mock.title
        assert release.tag_name == gh_release_mock.tag_name
        assert release.author is None
        assert release.repository is None

    def test_str_representation(self, mocker):
        """Tests the __str__ method returns the correct format."""
        mock_author = mocker.Mock(spec=User)
        mock_author.__str__ = lambda self: "testuser"
        mock_author._state = mocker.Mock()
        release = Release(name="v1.0", author=mock_author)
        assert str(release) == "v1.0 by testuser"

    def test_summary_property(self):
        """Tests the summary property returns the correct format."""
        from datetime import datetime, timezone
        release = Release(tag_name="v1.0", published_at=datetime(2023, 1, 1, tzinfo=timezone.utc))
        assert release.summary == "v1.0 on Jan 01, 2023"

    def test_url_property(self, mocker):
        """Tests the url property returns the correct format."""
        mock_repository = mocker.Mock(spec=Repository)
        mock_repository.url = "https://github.com/test/repo"
        mock_repository._state = mocker.Mock()
        release = Release(tag_name="v1.0", repository=mock_repository)
        assert release.url == "https://github.com/test/repo/releases/tag/v1.0"
