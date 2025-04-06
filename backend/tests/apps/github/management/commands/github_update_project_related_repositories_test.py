from unittest import mock

import pytest
from github.GithubException import UnknownObjectException

from apps.github.management.commands.github_update_project_related_repositories import (
    GITHUB_ITEMS_PER_PAGE,
    Command,
    Project,
)

magic_value_two = 2
builtins_print = "builtins.print"
test_repo_url = "https://github.com/OWASP/test-repo"
test_repo_path = "OWASP/test-repo"


@pytest.fixture
def command():
    return Command()


@pytest.fixture
def mock_project():
    project = mock.Mock(spec=Project)
    project.owasp_url = "https://owasp.org/www-project-test"
    project.related_urls = {test_repo_url}
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
@mock.patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"})
@mock.patch(
    "apps.github.management.commands.github_update_project_related_repositories.github.Github"
)
@mock.patch(
    "apps.github.management.commands.github_update_project_related_repositories.sync_repository"
)
@mock.patch(
    "apps.github.management.commands.github_update_project_related_repositories.get_repository_path"
)
def test_handle(
    mock_get_repository_path,
    mock_sync_repository,
    mock_github,
    command,
    mock_project,
    offset,
    projects,
):
    mock_gh_client = mock.Mock()
    mock_github.return_value = mock_gh_client

    mock_get_repository_path.return_value = test_repo_path

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
        mock.patch(builtins_print) as mock_print,
    ):
        command.handle(offset=offset)

        mock_github.assert_called_once_with("test-token", per_page=GITHUB_ITEMS_PER_PAGE)

        mock_get_repository_path.assert_called_with(test_repo_url)
        mock_gh_client.get_repo.assert_called_with(test_repo_path)

        assert mock_organization.save.called
        assert mock_project.repositories.add.called

        assert mock_sync_repository.call_count == projects - offset

        mock_project_bulk_save.assert_called_once()

        assert mock_print.call_count > 0


@mock.patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"})
@mock.patch(
    "apps.github.management.commands.github_update_project_related_repositories.github.Github"
)
@mock.patch(
    "apps.github.management.commands.github_update_project_related_repositories.get_repository_path"
)
def test_handle_invalid_repository_path(
    mock_get_repository_path,
    mock_github,
    command,
    mock_project,
):
    mock_gh_client = mock.Mock()
    mock_github.return_value = mock_gh_client
    builtins_print = "builtins.print"
    mock_get_repository_path.return_value = None

    mock_projects_list = [mock_project]

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
        mock.patch(builtins_print),
        mock.patch(
            "apps.github.management.commands.github_update_project_related_repositories.logger"
        ) as mock_logger,
    ):
        command.handle(offset=0)

        mock_logger.info.assert_called_with("Couldn't get repository path for %s", test_repo_url)
        mock_project_bulk_save.assert_called_once()
        mock_gh_client.get_repo.assert_not_called()


@mock.patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"})
@mock.patch(
    "apps.github.management.commands.github_update_project_related_repositories.github.Github"
)
@mock.patch(
    "apps.github.management.commands.github_update_project_related_repositories.get_repository_path"
)
def test_handle_github_not_found_exception(
    mock_get_repository_path,
    mock_github,
    command,
    mock_project,
):
    mock_gh_client = mock.Mock()
    mock_github.return_value = mock_gh_client

    mock_get_repository_path.return_value = test_repo_path

    not_found_exception = UnknownObjectException(404, {"status": "404", "message": "Not Found"})
    mock_gh_client.get_repo.side_effect = not_found_exception

    original_related_urls = mock_project.related_urls.copy()

    mock_projects_list = [mock_project]

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
        mock.patch(builtins_print),
    ):
        command.handle(offset=0)

        mock_gh_client.get_repo.assert_called_with(test_repo_path)

        for url in original_related_urls:
            assert url in mock_project.invalid_urls
            assert url not in mock_project.related_urls

        mock_project.save.assert_called_with(update_fields=("invalid_urls", "related_urls"))
        mock_project_bulk_save.assert_called_once()


@mock.patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"})
@mock.patch(
    "apps.github.management.commands.github_update_project_related_repositories.github.Github"
)
@mock.patch(
    "apps.github.management.commands.github_update_project_related_repositories.get_repository_path"
)
@mock.patch(
    "apps.github.management.commands.github_update_project_related_repositories.sync_repository"
)
def test_handle_github_other_exception(
    mock_sync_repository,
    mock_get_repository_path,
    mock_github,
    command,
    mock_project,
):
    mock_gh_client = mock.Mock()
    mock_github.return_value = mock_gh_client

    mock_get_repository_path.return_value = test_repo_path

    other_exception = UnknownObjectException(500, {"status": "500", "message": "Server Error"})
    mock_gh_client.get_repo.side_effect = other_exception

    mock_projects_list = [mock_project]

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
        mock.patch.object(Project, "bulk_save"),
        mock.patch(builtins_print),
    ):
        with pytest.raises(UnknownObjectException):
            command.handle(offset=0)

        mock_gh_client.get_repo.side_effect = UnknownObjectException(500, {"status": "500"})

        mock_gh_client.get_repo.assert_called_with(test_repo_path)
        mock_project.save.assert_not_called()

        mock_sync_repository.assert_not_called()


@mock.patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"})
@mock.patch(
    "apps.github.management.commands.github_update_project_related_repositories.github.Github"
)
@mock.patch(
    "apps.github.management.commands.github_update_project_related_repositories.get_repository_path"
)
@mock.patch(
    "apps.github.management.commands.github_update_project_related_repositories.sync_repository"
)
def test_handle_multiple_related_urls(
    mock_sync_repository,
    mock_get_repository_path,
    mock_github,
    command,
):
    mock_gh_client = mock.Mock()
    mock_github.return_value = mock_gh_client

    mock_project = mock.Mock(spec=Project)
    mock_project.owasp_url = "https://owasp.org/www-project-test"
    mock_project.related_urls = {
        "https://github.com/OWASP/repo1",
        "https://github.com/OWASP/repo2",
    }
    mock_project.invalid_urls = set()

    mock_get_repository_path.side_effect = ["OWASP/repo1", "OWASP/repo2"]

    mock_gh_repo1 = mock.Mock(name="repo1")
    mock_gh_repo2 = mock.Mock(name="repo2")
    mock_gh_client.get_repo.side_effect = [mock_gh_repo1, mock_gh_repo2]

    mock_organization1 = mock.Mock()
    mock_repository1 = mock.Mock()
    mock_organization2 = mock.Mock()
    mock_repository2 = mock.Mock()
    mock_sync_repository.side_effect = [
        (mock_organization1, mock_repository1),
        (mock_organization2, mock_repository2),
    ]

    mock_projects_list = [mock_project]

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
        mock.patch(builtins_print),
    ):
        command.handle(offset=0)

        assert mock_gh_client.get_repo.call_count == magic_value_two
        assert mock_sync_repository.call_count == magic_value_two

        assert mock_organization1.save.called
        assert mock_organization2.save.called

        assert mock_project.repositories.add.call_count == magic_value_two

        mock_project_bulk_save.assert_called_once_with([mock_project])
