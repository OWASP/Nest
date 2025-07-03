"""Test Cases for Health Stats GraphQL Node."""

import pytest

from apps.owasp.graphql.nodes.health_stats import HealthStatsNode


class TestHealthStatsNode:
    def test_health_stats_node_inheritance(self):
        assert hasattr(HealthStatsNode, "__strawberry_definition__")

    def test_meta_configuration(self):
        field_names = {field.name for field in HealthStatsNode.__strawberry_definition__.fields}
        expected_field_names = {
            "average_score",
            "monthly_overall_scores",
            "projects_count_healthy",
            "projects_count_need_attention",
            "projects_count_unhealthy",
            "projects_percentage_healthy",
            "projects_percentage_need_attention",
            "projects_percentage_unhealthy",
            "total_contributors",
            "total_forks",
            "total_stars",
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
            ("average_score", float),
            ("monthly_overall_scores", list[float]),
            ("projects_count_healthy", int),
            ("projects_count_need_attention", int),
            ("projects_count_unhealthy", int),
            ("projects_percentage_healthy", float),
            ("projects_percentage_need_attention", float),
            ("projects_percentage_unhealthy", float),
            ("total_contributors", int),
            ("total_forks", int),
            ("total_stars", int),
        ],
    )
    def test_field_types(self, field_name, expected_type):
        field = self._get_field_by_name(field_name)

        assert field is not None, f"Field {field_name} not found in HealthStatsNode."
        assert field.type == expected_type, (
            f"Field {field_name} has type {field.type}, expected {expected_type}."
        )
