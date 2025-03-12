from unittest.mock import Mock, patch

import pytest

from apps.github.models.repository import Repository
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
            (Project.ProjectType.CODE, True),
            (Project.ProjectType.DOCUMENTATION, False),
            (Project.ProjectType.TOOL, False),
        ],
    )
    def test_is_code_type(self, project_type, expected_result):
        project = Project(type=project_type)
        assert project.is_code_type == expected_result

    @pytest.mark.parametrize(
        ("project_type", "expected_result"),
        [
            (Project.ProjectType.CODE, False),
            (Project.ProjectType.DOCUMENTATION, True),
            (Project.ProjectType.TOOL, False),
        ],
    )
    def test_is_documentation_type(self, project_type, expected_result):
        project = Project(type=project_type)
        assert project.is_documentation_type == expected_result

    @pytest.mark.parametrize(
        ("project_type", "expected_result"),
        [
            (Project.ProjectType.CODE, False),
            (Project.ProjectType.DOCUMENTATION, False),
            (Project.ProjectType.TOOL, True),
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

        with patch.object(Project, "save", return_value=None) as mock_save:
            project = Project.update_data(gh_repository_mock, repository_mock, save=True)
            mock_save.assert_called_once()
            assert project.key == "new_repo"
            assert project.owasp_repository == repository_mock

    def test_from_github(self):
        repository_mock = Repository()
        repository_mock.name = "Test Repo"
        repository_mock.title = "Nest"
        repository_mock.pitch = "Nest Pitch"
        repository_mock.tags = "react, python"
        repository_mock.leaders = ["Leader1", "Leader2"]

        project = Project()

        with patch(
            "apps.owasp.models.project.RepositoryBasedEntityModel.from_github"
        ) as mock_from_github:
            mock_from_github.return_value = {"level": 3, "type": "tool"}

            project.from_github(repository_mock)

        assert project.owasp_repository == repository_mock
        mock_from_github.assert_called_once_with(
            project,
            {
                "description": "pitch",
                "leaders_raw": "leaders",
                "name": "title",
                "tags": "tags",
            },
            repository_mock,
        )

        assert project.level == Project.ProjectLevel.LAB
        assert project.type == Project.ProjectType.TOOL
