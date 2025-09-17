import logging
from http import HTTPStatus
from unittest import mock

import pytest
from github.GithubException import GithubException, UnknownObjectException

from apps.github.management.commands.github_update_owasp_organization import (
    Chapter,
    Command,
    Committee,
    Project,
    Repository,
)
from apps.owasp.constants import OWASP_ORGANIZATION_NAME


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
@mock.patch(
    "apps.github.management.commands.github_update_owasp_organization.Command._sync_entity_markdown_data"
)
def test_handle(
    mock__sync_entity_markdown_data,
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

    mock__sync_entity_markdown_data.return_value = None

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
        mock.patch("builtins.print") as mock_print,
    ):
        mock_project_update.return_value = mock_repository
        mock_chapter_update.return_value = mock_repository
        mock_committee_update.return_value = mock_repository

        mock_project_objects.all.return_value = []
        mock_chapter_objects.all.return_value = []
        mock_committee_objects.all.return_value = []
        mock_repository_objects.filter.return_value.count.return_value = 1

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
            assert mock_print.call_count > 0

        mock_project_bulk_save.assert_called_once()
        mock_chapter_bulk_save.assert_called_once()
        mock_committee_bulk_save.assert_called_once()


class TestPrivateMethods:
    @pytest.fixture
    def command(self):
        return Command()

    @pytest.fixture
    def mock_entity(self):
        entity = mock.Mock()
        entity.key = "test-entity"
        entity.owasp_url = "https://owasp.org/www-project-test"
        entity.github_url = "https://github.com/owasp/test-project"
        entity.get_related_url.side_effect = lambda url, **_: url
        entity.invalid_urls = []
        entity.related_urls = []
        entity.get_leaders.return_value = "leader1,leader2"
        entity.get_leaders_emails.return_value = ["leader1@test.com", "leader2@test.com"]
        entity.sync_leaders = mock.Mock()
        entity.get_urls.return_value = []
        return entity

    @pytest.fixture
    def mock_project(self):
        project = mock.Mock(spec=Project)
        project.key = "test-project"
        project.owasp_url = "https://owasp.org/www-project-test"
        project.github_url = "https://github.com/owasp/test-project"
        project.get_related_url.side_effect = lambda url, **_: url
        project.invalid_urls = []
        project.related_urls = []
        project.get_leaders.return_value = "leader1,leader2"
        project.get_leaders_emails.return_value = ["leader1@test.com", "leader2@test.com"]
        project.sync_leaders = mock.Mock()
        project.get_urls.return_value = []
        project.get_audience.return_value = ["builder", "breaker"]
        return project

    @pytest.mark.parametrize(
        ("model_class", "manager_name", "entity_count"),
        [
            (Chapter, "active_chapters", 3),
            (Committee, "active_committees", 5),
            (Project, "active_projects", 2),
        ],
    )
    @mock.patch("time.sleep")
    @mock.patch("builtins.print")
    def test_sync_entity_markdown_data(
        self, mock_print, mock_sleep, command, mock_entity, model_class, manager_name, entity_count
    ):
        """Test _sync_entity_markdown_data method."""
        mock_gh = mock.Mock()
        mock_entities = [mock_entity] * entity_count

        mock_queryset = mock.MagicMock()
        mock_queryset.__iter__.return_value = iter(mock_entities)
        mock_queryset.count.return_value = entity_count

        mock_manager = mock.MagicMock()
        mock_manager.order_by.return_value = mock_queryset

        with (
            mock.patch.object(model_class, manager_name, mock_manager)
            if hasattr(model_class, manager_name)
            else mock.patch.object(model_class, "objects", mock_manager),
            mock.patch.object(command, "_validate_github_repo", return_value=True),
            mock.patch.object(
                command,
                "_get_project_urls" if model_class == Project else "_get_generic_urls",
                return_value=([], []),
            ),
            mock.patch.object(model_class, "bulk_save") as mock_bulk_save,
        ):
            if model_class == Project:
                mock_entity.get_audience.return_value = ["builder"]

            command._sync_entity_markdown_data(model_class, manager_name, mock_gh)

            assert mock_print.call_count == entity_count
            mock_bulk_save.assert_called_once_with(mock_entities)
            assert mock_sleep.call_count == entity_count

    def test_sync_entity_markdown_data_project_specific(self, command, mock_project):
        """Test _sync_entity_markdown_data with project-specific logic."""
        mock_gh = mock.Mock()
        mock_entities = [mock_project]

        mock_queryset = mock.MagicMock()
        mock_queryset.__iter__.return_value = iter(mock_entities)
        mock_queryset.count.return_value = 1

        mock_manager = mock.MagicMock()
        mock_manager.order_by.return_value = mock_queryset

        with (
            mock.patch.object(Project, "active_projects", mock_manager),
            mock.patch.object(command, "_validate_github_repo", return_value=True),
            mock.patch.object(
                command, "_get_project_urls", return_value=(["invalid.com"], ["valid.com"])
            ),
            mock.patch.object(Project, "bulk_save") as mock_bulk_save,
            mock.patch("time.sleep"),
            mock.patch("builtins.print"),
        ):
            command._sync_entity_markdown_data(Project, "active_projects", mock_gh)

            assert mock_project.audience == ["builder", "breaker"]
            assert mock_project.invalid_urls == ["invalid.com"]
            assert mock_project.related_urls == ["valid.com"]
            mock_bulk_save.assert_called_once_with(mock_entities)

    def test_sync_entity_markdown_data_skip_invalid_repo(self, command, mock_entity):
        """Test _sync_entity_markdown_data skips entities with invalid repos."""
        mock_gh = mock.Mock()
        mock_entities = [mock_entity]

        mock_queryset = mock.MagicMock()
        mock_queryset.__iter__.return_value = iter(mock_entities)
        mock_queryset.count.return_value = 1

        mock_manager = mock.MagicMock()
        mock_manager.order_by.return_value = mock_queryset

        with (
            mock.patch.object(Chapter, "active_chapters", mock_manager),
            mock.patch.object(command, "_validate_github_repo", return_value=False),
            mock.patch.object(Chapter, "bulk_save") as mock_bulk_save,
            mock.patch("time.sleep"),
            mock.patch("builtins.print"),
        ):
            command._sync_entity_markdown_data(Chapter, "active_chapters", mock_gh)

            # Entity should not be processed further
            mock_entity.get_leaders.assert_not_called()
            # The entities list will be empty since invalid repo was skipped
            mock_bulk_save.assert_called_once()
            call_args = mock_bulk_save.call_args[0][0]
            assert len(call_args) == 0  # Empty list since entity was skipped

    @mock.patch("apps.github.management.commands.github_update_owasp_organization.normalize_url")
    def test_get_project_urls_basic(self, mock_normalize_url, command, mock_project):
        """Test _get_project_urls with basic functionality."""
        mock_gh = mock.Mock()
        mock_normalize_url.side_effect = lambda url: url

        mock_project.get_urls.return_value = [
            "https://github.com/org/repo1",
            "https://github.com/org/repo2",
            "https://invalid.com/repo3",
        ]

        with (
            mock.patch.object(command, "_verify_url") as mock_verify_url,
        ):
            mock_verify_url.side_effect = lambda url: None if "invalid" in url else url

            invalid_urls, related_urls = command._get_project_urls(mock_project, mock_gh)

            assert invalid_urls == ["https://invalid.com/repo3"]
            assert related_urls == ["https://github.com/org/repo1", "https://github.com/org/repo2"]

    @mock.patch("apps.github.management.commands.github_update_owasp_organization.normalize_url")
    @mock.patch("apps.github.management.commands.github_update_owasp_organization.GITHUB_USER_RE")
    def test_get_project_urls_github_organization(
        self, mock_github_user_re, mock_normalize_url, command, mock_project
    ):
        """Test _get_project_urls with GitHub organization URL."""
        mock_gh = mock.Mock()
        mock_normalize_url.side_effect = lambda url: url
        mock_github_user_re.match.return_value = True

        mock_project.get_urls.return_value = ["https://github.com/test-org"]
        mock_project.get_related_url.return_value = "https://github.com/test-org"

        mock_gh_org = mock.Mock()
        mock_repo1 = mock.Mock()
        mock_repo1.full_name = "test-org/repo1"
        mock_repo2 = mock.Mock()
        mock_repo2.full_name = "test-org/repo2"
        mock_gh_org.get_repos.return_value = [mock_repo1, mock_repo2]
        mock_gh.get_organization.return_value = mock_gh_org

        with mock.patch.object(command, "_verify_url", return_value="https://github.com/test-org"):
            invalid_urls, related_urls = command._get_project_urls(mock_project, mock_gh)

            assert invalid_urls == []
            assert "https://github.com/test-org/repo1" in related_urls
            assert "https://github.com/test-org/repo2" in related_urls

    @mock.patch("apps.github.management.commands.github_update_owasp_organization.normalize_url")
    @mock.patch("apps.github.management.commands.github_update_owasp_organization.GITHUB_USER_RE")
    def test_get_project_urls_github_organization_not_found(
        self, mock_github_user_re, mock_normalize_url, command, mock_project, caplog
    ):
        """Test _get_project_urls with GitHub organization that doesn't exist."""
        mock_gh = mock.Mock()
        mock_normalize_url.side_effect = lambda url: url
        mock_github_user_re.match.return_value = True

        mock_project.get_urls.return_value = ["https://github.com/nonexistent"]
        mock_project.get_related_url.return_value = "https://github.com/nonexistent"

        mock_gh.get_organization.side_effect = UnknownObjectException(404, "Not found")

        with (
            mock.patch.object(
                command, "_verify_url", return_value="https://github.com/nonexistent"
            ),
            caplog.at_level(logging.INFO),
        ):
            invalid_urls, related_urls = command._get_project_urls(mock_project, mock_gh)

            assert invalid_urls == []
            assert related_urls == []
            assert "Couldn't get GitHub organization repositories" in caplog.text

    @mock.patch("apps.github.management.commands.github_update_owasp_organization.normalize_url")
    def test_get_generic_urls(self, mock_normalize_url, command, mock_entity):
        """Test _get_generic_urls method."""
        mock_normalize_url.side_effect = lambda url, **_: url

        mock_entity.get_urls.return_value = [
            "https://example.com/repo1",
            "https://example.com/repo2",
            "https://invalid.com/repo3",
        ]

        with (
            mock.patch.object(command, "_verify_url") as mock_verify_url,
        ):
            mock_verify_url.side_effect = lambda url: None if "invalid" in url else url

            invalid_urls, related_urls = command._get_generic_urls(mock_entity)

            assert invalid_urls == ["https://invalid.com/repo3"]
            assert related_urls == ["https://example.com/repo1", "https://example.com/repo2"]

    @mock.patch("apps.github.management.commands.github_update_owasp_organization.normalize_url")
    def test_get_generic_urls_filtered_url(self, mock_normalize_url, command, mock_entity, caplog):
        """Test _get_generic_urls with URL that gets filtered out."""
        mock_normalize_url.side_effect = lambda url, **_: url

        mock_entity.get_urls.return_value = ["https://example.com/test"]
        mock_entity.get_related_url.side_effect = [
            None,
            None,
        ]  # First call for filtering, second for final check

        with (
            mock.patch.object(command, "_verify_url", return_value="https://example.com/test"),
            caplog.at_level(logging.INFO),
        ):
            invalid_urls, related_urls = command._get_generic_urls(mock_entity)

            assert invalid_urls == []
            assert related_urls == []

    def test_validate_github_repo_exists(self, command, mock_entity):
        """Test _validate_github_repo when repository exists."""
        mock_gh = mock.Mock()
        mock_gh.get_repo.return_value = mock.Mock()

        result = command._validate_github_repo(mock_gh, mock_entity)

        assert result is True
        mock_gh.get_repo.assert_called_once_with(f"{OWASP_ORGANIZATION_NAME}/test-entity")
        mock_entity.deactivate.assert_not_called()

    def test_validate_github_repo_not_found(self, command, mock_entity):
        """Test _validate_github_repo when repository doesn't exist."""
        mock_gh = mock.Mock()
        mock_gh.get_repo.side_effect = UnknownObjectException(404, "Not found")

        result = command._validate_github_repo(mock_gh, mock_entity)

        assert result is False
        mock_gh.get_repo.assert_called_once_with(f"{OWASP_ORGANIZATION_NAME}/test-entity")
        mock_entity.deactivate.assert_called_once()

    @mock.patch("time.sleep")
    def test_validate_github_repo_github_exception(self, mock_sleep, command, mock_entity, caplog):
        """Test _validate_github_repo with GitHub API error."""
        mock_gh = mock.Mock()
        mock_gh.get_repo.side_effect = GithubException(500, "Server error")

        with caplog.at_level(logging.WARNING):
            result = command._validate_github_repo(mock_gh, mock_entity)

        assert result is False
        assert "GitHub API error for test-entity" in caplog.text
        mock_sleep.assert_called_once_with(1)
        mock_entity.deactivate.assert_not_called()


class TestVerifyUrl:
    @pytest.fixture
    def command(self):
        return Command()

    @pytest.mark.parametrize(
        ("url", "expected"),
        [
            ("https://www.linkedin.com/in/test", "https://www.linkedin.com/in/test"),
            ("https://my-company.slack.com", "https://my-company.slack.com"),
            ("youtube.com", None),
        ],
    )
    @mock.patch("apps.github.management.commands.github_update_owasp_organization.requests.get")
    def test_verify_url_allowed_domains_bypass_request(self, mock_get, url, expected, command):
        """Test that specifically allowed domains bypass network requests."""
        assert command._verify_url(url) == expected
        mock_get.assert_not_called()

    def test_verify_url_invalid_url(self, command):
        """Test that an invalidly formatted URL returns None."""
        assert command._verify_url("invalid-url") is None

    @mock.patch("apps.github.management.commands.github_update_owasp_organization.requests.get")
    def test_verify_url_logs_warning(self, mock_get, caplog, command):
        """Test that a warning is logged for an unverified URL."""
        response = mock.Mock()
        response.status_code = HTTPStatus.FORBIDDEN  # 403
        mock_get.return_value = response

        with caplog.at_level(logging.WARNING):
            result = command._verify_url("https://test.org")

        assert result is None
        assert "Couldn't verify URL" in caplog.text

    @mock.patch("apps.github.management.commands.github_update_owasp_organization.requests.get")
    def test_verify_url_redirect_chain(self, mock_get, command):
        """Test URL verification with a redirect chain."""
        redirect_response = mock.Mock()
        redirect_response.status_code = HTTPStatus.MOVED_PERMANENTLY
        redirect_response.headers = {"Location": "https://new-url.org"}

        final_response = mock.Mock()
        final_response.status_code = HTTPStatus.OK
        mock_get.side_effect = [redirect_response, final_response]

        assert command._verify_url("https://old-url.org") == "https://new-url.org"
        assert mock_get.call_count == 2

    @pytest.mark.parametrize(
        "status_code",
        [
            HTTPStatus.MOVED_PERMANENTLY,  # 301
            HTTPStatus.FOUND,  # 302
            HTTPStatus.SEE_OTHER,  # 303
            HTTPStatus.TEMPORARY_REDIRECT,  # 307
            HTTPStatus.PERMANENT_REDIRECT,  # 308
        ],
    )
    @mock.patch("apps.github.management.commands.github_update_owasp_organization.requests.get")
    def test_verify_url_redirect_status_codes(self, mock_get, status_code, command):
        """Test URL verification with different redirect status codes."""
        redirect_response = mock.Mock()
        redirect_response.status_code = status_code
        redirect_response.headers = {"Location": "https://new-url.org"}

        final_response = mock.Mock()
        final_response.status_code = HTTPStatus.OK
        mock_get.side_effect = [redirect_response, final_response]

        assert command._verify_url("https://old-url.org") == "https://new-url.org"

    @mock.patch("apps.github.management.commands.github_update_owasp_organization.requests.get")
    def test_verify_url_unsupported_status_code(self, mock_get, command):
        """Test that a non-200, non-redirect status code returns None."""
        response = mock.Mock()
        response.status_code = HTTPStatus.IM_A_TEAPOT  # 418
        mock_get.return_value = response

        assert command._verify_url("https://test.org") is None
