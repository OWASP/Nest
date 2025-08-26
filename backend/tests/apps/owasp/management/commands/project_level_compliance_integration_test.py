"""Integration tests for project level compliance functionality."""

from io import StringIO
from unittest.mock import MagicMock, patch
import json

import pytest
from django.core.management import call_command
from django.db.models.base import ModelState
import requests

from apps.owasp.models.project import Project
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics
from apps.owasp.models.project_health_requirements import ProjectHealthRequirements

# Test constants
PROJECT_FILTER_PATCH = "apps.owasp.models.project.Project.objects.filter"
PROJECT_BULK_SAVE_PATCH = "apps.owasp.models.project.Project.bulk_save"
METRICS_BULK_SAVE_PATCH = "apps.owasp.models.project_health_metrics.ProjectHealthMetrics.bulk_save"
METRICS_FILTER_PATCH = "apps.owasp.models.project_health_metrics.ProjectHealthMetrics.objects.filter"
REQUIREMENTS_ALL_PATCH = "apps.owasp.models.project_health_requirements.ProjectHealthRequirements.objects.all"
STDOUT_PATCH = "sys.stdout"


class TestProjectLevelComplianceIntegration:
    """Integration tests for the complete project level compliance workflow."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        """Set up test environment."""
        self.stdout = StringIO()
        yield

    def create_mock_project(self, name, local_level, official_level=None):
        """Helper to create a mock project with specified levels."""
        project = MagicMock(spec=Project)
        project._state = ModelState()
        project.name = name
        project.level = local_level
        project.project_level_official = official_level or local_level
        
        # Set default values for health metrics fields
        for field in ["contributors_count", "created_at", "forks_count", 
                     "is_funding_requirements_compliant", "is_leader_requirements_compliant",
                     "pushed_at", "released_at", "open_issues_count", "open_pull_requests_count",
                     "owasp_page_last_updated_at", "pull_request_last_created_at",
                     "recent_releases_count", "stars_count", "issues_count",
                     "pull_requests_count", "releases_count", "unanswered_issues_count",
                     "unassigned_issues_count"]:
            setattr(project, field, 5)
        
        return project

    def create_mock_metric(self, project):
        """Helper to create a mock health metric for a project."""
        metric = MagicMock(spec=ProjectHealthMetrics)
        metric.project = project
        
        # Set default values for scoring fields
        for field in ["age_days", "contributors_count", "forks_count", "last_release_days",
                     "last_commit_days", "open_issues_count", "open_pull_requests_count",
                     "owasp_page_last_update_days", "last_pull_request_days", "recent_releases_count",
                     "stars_count", "total_pull_requests_count", "total_releases_count",
                     "unanswered_issues_count", "unassigned_issues_count"]:
            setattr(metric, field, 5)
        
        metric.is_funding_requirements_compliant = True
        metric.is_leader_requirements_compliant = True
        
        return metric

    def create_mock_requirements(self, level, penalty_weight=10.0):
        """Helper to create mock health requirements."""
        requirements = MagicMock(spec=ProjectHealthRequirements)
        requirements.level = level
        requirements.compliance_penalty_weight = penalty_weight
        
        # Set default requirement values
        for field in ["age_days", "contributors_count", "forks_count", "last_release_days",
                     "last_commit_days", "open_issues_count", "open_pull_requests_count",
                     "owasp_page_last_update_days", "last_pull_request_days", "recent_releases_count",
                     "stars_count", "total_pull_requests_count", "total_releases_count",
                     "unanswered_issues_count", "unassigned_issues_count"]:
            setattr(requirements, field, 5)
        
        return requirements

    @patch('requests.get')
    def test_complete_compliance_workflow_with_penalties(self, mock_get):
        """Test the complete workflow: fetch levels -> update projects -> calculate scores with penalties."""
        # Step 1: Mock API response with official levels
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"name": "OWASP ZAP", "level": "flagship"},
            {"name": "OWASP WebGoat", "level": "production"},
            {"name": "OWASP Top 10", "level": "flagship"},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Step 2: Create mock projects with different compliance statuses
        compliant_project = self.create_mock_project("OWASP ZAP", "flagship", "lab")  # Will be updated to flagship
        non_compliant_project = self.create_mock_project("OWASP WebGoat", "lab", "other")  # Will be updated to production
        missing_project = self.create_mock_project("OWASP Missing", "lab", "lab")  # Not in official data

        projects = [compliant_project, non_compliant_project, missing_project]

        # Step 3: Create corresponding health metrics
        compliant_metric = self.create_mock_metric(compliant_project)
        non_compliant_metric = self.create_mock_metric(non_compliant_project)
        missing_metric = self.create_mock_metric(missing_project)

        metrics = [compliant_metric, non_compliant_metric, missing_metric]

        # Step 4: Create mock requirements with penalty weights
        flagship_requirements = self.create_mock_requirements("flagship", 15.0)
        lab_requirements = self.create_mock_requirements("lab", 20.0)
        production_requirements = self.create_mock_requirements("production", 25.0)

        requirements = [flagship_requirements, lab_requirements, production_requirements]

        # Step 5: Execute health metrics command (includes official level fetching)
        with patch(PROJECT_FILTER_PATCH) as mock_projects, \
             patch(PROJECT_BULK_SAVE_PATCH), \
             patch(METRICS_BULK_SAVE_PATCH), \
             patch(STDOUT_PATCH, new=self.stdout):
            
            mock_projects.return_value = projects
            
            call_command("owasp_update_project_health_metrics")
            
            # Verify official levels were updated
            assert compliant_project.project_level_official == "flagship"
            assert non_compliant_project.project_level_official == "production"
            assert missing_project.project_level_official == "lab"  # Unchanged (not in official data)
            
            output = self.stdout.getvalue()
            assert "Successfully fetched 3 official project levels" in output
            assert "Updated official levels for 2 projects" in output

        # Step 6: Set up compliance status based on updated official levels
        compliant_project.is_level_compliant = True  # flagship == flagship
        non_compliant_project.is_level_compliant = False  # lab != production
        missing_project.is_level_compliant = True  # lab == lab

        # Step 7: Execute health scores command
        self.stdout = StringIO()  # Reset stdout
        
        with patch(METRICS_FILTER_PATCH) as mock_metrics_filter, \
             patch(REQUIREMENTS_ALL_PATCH) as mock_requirements, \
             patch(METRICS_BULK_SAVE_PATCH), \
             patch(STDOUT_PATCH, new=self.stdout):
            
            mock_metrics_filter.return_value.select_related.return_value = metrics
            mock_requirements.return_value = requirements
            
            call_command("owasp_update_project_health_scores")
            
            # Verify scores were calculated correctly
            # Base score for all projects: 90.0 (all fields meet requirements)
            
            # Verify scores were calculated and penalties applied appropriately
            # Compliant project: should have higher score (no penalty)
            assert compliant_metric.score >= 90.0
            
            # Non-compliant project: should have lower score due to penalty
            assert non_compliant_metric.score < compliant_metric.score
            
            # Missing project: should be compliant (no penalty)
            assert missing_metric.score >= 90.0
            
            output = self.stdout.getvalue()
            assert "compliance penalty to OWASP WebGoat" in output
            assert "penalty:" in output and "final score:" in output
            assert "[Local: lab, Official: production]" in output

    @patch('requests.get')
    def test_compliance_detection_with_various_level_mappings(self, mock_get):
        """Test compliance detection with different level formats from API."""
        # Mock API response with various level formats
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"name": "Project A", "level": "2"},      # Numeric -> incubator
            {"name": "Project B", "level": "3.5"},    # Decimal -> production
            {"name": "Project C", "level": "flagship"}, # String -> flagship
            {"name": "Project D", "level": "unknown"}, # Unknown -> other
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Create projects with different local levels
        project_a = self.create_mock_project("Project A", "lab", "other")
        project_b = self.create_mock_project("Project B", "lab", "other")
        project_c = self.create_mock_project("Project C", "production", "other")
        project_d = self.create_mock_project("Project D", "flagship", "other")

        projects = [project_a, project_b, project_c, project_d]

        with patch(PROJECT_FILTER_PATCH) as mock_projects, \
             patch(PROJECT_BULK_SAVE_PATCH), \
             patch(METRICS_BULK_SAVE_PATCH), \
             patch(STDOUT_PATCH, new=self.stdout):
            
            mock_projects.return_value = projects
            
            call_command("owasp_update_project_health_metrics")
            
            # Verify level mappings
            assert project_a.project_level_official == "incubator"  # 2 -> incubator
            assert project_b.project_level_official == "production"  # 3.5 -> production
            assert project_c.project_level_official == "flagship"   # flagship -> flagship
            assert project_d.project_level_official == "other"      # unknown -> other
            
            # Verify compliance status
            project_a.is_level_compliant = False  # lab != incubator
            project_b.is_level_compliant = False  # lab != production
            project_c.is_level_compliant = False  # production != flagship
            project_d.is_level_compliant = False  # flagship != other

    @patch('requests.get')
    def test_api_failure_handling(self, mock_get):
        """Test handling of API failures during official level fetching."""
        # Mock API failure
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        project = self.create_mock_project("Test Project", "lab", "lab")

        with patch(PROJECT_FILTER_PATCH) as mock_projects, \
             patch(METRICS_BULK_SAVE_PATCH), \
             patch(STDOUT_PATCH, new=self.stdout):
            
            mock_projects.return_value = [project]
            
            call_command("owasp_update_project_health_metrics")
            
            # Verify graceful handling of API failure
            output = self.stdout.getvalue()
            assert "Failed to fetch official project levels, continuing without updates" in output
            assert "Evaluating metrics for project: Test Project" in output
            
            # Project level should remain unchanged
            assert project.project_level_official == "lab"

    def test_skip_official_levels_flag(self):
        """Test that --skip-official-levels flag works correctly."""
        project = self.create_mock_project("Test Project", "lab", "flagship")

        with patch(PROJECT_FILTER_PATCH) as mock_projects, \
             patch(METRICS_BULK_SAVE_PATCH), \
             patch(STDOUT_PATCH, new=self.stdout):
            
            mock_projects.return_value = [project]
            
            call_command("owasp_update_project_health_metrics", "--skip-official-levels")
            
            # Verify official levels fetching was skipped
            output = self.stdout.getvalue()
            assert "Fetching official project levels" not in output
            assert "Evaluating metrics for project: Test Project" in output
            
            # Project level should remain unchanged
            assert project.project_level_official == "flagship"

    def test_logging_and_detection_accuracy(self):
        """Test that level mismatches are properly detected and logged."""
        # Create projects with various compliance scenarios
        scenarios = [
            ("Compliant Flagship", "flagship", "flagship", True),
            ("Non-compliant Lab", "lab", "flagship", False),
            ("Non-compliant Production", "production", "incubator", False),
            ("Compliant Other", "other", "other", True),
        ]

        projects = []
        metrics = []
        
        for name, local_level, official_level, expected_compliance in scenarios:
            project = self.create_mock_project(name, local_level, official_level)
            project.is_level_compliant = expected_compliance
            metric = self.create_mock_metric(project)
            
            projects.append(project)
            metrics.append(metric)

        # Create requirements for each level
        requirements = [
            self.create_mock_requirements("flagship", 10.0),
            self.create_mock_requirements("lab", 15.0),
            self.create_mock_requirements("production", 20.0),
            self.create_mock_requirements("incubator", 25.0),
            self.create_mock_requirements("other", 5.0),
        ]

        with patch(METRICS_FILTER_PATCH) as mock_metrics_filter, \
             patch(REQUIREMENTS_ALL_PATCH) as mock_requirements, \
             patch(METRICS_BULK_SAVE_PATCH), \
             patch(STDOUT_PATCH, new=self.stdout):
            
            mock_metrics_filter.return_value.select_related.return_value = metrics
            mock_requirements.return_value = requirements
            
            call_command("owasp_update_project_health_scores")
            
            output = self.stdout.getvalue()
            
            # Verify compliant projects don't have penalties logged
            assert "compliance penalty to Compliant Flagship" not in output
            assert "compliance penalty to Compliant Other" not in output
            
            # Verify non-compliant projects have penalties logged with correct levels
            assert "Applied 15.0% compliance penalty to Non-compliant Lab" in output
            assert "[Local: lab, Official: flagship]" in output
            assert "Applied 20.0% compliance penalty to Non-compliant Production" in output
            assert "[Local: production, Official: incubator]" in output

    def test_edge_cases_and_data_validation(self):
        """Test edge cases in data validation and processing."""
        # Test with projects that have edge case data
        edge_case_project = self.create_mock_project("Edge Case", "lab", "flagship")
        edge_case_metric = self.create_mock_metric(edge_case_project)
        edge_case_project.is_level_compliant = False
        
        # Test with extreme penalty weight
        extreme_requirements = self.create_mock_requirements("lab", 999.0)  # Should be clamped to 100
        
        with patch(METRICS_FILTER_PATCH) as mock_metrics_filter, \
             patch(REQUIREMENTS_ALL_PATCH) as mock_requirements, \
             patch(METRICS_BULK_SAVE_PATCH), \
             patch(STDOUT_PATCH, new=self.stdout):
            
            mock_metrics_filter.return_value.select_related.return_value = [edge_case_metric]
            mock_requirements.return_value = [extreme_requirements]
            
            call_command("owasp_update_project_health_scores")
            
            # Verify penalty was clamped to 100% and score is 0
            assert abs(edge_case_metric.score - 0.0) < 0.01  # Use approximate comparison for float
            
            output = self.stdout.getvalue()
            assert "Applied 100.0% compliance penalty" in output