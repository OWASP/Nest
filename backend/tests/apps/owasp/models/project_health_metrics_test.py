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
