"""Test Cases for Health Stats GraphQL Node."""

import pytest

from apps.owasp.graphql.nodes.health_stats import HealthStatsNode


class TestHealthStatsNode:
    def test_health_stats_node_inheritance(self):
        assert hasattr(HealthStatsNode, "__strawberry_definition__")

    def test_meta_configuration(self):
        field_names = {field.name for field in HealthStatsNode.__strawberry_definition__.fields}
        expected_field_names = {
            "healthy_projects_count",
            "projects_needing_attention_count",
            "unhealthy_projects_count",
            "average_score",
            "total_stars",
            "total_forks",
            "total_contributors",
            "monthly_overall_scores",
        }
        assert expected_field_names.issubset(field_names)

    def _get_field_by_name(self, name):
        return next(
            (
                field
                for field in HealthStatsNode.__strawberry_definition__.fields
                if field.name == name
            ),
            None,
        )

    @pytest.mark.parametrize(
        ("field_name", "expected_type"),
        [
            ("healthy_projects_count", int),
            ("projects_needing_attention_count", int),
            ("unhealthy_projects_count", int),
            ("average_score", float),
            ("total_stars", int),
            ("total_forks", int),
            ("total_contributors", int),
            ("monthly_overall_scores", list[float]),
        ],
    )
    def test_field_types(self, field_name, expected_type):
        field = self._get_field_by_name(field_name)
        assert field is not None, f"Field {field_name} not found in HealthStatsNode."
        assert field.type == expected_type, (
            f"Field {field_name} has type {field.type}, expected {expected_type}."
        )
