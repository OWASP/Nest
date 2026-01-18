"""Test Cases for Health Stats GraphQL Node."""

from typing import get_args, get_origin

import pytest
from strawberry.types.base import StrawberryList

from apps.owasp.api.internal.nodes.project_health_stats import ProjectHealthStatsNode
from tests.apps.common.graphql_node_base_test import GraphQLNodeBaseTest


class TestHealthStatsNode(GraphQLNodeBaseTest):
    def test_project_health_stats_node_inheritance(self):
        assert hasattr(ProjectHealthStatsNode, "__strawberry_definition__")

    def test_meta_configuration(self):
        field_names = {
            field.name for field in ProjectHealthStatsNode.__strawberry_definition__.fields
        }
        expected_field_names = {
            "average_score",
            "monthly_overall_scores",
            "monthly_overall_scores_months",
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
        assert expected_field_names == field_names

    @pytest.mark.parametrize(
        ("field_name", "expected_type"),
        [
            ("monthly_overall_scores", list[float]),
            ("monthly_overall_scores_months", list[int]),
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
        field = self._get_field_by_name(field_name, ProjectHealthStatsNode)
        assert field is not None, f"Field {field_name} not found in HealthStatsNode."

        origin = get_origin(expected_type)
        if origin is list:
            # list field: ensure StrawberryList with correct inner type
            inner_type = get_args(expected_type)[0]
            assert isinstance(field.type, StrawberryList), (
                f"Field {field_name} should be a StrawberryList, got {type(field.type)}"
            )
            assert field.type.of_type is inner_type, (
                f"Field {field_name} should be a StrawberryList of {inner_type}, "
                f"got {field.type.of_type}"
            )
        else:
            # scalar field: direct comparison
            assert field.type is expected_type, (
                f"Field {field_name} has type {field.type}, expected {expected_type}"
            )
