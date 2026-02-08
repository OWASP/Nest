from unittest import mock

import pytest
from github.GithubException import UnknownObjectException

from apps.github.management.commands.github_add_related_repositories import (
    Command,
    Project,
)


@pytest.fixture
def command():
    return Command()


@pytest.fixture
def mock_project():
    project = mock.Mock(spec=Project)
    project.owasp_url = "https://owasp.org/www-project-test"
    project.related_urls = mock.MagicMock()
    project.related_urls.copy.return_value = ["https://github.com/OWASP/test-repo"]
    project.invalid_urls = mock.MagicMock()
    project.repositories = mock.Mock()
    project.repositories.add = mock.MagicMock()
    project.save = mock.MagicMock()
    return project


@pytest.mark.parametrize(
    ("offset", "projects"),
    [
        (0, 3),
        (2, 5),
        (0, 6),
        (1, 8),
    ],
)
@mock.patch("apps.github.management.commands.github_add_related_repositories.get_github_client")
@mock.patch("apps.github.management.commands.github_add_related_repositories.sync_repository")
@mock.patch("apps.github.management.commands.github_add_related_repositories.get_repository_path")
def test_handle(
    mock_get_repository_path,
    mock_sync_repository,
    mock_get_github_client,
    command,
    mock_project,
    offset,
    projects,
):
    mock_gh_client = mock.Mock()
    mock_get_github_client.return_value = mock_gh_client

    mock_get_repository_path.return_value = "OWASP/test-repo"

    mock_gh_repo = mock.Mock(name="test-repo")
    mock_gh_client.get_repo.return_value = mock_gh_repo

    mock_organization = mock.Mock()
    mock_repository = mock.Mock()
    mock_sync_repository.return_value = (mock_organization, mock_repository)

    mock_projects_list = [mock_project] * projects

    mock_active_projects = mock.MagicMock()
    mock_active_projects.__iter__.return_value = iter(mock_projects_list)
    mock_active_projects.count.return_value = len(mock_projects_list)
    mock_active_projects.__getitem__ = lambda _, idx: (
        mock_projects_list[idx]
        if isinstance(idx, int)
        else mock_projects_list[idx.start : idx.stop]
    )
    mock_active_projects.order_by.return_value = mock_active_projects

    with (
        mock.patch.object(Project, "active_projects", mock_active_projects),
        mock.patch.object(Project, "bulk_save") as mock_project_bulk_save,
        mock.patch("builtins.print") as mock_print,
    ):
        command.handle(offset=offset)

        mock_get_github_client.assert_called_once()

        mock_get_repository_path.assert_called_with("https://github.com/OWASP/test-repo")
        mock_gh_client.get_repo.assert_called_with("OWASP/test-repo")

        assert mock_organization.save.called
        assert mock_project.repositories.add.called

        assert mock_sync_repository.call_count == projects - offset

        mock_project_bulk_save.assert_called_once()

        assert mock_print.call_count > 0


@mock.patch("apps.github.management.commands.github_add_related_repositories.get_github_client")
@mock.patch("apps.github.management.commands.github_add_related_repositories.sync_repository")
@mock.patch("apps.github.management.commands.github_add_related_repositories.get_repository_path")
@mock.patch("apps.owasp.models.project.Project.active_projects")
def test_handle_unknown_object_exception(
    mock_active_projects,
    mock_get_repository_path,
    mock_sync_repository,
    mock_get_github_client,
    command,
    mock_project,
):
    """Test handling of a 404 Not Found error from GitHub."""
    mock_projects_list = [mock_project]
    mock_active_projects.__iter__.return_value = iter(mock_projects_list)
    mock_active_projects.count.return_value = len(mock_projects_list)

    mock_active_projects.__getitem__.side_effect = lambda idx: mock_projects_list[idx]
    mock_active_projects.order_by.return_value = mock_active_projects

    mock_gh_client = mock.Mock()
    mock_get_github_client.return_value = mock_gh_client

    def raise_404(*a, **k):  # noqa: ARG001
        raise UnknownObjectException(
            status=404,
            data={"message": "Not Found", "status": "404"},
            headers={},
        )

    mock_gh_client.get_repo.side_effect = raise_404

    mock_get_repository_path.return_value = "OWASP/test-repo"
    with mock.patch.object(Project, "bulk_save") as mock_project_bulk_save:
        command.handle(offset=0)

    mock_project.related_urls.remove.assert_called_once_with("https://github.com/OWASP/test-repo")
    mock_project.invalid_urls.add.assert_called_once_with("https://github.com/OWASP/test-repo")
    mock_project.save.assert_called_once_with(update_fields=("invalid_urls", "related_urls"))

    mock_sync_repository.assert_not_called()

    mock_project_bulk_save.assert_called_once_with([mock_project])


@mock.patch("apps.github.management.commands.github_add_related_repositories.logger")
@mock.patch("apps.github.management.commands.github_add_related_repositories.get_github_client")
@mock.patch("apps.github.management.commands.github_add_related_repositories.sync_repository")
@mock.patch("apps.github.management.commands.github_add_related_repositories.get_repository_path")
@mock.patch("apps.owasp.models.project.Project.active_projects")
def test_handle_sync_repository_exception(
    mock_active_projects,
    mock_get_repository_path,
    mock_sync_repository,
    mock_get_github_client,
    mock_logger,
    command,
    mock_project,
):
    """Test that an exception during sync_repository is logged and handled."""
    mock_projects_list = [mock_project]
    mock_active_projects.__iter__.return_value = iter(mock_projects_list)
    mock_active_projects.count.return_value = len(mock_projects_list)

    mock_active_projects.__getitem__.side_effect = lambda idx: mock_projects_list[idx]
    mock_active_projects.order_by.return_value = mock_active_projects

    mock_gh_client = mock.Mock()
    mock_get_github_client.return_value = mock_gh_client

    mock_gh_repository = mock.MagicMock()
    mock_gh_client.get_repo.return_value = mock_gh_repository

    mock_sync_repository.side_effect = Exception("Test sync error")
    mock_get_repository_path.return_value = "OWASP/test-repo"

    with mock.patch.object(Project, "bulk_save") as mock_project_bulk_save:
        command.handle(offset=0)

    mock_logger.exception.assert_called_once_with(
        "Error syncing repository %s", "https://github.com/OWASP/test-repo"
    )
    mock_project_bulk_save.assert_called_once_with([mock_project])


@mock.patch("apps.github.management.commands.github_add_related_repositories.logger")
@mock.patch("apps.github.management.commands.github_add_related_repositories.get_repository_path")
@mock.patch("apps.github.management.commands.github_add_related_repositories.sync_repository")
@mock.patch("apps.github.management.commands.github_add_related_repositories.get_github_client")
@mock.patch("apps.owasp.models.project.Project.active_projects")
def test_handle_no_repository_path(
    mock_active_projects,
    mock_get_github_client,
    mock_sync_repository,
    mock_get_repository_path,
    mock_logger,
    command,
    mock_project,
):
    """Test that the command handles the case where a repository path cannot be determined."""
    mock_get_repository_path.return_value = None
    mock_projects_list = [mock_project]
    mock_active_projects.__iter__.return_value = iter(mock_projects_list)
    mock_active_projects.count.return_value = len(mock_projects_list)

    mock_active_projects.__getitem__.side_effect = lambda idx: mock_projects_list[idx]
    mock_active_projects.order_by.return_value = mock_active_projects

    mock_gh_client = mock.Mock()
    mock_get_github_client.return_value = mock_gh_client

    mock_gh_repository = mock.MagicMock()
    mock_gh_client.get_repo.return_value = mock_gh_repository

    with mock.patch.object(Project, "bulk_save") as mock_project_bulk_save:
        command.handle(offset=0)

    mock_get_repository_path.assert_called_once_with("https://github.com/OWASP/test-repo")
    mock_logger.info.assert_called_once_with(
        "Couldn't get repository path for %s", "https://github.com/OWASP/test-repo"
    )
    mock_get_github_client.return_value.get_repo.assert_not_called()
    mock_sync_repository.assert_not_called()
    mock_project_bulk_save.assert_called_once_with([mock_project])


def test_add_arguments(command):
    parser = mock.Mock()
    command.add_arguments(parser)
    parser.add_argument.assert_called_once_with(
        "--offset",
        type=int,
        default=0,
        required=False,
    )
