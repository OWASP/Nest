"""Test cases for ProjectHealthMetricsNode."""

import pytest

from apps.owasp.graphql.nodes.project_health_metrics import ProjectHealthMetricsNode


class TestProjectHealthMetricsNode:
    def test_project_health_metrics_node_inheritance(self):
        assert hasattr(ProjectHealthMetricsNode, "__strawberry_definition__")

    def test_meta_configuration(self):
        field_names = {
            field.name for field in ProjectHealthMetricsNode.__strawberry_definition__.fields
        }
        expected_field_names = {
            "age_days",
            "contributors_count",
            "forks_count",
            "is_funding_requirements_compliant",
            "is_leader_requirements_compliant",
            "last_commit_days",
            "last_pull_request_days",
            "last_release_days",
            "open_issues_count",
            "owasp_page_last_update_days",
            "recent_releases_count",
            "score",
            "stars_count",
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
            ("project_name", str),
            ("age_days", int),
            ("contributors_count", int),
            ("forks_count", int),
            ("is_funding_requirements_compliant", bool),
            ("is_leader_requirements_compliant", bool),
            ("last_commit_days", int),
            ("last_pull_request_days", int),
            ("last_release_days", int),
            ("open_issues_count", int),
            ("owasp_page_last_update_days", int),
            ("recent_releases_count", int),
            ("unanswered_issues_count", int),
            ("unassigned_issues_count", int),
        ],
    )
    def test_field_types(self, field_name, expected_type):
        field = self._get_field_by_name(field_name)
        assert field is not None
        assert field.type is expected_type
