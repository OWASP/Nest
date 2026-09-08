"""Test cases for SnapshotSubscriptionNode."""

from unittest.mock import MagicMock, patch

from apps.owasp.api.internal.nodes.snapshot_subscription import (
    EntitySectionNode,
    SnapshotSubscriptionNode,
    SubscribedEntityNode,
)
from apps.owasp.models.snapshot import Snapshot


class TestSubscribedEntityNode:
    """Test cases for SubscribedEntityNode."""

    def test_subscribed_entity_node_has_id_and_name(self):
        """Test SubscribedEntityNode can be instantiated with id, key, and name."""
        node = SubscribedEntityNode(id=1, key="www-project-zap", name="Test Entity")
        assert node.id == 1
        assert node.key == "www-project-zap"
        assert node.name == "Test Entity"


class TestEntitySectionNode:
    """Test cases for EntitySectionNode."""

    def test_entity_section_node_creation(self):
        """Test EntitySectionNode can be instantiated."""
        node = EntitySectionNode(
            entity_key="www-project-zap",
            entity_name="OWASP ZAP",
            entity_type="Project",
            pull_requests=[],
            issues=[],
            releases=[],
        )
        assert node.entity_key == "www-project-zap"
        assert node.entity_name == "OWASP ZAP"
        assert node.entity_type == "Project"
        assert node.pull_requests == []
        assert node.issues == []
        assert node.releases == []


class TestSnapshotSubscriptionNode:
    """Test cases for SnapshotSubscriptionNode."""

    def test_snapshot_subscription_node_has_definition(self):
        """Test SnapshotSubscriptionNode has strawberry definition."""
        assert hasattr(SnapshotSubscriptionNode, "__strawberry_definition__")

    def test_meta_configuration(self):
        """Test expected fields are present."""
        field_names = {
            field.name for field in SnapshotSubscriptionNode.__strawberry_definition__.fields
        }
        expected_field_names = {
            "created_at",
            "entity_sections",
            "frequency",
            "include_chapters",
            "include_events",
            "include_issues",
            "include_posts",
            "include_projects",
            "include_pull_requests",
            "include_releases",
            "include_users",
            "is_active",
            "name",
            "subscribed_chapters",
            "subscribed_committees",
            "subscribed_projects",
            "updated_at",
        }
        assert expected_field_names.issubset(field_names)


class TestSnapshotSubscriptionNodeResolvers:
    """Test SnapshotSubscriptionNode resolver execution."""

    def _get_resolver(self, field_name):
        """Get the resolver function for a field."""
        for field in SnapshotSubscriptionNode.__strawberry_definition__.fields:
            if field.name == field_name:
                return field.base_resolver.wrapped_func if field.base_resolver else None
        return None

    def test_subscribed_projects(self):
        """Test subscribed_projects resolver."""
        resolver = self._get_resolver("subscribed_projects")
        mock_sub = MagicMock()
        mock_p = MagicMock()
        mock_p.pk = 1
        mock_p.name = "Project 1"
        mock_sub.subscribed_projects.all.return_value = [mock_p]

        result = resolver(None, mock_sub)
        assert len(result) == 1
        assert result[0].id == 1
        assert result[0].name == "Project 1"

    def test_subscribed_chapters(self):
        """Test subscribed_chapters resolver."""
        resolver = self._get_resolver("subscribed_chapters")
        mock_sub = MagicMock()
        mock_c = MagicMock()
        mock_c.pk = 2
        mock_c.name = "Chapter 1"
        mock_sub.subscribed_chapters.all.return_value = [mock_c]

        result = resolver(None, mock_sub)
        assert len(result) == 1
        assert result[0].id == 2
        assert result[0].name == "Chapter 1"

    def test_subscribed_committees(self):
        """Test subscribed_committees resolver."""
        resolver = self._get_resolver("subscribed_committees")
        mock_sub = MagicMock()
        mock_c = MagicMock()
        mock_c.pk = 3
        mock_c.name = "Committee 1"
        mock_sub.subscribed_committees.all.return_value = [mock_c]

        result = resolver(None, mock_sub)
        assert len(result) == 1
        assert result[0].id == 3
        assert result[0].name == "Committee 1"

    @patch("apps.owasp.api.internal.nodes.snapshot_subscription.Snapshot")
    def test_entity_sections_with_valid_snapshot(self, mock_snapshot_model):
        """Test entity_sections resolver returns sections for subscribed entities."""
        resolver = self._get_resolver("entity_sections")

        mock_snapshot = MagicMock()
        mock_snapshot_model.objects.get.return_value = mock_snapshot
        mock_sub = MagicMock()
        mock_project = MagicMock()
        mock_project.key = "www-project-zap"
        mock_project.name = "OWASP ZAP"
        mock_repo = MagicMock()
        mock_repo.name = "zaproxy"
        mock_project.repositories.all.return_value = [mock_repo]
        mock_sub.subscribed_projects.all.return_value = [mock_project]
        mock_sub.subscribed_chapters.all.return_value = []
        mock_sub.subscribed_committees.all.return_value = []
        mock_pr = MagicMock()
        pr_qs = MagicMock()
        pr_prefetch = pr_qs.filter.return_value.order_by.return_value.prefetch_related
        pr_prefetch.return_value.__getitem__ = lambda _, _s: [mock_pr]
        mock_snapshot.pull_requests = pr_qs

        mock_issue = MagicMock()
        issue_qs = MagicMock()
        issue_prefetch = issue_qs.filter.return_value.order_by.return_value.prefetch_related
        issue_prefetch.return_value.__getitem__ = lambda _, _s: [mock_issue]
        mock_snapshot.issues = issue_qs

        release_qs = MagicMock()
        release_qs.filter.return_value.order_by.return_value.prefetch_related.return_value = []
        mock_snapshot.releases = release_qs

        result = resolver(None, mock_sub, snapshot_key="2025")
        assert len(result) == 1
        assert result[0].entity_key == "www-project-zap"
        assert result[0].entity_name == "OWASP ZAP"
        assert result[0].entity_type == "Project"
        assert result[0].pull_requests == [mock_pr]
        assert result[0].issues == [mock_issue]

    @patch("apps.owasp.api.internal.nodes.snapshot_subscription.Snapshot")
    def test_entity_sections_snapshot_not_found(self, mock_snapshot_model):
        """Test entity_sections returns empty list when snapshot not found."""
        resolver = self._get_resolver("entity_sections")
        mock_snapshot_model.DoesNotExist = Snapshot.DoesNotExist
        mock_snapshot_model.objects.get.side_effect = Snapshot.DoesNotExist
        mock_sub = MagicMock()

        result = resolver(None, mock_sub, snapshot_key="nonexistent")
        assert result == []

    @patch("apps.owasp.api.internal.nodes.snapshot_subscription.Snapshot")
    def test_entity_sections_no_subscribed_entities(self, mock_snapshot_model):
        """Test entity_sections returns empty list when no entities are subscribed."""
        resolver = self._get_resolver("entity_sections")
        mock_snapshot_model.objects.get.return_value = MagicMock()

        mock_sub = MagicMock()
        mock_sub.subscribed_projects.all.return_value = []
        mock_sub.subscribed_chapters.all.return_value = []
        mock_sub.subscribed_committees.all.return_value = []

        result = resolver(None, mock_sub, snapshot_key="2025")
        assert result == []

    @patch("apps.owasp.api.internal.nodes.snapshot_subscription.Snapshot")
    def test_entity_sections_skips_empty_entities(self, mock_snapshot_model):
        """Test entity_sections skips entities with no data."""
        resolver = self._get_resolver("entity_sections")
        mock_snapshot = MagicMock()
        mock_snapshot_model.objects.get.return_value = mock_snapshot

        mock_sub = MagicMock()
        mock_project = MagicMock()
        mock_project.key = "www-project-empty"
        mock_project.name = "Empty Project"
        mock_repo = MagicMock()
        mock_repo.name = "empty-repo"
        mock_project.repositories.all.return_value = [mock_repo]
        mock_sub.subscribed_projects.all.return_value = [mock_project]
        mock_sub.subscribed_chapters.all.return_value = []
        mock_sub.subscribed_committees.all.return_value = []
        for attr in ("pull_requests", "issues", "releases"):
            qs = MagicMock()
            qs_prefetch = qs.filter.return_value.order_by.return_value.prefetch_related
            qs_prefetch.return_value.__getitem__ = lambda _, _s: []
            qs_prefetch.return_value = []
            setattr(mock_snapshot, attr, qs)

        result = resolver(None, mock_sub, snapshot_key="2025")
        assert result == []
