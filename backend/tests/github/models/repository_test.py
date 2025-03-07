from base64 import b64encode
from unittest.mock import MagicMock

import pytest
from github.GithubException import GithubException

from apps.github.models.repository import Repository


class TestRepositoryModel:
    def test_update_data(self, mocker):
        gh_repository_mock = MagicMock()
        gh_repository_mock.raw_data = {"node_id": "12345"}

        mock_repository = mocker.Mock(spec=Repository)
        mock_repository.node_id = "12345"
        mocker.patch(
            "apps.github.models.repository.Repository.objects.get",
            return_value=mock_repository,
        )

        repository = Repository()
        repository.from_github = mocker.Mock()

        updated_repository = Repository.update_data(gh_repository_mock)

        assert updated_repository.node_id == mock_repository.node_id
        assert updated_repository.from_github.call_count == 1

    @pytest.fixture()
    def mock_gh_repository(self):
        """Fixture for a mocked GitHub repository."""
        gh_repository = MagicMock()
        gh_repository.name = "TestRepo"
        gh_repository.default_branch = "main"
        gh_repository.description = "A test repository"
        gh_repository.forks_count = 5
        gh_repository.archived = False
        gh_repository.fork = False
        gh_repository.is_template = False
        gh_repository.open_issues_count = 3
        gh_repository.size = 1024
        gh_repository.stargazers_count = 10
        gh_repository.subscribers_count = 2
        gh_repository.topics = ["python", "django"]
        gh_repository.updated_at = "2025-01-01"
        gh_repository.license = MagicMock(name="MIT")
        return gh_repository

    def test_from_github_with_missing_funding(self, mock_gh_repository):
        mock_gh_repository.get_contents.side_effect = GithubException(
            data={"status": "404"}, status=404
        )

        repository = Repository()
        repository.from_github(gh_repository=mock_gh_repository)

        assert not repository.has_funding_yml
        assert repository.is_funding_policy_compliant

    def test_from_github_with_funding(self, mock_gh_repository):
        mock_gh_repository.get_contents.return_value = MagicMock(
            content=b64encode(b"test: test").decode()
        )

        repository = Repository()
        repository.from_github(gh_repository=mock_gh_repository)

        assert repository.has_funding_yml
        assert not repository.is_funding_policy_compliant

    def test_latest_release(self, mock_gh_repository):
        mock_release = MagicMock()
        mock_release.created_at = "2025-01-01"

        mock_gh_repository.latest_release = mock_release
        assert mock_gh_repository.latest_release == mock_release
