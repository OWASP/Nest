"""Test cases for ProjectHealthMetricsNode."""

from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from apps.owasp.api.internal.nodes.project_health_metrics import ProjectHealthMetricsNode
from tests.apps.common.graphql_node_base_test import GraphQLNodeBaseTest


class TestProjectHealthMetricsNode(GraphQLNodeBaseTest):
    def test_project_health_metrics_node_inheritance(self):
        assert hasattr(ProjectHealthMetricsNode, "__strawberry_definition__")

    def test_meta_configuration(self):
        field_names = {
            field.name for field in ProjectHealthMetricsNode.__strawberry_definition__.fields
        }
        expected_field_names = {
            "age_days",
            "created_at",
            "contributors_count",
            "forks_count",
            "is_funding_requirements_compliant",
            "is_leader_requirements_compliant",
            "last_commit_days",
            "last_commit_days_requirement",
            "last_pull_request_days",
            "last_release_days",
            "last_release_days_requirement",
            "open_issues_count",
            "open_pull_requests_count",
            "owasp_page_last_update_days",
            "project_key",
            "project_name",
            "recent_releases_count",
            "score",
            "stars_count",
            "total_issues_count",
            "total_releases_count",
            "unanswered_issues_count",
            "unassigned_issues_count",
        }
        assert expected_field_names.issubset(field_names)

    @pytest.mark.parametrize(
        ("field_name", "expected_type"),
        [
            ("age_days", int),
            ("created_at", datetime),
            ("contributors_count", int),
            ("forks_count", int),
            ("is_funding_requirements_compliant", bool),
            ("is_leader_requirements_compliant", bool),
            ("last_commit_days", int),
            ("last_commit_days_requirement", int),
            ("last_pull_request_days", int),
            ("last_release_days", int),
            ("last_release_days_requirement", int),
            ("open_issues_count", int),
            ("open_pull_requests_count", int),
            ("owasp_page_last_update_days", int),
            ("project_key", str),
            ("project_name", str),
            ("recent_releases_count", int),
            ("stars_count", int),
            ("total_issues_count", int),
            ("total_releases_count", int),
            ("unanswered_issues_count", int),
            ("unassigned_issues_count", int),
        ],
    )
    def test_field_types(self, field_name, expected_type):
        field = self._get_field_by_name(field_name, ProjectHealthMetricsNode)
        assert field is not None
        assert field.type is expected_type


class TestProjectHealthMetricsNodeResolvers:
    """Test ProjectHealthMetricsNode resolver execution."""

    def _get_resolver(self, field_name):
        """Get the resolver function for a field."""
        for field in ProjectHealthMetricsNode.__strawberry_definition__.fields:
            if field.name == field_name:
                return field.base_resolver.wrapped_func if field.base_resolver else None
        return None

    def test_age_days_resolver(self):
        """Test age_days resolver returns root.age_days."""
        resolver = self._get_resolver("age_days")
        mock_metrics = MagicMock()
        mock_metrics.age_days = 365

        result = resolver(None, mock_metrics)

        assert result == 365

    def test_age_days_requirement_resolver(self):
        """Test age_days_requirement resolver."""
        resolver = self._get_resolver("age_days_requirement")
        mock_metrics = MagicMock()
        mock_metrics.age_days_requirement = 180

        result = resolver(None, mock_metrics)

        assert result == 180

    def test_created_at_resolver(self):
        """Test created_at resolver returns nest_created_at."""
        resolver = self._get_resolver("created_at")
        mock_metrics = MagicMock()
        mock_metrics.nest_created_at = datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)

        result = resolver(None, mock_metrics)

        assert result == datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)

    def test_last_commit_days_resolver(self):
        """Test last_commit_days resolver."""
        resolver = self._get_resolver("last_commit_days")
        mock_metrics = MagicMock()
        mock_metrics.last_commit_days = 30

        result = resolver(None, mock_metrics)

        assert result == 30

    def test_last_commit_days_requirement_resolver(self):
        """Test last_commit_days_requirement resolver."""
        resolver = self._get_resolver("last_commit_days_requirement")
        mock_metrics = MagicMock()
        mock_metrics.last_commit_days_requirement = 60

        result = resolver(None, mock_metrics)

        assert result == 60

    def test_last_pull_request_days_resolver(self):
        """Test last_pull_request_days resolver."""
        resolver = self._get_resolver("last_pull_request_days")
        mock_metrics = MagicMock()
        mock_metrics.last_pull_request_days = 15

        result = resolver(None, mock_metrics)

        assert result == 15

    def test_last_pull_request_days_requirement_resolver(self):
        """Test last_pull_request_days_requirement resolver."""
        resolver = self._get_resolver("last_pull_request_days_requirement")
        mock_metrics = MagicMock()
        mock_metrics.last_pull_request_days_requirement = 45

        result = resolver(None, mock_metrics)

        assert result == 45

    def test_last_release_days_resolver(self):
        """Test last_release_days resolver."""
        resolver = self._get_resolver("last_release_days")
        mock_metrics = MagicMock()
        mock_metrics.last_release_days = 90

        result = resolver(None, mock_metrics)

        assert result == 90

    def test_last_release_days_requirement_resolver(self):
        """Test last_release_days_requirement resolver."""
        resolver = self._get_resolver("last_release_days_requirement")
        mock_metrics = MagicMock()
        mock_metrics.last_release_days_requirement = 180

        result = resolver(None, mock_metrics)

        assert result == 180

    def test_project_key_resolver(self):
        """Test project_key resolver returns project.nest_key."""
        resolver = self._get_resolver("project_key")
        mock_metrics = MagicMock()
        mock_metrics.project.nest_key = "www-project-test"

        result = resolver(None, mock_metrics)

        assert result == "www-project-test"

    def test_project_name_resolver(self):
        """Test project_name resolver returns project.name."""
        resolver = self._get_resolver("project_name")
        mock_metrics = MagicMock()
        mock_metrics.project.name = "Test Project"

        result = resolver(None, mock_metrics)

        assert result == "Test Project"

    def test_owasp_page_last_update_days_resolver(self):
        """Test owasp_page_last_update_days resolver."""
        resolver = self._get_resolver("owasp_page_last_update_days")
        mock_metrics = MagicMock()
        mock_metrics.owasp_page_last_update_days = 45

        result = resolver(None, mock_metrics)

        assert result == 45

    def test_owasp_page_last_update_days_requirement_resolver(self):
        """Test owasp_page_last_update_days_requirement resolver."""
        resolver = self._get_resolver("owasp_page_last_update_days_requirement")
        mock_metrics = MagicMock()
        mock_metrics.owasp_page_last_update_days_requirement = 90

        result = resolver(None, mock_metrics)

        assert result == 90
