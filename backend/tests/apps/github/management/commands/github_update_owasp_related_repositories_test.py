from typing import NamedTuple
from unittest import mock

import pytest
from github.GithubException import BadCredentialsException

from apps.github.management.commands.github_update_owasp_related_organizations import (
    Command,
    Organization,
)

BUILTINS_PRINT = "builtins.print"


@pytest.fixture
def command():
    return Command()


@pytest.fixture
def mock_gh_repository():
    repo = mock.Mock()
    repo.name = "test-repo"
    repo.html_url = "https://github.com/TestOrg/test-repo"
    return repo


def setup_organizations(num_orgs, num_repos_per_org):
    orgs = []
    gh_orgs = []
    for i in range(num_orgs):
        org = mock.Mock(spec=Organization)
        org.login = f"TestOrg{i + 1}"
        org.is_owasp_related_organization = True
        orgs.append(org)

        gh_org = mock.Mock()
        gh_repos = mock.MagicMock()
        gh_repos.totalCount = num_repos_per_org[i]
        repo_mocks = []
        for j in range(num_repos_per_org[i]):
            repo_mock = mock.Mock()
            repo_mock.name = f"repo-{i}-{j}"
            repo_mock.html_url = f"https://github.com/{org.login}/repo-{i}-{j}"
            repo_mocks.append(repo_mock)
        gh_repos.__iter__.return_value = repo_mocks
        gh_org.get_repos.return_value = gh_repos
        gh_orgs.append(gh_org)

    return (orgs, gh_orgs)


class Scenario(NamedTuple):
    num_orgs: int
    num_repos_per_org: list[int]
    expected_sync_calls: int


class TestGithubUpdateExternalRepositories:
    @pytest.fixture(autouse=True)
    def setup(self, monkeypatch, command):
        monkeypatch.setenv("GITHUB_TOKEN", "valid-token")
        self.mock_gh = mock.Mock()
        gh_factory = mock.Mock(return_value=self.mock_gh)
        monkeypatch.setattr(
            "apps.github.management.commands.github_update_owasp_related_organizations.github.Github",
            gh_factory,
        )
        self.mock_sync_repository = mock.Mock()
        monkeypatch.setattr(
            "apps.github.management.commands.github_update_owasp_related_organizations.sync_repository",
            self.mock_sync_repository,
        )
        self.mock_org_filter = mock.Mock()
        monkeypatch.setattr(
            "apps.github.management.commands.github_update_owasp_related_organizations.Organization.objects.filter",
            self.mock_org_filter,
        )
        self.command = command

    @pytest.mark.parametrize(
        "scenario",
        [
            Scenario(
                num_orgs=1,
                num_repos_per_org=[2],
                expected_sync_calls=2,
            ),
            Scenario(
                num_orgs=2,
                num_repos_per_org=[1, 3],
                expected_sync_calls=4,
            ),
            Scenario(
                num_orgs=2,
                num_repos_per_org=[0, 2],
                expected_sync_calls=2,
            ),
        ],
    )
    def test_handle(self, scenario):
        """Test command execution with varying organizations and repositories."""
        orgs, gh_orgs = setup_organizations(scenario.num_orgs, scenario.num_repos_per_org)

        qs_mock = mock.MagicMock()
        qs_mock.count.return_value = scenario.num_orgs
        qs_mock.__iter__.return_value = orgs
        self.mock_org_filter.return_value.exclude.return_value = qs_mock

        self.mock_gh.get_organization.side_effect = gh_orgs

        with mock.patch(BUILTINS_PRINT):  # Suppress command output during testing
            self.command.handle(organization=None)

        assert self.mock_gh.get_organization.call_count == scenario.num_orgs
        for org in orgs:
            self.mock_gh.get_organization.assert_any_call(org.login)

        assert self.mock_sync_repository.call_count == scenario.expected_sync_calls

    def test_handle_with_specific_organization(self):
        """Test command execution with a specific organization."""
        org = mock.Mock(spec=Organization)
        org.login = "TestOrg"
        org.is_owasp_related_organization = True

        gh_org = mock.Mock()
        gh_repos = mock.MagicMock()
        gh_repos.totalCount = 2
        repo_mocks = [
            mock.Mock(name="repo1", html_url="https://github.com/TestOrg/repo1"),
            mock.Mock(name="repo2", html_url="https://github.com/TestOrg/repo2"),
        ]
        gh_repos.__iter__.return_value = repo_mocks
        gh_org.get_repos.return_value = gh_repos

        self.mock_org_filter.return_value.first.return_value = org
        self.mock_gh.get_organization.return_value = gh_org

        with mock.patch(BUILTINS_PRINT):  # Suppress command output during testing
            self.command.handle(organization="TestOrg")

        self.mock_org_filter.assert_called_with(login="TestOrg")
        assert self.mock_gh.get_organization.call_count == 1
        self.mock_gh.get_organization.assert_called_with("TestOrg")
        assert self.mock_sync_repository.call_count == 2


@pytest.mark.parametrize(
    ("side_effects"),
    [
        # First repo fails with error, second succeeds
        (
            [
                Exception("GitHub API error"),
                None,
            ],
        ),
        # First repo fails with network error, second succeeds
        (
            [
                ConnectionError("Network timeout"),
                None,
            ],
        ),
        # Credential error should return None immediately
        (
            [
                BadCredentialsException(401),
                None,
            ],
        ),
    ],
)
@mock.patch(
    "apps.github.management.commands.github_update_owasp_related_organizations.sync_repository"
)
def test_sync_organization_repositories_error_handling(
    mock_sync_repository, command, mock_gh_repository, side_effects
):
    """Test repository synchronization error handling."""
    mock_organization = mock.Mock(spec=Organization)
    mock_organization.login = "TestOrg"

    mock_repositories = mock.MagicMock()
    mock_repositories.totalCount = 2  # Try to sync 2 repositories
    mock_repositories.__iter__.return_value = [mock_gh_repository] * 2

    mock_sync_repository.side_effect = side_effects

    with mock.patch(BUILTINS_PRINT), mock.patch("logging.getLogger") as mock_logger:
        logger = mock.Mock()
        mock_logger.return_value = logger
        command.sync_organization_repositories(mock_organization, mock_repositories)

    if isinstance(side_effects[0], BadCredentialsException):
        logger.warning.assert_called_with(
            "Invalid GitHub token. Please update .env file with a valid token."
        )
    assert mock_sync_repository.call_count == 2  # All cases try both repos
