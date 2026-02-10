from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from django.utils import timezone

from apps.github.models.repository import Repository
from apps.github.models.user import User
from apps.owasp.models.enums.project import ProjectLevel, ProjectType
from apps.owasp.models.project import Project


class TestProjectModel:
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
        gh_repository_mock = Mock()
        gh_repository_mock.name = "new_repo"
        repository_mock = Repository()

        with patch.object(Project, "save", return_value=None) as mock_save:
            project = Project.update_data(gh_repository_mock, repository_mock, save=True)
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

        with patch(
            "apps.owasp.models.project.RepositoryBasedEntityModel.from_github"
        ) as mock_from_github:
            mock_from_github.return_value = {"level": 3, "type": "tool"}
            project.from_github(owasp_repository)

        mock_from_github.assert_called_once_with(
            project,
            {
                "description": "pitch",
                "name": "title",
                "tags": "tags",
            },
        )

        assert project.created_at == owasp_repository.created_at
        assert project.level == ProjectLevel.LAB
        assert project.type == ProjectType.TOOL
        assert project.updated_at == owasp_repository.updated_at


class TestProjectPullRequestsM2M:
    """Test Project pull_requests M2M field and related properties."""

    @pytest.fixture
    def mock_project(self):
        """Create mock project with pull_requests M2M field."""
        project = Mock(spec=Project)
        project.pull_requests = Mock()
        return project

    def test_pull_requests_count_with_empty_m2m(self, mock_project):
        """Test pull_requests_count returns 0 when no PRs are associated."""
        mock_project.pull_requests.count.return_value = 0

        result = Project.pull_requests_count.fget(mock_project)

        assert result == 0
        mock_project.pull_requests.count.assert_called_once()

    def test_pull_requests_count_with_m2m_data(self, mock_project):
        """Test pull_requests_count uses M2M field."""
        mock_project.pull_requests.count.return_value = 5

        result = Project.pull_requests_count.fget(mock_project)

        assert result == 5
        mock_project.pull_requests.count.assert_called_once()

    def test_open_pull_requests_count_filters_by_state(self, mock_project):
        """Test open_pull_requests_count filters by state='open'."""
        mock_filtered = Mock()
        mock_filtered.count.return_value = 3
        mock_project.pull_requests.filter.return_value = mock_filtered

        result = Project.open_pull_requests_count.fget(mock_project)

        assert result == 3
        mock_project.pull_requests.filter.assert_called_once_with(state="open")

    def test_pull_request_last_created_at_returns_max_date(self, mock_project):
        """Test pull_request_last_created_at returns the most recent created_at."""
        expected_date = datetime(2024, 1, 15, tzinfo=timezone.UTC)
        mock_project.pull_requests.aggregate.return_value = {"created_at__max": expected_date}

        result = Project.pull_request_last_created_at.fget(mock_project)

        assert result == expected_date
        mock_project.pull_requests.aggregate.assert_called_once()

    def test_pull_request_last_created_at_returns_none_when_empty(self, mock_project):
        """Test pull_request_last_created_at returns None when no PRs exist."""
        mock_project.pull_requests.aggregate.return_value = {"created_at__max": None}

        result = Project.pull_request_last_created_at.fget(mock_project)

        assert result is None
