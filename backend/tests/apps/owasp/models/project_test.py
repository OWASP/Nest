from datetime import UTC, datetime
from unittest.mock import Mock, patch

import pytest

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


class TestProjectProperties:
    """Tests for additional Project property methods."""

    def test_entity_leaders(self, mocker):
        """Test entity_leaders returns up to MAX_LEADERS_COUNT leaders."""
        mock_leaders = [Mock() for _ in range(7)]
        mocker.patch(
            "apps.owasp.models.common.RepositoryBasedEntityModel.entity_leaders",
            new_callable=mocker.PropertyMock,
            return_value=mock_leaders,
        )

        project = Project()
        result = project.entity_leaders

        assert len(result) == 5  # MAX_LEADERS_COUNT

    def test_health_score_with_metrics(self, mocker):
        """Test health_score returns score when metrics exist."""
        mock_metrics = Mock()
        mock_metrics.score = 85.5
        mocker.patch.object(
            Project,
            "last_health_metrics",
            new_callable=mocker.PropertyMock,
            return_value=mock_metrics,
        )

        project = Project()
        assert project.health_score == 85.5

    def test_health_score_without_metrics(self, mocker):
        """Test health_score returns None when no metrics."""
        mocker.patch.object(
            Project, "last_health_metrics", new_callable=mocker.PropertyMock, return_value=None
        )

        project = Project()
        assert project.health_score is None

    def test_is_funding_requirements_compliant(self, mocker):
        """Test is_funding_requirements_compliant checks repositories."""
        mock_repos = Mock()
        mock_repos.filter.return_value.exists.return_value = False
        mocker.patch.object(
            Project, "repositories", new_callable=mocker.PropertyMock, return_value=mock_repos
        )

        project = Project()
        assert project.is_funding_requirements_compliant

    def test_is_leader_requirements_compliant_with_multiple_leaders(self, mocker):
        """Test returns True when more than one leader."""
        mocker.patch.object(
            Project, "leaders_count", new_callable=mocker.PropertyMock, return_value=3
        )

        project = Project()
        assert project.is_leader_requirements_compliant

    def test_is_leader_requirements_compliant_with_single_leader(self, mocker):
        """Test returns False when only one leader."""
        mocker.patch.object(
            Project, "leaders_count", new_callable=mocker.PropertyMock, return_value=1
        )

        project = Project()
        assert not project.is_leader_requirements_compliant

    def test_issues(self, mocker):
        """Test issues property returns filtered queryset."""
        mock_issue = mocker.patch("apps.owasp.models.project.Issue")
        mock_repos = Mock()
        mock_repos.all.return_value = ["repo1"]
        mocker.patch.object(
            Project, "repositories", new_callable=mocker.PropertyMock, return_value=mock_repos
        )

        project = Project()
        _ = project.issues

        mock_issue.objects.filter.assert_called_once()

    def test_issues_count(self, mocker):
        """Test issues_count returns count."""
        mock_issues = Mock()
        mock_issues.count.return_value = 42
        mocker.patch.object(
            Project, "issues", new_callable=mocker.PropertyMock, return_value=mock_issues
        )

        project = Project()
        assert project.issues_count == 42

    def test_last_health_metrics(self, mocker):
        """Test last_health_metrics returns the latest metrics."""
        mock_metrics = Mock()
        mock_health_metrics = Mock()
        mock_health_metrics.order_by.return_value.first.return_value = mock_metrics
        mocker.patch.object(
            Project,
            "health_metrics",
            new_callable=mocker.PropertyMock,
            return_value=mock_health_metrics,
        )

        project = Project()
        result = project.last_health_metrics

        mock_health_metrics.order_by.assert_called_once_with("-nest_created_at")
        assert result == mock_metrics

    def test_leaders_count(self):
        """Test leaders_count returns length of leaders_raw."""
        project = Project()
        project.leaders_raw = ["leader1", "leader2", "leader3"]
        assert project.leaders_count == 3

    def test_nest_key(self):
        """Test nest_key removes www-project- prefix."""
        project = Project(key="www-project-juice-shop")
        assert project.nest_key == "juice-shop"

    def test_nest_url(self, mocker):
        """Test nest_url returns full URL."""
        mocker.patch(
            "apps.owasp.models.project.get_absolute_url",
            return_value="https://nest.owasp.org/projects/juice-shop",
        )

        project = Project(key="www-project-juice-shop")
        assert "juice-shop" in project.nest_url

    def test_open_issues(self, mocker):
        """Test open_issues returns filtered queryset."""
        mock_issue = mocker.patch("apps.owasp.models.project.Issue")
        mock_repos = Mock()
        mock_repos.all.return_value = ["repo1"]
        mocker.patch.object(
            Project, "repositories", new_callable=mocker.PropertyMock, return_value=mock_repos
        )

        project = Project()
        _ = project.open_issues

        mock_issue.open_issues.filter.assert_called_once()

    def test_open_pull_requests_count(self, mocker):
        """Test open_pull_requests_count returns count of open PRs."""
        mock_prs = Mock()
        mock_prs.filter.return_value.count.return_value = 7
        mocker.patch.object(
            Project, "pull_requests", new_callable=mocker.PropertyMock, return_value=mock_prs
        )

        project = Project()
        assert project.open_pull_requests_count == 7

    def test_owasp_page_last_updated_at_with_repo(self, mocker):
        """Test returns updated_at from owasp_repository."""
        mock_repo = Mock()
        mock_repo.updated_at = datetime(2024, 1, 15, tzinfo=UTC)
        mocker.patch.object(
            Project, "owasp_repository", new_callable=mocker.PropertyMock, return_value=mock_repo
        )

        project = Project()
        assert project.owasp_page_last_updated_at == datetime(2024, 1, 15, tzinfo=UTC)

    def test_owasp_page_last_updated_at_without_repo(self, mocker):
        """Test returns None when no owasp_repository."""
        mocker.patch.object(
            Project, "owasp_repository", new_callable=mocker.PropertyMock, return_value=None
        )

        project = Project()
        assert project.owasp_page_last_updated_at is None

    def test_pull_requests(self, mocker):
        """Test pull_requests property returns filtered queryset."""
        mock_pr = mocker.patch("apps.owasp.models.project.PullRequest")
        mock_repos = Mock()
        mock_repos.all.return_value = ["repo1"]
        mocker.patch.object(
            Project, "repositories", new_callable=mocker.PropertyMock, return_value=mock_repos
        )

        project = Project()
        _ = project.pull_requests

        mock_pr.objects.filter.assert_called_once()

    def test_pull_requests_count(self, mocker):
        """Test pull_requests_count returns count."""
        mock_prs = Mock()
        mock_prs.count.return_value = 25
        mocker.patch.object(
            Project, "pull_requests", new_callable=mocker.PropertyMock, return_value=mock_prs
        )

        project = Project()
        assert project.pull_requests_count == 25

    def test_pull_request_last_created_at(self, mocker):
        """Test pull_request_last_created_at returns max created_at."""
        mock_prs = Mock()
        mock_prs.aggregate.return_value = {"created_at__max": datetime(2024, 1, 20, tzinfo=UTC)}
        mocker.patch.object(
            Project, "pull_requests", new_callable=mocker.PropertyMock, return_value=mock_prs
        )

        project = Project()
        result = project.pull_request_last_created_at

        assert result == datetime(2024, 1, 20, tzinfo=UTC)

    def test_published_releases(self, mocker):
        """Test published_releases returns filtered queryset."""
        mock_release = mocker.patch("apps.owasp.models.project.Release")
        mock_repos = Mock()
        mock_repos.all.return_value = ["repo1"]
        mocker.patch.object(
            Project, "repositories", new_callable=mocker.PropertyMock, return_value=mock_repos
        )

        project = Project()
        _ = project.published_releases

        mock_release.objects.filter.assert_called_once()

    def test_recent_milestones(self, mocker):
        """Test recent_milestones returns filtered queryset."""
        mock_milestone = mocker.patch("apps.owasp.models.project.Milestone")
        mock_repos = Mock()
        mock_repos.all.return_value = ["repo1"]
        mocker.patch.object(
            Project, "repositories", new_callable=mocker.PropertyMock, return_value=mock_repos
        )

        project = Project()
        _ = project.recent_milestones

        mock_milestone.objects.filter.assert_called_once()

    def test_recent_releases_count(self, mocker):
        """Test recent_releases_count returns count of recent releases."""
        mock_releases = Mock()
        mock_releases.filter.return_value.count.return_value = 3
        mocker.patch.object(
            Project,
            "published_releases",
            new_callable=mocker.PropertyMock,
            return_value=mock_releases,
        )

        project = Project()
        result = project.recent_releases_count

        assert result == 3

    def test_repositories_count(self, mocker):
        """Test repositories_count returns count."""
        mock_repos = Mock()
        mock_repos.count.return_value = 5
        mocker.patch.object(
            Project, "repositories", new_callable=mocker.PropertyMock, return_value=mock_repos
        )

        project = Project()
        assert project.repositories_count == 5

    def test_unanswered_issues_count(self, mocker):
        """Test unanswered_issues_count returns count of issues with no comments."""
        mock_issues = Mock()
        mock_issues.filter.return_value.count.return_value = 10
        mocker.patch.object(
            Project, "issues", new_callable=mocker.PropertyMock, return_value=mock_issues
        )

        project = Project()
        result = project.unanswered_issues_count

        mock_issues.filter.assert_called_once_with(comments_count=0)
        assert result == 10

    def test_unassigned_issues_count(self, mocker):
        """Test unassigned_issues_count returns count of unassigned issues."""
        mock_issues = Mock()
        mock_issues.filter.return_value.count.return_value = 8
        mocker.patch.object(
            Project, "issues", new_callable=mocker.PropertyMock, return_value=mock_issues
        )

        project = Project()
        result = project.unassigned_issues_count

        mock_issues.filter.assert_called_once_with(assignees__isnull=True)
        assert result == 8

    def test_get_absolute_url(self):
        """Test get_absolute_url returns project URL."""
        project = Project(key="www-project-test")
        assert project.get_absolute_url() == "/projects/test"

    def test_save_generates_summary(self, mocker):
        """Test save generates summary when conditions are met."""
        mock_prompt = Mock()
        mocker.patch(
            "apps.owasp.models.project.Prompt.get_owasp_project_summary",
            return_value=mock_prompt,
        )
        mock_generate = mocker.patch.object(Project, "generate_summary")
        mocker.patch.object(Project.__bases__[0], "save")

        project = Project(is_active=True, summary="")
        project.save()

        mock_generate.assert_called_once_with(prompt=mock_prompt)

    def test_save_skips_summary_when_exists(self, mocker):
        """Test save skips summary generation when summary exists."""
        mock_generate = mocker.patch.object(Project, "generate_summary")
        mocker.patch.object(Project.__bases__[0], "save")

        project = Project(is_active=True, summary="Existing summary")
        project.save()

        mock_generate.assert_not_called()
