import pytest
from django.core.exceptions import ValidationError
from django.db import models

from apps.owasp.models.project_health_metrics import ProjectHealthMetrics
from apps.owasp.models.project import Project


class TestProjectHealthMetricsModel:
    DEFAULT_SCORE = 0.0
    VALID_SCORE = 75.0
    MAX_SCORE = 100.0
    MIN_SCORE = 0.0
    
    @pytest.fixture
    def mock_project(self):
        """Mock a Project instance with simulated persistence."""
        project = Project(key="test_project", name="Test Project")
        project.pk = 1
        return project
    
    @pytest.mark.parametrize(
        "project_name, expected",
        [
            ("Secure Project", "Health Metrics for Secure Project"),
            ("", "Health Metrics for "),
            (None, "Health Metrics for None"),
        ]
    )
    def test_str_representation(self, mock_project, project_name, expected):
        """Should return correct string representation."""
        mock_project.name = project_name
        metrics = ProjectHealthMetrics(project=mock_project)
        assert str(metrics) == expected

    @pytest.mark.parametrize(
        "score, is_valid",
        [
            (VALID_SCORE, True),
            (MAX_SCORE, True),
            (MIN_SCORE, True),
            (MAX_SCORE + 0.1, False),
            (MIN_SCORE - 10.0, False),
            (None, False),
        ]
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
        "field_name, expected_default",
        [
            ("contributors_count", 0),
            ("forks_count", 0),
            ("is_funding_requirements_compliant", False),
            ("is_project_leaders_requirements_compliant", False),
            ("open_issues_count", 0),
            ("open_pull_requests_count", 0),
            ("recent_releases_count", 0),
            ("stars_count", 0),
            ("total_issues_count", 0),
            ("total_pull_request_count", 0),
            ("total_releases_count", 0),
            ("unanswered_issues_count", 0),
            ("unassigned_issues_count", 0),
        ]
    )
    def test_count_defaults(self, field_name, expected_default):
        """Should initialize count fields with proper defaults."""
        metrics = ProjectHealthMetrics()
        assert getattr(metrics, field_name) == expected_default