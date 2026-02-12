from unittest import mock

import pytest

from apps.github.management.commands.github_update_owasp_organization import (
    Chapter,
    Command,
    Committee,
    Project,
    Repository,
)


@pytest.mark.parametrize(
    ("argument_name", "expected_properties"),
    [
        ("--offset", {"default": 0, "required": False, "type": int}),
        (
            "--repository",
            {
                "required": False,
                "type": str,
                "help": "The OWASP organization's repository name (e.g. Nest, www-project-nest')",
            },
        ),
    ],
)
def test_add_arguments(argument_name, expected_properties):
    mock_parser = mock.Mock()
    command = Command()
    command.add_arguments(mock_parser)
    mock_parser.add_argument.assert_any_call(argument_name, **expected_properties)


@pytest.fixture
def command():
    return Command()


@pytest.fixture
def mock_gh_repo():
    repo = mock.Mock(spec=Repository)
    repo.name = "test-repo"
    repo.html_url = "https://github.com/OWASP/test-repo"
    return repo


@pytest.mark.parametrize(
    ("repository_name", "offset", "expected_calls"),
    [
        (
            "www-project-test",
            0,
            {"project": 1, "chapter": 0, "committee": 0},
        ),
        (
            "www-chapter-test",
            0,
            {"project": 0, "chapter": 1, "committee": 0},
        ),
        (
            "www-committee-test",
            0,
            {"project": 0, "chapter": 0, "committee": 1},
        ),
        (
            "www-event-test",
            0,
            {"project": 0, "chapter": 0, "committee": 0},
        ),
        (None, 0, {"project": 1, "chapter": 1, "committee": 1, "event": 1}),
        (None, 1, {"project": 0, "chapter": 1, "committee": 1, "event": 1}),
    ],
)
@mock.patch("apps.github.management.commands.github_update_owasp_organization.get_github_client")
@mock.patch("apps.github.management.commands.github_update_owasp_organization.sync_repository")
def test_handle(
    mock_sync_repository,
    mock_get_github_client,
    command,
    repository_name,
    offset,
    expected_calls,
):
    mock_gh_client = mock.Mock()
    mock_get_github_client.return_value = mock_gh_client
    mock_org = mock.Mock()
    mock_gh_client.get_organization.return_value = mock_org

    def create_mock_repo(name):
        mock_repo = mock.Mock()
        mock_repo.name = name
        mock_repo.organization.raw_data = {"node_id": "12345"}
        return mock_repo

    mock_repos = [
        create_mock_repo("www-project-test"),
        create_mock_repo("www-chapter-test"),
        create_mock_repo("www-committee-test"),
        create_mock_repo("www-other-test"),
    ]

    if repository_name:
        mock_repo = create_mock_repo(repository_name)
        mock_org.get_repo.return_value = mock_repo
    else:

        class PaginatedListMock(list):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.totalCount = len(self)

            def __getitem__(self, index):
                if isinstance(index, slice):
                    result = super().__getitem__(index)
                    new_list = PaginatedListMock(result)
                    new_list.totalCount = self.totalCount
                    return new_list
                return super().__getitem__(index)

        paginated_repos = PaginatedListMock(mock_repos)
        mock_org.get_repos.return_value = paginated_repos

    mock_sync_repository.return_value = (None, Repository())
    mock_repository = Repository()

    with (
        mock.patch.object(Project, "bulk_save") as mock_project_bulk_save,
        mock.patch.object(Chapter, "bulk_save") as mock_chapter_bulk_save,
        mock.patch.object(Committee, "bulk_save") as mock_committee_bulk_save,
        mock.patch.object(Project, "update_data") as mock_project_update,
        mock.patch.object(Chapter, "update_data") as mock_chapter_update,
        mock.patch.object(Committee, "update_data") as mock_committee_update,
        mock.patch.object(Project, "objects") as mock_project_objects,
        mock.patch.object(Chapter, "objects") as mock_chapter_objects,
        mock.patch.object(Committee, "objects") as mock_committee_objects,
        mock.patch.object(Repository, "objects") as mock_repository_objects,
    ):
        mock_project_update.return_value = mock_repository
        mock_chapter_update.return_value = mock_repository
        mock_committee_update.return_value = mock_repository

        mock_project_objects.all.return_value = []
        mock_chapter_objects.all.return_value = []
        mock_committee_objects.all.return_value = []
        mock_repository_objects.filter.return_value.count.return_value = 1

        command.stdout = mock.MagicMock()
        command.handle(repository=repository_name, offset=offset)

        mock_get_github_client.assert_called_once()
        mock_gh_client.get_organization.assert_called_once_with("OWASP")

        if repository_name:
            mock_org.get_repo.assert_called_once_with(repository_name)
        else:
            mock_org.get_repos.assert_called_once_with(
                type="public", sort="created", direction="desc"
            )

        if repository_name:
            if repository_name.startswith("www-project-"):
                assert mock_project_update.call_count == expected_calls["project"]
            elif repository_name.startswith("www-chapter-"):
                assert mock_chapter_update.call_count == expected_calls["chapter"]
            elif repository_name.startswith("www-committee-"):
                assert mock_committee_update.call_count == expected_calls["committee"]
        else:
            assert command.stdout.write.call_count > 0

        mock_project_bulk_save.assert_called_once()
        mock_chapter_bulk_save.assert_called_once()
        mock_committee_bulk_save.assert_called_once()


@mock.patch("apps.github.management.commands.github_update_owasp_organization.get_github_client")
@mock.patch("apps.github.management.commands.github_update_owasp_organization.sync_repository")
@mock.patch("apps.github.management.commands.github_update_owasp_organization.logger")
def test_handle_full_sync_with_errors_and_repo_linking(
    mock_logger,
    mock_sync_repository,
    mock_get_github_client,
    command,
):
    """Tests the full organization sync."""
    mock_gh_client = mock.Mock()
    mock_get_github_client.return_value = mock_gh_client
    mock_org = mock.Mock()
    mock_org.public_repos = 3
    mock_gh_client.get_organization.return_value = mock_org

    def create_mock_repo(name):
        mock_repo = mock.Mock()
        mock_repo.name = name
        mock_repo.html_url = f"https://github.com/OWASP/{name}"
        return mock_repo

    class PaginatedListMock(list):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.totalCount = len(self)

        def __getitem__(self, index):
            if isinstance(index, slice):
                result = super().__getitem__(index)
                new_list = PaginatedListMock(result)
                new_list.totalCount = self.totalCount
                return new_list
            return super().__getitem__(index)

    repos = [
        create_mock_repo("www-project-test"),
        create_mock_repo("www-chapter-error"),
        create_mock_repo("www-committee-test"),
    ]
    mock_repos = PaginatedListMock(repos)
    mock_org.get_repos.return_value = mock_repos
    mock_repos.totalCount = 3
    mock_sync_repository.side_effect = [
        (mock.Mock(), mock.Mock()),
        Exception("Sync failed"),
        (mock.Mock(), mock.Mock()),
    ]

    with (
        mock.patch.object(Project, "bulk_save"),
        mock.patch.object(Chapter, "bulk_save"),
        mock.patch.object(Committee, "bulk_save"),
        mock.patch.object(Project, "update_data"),
        mock.patch.object(Chapter, "update_data"),
        mock.patch.object(Committee, "update_data"),
        mock.patch.object(Project, "objects") as mock_project_objects,
        mock.patch.object(Repository, "objects") as mock_repository_objects,
    ):
        mock_project = mock.Mock()
        mock_project.owasp_repository = mock.Mock()
        mock_project_objects.all.return_value = [mock_project]
        mock_repository_objects.filter.return_value.count.return_value = 2
        command.stdout = mock.MagicMock()
        command.handle(repository=None, offset=0)
        assert mock_sync_repository.call_count == 3
        mock_logger.exception.assert_called_once_with(
            "Error syncing repository %s", "https://github.com/OWASP/www-chapter-error"
        )
        command.stdout.write.assert_any_call(
            "\nOWASP GitHub repositories count != synced repositories count: 3 != 2"
        )
        mock_project_objects.all.assert_called_once()
        mock_project.repositories.add.assert_called_once_with(mock_project.owasp_repository)
