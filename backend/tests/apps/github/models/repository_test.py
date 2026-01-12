from base64 import b64encode
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import pytest
from github.GithubException import GithubException

from apps.github.models.repository import Repository
from apps.github.models.user import User


class TestRepositoryModel:
    def test_update_data(self, mocker):
        gh_repository_mock = MagicMock()
        gh_repository_mock.raw_data = {"node_id": "12345"}

        mock_repository = mocker.Mock(spec=Repository)
        mock_repository.node_id = "12345"
        mocker.patch(
            "apps.github.models.repository.Repository.objects.get", return_value=mock_repository
        )

        repository = Repository()
        repository.from_github = mocker.Mock()

        updated_repository = Repository.update_data(gh_repository_mock)

        assert updated_repository.node_id == mock_repository.node_id
        assert updated_repository.from_github.call_count == 1

    @pytest.fixture
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


class TestRepositoryFromGithub:
    @pytest.fixture(autouse=True)
    def gh_repository_setup(self):
        """Autouse fixture to set up a mocked GitHub repository for all tests in this class."""
        gh_repository = MagicMock()
        gh_repository.created_at = "2025-01-01T00:00:00Z"
        gh_repository.default_branch = "main"
        gh_repository.description = "Test Description"
        gh_repository.forks_count = 10
        gh_repository.has_downloads = True
        gh_repository.has_issues = True
        gh_repository.has_pages = False
        gh_repository.has_projects = True
        gh_repository.has_wiki = False
        gh_repository.homepage = "https://example.com"
        gh_repository.archived = False
        gh_repository.fork = False
        gh_repository.is_template = False
        gh_repository.name = "test-repo"
        gh_repository.open_issues_count = 5
        gh_repository.pushed_at = "2025-01-01T00:00:00Z"
        gh_repository.size = 2048
        gh_repository.stargazers_count = 50
        gh_repository.subscribers_count = 5
        gh_repository.topics = ["test", "mock"]
        gh_repository.updated_at = "2025-01-01T00:00:00Z"
        gh_repository.watchers_count = 5
        gh_repository.license = None
        gh_repository.get_contents.side_effect = GithubException(status=404, data={})
        return gh_repository

    def test_from_github_handles_none_values(self, gh_repository_setup):
        """Test that from_github correctly handles None values for optional fields."""
        gh_repository_setup.description = None
        gh_repository_setup.license = None

        repository = Repository()
        repository.from_github(gh_repository_setup)

        assert repository.description == ""
        assert repository.license == ""

    def test_from_github_with_empty_commits(self, gh_repository_setup):
        """Test that from_github sets the is_empty flag when a repository has no commits."""
        commits_mock = MagicMock()
        type(commits_mock).totalCount = PropertyMock(
            side_effect=GithubException(
                status=409, data={"message": "Git Repository is empty", "status": "409"}
            )
        )
        owner_mock = MagicMock(spec=User, login="test-owner", _state=Mock(db=None))

        repository = Repository()
        repository.from_github(gh_repository_setup, commits=commits_mock, user=owner_mock)

        assert repository.is_empty

    def test_from_github_calculates_languages(self, gh_repository_setup):
        """Test that from_github correctly calculates language percentages."""
        languages = {"Python": 300, "JavaScript": 600, "HTML": 100}
        repository = Repository()
        repository.from_github(gh_repository_setup, languages=languages)

        assert repository.languages == {"Python": 30.0, "JavaScript": 60.0, "HTML": 10.0}

    def test_from_github_with_compliant_funding_yml(self, gh_repository_setup):
        """Test that from_github correctly identifies a compliant FUNDING.yml file."""
        funding_yml_content = (
            b"custom: ['https://owasp.org/donate?reponame=test-repo&owner=test-owner']"
        )
        mock_contents = MagicMock(content=b64encode(funding_yml_content))
        gh_repository_setup.get_contents.return_value = mock_contents
        gh_repository_setup.get_contents.side_effect = None

        owner_mock = MagicMock(spec=User, login="test-owner", _state=Mock(db=None))
        repository = Repository(owner=owner_mock, name="test-repo")
        repository.from_github(gh_repository_setup, user=owner_mock)

        assert repository.has_funding_yml
        assert repository.is_funding_policy_compliant

    def test_from_github_with_non_compliant_funding_yml(self, gh_repository_setup):
        """Test that from_github correctly identifies a non-compliant FUNDING.yml file."""
        funding_yml_content = b"custom: 'not-a-valid-link'"
        mock_contents = MagicMock(content=b64encode(funding_yml_content))
        gh_repository_setup.get_contents.return_value = mock_contents
        gh_repository_setup.get_contents.side_effect = None

        owner_mock = MagicMock(spec=User, login="test-owner", _state=Mock(db=None))
        repository = Repository(owner=owner_mock, name="test-repo")
        repository.from_github(gh_repository_setup, user=owner_mock)

        assert repository.has_funding_yml
        assert not repository.is_funding_policy_compliant

    def test_from_github_with_empty_target_in_funding_yml(self, gh_repository_setup):
        """Test that from_github handles empty targets in FUNDING.yml as compliant."""
        funding_yml_content = b"custom: ['']"
        mock_contents = MagicMock(content=b64encode(funding_yml_content))
        gh_repository_setup.get_contents.return_value = mock_contents
        gh_repository_setup.get_contents.side_effect = None

        owner_mock = MagicMock(spec=User, login="test-owner", _state=Mock(db=None))
        repository = Repository(owner=owner_mock, name="test-repo")
        repository.from_github(gh_repository_setup, user=owner_mock)

        assert repository.has_funding_yml
        assert repository.is_funding_policy_compliant


class TestRepositoryProperties:
    @pytest.fixture(autouse=True)
    def repository_setup(self):
        """Autouse fixture to set up a mocked owner and repository for all tests in this class."""
        owner = MagicMock(spec=User, login="test-owner", _state=Mock(db=None))
        repository = Repository(owner=owner, name="test-repo")
        return owner, repository

    def test_latest_pull_request(self, repository_setup):
        """Test the latest_pull_request property to ensure it returns the most.

        recent pull request.
        """
        _owner, repository = repository_setup
        with patch.object(Repository, "pull_requests", new_callable=PropertyMock) as mock_prop:
            mock_manager = mock_prop.return_value
            mock_pr = MagicMock()
            mock_manager.order_by.return_value.first.return_value = mock_pr
            assert repository.latest_pull_request == mock_pr
            mock_manager.order_by.assert_called_with("-created_at")

    def test_latest_release(self, repository_setup):
        """Test the latest_release property to ensure it returns the most recently.

        published release.
        """
        _owner, repository = repository_setup
        with patch.object(Repository, "releases", new_callable=PropertyMock) as mock_prop:
            mock_manager = mock_prop.return_value
            mock_release = MagicMock()
            mock_manager.filter.return_value.order_by.return_value.first.return_value = (
                mock_release
            )
            assert repository.latest_release == mock_release
            mock_manager.filter.assert_called_with(
                is_draft=False, is_pre_release=False, published_at__isnull=False
            )
            mock_manager.filter.return_value.order_by.assert_called_with("-published_at")

    def test_latest_updated_issue(self, repository_setup):
        """Test the latest_updated_issue property to ensure it returns the most.

        recently updated issue.
        """
        _owner, repository = repository_setup
        with patch.object(Repository, "issues", new_callable=PropertyMock) as mock_prop:
            mock_manager = mock_prop.return_value
            mock_issue = MagicMock()
            mock_manager.order_by.return_value.first.return_value = mock_issue
            assert repository.latest_updated_issue == mock_issue
            mock_manager.order_by.assert_called_with("-updated_at")

    def test_latest_updated_milestone(self, repository_setup):
        """Test the latest_updated_milestone property to ensure it returns the most.

        recently updated milestone.
        """
        _owner, repository = repository_setup
        with patch.object(Repository, "milestones", new_callable=PropertyMock) as mock_prop:
            mock_manager = mock_prop.return_value
            mock_milestone = MagicMock()
            mock_manager.order_by.return_value.first.return_value = mock_milestone
            assert repository.latest_updated_milestone == mock_milestone
            mock_manager.order_by.assert_called_with("-updated_at")

    def test_latest_updated_pull_request(self, repository_setup):
        """Test the latest_updated_pull_request property to ensure it returns the.

        most recently updated pull request.
        """
        _owner, repository = repository_setup
        with patch.object(Repository, "pull_requests", new_callable=PropertyMock) as mock_prop:
            mock_manager = mock_prop.return_value
            mock_pr = MagicMock()
            mock_manager.order_by.return_value.first.return_value = mock_pr
            assert repository.latest_updated_pull_request == mock_pr
            mock_manager.order_by.assert_called_with("-updated_at")

    def test_nest_key(self, repository_setup):
        """Test the nest_key property to ensure it returns the correct key format."""
        _owner, repository = repository_setup
        assert repository.nest_key == "test-owner-test-repo"

    def test_path(self, repository_setup):
        """Test the path property to ensure it returns the correct repository path."""
        _owner, repository = repository_setup
        assert repository.path == "test-owner/test-repo"

    def test_project(self, repository_setup):
        """Test the project property to ensure it returns the associated project."""
        _owner, repository = repository_setup
        with patch.object(Repository, "project_set", new_callable=PropertyMock) as mock_prop:
            mock_manager = mock_prop.return_value
            mock_project = MagicMock()
            mock_manager.first.return_value = mock_project
            assert repository.project == mock_project

    def test_published_releases(self, repository_setup):
        """Test the published_releases property to ensure it filters for non-draft,.

        non-prerelease releases.
        """
        _owner, repository = repository_setup
        with patch.object(Repository, "releases", new_callable=PropertyMock) as mock_prop:
            mock_manager = mock_prop.return_value
            mock_manager.filter.return_value = "filtered_releases"
            assert repository.published_releases == "filtered_releases"
            mock_manager.filter.assert_called_with(
                is_draft=False, is_pre_release=False, published_at__isnull=False
            )

    def test_recent_milestones(self, repository_setup):
        """Test the recent_milestones property to ensure it returns milestones.

        ordered by creation date.
        """
        _owner, repository = repository_setup
        with patch.object(Repository, "milestones", new_callable=PropertyMock) as mock_prop:
            mock_manager = mock_prop.return_value
            mock_manager.order_by.return_value = "recent_milestones"
            assert repository.recent_milestones == "recent_milestones"
            mock_manager.order_by.assert_called_with("-created_at")

    def test_top_languages(self, repository_setup):
        """Test the top_languages property to ensure it returns a sorted list of.

        top languages, excluding ignored ones.
        """
        _owner, repository = repository_setup
        repository.languages = {
            "Python": 95,
            "HTML": 3,
            "CSS": 1,
            "JavaScript": 0.5,
        }
        assert repository.top_languages == ["Python"]

    def test_url(self, repository_setup):
        """Test the url property to ensure it returns the correct GitHub URL."""
        _owner, repository = repository_setup
        assert repository.url == "https://github.com/test-owner/test-repo"
