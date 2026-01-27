from unittest.mock import Mock, patch
import uuid

import pytest
from django.utils import timezone

from apps.github.models.release import Release
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

        with patch("apps.owasp.models.project.RepositoryBasedEntityModel.from_github") as mock_from_github:
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

    def test_project_has_published_releases_m2m_field(self):
        """Ensure Project.published_releases is a real ManyToManyField (not a property)."""
        m2m_fields = [f.name for f in Project._meta.many_to_many]
        assert "published_releases" in m2m_fields

    @pytest.mark.django_db
    def test_recent_releases_count_uses_published_releases_m2m(self):
        """Ensure recent_releases_count uses published_releases M2M relation."""
        unique = uuid.uuid4().hex[:8]
        now = timezone.now()

        project = Project.objects.create(
            key=f"test-project-{unique}",
            name="Test Project",
        )

        # ✅ REQUIRED: Repository.path uses owner.login
        owner = User.objects.create(
            login=f"owasp-{unique}",
            name="OWASP",
            created_at=now,        # ✅ REQUIRED (NOT NULL)
            updated_at=now,
        )

        repo = Repository.objects.create(
            key=f"test-repo-{unique}",
            name="Test Repo",
            owner=owner,  # ✅ FIX
            created_at=now,
            updated_at=now,
            pushed_at=now,
        )

        old_release = Release.objects.create(
            node_id=f"release-old-{unique}",  # ✅ FIX (unique + not empty)
            repository=repo,
            name="Old Release",
            tag_name="0.1.0",
            description="",
            is_draft=False,
            is_pre_release=False,
            sequence_id=1,
            created_at=now,
            published_at=now - timezone.timedelta(days=120),
        )

        recent_release = Release.objects.create(
            node_id=f"release-recent-{unique}",  # ✅ FIX (unique + not empty)
            repository=repo,
            name="Recent Release",
            tag_name="0.2.0",
            description="",
            is_draft=False,
            is_pre_release=False,
            sequence_id=2,
            created_at=now,
            published_at=now - timezone.timedelta(days=10),
        )

        project.published_releases.add(old_release, recent_release)

        # ✅ FIX: recent_releases_count is a method
        assert project.recent_releases_count == 1
