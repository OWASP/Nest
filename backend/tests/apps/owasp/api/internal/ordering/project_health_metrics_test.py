"""Tests for OWASP Project Health Metrics Ordering."""

from apps.owasp.api.internal.ordering.project_health_metrics import ProjectHealthMetricsOrder


class TestProjectHealthMetricsOrder:
    """Test cases for ProjectHealthMetricsOrder class."""

    def test_order_has_strawberry_definition(self):
        """Check if ProjectHealthMetricsOrder has valid Strawberry definition."""
        assert hasattr(ProjectHealthMetricsOrder, "__strawberry_definition__")

    def test_order_fields(self):
        """Test if the order fields are correctly defined."""
        order_fields = {
            field.name for field in ProjectHealthMetricsOrder.__strawberry_definition__.fields
        }
        expected_fields = {"score", "project__name"}
        assert expected_fields == order_fields

    def test_order_by(self):
        """Test ordering by score."""
        order_instance = ProjectHealthMetricsOrder(score="DESC", project__name="ASC")
        assert order_instance.score == "DESC"
        assert order_instance.project__name == "ASC"
