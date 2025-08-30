from io import StringIO
from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from django.core.management import call_command

from apps.owasp.management.commands.owasp_update_project_health_scores import Command
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics
from apps.owasp.models.project_health_requirements import ProjectHealthRequirements

# Test constants
TEST_PROJECT_NAME = "Test Project"
NON_COMPLIANT_PROJECT_NAME = "Non-Compliant Project"
COMPLIANT_PROJECT_NAME = "Compliant Project"
STDOUT_PATCH = "sys.stdout"
# Long constants broken down for line length
METRICS_FILTER_PATCH = (
    "apps.owasp.models.project_health_metrics.ProjectHealthMetrics.objects.filter"
)
REQUIREMENTS_ALL_PATCH = (
    "apps.owasp.models.project_health_requirements.ProjectHealthRequirements.objects.all"
)
METRICS_BULK_SAVE_PATCH = "apps.owasp.models.project_health_metrics.ProjectHealthMetrics.bulk_save"
EXPECTED_SCORE = 34.0
LAB_LEVEL = "lab"
FLAGSHIP_LEVEL = "flagship"
PRODUCTION_LEVEL = "production"
PENALTY_TWENTY_PERCENT = 20.0
PENALTY_ZERO_PERCENT = 0.0
PENALTY_HUNDRED_PERCENT = 100.0
FULL_SCORE_THRESHOLD = 90.0
FLOAT_PRECISION = 0.01


class TestUpdateProjectHealthMetricsScoreCommand:
    @pytest.fixture(autouse=True)
    def _setup(self):
        """Set up test environment."""
        self.stdout = StringIO()
        self.command = Command()
        with (
            patch(METRICS_FILTER_PATCH) as metrics_patch,
            patch(REQUIREMENTS_ALL_PATCH) as requirements_patch,
            patch(METRICS_BULK_SAVE_PATCH) as bulk_save_patch,
        ):
            self.mock_metrics = metrics_patch
            self.mock_requirements = requirements_patch
            self.mock_bulk_save = bulk_save_patch
            yield

    def test_handle_successful_update(self):
        """Test successful metrics score update."""
        fields_weights = {
            "age_days": (5, 6),
            "contributors_count": (5, 6),
            "forks_count": (5, 6),
            "last_release_days": (5, 6),
            "last_commit_days": (5, 6),
            "open_issues_count": (7, 6),
            "open_pull_requests_count": (5, 6),
            "owasp_page_last_update_days": (5, 6),
            "last_pull_request_days": (5, 6),
            "recent_releases_count": (5, 6),
            "stars_count": (5, 6),
            "total_pull_requests_count": (5, 6),
            "total_releases_count": (5, 6),
            "unanswered_issues_count": (7, 6),
            "unassigned_issues_count": (7, 6),
        }

        # Create mock metrics with test data
        mock_metric = MagicMock(spec=ProjectHealthMetrics)
        mock_requirements = MagicMock(spec=ProjectHealthRequirements)
        for field, (metric_weight, requirement_weight) in fields_weights.items():
            setattr(mock_metric, field, metric_weight)
            setattr(mock_requirements, field, requirement_weight)
        mock_metric.project.level = "test_level"
        mock_metric.project.name = TEST_PROJECT_NAME
        type(mock_metric.project).is_level_compliant = PropertyMock(return_value=True)
        mock_metric.is_funding_requirements_compliant = True
        mock_metric.is_leader_requirements_compliant = True
        self.mock_metrics.return_value.select_related.return_value = [mock_metric]
        self.mock_requirements.return_value = [mock_requirements]
        mock_requirements.level = "test_level"
        # Execute command
        with patch(STDOUT_PATCH, new=self.stdout):
            call_command("owasp_update_project_health_scores")

        self.mock_requirements.assert_called_once()

        # Check if score was calculated correctly
        self.mock_bulk_save.assert_called_once_with(
            [mock_metric],
            fields=[
                "score",
            ],
        )
        assert (
            abs(mock_metric.score - EXPECTED_SCORE) < FLOAT_PRECISION
        )  # Use approximate comparison for float
        assert "Updated project health scores successfully." in self.stdout.getvalue()
        assert f"Updating score for project: {TEST_PROJECT_NAME}" in self.stdout.getvalue()

    def test_handle_with_compliance_penalty(self):
        """Test score calculation with compliance penalty applied."""
        # Create mock metrics with test data that matches actual scoring fields
        mock_metric = MagicMock(spec=ProjectHealthMetrics)
        mock_requirements = MagicMock(spec=ProjectHealthRequirements)

        # Set up forward fields (higher is better) - all should meet requirements
        mock_metric.age_days = 10
        mock_requirements.age_days = 5
        mock_metric.contributors_count = 10
        mock_requirements.contributors_count = 5
        mock_metric.forks_count = 10
        mock_requirements.forks_count = 5
        mock_metric.is_funding_requirements_compliant = True
        mock_requirements.is_funding_requirements_compliant = True
        mock_metric.is_leader_requirements_compliant = True
        mock_requirements.is_leader_requirements_compliant = True
        mock_metric.open_pull_requests_count = 10
        mock_requirements.open_pull_requests_count = 5
        mock_metric.recent_releases_count = 10
        mock_requirements.recent_releases_count = 5
        mock_metric.stars_count = 10
        mock_requirements.stars_count = 5
        mock_metric.total_pull_requests_count = 10
        mock_requirements.total_pull_requests_count = 5
        mock_metric.total_releases_count = 10
        mock_requirements.total_releases_count = 5

        # Set up backward fields (lower is better) - all should meet requirements
        mock_metric.last_commit_days = 1
        mock_requirements.last_commit_days = 5
        mock_metric.last_pull_request_days = 1
        mock_requirements.last_pull_request_days = 5
        mock_metric.last_release_days = 1
        mock_requirements.last_release_days = 5
        mock_metric.open_issues_count = 1
        mock_requirements.open_issues_count = 5
        mock_metric.owasp_page_last_update_days = 1
        mock_requirements.owasp_page_last_update_days = 5
        mock_metric.unanswered_issues_count = 1
        mock_requirements.unanswered_issues_count = 5
        mock_metric.unassigned_issues_count = 1
        mock_requirements.unassigned_issues_count = 5

        # Set up project with non-compliant level
        mock_metric.project.level = LAB_LEVEL
        mock_metric.project.project_level_official = FLAGSHIP_LEVEL
        mock_metric.project.name = NON_COMPLIANT_PROJECT_NAME
        type(mock_metric.project).is_level_compliant = PropertyMock(return_value=False)

        # Set compliance requirements
        mock_metric.is_funding_requirements_compliant = True
        mock_metric.is_leader_requirements_compliant = True

        # Set penalty weight
        mock_requirements.compliance_penalty_weight = PENALTY_TWENTY_PERCENT  # 20% penalty

        self.mock_metrics.return_value.select_related.return_value = [mock_metric]
        self.mock_requirements.return_value = [mock_requirements]
        mock_requirements.level = LAB_LEVEL

        # Execute command
        with patch(STDOUT_PATCH, new=self.stdout):
            call_command("owasp_update_project_health_scores")

        # Calculate expected score
        # 8 forward fields * 6.0 + 2 compliance fields * 5.0 + 7 backward fields * 6.0 = 100
        # Final score: 100.0 - 20.0 = 80.0

        # Verify that penalty was applied
        assert abs(mock_metric.score - 80.0) < FLOAT_PRECISION  # Should be 80 after 20% penalty

        # Verify penalty was logged
        output = self.stdout.getvalue()
        assert (
            f"Applied {PENALTY_TWENTY_PERCENT}% compliance penalty to {NON_COMPLIANT_PROJECT_NAME}"
            in output
        )
        assert "penalty:" in output
        assert "final score:" in output
        assert f"[Local: {LAB_LEVEL}, Official: {FLAGSHIP_LEVEL}]" in output

    def test_handle_without_compliance_penalty(self):
        """Test score calculation without compliance penalty for compliant project."""
        # Create mock metrics with test data that matches actual scoring fields
        mock_metric = MagicMock(spec=ProjectHealthMetrics)
        mock_requirements = MagicMock(spec=ProjectHealthRequirements)

        # Set up forward fields (higher is better) - all should meet requirements
        mock_metric.age_days = 10
        mock_requirements.age_days = 5
        mock_metric.contributors_count = 10
        mock_requirements.contributors_count = 5
        mock_metric.forks_count = 10
        mock_requirements.forks_count = 5
        mock_metric.is_funding_requirements_compliant = True
        mock_requirements.is_funding_requirements_compliant = True
        mock_metric.is_leader_requirements_compliant = True
        mock_requirements.is_leader_requirements_compliant = True
        mock_metric.open_pull_requests_count = 10
        mock_requirements.open_pull_requests_count = 5
        mock_metric.recent_releases_count = 10
        mock_requirements.recent_releases_count = 5
        mock_metric.stars_count = 10
        mock_requirements.stars_count = 5
        mock_metric.total_pull_requests_count = 10
        mock_requirements.total_pull_requests_count = 5
        mock_metric.total_releases_count = 10
        mock_requirements.total_releases_count = 5

        # Set up backward fields (lower is better) - all should meet requirements
        mock_metric.last_commit_days = 1
        mock_requirements.last_commit_days = 5
        mock_metric.last_pull_request_days = 1
        mock_requirements.last_pull_request_days = 5
        mock_metric.last_release_days = 1
        mock_requirements.last_release_days = 5
        mock_metric.open_issues_count = 1
        mock_requirements.open_issues_count = 5
        mock_metric.owasp_page_last_update_days = 1
        mock_requirements.owasp_page_last_update_days = 5
        mock_metric.unanswered_issues_count = 1
        mock_requirements.unanswered_issues_count = 5
        mock_metric.unassigned_issues_count = 1
        mock_requirements.unassigned_issues_count = 5

        # Set up project with compliant level
        mock_metric.project.level = FLAGSHIP_LEVEL
        mock_metric.project.project_level_official = FLAGSHIP_LEVEL
        mock_metric.project.name = COMPLIANT_PROJECT_NAME
        type(mock_metric.project).is_level_compliant = PropertyMock(return_value=True)

        mock_metric.is_funding_requirements_compliant = True
        mock_metric.is_leader_requirements_compliant = True

        # Set penalty weight (should not be applied)
        mock_requirements.compliance_penalty_weight = PENALTY_TWENTY_PERCENT

        self.mock_metrics.return_value.select_related.return_value = [mock_metric]
        self.mock_requirements.return_value = [mock_requirements]
        mock_requirements.level = FLAGSHIP_LEVEL

        # Execute command
        with patch(STDOUT_PATCH, new=self.stdout):
            call_command("owasp_update_project_health_scores")

        # Verify no penalty was applied for compliant project
        # Expected: total possible 100 points without penalty
        # (48 + 10 + 42 = 100 points total)
        assert abs(mock_metric.score - 100.0) < FLOAT_PRECISION  # Should be maximum score

        # Verify no penalty was logged
        output = self.stdout.getvalue()
        assert "compliance penalty" not in output

    def test_handle_zero_penalty_weight(self):
        """Test score calculation with zero penalty weight."""
        mock_metric = MagicMock(spec=ProjectHealthMetrics)
        mock_requirements = MagicMock(spec=ProjectHealthRequirements)

        # Set up basic scoring fields using explicit values (all meet requirements)
        mock_metric.age_days = 5
        mock_requirements.age_days = 5
        mock_metric.contributors_count = 5
        mock_requirements.contributors_count = 5
        mock_metric.forks_count = 5
        mock_requirements.forks_count = 5
        mock_metric.is_funding_requirements_compliant = True
        mock_requirements.is_funding_requirements_compliant = True
        mock_metric.is_leader_requirements_compliant = True
        mock_requirements.is_leader_requirements_compliant = True
        mock_metric.open_pull_requests_count = 5
        mock_requirements.open_pull_requests_count = 5
        mock_metric.recent_releases_count = 5
        mock_requirements.recent_releases_count = 5
        mock_metric.stars_count = 5
        mock_requirements.stars_count = 5
        mock_metric.total_pull_requests_count = 5
        mock_requirements.total_pull_requests_count = 5
        mock_metric.total_releases_count = 5
        mock_requirements.total_releases_count = 5
        mock_metric.last_commit_days = 5
        mock_requirements.last_commit_days = 5
        mock_metric.last_pull_request_days = 5
        mock_requirements.last_pull_request_days = 5
        mock_metric.last_release_days = 5
        mock_requirements.last_release_days = 5
        mock_metric.open_issues_count = 5
        mock_requirements.open_issues_count = 5
        mock_metric.owasp_page_last_update_days = 5
        mock_requirements.owasp_page_last_update_days = 5
        mock_metric.unanswered_issues_count = 5
        mock_requirements.unanswered_issues_count = 5
        mock_metric.unassigned_issues_count = 5
        mock_requirements.unassigned_issues_count = 5

        # Set up non-compliant project
        mock_metric.project.level = LAB_LEVEL
        mock_metric.project.project_level_official = FLAGSHIP_LEVEL
        mock_metric.project.name = TEST_PROJECT_NAME
        type(mock_metric.project).is_level_compliant = PropertyMock(return_value=False)

        mock_metric.is_funding_requirements_compliant = True
        mock_metric.is_leader_requirements_compliant = True

        # Set zero penalty weight
        mock_requirements.compliance_penalty_weight = PENALTY_ZERO_PERCENT

        self.mock_metrics.return_value.select_related.return_value = [mock_metric]
        self.mock_requirements.return_value = [mock_requirements]
        mock_requirements.level = LAB_LEVEL

        # Execute command
        with patch(STDOUT_PATCH, new=self.stdout):
            call_command("owasp_update_project_health_scores")

        # Score should be unchanged (no penalty applied)
        # Expected: total possible 100 points without penalty
        assert abs(mock_metric.score - 100.0) < FLOAT_PRECISION  # Should be maximum score

        # Verify penalty was applied but with 0% (should be logged)
        output = self.stdout.getvalue()
        assert f"Applied {PENALTY_ZERO_PERCENT}% compliance penalty" in output

    def test_handle_maximum_penalty_weight(self):
        """Test score calculation with maximum penalty weight (100%)."""
        mock_metric = MagicMock(spec=ProjectHealthMetrics)
        mock_requirements = MagicMock(spec=ProjectHealthRequirements)

        # Set up basic scoring fields using explicit values (all meet requirements)
        mock_metric.age_days = 10
        mock_requirements.age_days = 5
        mock_metric.contributors_count = 10
        mock_requirements.contributors_count = 5
        mock_metric.forks_count = 10
        mock_requirements.forks_count = 5
        mock_metric.is_funding_requirements_compliant = True
        mock_requirements.is_funding_requirements_compliant = True
        mock_metric.is_leader_requirements_compliant = True
        mock_requirements.is_leader_requirements_compliant = True
        mock_metric.open_pull_requests_count = 10
        mock_requirements.open_pull_requests_count = 5
        mock_metric.recent_releases_count = 10
        mock_requirements.recent_releases_count = 5
        mock_metric.stars_count = 10
        mock_requirements.stars_count = 5
        mock_metric.total_pull_requests_count = 10
        mock_requirements.total_pull_requests_count = 5
        mock_metric.total_releases_count = 10
        mock_requirements.total_releases_count = 5
        mock_metric.last_commit_days = 1
        mock_requirements.last_commit_days = 5
        mock_metric.last_pull_request_days = 1
        mock_requirements.last_pull_request_days = 5
        mock_metric.last_release_days = 1
        mock_requirements.last_release_days = 5
        mock_metric.open_issues_count = 1
        mock_requirements.open_issues_count = 5
        mock_metric.owasp_page_last_update_days = 1
        mock_requirements.owasp_page_last_update_days = 5
        mock_metric.unanswered_issues_count = 1
        mock_requirements.unanswered_issues_count = 5
        mock_metric.unassigned_issues_count = 1
        mock_requirements.unassigned_issues_count = 5

        # Set up non-compliant project
        mock_metric.project.level = LAB_LEVEL
        mock_metric.project.project_level_official = FLAGSHIP_LEVEL
        mock_metric.project.name = TEST_PROJECT_NAME
        type(mock_metric.project).is_level_compliant = PropertyMock(return_value=False)

        mock_metric.is_funding_requirements_compliant = True
        mock_metric.is_leader_requirements_compliant = True

        # Set maximum penalty weight
        mock_requirements.compliance_penalty_weight = PENALTY_HUNDRED_PERCENT

        self.mock_metrics.return_value.select_related.return_value = [mock_metric]
        self.mock_requirements.return_value = [mock_requirements]
        mock_requirements.level = LAB_LEVEL

        # Execute command
        with patch(STDOUT_PATCH, new=self.stdout):
            call_command("owasp_update_project_health_scores")

        # Score should be 0 (100% penalty)
        assert (
            abs(mock_metric.score - PENALTY_ZERO_PERCENT) < FLOAT_PRECISION
        )  # Use approximate comparison for float

    def test_handle_penalty_weight_clamping(self):
        """Test that penalty weight is properly clamped to [0, 100] range."""
        mock_metric = MagicMock(spec=ProjectHealthMetrics)
        mock_requirements = MagicMock(spec=ProjectHealthRequirements)

        # Set up basic scoring fields for partial score (some fields meet requirements)
        mock_metric.age_days = 5
        mock_requirements.age_days = 10  # Does not meet requirement
        mock_metric.contributors_count = 10
        mock_requirements.contributors_count = 5  # Meets requirement
        mock_metric.forks_count = 5
        mock_requirements.forks_count = 10  # Does not meet requirement
        mock_metric.is_funding_requirements_compliant = True
        mock_requirements.is_funding_requirements_compliant = True  # Meets requirement
        mock_metric.is_leader_requirements_compliant = True
        mock_requirements.is_leader_requirements_compliant = True  # Meets requirement
        mock_metric.open_pull_requests_count = 10
        mock_requirements.open_pull_requests_count = 5  # Meets requirement
        mock_metric.recent_releases_count = 5
        mock_requirements.recent_releases_count = 10  # Does not meet requirement
        mock_metric.stars_count = 10
        mock_requirements.stars_count = 5  # Meets requirement
        mock_metric.total_pull_requests_count = 10
        mock_requirements.total_pull_requests_count = 5  # Meets requirement
        mock_metric.total_releases_count = 5
        mock_requirements.total_releases_count = 10  # Does not meet requirement
        mock_metric.last_commit_days = 10
        mock_requirements.last_commit_days = 5  # Does not meet requirement
        mock_metric.last_pull_request_days = 3
        mock_requirements.last_pull_request_days = 5  # Meets requirement
        mock_metric.last_release_days = 10
        mock_requirements.last_release_days = 5  # Does not meet requirement
        mock_metric.open_issues_count = 3
        mock_requirements.open_issues_count = 5  # Meets requirement
        mock_metric.owasp_page_last_update_days = 3
        mock_requirements.owasp_page_last_update_days = 5  # Meets requirement
        mock_metric.unanswered_issues_count = 3
        mock_requirements.unanswered_issues_count = 5  # Meets requirement
        mock_metric.unassigned_issues_count = 10
        mock_requirements.unassigned_issues_count = 5  # Does not meet requirement

        # Expected base score calculation:
        # Total base score: 58.0
        base_score = 58.0

        # Set up non-compliant project
        mock_metric.project.level = LAB_LEVEL
        mock_metric.project.project_level_official = FLAGSHIP_LEVEL
        mock_metric.project.name = TEST_PROJECT_NAME
        type(mock_metric.project).is_level_compliant = PropertyMock(return_value=False)
        mock_metric.is_funding_requirements_compliant = True
        mock_metric.is_leader_requirements_compliant = True

        # Test cases for penalty weight clamping
        test_cases = [
            (-10.0, PENALTY_ZERO_PERCENT, base_score),  # Negative should be clamped to 0
            (150.0, PENALTY_HUNDRED_PERCENT, 0.0),  # Over 100 should be clamped to 100
            (50.0, 50.0, base_score * 0.5),  # Valid value should remain unchanged
        ]

        for input_penalty, expected_penalty, expected_score in test_cases:
            mock_requirements.compliance_penalty_weight = input_penalty

            self.mock_metrics.return_value.select_related.return_value = [mock_metric]
            self.mock_requirements.return_value = [mock_requirements]
            mock_requirements.level = LAB_LEVEL

            # Reset stdout for each test
            self.stdout = StringIO()

            # Execute command
            with patch(STDOUT_PATCH, new=self.stdout):
                call_command("owasp_update_project_health_scores")

            # Verify penalty was clamped correctly
            output = self.stdout.getvalue()
            assert f"Applied {expected_penalty}% compliance penalty" in output

            # Verify final score is correct
            assert abs(mock_metric.score - expected_score) < FLOAT_PRECISION

    def test_handle_no_projects_to_update(self):
        """Test command when no projects need score updates."""
        # Mock empty queryset (no projects with null scores)
        self.mock_metrics.return_value.select_related.return_value = []
        self.mock_requirements.return_value = []

        # Execute command
        with patch(STDOUT_PATCH, new=self.stdout):
            call_command("owasp_update_project_health_scores")

        # Verify no bulk save was called and success message shown
        self.mock_bulk_save.assert_called_once_with([], fields=["score"])
        assert "Updated project health scores successfully." in self.stdout.getvalue()
