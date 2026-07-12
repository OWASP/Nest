"""Tests for project subscription preference model."""

from unittest.mock import MagicMock

from apps.owasp.models.project import Project
from apps.owasp.models.project_subscription_preference import ProjectSubscriptionPreference
from apps.owasp.models.snapshot_subscription import SnapshotSubscription


class TestProjectSubscriptionPreference:
    """Test ProjectSubscriptionPreference model."""

    def test_str_representation(self):
        """Test string representation."""
        pref = MagicMock(spec=ProjectSubscriptionPreference)
        pref.subscription = MagicMock(spec=SnapshotSubscription)
        pref.subscription.user = MagicMock()
        pref.subscription.user.__str__ = lambda _: "testuser"
        pref.project = MagicMock(spec=Project)
        pref.project.__str__ = lambda _: "OWASP Nest"

        result = ProjectSubscriptionPreference.__str__(pref)
        assert result == "OWASP Nest"

    def test_default_values(self):
        """Test default values for per-project toggles."""
        pref = ProjectSubscriptionPreference()
        assert pref.include_issues is True
        assert pref.include_pull_requests is True
        assert pref.include_releases is True

    def test_subscription_fk_field(self):
        """Test subscription FK field is correctly configured."""
        field = ProjectSubscriptionPreference._meta.get_field("subscription")
        assert field.many_to_one
        assert field.related_model is SnapshotSubscription

    def test_project_fk_field(self):
        """Test project FK field is correctly configured."""
        field = ProjectSubscriptionPreference._meta.get_field("project")
        assert field.many_to_one
        assert field.related_model is Project

    def test_unique_constraint(self):
        """Test unique constraint on (subscription, project)."""
        constraints = ProjectSubscriptionPreference._meta.constraints
        unique_constraints = [c for c in constraints if hasattr(c, "fields")]
        assert len(unique_constraints) == 1
        assert set(unique_constraints[0].fields) == {"subscription", "project"}
