from typing import NamedTuple
from unittest import mock

import pytest
from github.GithubException import BadCredentialsException

from apps.github.management.commands.github_update_related_organizations import (
    Command,
    Organization,
)


@pytest.fixture
def command():
    return Command()


@pytest.fixture
def mock_logger():
    with mock.patch(
        "apps.github.management.commands.github_update_related_organizations.logger"
    ) as mock_logger:
        yield mock_logger


@pytest.fixture
def mock_github_class():
    with mock.patch(
        "apps.github.management.commands.github_update_related_organizations.github.Github"
    ) as mock_github:
        yield mock_github


def create_mock_organization(login="TestOrg", num_related_projects=1):
    org = mock.Mock(spec=Organization)
    org.login = login
    org.url = f"https://github.com/{login}"

    org.related_projects = mock.Mock()
    org.related_projects.count.return_value = num_related_projects

    if num_related_projects == 1:
        related_project = mock.Mock()
        related_project.repositories = mock.Mock()
        related_project.repositories.add = mock.Mock()
        org.related_projects.first.return_value = related_project

    return org


def create_mock_github_org(org_login, num_repos):
    gh_org = mock.Mock()
    gh_repos = mock.MagicMock()
    gh_repos.totalCount = num_repos

    repo_mocks = []
    for i in range(num_repos):
        repo_mock = mock.Mock()
        repo_mock.name = f"repo-{i}"
        repo_mock.html_url = f"https://github.com/{org_login}/repo-{i}"
        repo_mocks.append(repo_mock)

    gh_repos.__iter__.return_value = repo_mocks
    gh_org.get_repos.return_value = gh_repos
    return gh_org


def setup_organizations(num_orgs, num_repos_per_org):
    """Create multiple mock organizations and their corresponding GitHub organizations."""
    orgs = []
    gh_orgs = []

    for i in range(num_orgs):
        org_login = f"TestOrg{i + 1}"
        org = create_mock_organization(org_login)
        orgs.append(org)

        gh_org = create_mock_github_org(org_login, num_repos_per_org[i])
        gh_orgs.append(gh_org)

    return orgs, gh_orgs


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
            "apps.github.management.commands.github_update_related_organizations.github.Github",
            gh_factory,
        )

        self.mock_sync_repository = mock.Mock()
        monkeypatch.setattr(
            "apps.github.management.commands.github_update_related_organizations.sync_repository",
            self.mock_sync_repository,
        )

        self.mock_unregister_indexes = mock.Mock()
        monkeypatch.setattr(
            "apps.github.management.commands.github_update_related_organizations.unregister_indexes",
            self.mock_unregister_indexes,
        )

        self.mock_related_orgs = mock.MagicMock()
        type(Organization).related_organizations = mock.PropertyMock(
            return_value=self.mock_related_orgs
        )

        self.command = command

    def _setup_organizations_mock(self, orgs, exists=True):
        self.mock_related_orgs.exists.return_value = exists
        self.mock_related_orgs.count.return_value = len(orgs)
        self.mock_related_orgs.__iter__.return_value = orgs
        self.mock_related_orgs.all.return_value = self.mock_related_orgs
        self.mock_related_orgs.filter.return_value = self.mock_related_orgs

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
        self._setup_organizations_mock(orgs)
        self.mock_gh.get_organization.side_effect = gh_orgs

        with mock.patch("builtins.print"):
            self.command.handle(organization=None)

        assert self.mock_unregister_indexes.called
        assert self.mock_gh.get_organization.call_count == scenario.num_orgs
        for org in orgs:
            self.mock_gh.get_organization.assert_any_call(org.login)
        assert self.mock_sync_repository.call_count == scenario.expected_sync_calls

    def test_handle_with_specific_organization(self):
        """Test command execution with a specific organization."""
        org = create_mock_organization("TestOrg")
        gh_org = create_mock_github_org("TestOrg", 2)

        self._setup_organizations_mock([org])
        self.mock_gh.get_organization.return_value = gh_org

        with mock.patch("builtins.print"):
            self.command.handle(organization="TestOrg")

        self.mock_related_orgs.filter.assert_called_with(login__iexact="TestOrg")
        assert self.mock_unregister_indexes.called
        assert self.mock_gh.get_organization.call_count == 1
        self.mock_gh.get_organization.assert_called_with("TestOrg")
        assert self.mock_sync_repository.call_count == 2

    def test_handle_no_organizations_found(self, mock_logger):
        """Test command execution when no organizations are found."""
        self._setup_organizations_mock([], exists=False)

        with mock.patch("builtins.print"):
            self.command.handle(organization=None)

        mock_logger.error.assert_called_once_with("No OWASP related organizations found")
        assert not self.mock_gh.get_organization.called
        assert not self.mock_sync_repository.called

    def test_handle_invalid_token(self, mock_github_class, mock_logger):
        """Test command execution with invalid GitHub token."""
        mock_github_class.side_effect = BadCredentialsException(401, "Invalid token")

        with mock.patch("builtins.print"):
            self.command.handle(organization=None)

        mock_logger.warning.assert_called_once_with(
            "Invalid GitHub token. Please create or update .env file with a valid token."
        )
        assert not self.mock_sync_repository.called

    def test_handle_invalid_related_projects(self, mock_logger):
        """Test handling of organization with invalid number of related projects."""
        org = create_mock_organization("TestOrg", num_related_projects=0)
        self._setup_organizations_mock([org])

        with mock.patch("builtins.print"):
            self.command.handle(organization=None)

        mock_logger.error.assert_called_once_with(
            "Couldn't identify related project for external organization %s. "
            "The related projects: %s.",
            org,
            org.related_projects,
        )
        assert not self.mock_gh.get_organization.called
        assert not self.mock_sync_repository.called

    def test_handle_sync_repository_exception(self, mock_logger):
        """Test handling of sync_repository exceptions."""
        org = create_mock_organization("TestOrg")
        gh_org = create_mock_github_org("TestOrg", 1)

        self._setup_organizations_mock([org])
        self.mock_gh.get_organization.return_value = gh_org
        self.mock_sync_repository.side_effect = Exception("Sync failed")

        with mock.patch("builtins.print"):
            self.command.handle(organization=None)

        mock_logger.exception.assert_called_once_with(
            "Error syncing repository %s", "https://github.com/TestOrg/repo-0"
        )
        assert self.mock_sync_repository.call_count == 1
