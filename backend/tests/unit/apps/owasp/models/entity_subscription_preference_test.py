"""Tests for entity subscription preference model."""

from unittest.mock import MagicMock, PropertyMock

from apps.owasp.models.chapter import Chapter
from apps.owasp.models.committee import Committee
from apps.owasp.models.entity_subscription import EntitySubscription
from apps.owasp.models.entity_subscription_preference import EntitySubscriptionPreference
from apps.owasp.models.project import Project


class TestEntitySubscriptionPreference:
    """Test EntitySubscriptionPreference model."""

    def test_str_representation_project(self):
        """Test string representation with a project."""
        pref = MagicMock(spec=EntitySubscriptionPreference)
        project_mock = MagicMock()
        project_mock.__str__ = lambda _: "OWASP Nest"
        type(pref).entity = PropertyMock(return_value=project_mock)

        result = EntitySubscriptionPreference.__str__(pref)
        assert result == "OWASP Nest"

    def test_str_representation_chapter(self):
        """Test string representation with a chapter."""
        pref = MagicMock(spec=EntitySubscriptionPreference)
        chapter_mock = MagicMock()
        chapter_mock.__str__ = lambda _: "London Chapter"
        type(pref).entity = PropertyMock(return_value=chapter_mock)

        result = EntitySubscriptionPreference.__str__(pref)
        assert result == "London Chapter"

    def test_str_representation_committee(self):
        """Test string representation with a committee."""
        pref = MagicMock(spec=EntitySubscriptionPreference)
        committee_mock = MagicMock()
        committee_mock.__str__ = lambda _: "Security Committee"
        type(pref).entity = PropertyMock(return_value=committee_mock)

        result = EntitySubscriptionPreference.__str__(pref)
        assert result == "Security Committee"

    def test_default_values(self):
        """Test default values for per-entity toggles."""
        pref = EntitySubscriptionPreference()
        assert pref.include_issues is True
        assert pref.include_pull_requests is True
        assert pref.include_releases is True

    def test_entity_property_project(self):
        """Test entity property returns project."""
        pref = MagicMock(spec=EntitySubscriptionPreference)
        pref.chapter = None
        pref.committee = None
        pref.project = MagicMock()

        result = EntitySubscriptionPreference.entity.fget(pref)
        assert result == pref.project

    def test_entity_property_chapter(self):
        """Test entity property returns chapter."""
        pref = MagicMock(spec=EntitySubscriptionPreference)
        pref.chapter = MagicMock()
        pref.committee = None
        pref.project = None

        result = EntitySubscriptionPreference.entity.fget(pref)
        assert result == pref.chapter

    def test_entity_property_committee(self):
        """Test entity property returns committee."""
        pref = MagicMock(spec=EntitySubscriptionPreference)
        pref.chapter = None
        pref.committee = MagicMock()
        pref.project = None

        result = EntitySubscriptionPreference.entity.fget(pref)
        assert result == pref.committee

    def test_subscription_fk_field(self):
        """Test subscription FK field is correctly configured."""
        field = EntitySubscriptionPreference._meta.get_field("subscription")
        assert field.many_to_one
        assert field.related_model is EntitySubscription

    def test_project_fk_field(self):
        """Test project FK field is correctly configured."""
        field = EntitySubscriptionPreference._meta.get_field("project")
        assert field.many_to_one
        assert field.related_model is Project

    def test_chapter_fk_field(self):
        """Test chapter FK field is correctly configured."""
        field = EntitySubscriptionPreference._meta.get_field("chapter")
        assert field.many_to_one
        assert field.related_model is Chapter

    def test_committee_fk_field(self):
        """Test committee FK field is correctly configured."""
        field = EntitySubscriptionPreference._meta.get_field("committee")
        assert field.many_to_one
        assert field.related_model is Committee

    def test_check_constraint_exists(self):
        """Test exactly_one_entity_set check constraint exists."""
        constraints = EntitySubscriptionPreference._meta.constraints
        check_constraints = [c for c in constraints if hasattr(c, "condition")]
        assert any(c.name == "exactly_one_entity_set" for c in check_constraints)

    def test_unique_constraints_exist(self):
        """Test unique constraints for each entity type exist."""
        constraints = EntitySubscriptionPreference._meta.constraints
        constraint_names = {c.name for c in constraints}
        assert "unique_subscription_project" in constraint_names
        assert "unique_subscription_chapter" in constraint_names
        assert "unique_subscription_committee" in constraint_names
