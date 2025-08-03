from unittest import mock

import pytest

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
    project.related_urls = {"https://github.com/OWASP/test-repo"}
    project.invalid_urls = set()
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
    mock_active_projects.__getitem__ = (
        lambda _, idx: mock_projects_list[idx]
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
