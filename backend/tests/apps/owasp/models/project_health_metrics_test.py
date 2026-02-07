import math
from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.owasp.models.project import Project
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics


class TestProjectHealthMetricsModel:
    DEFAULT_SCORE = None
    VALID_SCORE = 75.0
    MAX_SCORE = 100.0
    MIN_SCORE = 0.0
    FIXED_DATE = timezone.make_aware(
        timezone.datetime(2025, 1, 1), timezone.get_default_timezone()
    )

    @pytest.fixture
    def mock_project(self):
        """Mock a Project instance with simulated persistence."""
        project = Project(key="test_project", name="Test Project")
        project.pk = 1
        return project

    @pytest.mark.parametrize(
        ("project_name", "expected"),
        [
            ("Secure Project", "Health Metrics for Secure Project"),
            ("", "Health Metrics for "),
            (None, "Health Metrics for None"),
        ],
    )
    def test_str_representation(self, mock_project, project_name, expected):
        """Should return correct string representation."""
        mock_project.name = project_name
        metrics = ProjectHealthMetrics(project=mock_project)
        assert str(metrics) == expected

    @pytest.mark.parametrize(
        ("score", "is_valid"),
        [
            (VALID_SCORE, True),
            (MAX_SCORE, True),
            (MIN_SCORE, True),
            (MAX_SCORE + 0.1, False),
            (MIN_SCORE - 10.0, False),
        ],
    )
    def test_score_validation(self, score, is_valid):
        """Should validate score within allowed range."""
        metrics = ProjectHealthMetrics(score=score)

        if is_valid:
            metrics.clean_fields(exclude=["project"])
            assert metrics.score == score
        else:
            with pytest.raises(ValidationError) as exc_info:
                metrics.clean_fields(exclude=["project"])
            assert "score" in exc_info.value.error_dict

    def test_default_score(self):
        """Should initialize with default score value."""
        metrics = ProjectHealthMetrics()
        assert metrics.score == self.DEFAULT_SCORE

    @pytest.mark.parametrize(
        ("field_name", "expected_default"),
        [
            ("age_days", 0),
            ("contributors_count", 0),
            ("forks_count", 0),
            ("is_funding_requirements_compliant", False),
            ("is_leader_requirements_compliant", False),
            ("last_committed_at", None),
            ("last_commit_days", 0),
            ("last_pull_request_days", 0),
            ("last_released_at", None),
            ("last_release_days", 0),
            ("open_issues_count", 0),
            ("open_pull_requests_count", 0),
            ("owasp_page_last_updated_at", None),
            ("owasp_page_last_update_days", 0),
            ("pull_request_last_created_at", None),
            ("recent_releases_count", 0),
            ("score", None),
            ("stars_count", 0),
            ("total_issues_count", 0),
            ("total_pull_requests_count", 0),
            ("total_releases_count", 0),
            ("unanswered_issues_count", 0),
            ("unassigned_issues_count", 0),
        ],
    )
    def test_count_defaults(self, field_name, expected_default):
        """Should initialize count fields with proper defaults."""
        metrics = ProjectHealthMetrics()
        assert getattr(metrics, field_name) == expected_default

    @pytest.mark.parametrize(
        ("field_name", "expected_days"),
        [
            ("age_days", (timezone.now() - FIXED_DATE).days),
            ("last_commit_days", (timezone.now() - FIXED_DATE).days),
            ("last_pull_request_days", (timezone.now() - FIXED_DATE).days),
            ("last_release_days", (timezone.now() - FIXED_DATE).days),
            ("owasp_page_last_update_days", (timezone.now() - FIXED_DATE).days),
        ],
    )
    def test_handle_days_calculation(self, field_name, expected_days):
        """Should return correct days for date fields."""
        metrics = ProjectHealthMetrics()
        metrics.created_at = self.FIXED_DATE
        metrics.last_committed_at = self.FIXED_DATE
        metrics.last_released_at = self.FIXED_DATE
        metrics.owasp_page_last_updated_at = self.FIXED_DATE
        metrics.pull_request_last_created_at = self.FIXED_DATE

        assert getattr(metrics, field_name) == expected_days


class TestProjectHealthMetricsRequirements:
    """Tests for requirement properties."""

    def test_age_days_requirement_with_requirements(self):
        """Test age_days_requirement returns value when requirements exist."""
        mock_requirements = MagicMock()
        mock_requirements.age_days = 30

        metrics = ProjectHealthMetrics()
        with patch.object(
            ProjectHealthMetrics,
            "project_requirements",
            new_callable=lambda: property(lambda _: mock_requirements),
        ):
            assert metrics.age_days_requirement == 30

    def test_age_days_requirement_without_requirements(self):
        """Test age_days_requirement returns 0 when no requirements."""
        metrics = ProjectHealthMetrics()
        with patch.object(
            ProjectHealthMetrics,
            "project_requirements",
            new_callable=lambda: property(lambda _: None),
        ):
            assert metrics.age_days_requirement == 0

    def test_last_commit_days_requirement_with_requirements(self):
        """Test last_commit_days_requirement returns value when requirements exist."""
        mock_requirements = MagicMock()
        mock_requirements.last_commit_days = 14

        metrics = ProjectHealthMetrics()
        with patch.object(
            ProjectHealthMetrics,
            "project_requirements",
            new_callable=lambda: property(lambda _: mock_requirements),
        ):
            assert metrics.last_commit_days_requirement == 14

    def test_last_commit_days_requirement_without_requirements(self):
        """Test last_commit_days_requirement returns 0 when no requirements."""
        metrics = ProjectHealthMetrics()
        with patch.object(
            ProjectHealthMetrics,
            "project_requirements",
            new_callable=lambda: property(lambda _: None),
        ):
            assert metrics.last_commit_days_requirement == 0

    def test_last_pull_request_days_requirement_with_requirements(self):
        """Test last_pull_request_days_requirement returns value when requirements exist."""
        mock_requirements = MagicMock()
        mock_requirements.last_pull_request_days = 21

        metrics = ProjectHealthMetrics()
        with patch.object(
            ProjectHealthMetrics,
            "project_requirements",
            new_callable=lambda: property(lambda _: mock_requirements),
        ):
            assert metrics.last_pull_request_days_requirement == 21

    def test_last_pull_request_days_requirement_without_requirements(self):
        """Test last_pull_request_days_requirement returns 0 when no requirements."""
        metrics = ProjectHealthMetrics()
        with patch.object(
            ProjectHealthMetrics,
            "project_requirements",
            new_callable=lambda: property(lambda _: None),
        ):
            assert metrics.last_pull_request_days_requirement == 0

    def test_last_release_days_requirement_with_requirements(self):
        """Test last_release_days_requirement returns value when requirements exist."""
        mock_requirements = MagicMock()
        mock_requirements.last_release_days = 90

        metrics = ProjectHealthMetrics()
        with patch.object(
            ProjectHealthMetrics,
            "project_requirements",
            new_callable=lambda: property(lambda _: mock_requirements),
        ):
            assert metrics.last_release_days_requirement == 90

    def test_last_release_days_requirement_without_requirements(self):
        """Test last_release_days_requirement returns 0 when no requirements."""
        metrics = ProjectHealthMetrics()
        with patch.object(
            ProjectHealthMetrics,
            "project_requirements",
            new_callable=lambda: property(lambda _: None),
        ):
            assert metrics.last_release_days_requirement == 0

    def test_owasp_page_last_update_days_requirement_with_requirements(self):
        """Test owasp_page_last_update_days_requirement returns value when requirements exist."""
        mock_requirements = MagicMock()
        mock_requirements.owasp_page_last_update_days = 60

        metrics = ProjectHealthMetrics()
        with patch.object(
            ProjectHealthMetrics,
            "project_requirements",
            new_callable=lambda: property(lambda _: mock_requirements),
        ):
            assert metrics.owasp_page_last_update_days_requirement == 60

    def test_owasp_page_last_update_days_requirement_without_requirements(self):
        """Test owasp_page_last_update_days_requirement returns 0 when no requirements."""
        metrics = ProjectHealthMetrics()
        with patch.object(
            ProjectHealthMetrics,
            "project_requirements",
            new_callable=lambda: property(lambda _: None),
        ):
            assert metrics.owasp_page_last_update_days_requirement == 0


class TestProjectHealthMetricsStaticMethods:
    """Tests for static methods."""

    @patch("apps.owasp.models.project_health_metrics.BulkSaveModel")
    def test_bulk_save(self, mock_bulk_save_model):
        """Test bulk_save calls BulkSaveModel correctly."""
        mock_metrics = [MagicMock(), MagicMock()]
        mock_fields = ["score", "contributors_count"]

        ProjectHealthMetrics.bulk_save(mock_metrics, fields=mock_fields)

        mock_bulk_save_model.bulk_save.assert_called_once_with(
            ProjectHealthMetrics, mock_metrics, fields=mock_fields
        )

    @patch.object(ProjectHealthMetrics.objects, "filter")
    def test_get_latest_health_metrics(self, mock_filter):
        """Test get_latest_health_metrics returns filtered queryset."""
        mock_queryset = MagicMock()
        mock_filter.return_value = mock_queryset

        result = ProjectHealthMetrics.get_latest_health_metrics()
        assert mock_filter.call_count == 2
        assert result == mock_queryset


class TestProjectHealthMetricsProperties:
    """Tests for property methods."""

    @patch("apps.owasp.models.project_health_metrics.ProjectHealthRequirements")
    def test_project_requirements_returns_requirements(self, mock_requirements_model):
        """Test project_requirements returns requirements for project level."""
        mock_requirements = MagicMock()
        mock_requirements_model.objects.filter.return_value.first.return_value = mock_requirements

        project = Project(level="FLAGSHIP")

        metrics = ProjectHealthMetrics()
        metrics.project = project

        result = metrics.project_requirements

        mock_requirements_model.objects.filter.assert_called_once_with(level="FLAGSHIP")
        assert result == mock_requirements


class TestProjectHealthMetricsGetStats:
    """Tests for get_stats method."""

    @patch.object(ProjectHealthMetrics, "get_latest_health_metrics")
    @patch.object(ProjectHealthMetrics.objects, "annotate")
    def test_get_stats(self, mock_annotate, mock_get_latest):
        """Test get_stats returns ProjectHealthStatsNode with all data."""
        mock_queryset = MagicMock()
        mock_queryset.aggregate.return_value = {
            "projects_count_healthy": 10,
            "projects_count_need_attention": 5,
            "projects_count_unhealthy": 3,
            "projects_count_total": 18,
            "average_score": 75.5,
            "total_contributors": 100,
            "total_forks": 50,
            "total_stars": 200,
        }
        mock_get_latest.return_value = mock_queryset
        mock_monthly_queryset = MagicMock()
        mock_monthly_queryset.filter.return_value.order_by.return_value.values.return_value.distinct.return_value.annotate.return_value = [  # noqa: E501
            {"month": 1, "score": 70.0},
            {"month": 2, "score": 72.5},
            {"month": 3, "score": 75.0},
        ]
        mock_annotate.return_value = mock_monthly_queryset

        result = ProjectHealthMetrics.get_stats()
        assert math.isclose(result.average_score, 75.5)
        assert result.projects_count_healthy == 10
        assert result.projects_count_need_attention == 5
        assert result.projects_count_unhealthy == 3
        assert all(
            math.isclose(a, b)
            for a, b in zip(result.monthly_overall_scores, [70.0, 72.5, 75.0], strict=True)
        )
        assert result.monthly_overall_scores_months == [1, 2, 3]

    @patch.object(ProjectHealthMetrics, "get_latest_health_metrics")
    @patch.object(ProjectHealthMetrics.objects, "annotate")
    def test_get_stats_avoids_division_by_zero(self, mock_annotate, mock_get_latest):
        """Test get_stats handles zero projects gracefully."""
        mock_queryset = MagicMock()
        mock_queryset.aggregate.return_value = {
            "projects_count_healthy": 0,
            "projects_count_need_attention": 0,
            "projects_count_unhealthy": 0,
            "projects_count_total": 0,
            "average_score": 0.0,
            "total_contributors": 0,
            "total_forks": 0,
            "total_stars": 0,
        }
        mock_get_latest.return_value = mock_queryset
        mock_monthly_queryset = MagicMock()
        mock_monthly_queryset.filter.return_value.order_by.return_value.values.return_value.distinct.return_value.annotate.return_value = []  # noqa: E501
        mock_annotate.return_value = mock_monthly_queryset

        result = ProjectHealthMetrics.get_stats()

        assert result.projects_percentage_healthy == 0
        assert result.projects_percentage_need_attention == 0
        assert result.projects_percentage_unhealthy == 0
