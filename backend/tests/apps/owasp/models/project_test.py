import logging
from unittest.mock import Mock, patch

import pytest
from github.GithubException import UnknownObjectException

from apps.github.models.repository import Repository
from apps.github.models.user import User
from apps.owasp.models.enums.project import ProjectLevel, ProjectType
from apps.owasp.models.project import Project


class TestProjectModel:
    def setup_method(self):
        """Set up test fixtures."""
        self.model = Project()
        self.model.id = 1

    @pytest.mark.parametrize(
        ("content", "expected_audience"),
        [
            (
                """### Top Ten Card Game Information
* [Incubator Project](#)
* [Type of Project](#)
* [Version 0.0.0](#)
* [Builder](#)
* [Breaker](#)""",
                ["breaker", "builder"],
            ),
            ("This test contains no audience information.", []),
            ("", []),
            (None, []),
        ],
    )
    def test_get_audience(self, content, expected_audience):
        project = Project()
        repository = Repository()
        repository.name = "www-project-example"
        project.owasp_repository = repository

        with patch("apps.owasp.models.project.get_repository_file_content", return_value=content):
            audience = project.get_audience()

        assert audience == expected_audience

    @pytest.mark.parametrize(
        ("url", "expected_url"),
        [
            ("https://github.com/owasp/repository", "https://github.com/owasp/repository"),
            ("https://owasp.org/repository", "https://owasp.org/repository"),
            ("https://github.com/username", "https://github.com/username"),
            ("https://github.com/OWASP/repo/tree/v1.0.0/1.0", "https://github.com/owasp/repo"),
        ],
    )
    def test_get_related_url(self, url, expected_url):
        project = Project()
        project.key = "repository"
        assert project.get_related_url(url) == expected_url

    @pytest.mark.parametrize(
        ("level", "project_type", "name", "key", "expected_str"),
        [
            ("lab", "code", None, "project_key", "project_key"),
            ("flagship", "tool", "Project Name", None, "Project Name"),
        ],
    )
    def test_project_str(self, level, project_type, name, key, expected_str):
        project = Project(level=level, type=project_type, name=name, key=key)
        assert str(project) == expected_str

    @pytest.mark.parametrize(
        ("project_type", "expected_result"),
        [
            (ProjectType.CODE, True),
            (ProjectType.DOCUMENTATION, False),
            (ProjectType.TOOL, False),
        ],
    )
    def test_is_code_type(self, project_type, expected_result):
        project = Project(type=project_type)
        assert project.is_code_type == expected_result

    @pytest.mark.parametrize(
        ("project_type", "expected_result"),
        [
            (ProjectType.CODE, False),
            (ProjectType.DOCUMENTATION, True),
            (ProjectType.TOOL, False),
        ],
    )
    def test_is_documentation_type(self, project_type, expected_result):
        project = Project(type=project_type)
        assert project.is_documentation_type == expected_result

    @pytest.mark.parametrize(
        ("project_type", "expected_result"),
        [
            (ProjectType.CODE, False),
            (ProjectType.DOCUMENTATION, False),
            (ProjectType.TOOL, True),
        ],
    )
    def test_is_tool_type(self, project_type, expected_result):
        project = Project(type=project_type)
        assert project.is_tool_type == expected_result

    @patch.object(Project, "save")
    def test_deactivate(self, mock_save):
        project = Project(is_active=True)
        project.deactivate()
        assert not project.is_active
        mock_save.assert_called_once_with(update_fields=("is_active",))

    @patch("apps.owasp.models.project.Project.objects.get")
    @patch("apps.github.utils.requests.get")
    def test_update_data_project_does_not_exist(self, mock_requests_get, mock_get):
        """Test updating project data when the project doesn't exist."""
        mock_get.side_effect = Project.DoesNotExist

        mock_response = Mock()
        mock_response.text = """
        # Project Title
        Some project description
        """
        mock_requests_get.return_value = mock_response

        # Setup test data
        gh_repository_mock = Mock()
        gh_repository_mock.name = "new_repo"
        repository_mock = Repository()

        with (
            patch.object(Project, "save", return_value=None) as mock_save,
            patch("apps.github.auth.Github") as mock_github,
        ):
            project = Project.update_data(
                gh_repository_mock, repository_mock, mock_github, save=True
            )
            mock_save.assert_called_once()
            assert project.key == "new_repo"
            assert project.owasp_repository == repository_mock

    def test_from_github(self):
        owasp_repository = Repository()
        owasp_repository.name = "Test Repo"
        owasp_repository.owner = User(name="OWASP")
        owasp_repository.pitch = "Nest Pitch"
        owasp_repository.tags = "react, python"
        owasp_repository.title = "Nest"

        project = Project()
        project.owasp_repository = owasp_repository

        with (
            patch(
                "apps.owasp.models.project.RepositoryBasedEntityModel.from_github"
            ) as mock_from_github,
            patch("apps.github.auth.Github") as mock_github,
        ):
            mock_from_github.return_value = {"level": 3, "type": "tool"}
            project.from_github(owasp_repository, mock_github)

        mock_from_github.assert_called_once_with(
            project,
            {
                "description": "pitch",
                "name": "title",
                "tags": "tags",
            },
            mock_github,
        )

        assert project.created_at == owasp_repository.created_at
        assert project.level == ProjectLevel.LAB
        assert project.type == ProjectType.TOOL
        assert project.updated_at == owasp_repository.updated_at

    @patch("apps.owasp.models.project.normalize_url")
    def test__process_urls_basic(self, mock_normalize_url):
        """Test _process_urls with basic functionality."""
        mock_gh = Mock()
        mock_normalize_url.side_effect = lambda url: url

        with (
            patch.object(
                self.model,
                "get_urls",
                return_value=[
                    "https://github.com/org/repo1",
                    "https://github.com/org/repo2",
                    "https://invalid.com/repo3",
                ],
            ),
            patch.object(self.model, "_verify_url") as mock_verify_url,
        ):
            mock_verify_url.side_effect = lambda url: None if "invalid" in url else url

            self.model._process_urls(mock_gh)

            assert self.model.invalid_urls == ["https://invalid.com/repo3"]
            assert self.model.related_urls == [
                "https://github.com/org/repo1",
                "https://github.com/org/repo2",
            ]

    @patch("apps.owasp.models.project.normalize_url")
    @patch("apps.owasp.models.project.GITHUB_USER_RE")
    def test__process_urls_github_organization(self, mock_github_user_re, mock_normalize_url):
        """Test _process_urls with GitHub organization URL."""
        mock_gh = Mock()
        mock_normalize_url.side_effect = lambda url: url
        mock_github_user_re.match.return_value = True

        mock_gh_org = Mock()
        mock_repo1 = Mock()
        mock_repo1.full_name = "test-org/repo1"
        mock_repo2 = Mock()
        mock_repo2.full_name = "test-org/repo2"
        mock_gh_org.get_repos.return_value = [mock_repo1, mock_repo2]
        mock_gh.get_organization.return_value = mock_gh_org

        with (
            patch.object(self.model, "get_urls", return_value=["https://github.com/test-org"]),
            patch.object(
                self.model, "get_related_url", return_value="https://github.com/test-org"
            ),
            patch.object(self.model, "_verify_url", return_value="https://github.com/test-org"),
        ):
            self.model._process_urls(mock_gh)

            assert self.model.invalid_urls == []
            assert "https://github.com/test-org/repo1" in self.model.related_urls
            assert "https://github.com/test-org/repo2" in self.model.related_urls

    @patch("apps.owasp.models.project.normalize_url")
    @patch("apps.owasp.models.project.GITHUB_USER_RE")
    def test__process_urls_github_organization_not_found(
        self, mock_github_user_re, mock_normalize_url, caplog
    ):
        """Test _get_project_urls with GitHub organization that doesn't exist."""
        mock_gh = Mock()
        mock_normalize_url.side_effect = lambda url: url
        mock_github_user_re.match.return_value = True

        mock_gh.get_organization.side_effect = UnknownObjectException(404, "Not found")

        with (
            patch.object(self.model, "get_urls", return_value=["https://github.com/nonexistent"]),
            patch.object(
                self.model, "get_related_url", return_value="https://github.com/nonexistent"
            ),
            patch.object(self.model, "_verify_url", return_value="https://github.com/nonexistent"),
            caplog.at_level(logging.INFO),
        ):
            self.model._process_urls(mock_gh)

            assert self.model.invalid_urls == []
            assert self.model.related_urls == []
            assert "Couldn't get GitHub organization repositories" in caplog.text
