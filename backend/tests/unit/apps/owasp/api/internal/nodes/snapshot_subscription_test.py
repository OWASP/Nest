"""Test cases for SnapshotSubscriptionNode."""

from unittest.mock import MagicMock, call, patch

from apps.owasp.api.internal.nodes.snapshot_subscription import (
    ENTITY_ITEMS_LIMIT,
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
            "chapters",
            "committees",
            "projects",
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

    def _make_entity_mocks(self, *, projects=None, chapters=None, committees=None):
        """Create common mocks for entity_sections tests."""
        mock_snapshot = MagicMock()
        mock_sub = MagicMock()
        mock_sub.projects.all.return_value = projects or []
        mock_sub.chapters.all.return_value = chapters or []
        mock_sub.committees.all.return_value = committees or []
        return mock_snapshot, mock_sub

    def _make_snapshot_qs(self, mock_snapshot, items_map=None):
        """Set up PR, issue, and release querysets on mock_snapshot."""
        for attr in ("pull_requests", "issues", "releases"):
            qs = MagicMock()
            qs_prefetch = qs.filter.return_value.order_by.return_value.prefetch_related
            # A real list respects the resolver's slice, so limits are exercised.
            qs_prefetch.return_value = list((items_map or {}).get(attr, []))
            setattr(mock_snapshot, attr, qs)

    def test_projects(self):
        """Test projects resolver."""
        resolver = self._get_resolver("projects")
        mock_sub = MagicMock()
        mock_p = MagicMock()
        mock_p.pk = 1
        mock_p.key = "www-project-zap"
        mock_p.name = "Project 1"
        mock_repository = MagicMock()
        mock_repository.name = "zaproxy"
        mock_p.repositories.all.return_value = [mock_repository]
        mock_sub.projects.all.return_value = [mock_p]

        result = resolver(None, mock_sub)
        assert len(result) == 1
        assert result[0].id == 1
        assert result[0].key == "www-project-zap"
        assert result[0].name == "Project 1"
        assert result[0].repository_names == ["zaproxy"]

    def test_chapters(self):
        """Test chapters resolver."""
        resolver = self._get_resolver("chapters")
        mock_sub = MagicMock()
        mock_c = MagicMock()
        mock_c.pk = 2
        mock_c.key = "www-chapter-london"
        mock_c.name = "Chapter 1"
        mock_sub.chapters.all.return_value = [mock_c]

        result = resolver(None, mock_sub)
        assert len(result) == 1
        assert result[0].id == 2
        assert result[0].key == "www-chapter-london"
        assert result[0].name == "Chapter 1"

    def test_committees(self):
        """Test committees resolver."""
        resolver = self._get_resolver("committees")
        mock_sub = MagicMock()
        mock_c = MagicMock()
        mock_c.pk = 3
        mock_c.key = "www-committee-test"
        mock_c.name = "Committee 1"
        mock_sub.committees.all.return_value = [mock_c]

        result = resolver(None, mock_sub)
        assert len(result) == 1
        assert result[0].id == 3
        assert result[0].key == "www-committee-test"
        assert result[0].name == "Committee 1"

    @patch("apps.owasp.api.internal.nodes.snapshot_subscription.Snapshot")
    def test_entity_sections_with_valid_snapshot(self, mock_snapshot_model):
        """Test entity_sections resolver returns sections for subscribed entities."""
        resolver = self._get_resolver("entity_sections")
        mock_repository = MagicMock()
        mock_repository.pk = 101
        mock_repository.name = "zaproxy"
        mock_project = MagicMock()
        mock_project.key = "www-project-zap"
        mock_project.name = "OWASP ZAP"
        mock_project.repositories.all.return_value = [mock_repository]

        mock_pr = MagicMock()
        mock_issue = MagicMock()
        mock_snapshot, mock_sub = self._make_entity_mocks(projects=[mock_project])
        mock_snapshot_model.Status = Snapshot.Status
        mock_snapshot_model.objects.get.return_value = mock_snapshot
        self._make_snapshot_qs(
            mock_snapshot,
            items_map={"pull_requests": [mock_pr], "issues": [mock_issue]},
        )

        result = resolver(None, mock_sub, snapshot_key="2025")
        mock_snapshot_model.objects.get.assert_called_once_with(
            key="2025", status=Snapshot.Status.COMPLETED
        )
        for attr in ("pull_requests", "issues", "releases"):
            getattr(mock_snapshot, attr).filter.assert_called_once_with(repository_id__in=[101])
        assert len(result) == 1
        assert result[0].entity_key == "www-project-zap"
        assert result[0].entity_name == "OWASP ZAP"
        assert result[0].entity_type == "Project"
        assert result[0].pull_requests == [mock_pr]
        assert result[0].issues == [mock_issue]

    @patch("apps.owasp.api.internal.nodes.snapshot_subscription.Snapshot")
    def test_entity_sections_limits_pull_requests_and_issues(self, mock_snapshot_model):
        """Test entity_sections caps PRs and issues at ENTITY_ITEMS_LIMIT per entity."""
        resolver = self._get_resolver("entity_sections")
        mock_project = MagicMock()
        mock_project.repositories.all.return_value = [MagicMock(pk=101)]

        mock_prs = [MagicMock() for _ in range(ENTITY_ITEMS_LIMIT + 2)]
        mock_issues = [MagicMock() for _ in range(ENTITY_ITEMS_LIMIT + 2)]
        mock_snapshot, mock_sub = self._make_entity_mocks(projects=[mock_project])
        mock_snapshot_model.objects.get.return_value = mock_snapshot
        self._make_snapshot_qs(
            mock_snapshot,
            items_map={"pull_requests": mock_prs, "issues": mock_issues},
        )

        result = resolver(None, mock_sub, snapshot_key="2025")
        assert len(result) == 1
        assert result[0].pull_requests == mock_prs[:ENTITY_ITEMS_LIMIT]
        assert result[0].issues == mock_issues[:ENTITY_ITEMS_LIMIT]

    @patch("apps.owasp.api.internal.nodes.snapshot_subscription.Snapshot")
    def test_entity_sections_includes_prs_regardless_of_flag(self, mock_snapshot_model):
        """Test entity_sections includes PRs even if include_pull_requests is False."""
        resolver = self._get_resolver("entity_sections")
        mock_project = MagicMock()
        mock_project.repositories.all.return_value = [MagicMock()]

        mock_pr = MagicMock()
        mock_issue = MagicMock()
        mock_snapshot, mock_sub = self._make_entity_mocks(projects=[mock_project])
        mock_sub.include_pull_requests = False
        mock_snapshot_model.objects.get.return_value = mock_snapshot
        self._make_snapshot_qs(
            mock_snapshot,
            items_map={"pull_requests": [mock_pr], "issues": [mock_issue]},
        )

        result = resolver(None, mock_sub, snapshot_key="2025")
        assert len(result) == 1
        assert result[0].pull_requests == [mock_pr]
        assert result[0].issues == [mock_issue]

    @patch("apps.owasp.api.internal.nodes.snapshot_subscription.Snapshot")
    def test_entity_sections_includes_issues_regardless_of_flag(self, mock_snapshot_model):
        """Test entity_sections includes issues even if include_issues is False."""
        resolver = self._get_resolver("entity_sections")
        mock_project = MagicMock()
        mock_project.repositories.all.return_value = [MagicMock()]

        mock_pr = MagicMock()
        mock_issue = MagicMock()
        mock_snapshot, mock_sub = self._make_entity_mocks(projects=[mock_project])
        mock_sub.include_issues = False
        mock_snapshot_model.objects.get.return_value = mock_snapshot
        self._make_snapshot_qs(
            mock_snapshot,
            items_map={"pull_requests": [mock_pr], "issues": [mock_issue]},
        )

        result = resolver(None, mock_sub, snapshot_key="2025")
        assert len(result) == 1
        assert result[0].pull_requests == [mock_pr]
        assert result[0].issues == [mock_issue]

    @patch("apps.owasp.api.internal.nodes.snapshot_subscription.Snapshot")
    def test_entity_sections_includes_releases_regardless_of_flag(self, mock_snapshot_model):
        """Test entity_sections includes releases even if include_releases is False."""
        resolver = self._get_resolver("entity_sections")
        mock_project = MagicMock()
        mock_project.repositories.all.return_value = [MagicMock()]

        mock_pr = MagicMock()
        mock_release = MagicMock()
        mock_snapshot, mock_sub = self._make_entity_mocks(projects=[mock_project])
        mock_sub.include_releases = False
        mock_snapshot_model.objects.get.return_value = mock_snapshot
        self._make_snapshot_qs(
            mock_snapshot,
            items_map={"pull_requests": [mock_pr], "releases": [mock_release]},
        )

        result = resolver(None, mock_sub, snapshot_key="2025")
        assert len(result) == 1
        assert result[0].pull_requests == [mock_pr]
        assert result[0].releases == [mock_release]

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
        mock_snapshot, mock_sub = self._make_entity_mocks()
        mock_snapshot_model.objects.get.return_value = mock_snapshot

        result = resolver(None, mock_sub, snapshot_key="2025")
        assert result == []

    @patch("apps.owasp.api.internal.nodes.snapshot_subscription.Snapshot")
    def test_entity_sections_skips_empty_entities(self, mock_snapshot_model):
        """Test entity_sections skips entities with no data."""
        resolver = self._get_resolver("entity_sections")
        mock_project = MagicMock()
        mock_project.key = "www-project-empty"
        mock_project.name = "Empty Project"
        mock_project.repositories.all.return_value = [MagicMock(name="empty-repo")]

        mock_snapshot, mock_sub = self._make_entity_mocks(projects=[mock_project])
        mock_snapshot_model.objects.get.return_value = mock_snapshot
        self._make_snapshot_qs(mock_snapshot)

        result = resolver(None, mock_sub, snapshot_key="2025")
        assert result == []

    @patch("apps.owasp.api.internal.nodes.snapshot_subscription.Snapshot")
    def test_entity_sections_with_chapter_and_committee(self, mock_snapshot_model):
        """Test entity_sections resolver handles chapters and committees."""
        resolver = self._get_resolver("entity_sections")

        mock_snapshot = MagicMock()
        mock_snapshot_model.objects.get.return_value = mock_snapshot

        mock_sub = MagicMock()
        mock_sub.projects.all.return_value = []

        mock_chapter = MagicMock()
        mock_chapter.key = "www-chapter-london"
        mock_chapter.name = "OWASP London"
        mock_chapter.owasp_repository_id = 201
        mock_sub.chapters.all.return_value = [mock_chapter]

        mock_committee = MagicMock()
        mock_committee.key = "www-committee-test"
        mock_committee.name = "Women in AppSec"
        mock_committee.owasp_repository_id = 202
        mock_sub.committees.all.return_value = [mock_committee]

        mock_release = MagicMock()
        self._make_snapshot_qs(mock_snapshot, items_map={"releases": [mock_release]})

        result = resolver(None, mock_sub, snapshot_key="2025")
        for attr in ("pull_requests", "issues", "releases"):
            assert getattr(mock_snapshot, attr).filter.call_args_list == [
                call(repository_id__in=[201]),
                call(repository_id__in=[202]),
            ]
        assert len(result) == 2
        assert result[0].entity_key == "www-chapter-london"
        assert result[0].entity_type == "Chapter"
        assert result[0].releases == [mock_release]
        assert result[1].entity_key == "www-committee-test"
        assert result[1].entity_type == "Committee"
