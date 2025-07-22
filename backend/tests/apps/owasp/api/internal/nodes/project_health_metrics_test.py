"""Test cases for ProjectHealthMetricsNode."""

from datetime import datetime

import pytest

from apps.owasp.api.internal.nodes.project_health_metrics import ProjectHealthMetricsNode


class TestProjectHealthMetricsNode:
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

    def _get_field_by_name(self, name):
        return next(
            (
                f
                for f in ProjectHealthMetricsNode.__strawberry_definition__.fields
                if f.name == name
            ),
            None,
        )

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
        field = self._get_field_by_name(field_name)
        assert field is not None
        assert field.type is expected_type
