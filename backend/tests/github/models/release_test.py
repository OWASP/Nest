from unittest.mock import Mock

from apps.github.models.release import Release


class TestReleaseModel:
    def test_bulk_save(self, mocker):
        mock_releases = [mocker.Mock(id=None), mocker.Mock(id=1)]
        mock_bulk_save = mocker.patch("apps.common.models.BulkSaveModel.bulk_save")
        Release.bulk_save(mock_releases)
        mock_bulk_save.assert_called_once_with(Release, mock_releases)

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
