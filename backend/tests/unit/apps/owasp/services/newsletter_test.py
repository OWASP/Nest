"""Tests for newsletter digest generation and sending service."""

from unittest.mock import MagicMock, patch

from apps.owasp.models.snapshot import Snapshot
from apps.owasp.models.snapshot_subscription import SnapshotSubscription
from apps.owasp.services.newsletter import SnapshotDigestService, send_digest_email


def _make_subscription(preferences, *, projects=None, chapters=None, committees=None):
    """Create a mock SnapshotSubscription with the given preferences."""
    subscription = MagicMock(spec=SnapshotSubscription)
    subscription.content_preferences = preferences
    subscription.subscribed_projects.all.return_value = projects or []
    subscription.subscribed_chapters.all.return_value = chapters or []
    subscription.subscribed_committees.all.return_value = committees or []
    subscription.unsubscribe_token = "test-token"  # noqa: S105
    return subscription


def _make_orderable_qs(items, total=None):
    """Create a mock queryset that supports order_by(), slicing, and count()."""
    qs = MagicMock()
    qs.order_by.return_value = qs
    qs.__getitem__ = lambda _, s: items  # noqa: ARG005
    qs.count.return_value = total if total is not None else len(items)
    return qs


def _make_filterable_qs(items, total=None):
    """Create a mock queryset that supports filter(), order_by(), slicing, and count()."""
    inner_qs = _make_orderable_qs(items, total)
    outer_qs = MagicMock()
    outer_qs.filter.return_value = inner_qs
    inner_qs.filter.return_value = inner_qs
    inner_qs.order_by.return_value = inner_qs
    return outer_qs, inner_qs


def _all_false_preferences():
    """Return preferences dict with all toggles off."""
    return dict.fromkeys(
        (
            "chapters",
            "events",
            "issues",
            "posts",
            "projects",
            "pull_requests",
            "releases",
            "users",
        ),
        False,
    )


def _make_base_snapshot():
    """Create a snapshot with posts, events, and projects returning empty by default."""
    snapshot = MagicMock(spec=Snapshot)
    snapshot.posts = _make_orderable_qs([])
    snapshot.events = _make_orderable_qs([])
    # projects stub needed because issues/PRs/releases prefs trigger the projects block
    projects_qs = MagicMock()
    projects_qs.count.return_value = 0
    projects_qs.all.return_value = MagicMock()
    projects_qs.all.return_value.__getitem__ = lambda _, s: []  # noqa: ARG005
    snapshot.projects = projects_qs
    return snapshot


class TestSnapshotDigestService:
    """Test SnapshotDigestService."""

    def test_generate_includes_chapters_data(self):
        """Test generate includes chapters_data when enabled and items exist."""
        preferences = _all_false_preferences()
        preferences["chapters"] = True

        snapshot = _make_base_snapshot()
        snapshot.chapters = _make_orderable_qs(["ch1", "ch2"], total=2)
        subscription = _make_subscription(preferences)

        result = SnapshotDigestService().generate(snapshot, subscription)

        assert result["chapters_data"] is not None
        assert result["chapters_data"]["total"] == 2

    def test_generate_chapters_data_none_when_empty(self):
        """Test generate returns None chapters_data when no items."""
        preferences = _all_false_preferences()
        preferences["chapters"] = True

        snapshot = _make_base_snapshot()
        snapshot.chapters = _make_orderable_qs([], total=0)
        subscription = _make_subscription(preferences)

        result = SnapshotDigestService().generate(snapshot, subscription)

        assert result["chapters_data"] is None

    def test_generate_includes_users_data(self):
        """Test generate includes users_data when enabled and items exist."""
        preferences = _all_false_preferences()
        preferences["users"] = True

        snapshot = _make_base_snapshot()
        snapshot.users = _make_orderable_qs(["user1"], total=1)
        subscription = _make_subscription(preferences)

        result = SnapshotDigestService().generate(snapshot, subscription)

        assert result["users_data"] is not None
        assert result["users_data"]["total"] == 1

    def test_generate_includes_issues_data(self):
        """Test generate includes issues_data when enabled and items exist."""
        preferences = _all_false_preferences()
        preferences["issues"] = True

        snapshot = _make_base_snapshot()
        snapshot.issues = _make_orderable_qs(["issue1"], total=3)
        subscription = _make_subscription(preferences)

        result = SnapshotDigestService().generate(snapshot, subscription)

        assert result["issues_data"] is not None
        assert result["issues_data"]["total"] == 3

    def test_generate_includes_prs_data(self):
        """Test generate includes prs_data when enabled and items exist."""
        preferences = _all_false_preferences()
        preferences["pull_requests"] = True

        snapshot = _make_base_snapshot()
        snapshot.pull_requests = _make_orderable_qs(["pr1"], total=5)
        subscription = _make_subscription(preferences)

        result = SnapshotDigestService().generate(snapshot, subscription)

        assert result["prs_data"] is not None
        assert result["prs_data"]["total"] == 5

    def test_generate_includes_releases_data(self):
        """Test generate includes releases_data when enabled and items exist."""
        preferences = _all_false_preferences()
        preferences["releases"] = True

        snapshot = _make_base_snapshot()
        snapshot.releases = _make_orderable_qs(["rel1"], total=2)
        subscription = _make_subscription(preferences)

        result = SnapshotDigestService().generate(snapshot, subscription)

        assert result["releases_data"] is not None
        assert result["releases_data"]["total"] == 2

    def test_generate_includes_posts_data(self):
        """Test generate includes posts_data when enabled."""
        preferences = _all_false_preferences()
        preferences["posts"] = True

        snapshot = _make_base_snapshot()
        snapshot.posts = _make_orderable_qs(["post1"], total=1)
        subscription = _make_subscription(preferences)

        result = SnapshotDigestService().generate(snapshot, subscription)

        assert result["posts_data"]["items"] == ["post1"]
        assert result["posts_data"]["extra"] == 0

    def test_generate_includes_events_data(self):
        """Test generate includes events_data when enabled."""
        preferences = _all_false_preferences()
        preferences["events"] = True

        snapshot = _make_base_snapshot()
        snapshot.events = _make_orderable_qs(["event1"], total=1)
        subscription = _make_subscription(preferences)

        result = SnapshotDigestService().generate(snapshot, subscription)

        assert result["events_data"]["items"] == ["event1"]
        assert result["events_data"]["extra"] == 0

    def test_generate_includes_projects_data(self):
        """Test generate includes projects_data when projects toggle enabled."""
        preferences = _all_false_preferences()
        preferences["projects"] = True
        preferences["issues"] = True
        preferences["pull_requests"] = True
        preferences["releases"] = True

        snapshot = _make_base_snapshot()

        mock_project = MagicMock()
        mock_repos_qs = MagicMock()
        mock_repos_qs.exists.return_value = True
        mock_project.repositories.all.return_value = mock_repos_qs

        projects_qs = MagicMock()
        projects_qs.count.return_value = 1
        projects_qs.all.return_value = MagicMock()
        projects_qs.all.return_value.__getitem__ = lambda _, s: [mock_project]  # noqa: ARG005
        snapshot.projects = projects_qs

        # Setup snapshot querysets for global sections AND _get_project_content
        for attr in ("issues", "pull_requests", "releases"):
            qs = MagicMock()
            # Global section: order_by() -> sliceable -> count()
            qs.order_by.return_value = _make_orderable_qs(["item1"], total=1)
            # _get_project_content: filter() -> order_by() -> count()
            filter_qs = MagicMock()
            order_qs = _make_orderable_qs(["item1"], total=1)
            filter_qs.order_by.return_value = order_qs
            qs.filter.return_value = filter_qs
            qs.count.return_value = 1
            setattr(snapshot, attr, qs)

        subscription = _make_subscription(preferences)

        result = SnapshotDigestService().generate(snapshot, subscription)

        assert len(result["projects_data"]) == 1
        assert result["projects_data"][0]["project"] == mock_project

    def test_generate_skips_project_without_repos(self):
        """Test generate skips projects without repositories."""
        preferences = _all_false_preferences()
        preferences["projects"] = True

        snapshot = _make_base_snapshot()

        mock_project = MagicMock()
        mock_repos_qs = MagicMock()
        mock_repos_qs.exists.return_value = False
        mock_project.repositories.all.return_value = mock_repos_qs

        projects_qs = MagicMock()
        projects_qs.count.return_value = 1
        projects_qs.all.return_value = MagicMock()
        projects_qs.all.return_value.__getitem__ = lambda _, s: [mock_project]  # noqa: ARG005
        snapshot.projects = projects_qs

        subscription = _make_subscription(preferences)

        result = SnapshotDigestService().generate(snapshot, subscription)

        assert result["projects_data"] == []

    def test_generate_all_disabled(self):
        """Test generate returns None/empty for all sections when all toggles off."""
        preferences = _all_false_preferences()
        snapshot = _make_base_snapshot()
        subscription = _make_subscription(preferences)

        result = SnapshotDigestService().generate(snapshot, subscription)

        assert result["chapters_data"] is None
        assert result["users_data"] is None
        assert result["issues_data"] is None
        assert result["prs_data"] is None
        assert result["releases_data"] is None
        assert result["projects_data"] == []
        assert result["entity_sections"] == []

    def test_generate_includes_entity_sections_for_subscribed_projects(self):
        """Test generate includes entity sections for subscribed projects."""
        preferences = _all_false_preferences()
        snapshot = _make_base_snapshot()

        project = MagicMock()
        project.repositories.all.return_value = [MagicMock()]
        subscription = _make_subscription(preferences, projects=[project])

        # Setup snapshot querysets for entity content
        for attr in ("issues", "pull_requests", "releases"):
            outer_qs, _inner_qs = _make_filterable_qs(
                ["item1"] if attr == "issues" else [],
                total=2 if attr == "issues" else 0,
            )
            setattr(snapshot, attr, outer_qs)

        result = SnapshotDigestService().generate(snapshot, subscription)

        assert len(result["entity_sections"]) == 1
        section = result["entity_sections"][0]
        assert section["entity_type"] == "project"
        content_types = [c["type"] for c in section["content"]]
        assert "issues" in content_types

    def test_generate_skips_entities_without_updates(self):
        """Test generate skips entities that have no matching data."""
        preferences = _all_false_preferences()
        snapshot = _make_base_snapshot()

        project = MagicMock()
        project.repositories.all.return_value = [MagicMock()]
        subscription = _make_subscription(preferences, projects=[project])

        for attr in ("issues", "pull_requests", "releases"):
            outer_qs, _ = _make_filterable_qs([], total=0)
            setattr(snapshot, attr, outer_qs)

        result = SnapshotDigestService().generate(snapshot, subscription)

        assert result["entity_sections"] == []

    def test_generate_entity_sections_for_chapter(self):
        """Test generate includes entity sections for subscribed chapters."""
        preferences = _all_false_preferences()
        snapshot = _make_base_snapshot()

        chapter = MagicMock(spec=[])
        chapter.owasp_repository = MagicMock()
        subscription = _make_subscription(preferences, chapters=[chapter])

        for attr in ("issues", "pull_requests", "releases"):
            outer_qs, _ = _make_filterable_qs(
                ["item1"] if attr == "pull_requests" else [],
                total=1 if attr == "pull_requests" else 0,
            )
            setattr(snapshot, attr, outer_qs)

        result = SnapshotDigestService().generate(snapshot, subscription)

        assert len(result["entity_sections"]) == 1
        assert result["entity_sections"][0]["entity_type"] == "chapter"

    def test_generate_extra_calculation(self):
        """Test extra count is calculated correctly when total exceeds limit."""
        preferences = _all_false_preferences()
        preferences["chapters"] = True

        snapshot = _make_base_snapshot()
        snapshot.chapters = _make_orderable_qs(["ch1"], total=5)
        subscription = _make_subscription(preferences)

        result = SnapshotDigestService().generate(snapshot, subscription)

        assert result["chapters_data"]["extra"] == 4  # 5 - MAX_ITEMS_PER_SECTION(1)

    def test_get_repositories_for_project(self):
        """Test _get_repositories returns M2M repos for a project."""
        project = MagicMock()
        project.repositories.all.return_value = ["repo1", "repo2"]

        result = SnapshotDigestService._get_repositories(project)

        assert result == ["repo1", "repo2"]

    def test_get_repositories_for_chapter(self):
        """Test _get_repositories returns single repo for a chapter."""
        chapter = MagicMock(spec=[])
        chapter.owasp_repository = MagicMock()

        result = SnapshotDigestService._get_repositories(chapter)

        assert result == [chapter.owasp_repository]

    def test_get_repositories_returns_empty_when_no_repo(self):
        """Test _get_repositories returns empty list when no repo set."""
        entity = MagicMock(spec=[])
        entity.owasp_repository = None

        result = SnapshotDigestService._get_repositories(entity)

        assert result == []


class TestGetProjectContent:
    """Test _get_project_content method."""

    def test_returns_empty_when_no_repos(self):
        """Test returns empty list when project has no repositories."""
        service = SnapshotDigestService()
        snapshot = MagicMock(spec=Snapshot)
        project = MagicMock()
        repos_qs = MagicMock()
        repos_qs.exists.return_value = False
        project.repositories.all.return_value = repos_qs
        preferences = {"issues": True}

        result = service._get_project_content(snapshot, project, preferences)

        assert result == []

    def test_returns_content_when_items_found(self):
        """Test returns content dicts when snapshot has matching items."""
        service = SnapshotDigestService()
        snapshot = MagicMock(spec=Snapshot)

        project = MagicMock()
        repos_qs = MagicMock()
        repos_qs.exists.return_value = True
        project.repositories.all.return_value = repos_qs

        for attr in ("issues", "pull_requests", "releases"):
            outer_qs, _inner_qs = _make_filterable_qs(
                ["item1"] if attr == "issues" else [],
                total=3 if attr == "issues" else 0,
            )
            setattr(snapshot, attr, outer_qs)

        preferences = {"issues": True, "pull_requests": True, "releases": True}

        result = service._get_project_content(snapshot, project, preferences)

        assert len(result) == 1
        assert result[0]["type"] == "issues"
        assert result[0]["total"] == 3

    def test_skips_disabled_content_types(self):
        """Test skips content types that are disabled in preferences."""
        service = SnapshotDigestService()
        snapshot = MagicMock(spec=Snapshot)

        project = MagicMock()
        repos_qs = MagicMock()
        repos_qs.exists.return_value = True
        project.repositories.all.return_value = repos_qs

        for attr in ("issues", "pull_requests", "releases"):
            outer_qs, _ = _make_filterable_qs(["item1"], total=1)
            setattr(snapshot, attr, outer_qs)

        preferences = {"issues": False, "pull_requests": False, "releases": False}

        result = service._get_project_content(snapshot, project, preferences)

        assert result == []


class TestGetEntityContent:
    """Test _get_entity_content method."""

    def test_returns_empty_when_no_repos(self):
        """Test returns empty list when entity has no repositories."""
        service = SnapshotDigestService()
        snapshot = MagicMock(spec=Snapshot)
        entity = MagicMock(spec=[])
        entity.owasp_repository = None

        result = service._get_entity_content(snapshot, entity)

        assert result == []

    def test_returns_content_when_items_found(self):
        """Test returns content dicts for entity with matching data."""
        service = SnapshotDigestService()
        snapshot = MagicMock(spec=Snapshot)

        entity = MagicMock(spec=[])
        entity.owasp_repository = MagicMock()

        for attr in ("issues", "pull_requests", "releases"):
            outer_qs, _ = _make_filterable_qs(
                ["item1"] if attr == "releases" else [],
                total=2 if attr == "releases" else 0,
            )
            setattr(snapshot, attr, outer_qs)

        result = service._get_entity_content(snapshot, entity)

        assert len(result) == 1
        assert result[0]["type"] == "releases"
        assert result[0]["total"] == 2


class TestSendDigestEmail:
    """Test send_digest_email RQ job function."""

    @patch("apps.owasp.services.newsletter.SnapshotSubscription")
    @patch("apps.owasp.services.newsletter.Snapshot")
    def test_skips_if_snapshot_not_found(self, mock_snapshot_cls, mock_sub_cls):
        """Test job exits early when snapshot doesn't exist."""
        mock_snapshot_cls.DoesNotExist = Snapshot.DoesNotExist
        mock_sub_cls.DoesNotExist = SnapshotSubscription.DoesNotExist
        mock_snapshot_cls.objects.get.side_effect = Snapshot.DoesNotExist

        send_digest_email(snapshot_id=999, subscription_id=1)

        mock_sub_cls.objects.get.assert_not_called()

    @patch("apps.owasp.services.newsletter.EmailLog")
    @patch("apps.owasp.services.newsletter.SnapshotSubscription")
    @patch("apps.owasp.services.newsletter.Snapshot")
    def test_skips_duplicate(self, mock_snapshot_cls, mock_sub_cls, mock_email_log):
        """Test job exits early on duplicate EmailLog."""
        mock_snapshot_cls.objects.get.return_value = MagicMock()
        mock_sub_cls.objects.get.return_value = MagicMock()
        mock_email_log.is_duplicate.return_value = True

        send_digest_email(snapshot_id=1, subscription_id=1)

        mock_email_log.mark_sent.assert_not_called()

    @patch("apps.owasp.services.newsletter.get_email_service")
    @patch("apps.owasp.services.newsletter.render_to_string")
    @patch("apps.owasp.services.newsletter.SnapshotDigestService")
    @patch("apps.owasp.services.newsletter.EmailLog")
    @patch("apps.owasp.services.newsletter.SnapshotSubscription")
    @patch("apps.owasp.services.newsletter.Snapshot")
    def test_sends_and_logs_success(
        self,
        mock_snapshot_cls,
        mock_sub_cls,
        mock_email_log,
        mock_digest_cls,
        mock_render,
        mock_get_service,
    ):
        """Test job sends email and creates SENT EmailLog."""
        mock_snapshot = MagicMock()
        mock_snapshot.title = "Week 30"
        mock_snapshot_cls.objects.get.return_value = mock_snapshot
        mock_sub = MagicMock()
        mock_sub.user.email = "test@example.com"
        mock_sub_cls.objects.get.return_value = mock_sub
        mock_email_log.is_duplicate.return_value = False
        mock_digest_cls.return_value.generate.return_value = {
            "chapters_data": {"items": ["ch1"], "total": 1, "extra": 0},
            "users_data": None,
            "issues_data": None,
            "prs_data": None,
            "releases_data": None,
            "projects_data": [],
            "entity_sections": [],
            "posts_data": None,
            "events_data": None,
            "unsubscribe_url": "https://example.com/unsubscribe",
            "snapshot_url": "https://example.com/snapshot",
        }
        mock_render.return_value = "<html>body</html>"
        mock_service = MagicMock()
        mock_service.send.return_value = True
        mock_get_service.return_value = mock_service

        send_digest_email(snapshot_id=1, subscription_id=1)

        mock_service.send.assert_called_once()
        mock_email_log.mark_sent.assert_called_once_with(
            snapshot=mock_snapshot, snapshot_subscription=mock_sub
        )

    @patch("apps.owasp.services.newsletter.get_email_service")
    @patch("apps.owasp.services.newsletter.render_to_string")
    @patch("apps.owasp.services.newsletter.SnapshotDigestService")
    @patch("apps.owasp.services.newsletter.EmailLog")
    @patch("apps.owasp.services.newsletter.SnapshotSubscription")
    @patch("apps.owasp.services.newsletter.Snapshot")
    def test_skips_when_no_content(
        self,
        mock_snapshot_cls,
        mock_sub_cls,
        mock_email_log,
        mock_digest_cls,
        mock_render,
        mock_get_service,
    ):
        """Test job skips sending when all content is empty."""
        mock_snapshot_cls.objects.get.return_value = MagicMock()
        mock_sub_cls.objects.get.return_value = MagicMock()
        mock_email_log.is_duplicate.return_value = False
        mock_digest_cls.return_value.generate.return_value = {
            "chapters_data": None,
            "users_data": None,
            "issues_data": None,
            "prs_data": None,
            "releases_data": None,
            "projects_data": [],
            "entity_sections": [],
            "posts_data": None,
            "events_data": None,
            "unsubscribe_url": "https://example.com/unsubscribe",
            "snapshot_url": "https://example.com/snapshot",
        }

        send_digest_email(snapshot_id=1, subscription_id=1)

        mock_get_service.return_value.send.assert_not_called()
        mock_email_log.mark_sent.assert_not_called()

    @patch("apps.owasp.services.newsletter.get_email_service")
    @patch("apps.owasp.services.newsletter.render_to_string")
    @patch("apps.owasp.services.newsletter.SnapshotDigestService")
    @patch("apps.owasp.services.newsletter.EmailLog")
    @patch("apps.owasp.services.newsletter.SnapshotSubscription")
    @patch("apps.owasp.services.newsletter.Snapshot")
    def test_logs_failure_on_exception(
        self,
        mock_snapshot_cls,
        mock_sub_cls,
        mock_email_log,
        mock_digest_cls,
        mock_render,
        mock_get_service,
    ):
        """Test job logs failure when exception occurs during send."""
        mock_snapshot = MagicMock()
        mock_snapshot_cls.objects.get.return_value = mock_snapshot
        mock_sub = MagicMock()
        mock_sub_cls.objects.get.return_value = mock_sub
        mock_email_log.is_duplicate.return_value = False
        mock_digest_cls.return_value.generate.return_value = {
            "chapters_data": {"items": ["ch1"], "total": 1, "extra": 0},
            "users_data": None,
            "issues_data": None,
            "prs_data": None,
            "releases_data": None,
            "projects_data": [],
            "entity_sections": [],
            "posts_data": None,
            "events_data": None,
            "unsubscribe_url": "https://example.com/unsubscribe",
            "snapshot_url": "https://example.com/snapshot",
        }
        mock_render.return_value = "<html>body</html>"
        mock_get_service.return_value.send.side_effect = Exception("Send failed")

        send_digest_email(snapshot_id=1, subscription_id=1)

        mock_email_log.mark_failed.assert_called_once_with(
            snapshot=mock_snapshot,
            snapshot_subscription=mock_sub,
            error_message="Send failed",
        )

    @patch("apps.owasp.services.newsletter.get_email_service")
    @patch("apps.owasp.services.newsletter.render_to_string")
    @patch("apps.owasp.services.newsletter.SnapshotDigestService")
    @patch("apps.owasp.services.newsletter.EmailLog")
    @patch("apps.owasp.services.newsletter.SnapshotSubscription")
    @patch("apps.owasp.services.newsletter.Snapshot")
    def test_logs_failure_when_send_returns_false(
        self,
        mock_snapshot_cls,
        mock_sub_cls,
        mock_email_log,
        mock_digest_cls,
        mock_render,
        mock_get_service,
    ):
        """Test job logs failure when send returns False without exception."""
        mock_snapshot = MagicMock()
        mock_snapshot_cls.objects.get.return_value = mock_snapshot
        mock_sub = MagicMock()
        mock_sub_cls.objects.get.return_value = mock_sub
        mock_email_log.is_duplicate.return_value = False
        mock_digest_cls.return_value.generate.return_value = {
            "chapters_data": {"items": ["ch1"], "total": 1, "extra": 0},
            "users_data": None,
            "issues_data": None,
            "prs_data": None,
            "releases_data": None,
            "projects_data": [],
            "entity_sections": [],
            "posts_data": None,
            "events_data": None,
            "unsubscribe_url": "https://example.com/unsubscribe",
            "snapshot_url": "https://example.com/snapshot",
        }
        mock_render.return_value = "<html>body</html>"
        mock_get_service.return_value.send.return_value = False

        send_digest_email(snapshot_id=1, subscription_id=1)

        mock_email_log.mark_sent.assert_not_called()
        mock_email_log.mark_failed.assert_called_once_with(
            snapshot=mock_snapshot,
            snapshot_subscription=mock_sub,
            error_message="Failed to send email.",
        )

    @patch("apps.owasp.services.newsletter.SnapshotSubscription")
    @patch("apps.owasp.services.newsletter.Snapshot")
    def test_skips_if_subscription_not_found(self, mock_snapshot_cls, mock_sub_cls):
        """Test job exits early when subscription doesn't exist."""
        mock_snapshot_cls.DoesNotExist = Snapshot.DoesNotExist
        mock_sub_cls.DoesNotExist = SnapshotSubscription.DoesNotExist
        mock_snapshot_cls.objects.get.return_value = MagicMock()
        mock_sub_cls.objects.get.side_effect = SnapshotSubscription.DoesNotExist

        send_digest_email(snapshot_id=1, subscription_id=999)
