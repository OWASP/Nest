"""Newsletter digest generation and sending service."""

import logging

from django.conf import settings
from django.template.loader import render_to_string
from django_rq import job

from apps.owasp.models.email_log import EmailLog
from apps.owasp.models.snapshot import Snapshot
from apps.owasp.models.snapshot_subscription import SnapshotSubscription
from apps.owasp.services.email.factory import get_email_service

logger = logging.getLogger(__name__)

SNAPSHOT_TEMPLATE_HTML = "emails/snapshot_digest.html"
SNAPSHOT_TEMPLATE_TXT = "emails/snapshot_digest.txt"

TOTAL_ITEMS_BUDGET = 12
MIN_ITEMS_PER_SECTION = 1
MAX_ITEMS_PER_SECTION = 2
ITEMS_PER_ROW = 2
ENTITY_SUB_SECTIONS = 3
USERS_DISPLAY_COUNT = 11


class SnapshotDigestService:
    """Generate personalized snapshot digest content.

    Produces both:
    1. Global sections — filtered by the 8 content toggles.
    2. Entity sections — per subscribed project/chapter/committee,
       showing issues, pull requests, and releases from the snapshot.

    Each section displays items in side-by-side rows (2 items per row).
    The budget system counts in rows, not individual items.
    """

    def _calculate_limits(self, preferences, entity_count):
        """Calculate two-tier row limits for global sections and subscribed entities."""
        # All 8 main sections
        global_sections = [
            key
            for key in (
                "chapters",
                "users",
                "issues",
                "pull_requests",
                "releases",
                "projects",
                "posts",
                "events",
            )
            if preferences.get(key)
        ]
        card_sections = [s for s in global_sections if s != "users"]

        has_entities = entity_count > 0
        active_count = len(global_sections) + (1 if has_entities else 0)

        if active_count == 0:
            return {}
        per_section = max(
            MIN_ITEMS_PER_SECTION,
            min(MAX_ITEMS_PER_SECTION, TOTAL_ITEMS_BUDGET // active_count),
        )

        limits = dict.fromkeys(global_sections, per_section)
        if "users" in limits:
            limits["users"] = USERS_DISPLAY_COUNT
        if has_entities:
            entity_budget = TOTAL_ITEMS_BUDGET - (per_section * len(card_sections))
            entity_budget = max(entity_budget, ENTITY_SUB_SECTIONS * MIN_ITEMS_PER_SECTION)
            max_entities = max(1, entity_budget // ENTITY_SUB_SECTIONS)
            entities_shown = min(entity_count, max_entities)
            rows_per_sub = max(
                MIN_ITEMS_PER_SECTION,
                min(
                    MAX_ITEMS_PER_SECTION, entity_budget // (entities_shown * ENTITY_SUB_SECTIONS)
                ),
            )

            limits["entity_max"] = entities_shown
            limits["entity_rows"] = rows_per_sub

        return limits

    @staticmethod
    def _chunk_rows(items):
        """Split a list of items into rows of ITEMS_PER_ROW for side-by-side display.

        Args:
            items: List of items to chunk.

        Returns:
            List of lists, each containing up to ITEMS_PER_ROW items.

        """
        return [items[i : i + ITEMS_PER_ROW] for i in range(0, len(items), ITEMS_PER_ROW)]

    def generate(self, snapshot, subscription):
        """Return filtered content based on subscriber preferences.

        Args:
            snapshot: The Snapshot containing community data.
            subscription: The SnapshotSubscription with toggles and M2M entities.

        Returns:
            Dict with snapshot metadata, sections list, and entity sections.

        """
        preferences = subscription.content_preferences

        entity_count = sum(
            getattr(subscription, field).count()
            for field in ("subscribed_projects", "subscribed_chapters", "subscribed_committees")
        )
        limits = self._calculate_limits(preferences, entity_count)

        # Chapters section
        chapters_data = None
        if preferences.get("chapters"):
            rows_limit = limits.get("chapters", MIN_ITEMS_PER_SECTION)
            items_limit = rows_limit * ITEMS_PER_ROW
            items = list(snapshot.chapters.order_by("created_at")[:items_limit])
            total = snapshot.chapters.count()
            if items:
                chapters_data = {
                    "rows": self._chunk_rows(items),
                    "total": total,
                    "extra": max(0, total - items_limit),
                }

        # Users section
        users_data = None
        if preferences.get("users"):
            limit = limits.get("users", MIN_ITEMS_PER_SECTION)
            items = list(snapshot.users.order_by("created_at")[:limit])
            total = snapshot.users.count()
            if items:
                users_data = {
                    "items": items,
                    "total": total,
                    "extra": max(0, total - limit),
                }

        # Issues section
        issues_data = None
        if preferences.get("issues"):
            rows_limit = limits.get("issues", MIN_ITEMS_PER_SECTION)
            items_limit = rows_limit * ITEMS_PER_ROW
            items = list(snapshot.issues.order_by("created_at")[:items_limit])
            total = snapshot.issues.count()
            if items:
                issues_data = {
                    "rows": self._chunk_rows(items),
                    "total": total,
                    "extra": max(0, total - items_limit),
                }

        # Pull Requests section
        prs_data = None
        if preferences.get("pull_requests"):
            rows_limit = limits.get("pull_requests", MIN_ITEMS_PER_SECTION)
            items_limit = rows_limit * ITEMS_PER_ROW
            items = list(snapshot.pull_requests.order_by("created_at")[:items_limit])
            total = snapshot.pull_requests.count()
            if items:
                prs_data = {
                    "rows": self._chunk_rows(items),
                    "total": total,
                    "extra": max(0, total - items_limit),
                }

        # Releases section
        releases_data = None
        if preferences.get("releases"):
            rows_limit = limits.get("releases", MIN_ITEMS_PER_SECTION)
            items_limit = rows_limit * ITEMS_PER_ROW
            items = list(snapshot.releases.order_by("created_at")[:items_limit])
            total = snapshot.releases.count()
            if items:
                releases_data = {
                    "rows": self._chunk_rows(items),
                    "total": total,
                    "extra": max(0, total - items_limit),
                }

        # Project sections
        projects_data = None
        projects_extra = 0
        if preferences.get("projects"):
            rows_limit = limits.get("projects", MIN_ITEMS_PER_SECTION)
            items_limit = rows_limit * ITEMS_PER_ROW
            project_content_limit = limits.get("entity_rows", MIN_ITEMS_PER_SECTION)
            total_projects = snapshot.projects.count()
            projects_extra = max(0, total_projects - items_limit)
            project_list = []
            for project in snapshot.projects.all()[:items_limit]:
                content = self._get_project_content(
                    snapshot, project, preferences, limit=project_content_limit
                )
                project_list.append(
                    {
                        "project": project,
                        "content": content,
                    }
                )
            if project_list:
                projects_data = {
                    "rows": self._chunk_rows(project_list),
                    "extra": projects_extra,
                }

        # Posts
        posts_data = None
        if preferences.get("posts"):
            rows_limit = limits.get("posts", MIN_ITEMS_PER_SECTION)
            items_limit = rows_limit * ITEMS_PER_ROW
            items = list(snapshot.posts.order_by("published_at")[:items_limit])
            total = snapshot.posts.count()
            if items:
                posts_data = {
                    "rows": self._chunk_rows(items),
                    "total": total,
                    "extra": max(0, total - items_limit),
                }

        # Events
        events_data = None
        if preferences.get("events"):
            rows_limit = limits.get("events", MIN_ITEMS_PER_SECTION)
            items_limit = rows_limit * ITEMS_PER_ROW
            items = list(snapshot.events.order_by("start_date")[:items_limit])
            total = snapshot.events.count()
            if items:
                events_data = {
                    "rows": self._chunk_rows(items),
                    "total": total,
                    "extra": max(0, total - items_limit),
                }

        # Entity sections
        entity_rows_limit = limits.get("entity_rows", MIN_ITEMS_PER_SECTION)
        entity_max = limits.get("entity_max", entity_count)
        all_entity_sections = []
        for entity_type, m2m_field in (
            ("project", "subscribed_projects"),
            ("chapter", "subscribed_chapters"),
            ("committee", "subscribed_committees"),
        ):
            for entity in getattr(subscription, m2m_field).all():
                content = self._get_entity_content(snapshot, entity, rows_limit=entity_rows_limit)
                if content:
                    all_entity_sections.append(
                        {
                            "entity": entity,
                            "entity_type": entity_type,
                            "content": content,
                        }
                    )

        entity_sections = all_entity_sections[:entity_max]
        entities_extra = max(0, len(all_entity_sections) - entity_max)

        unsubscribe_url = f"{settings.SITE_URL}/unsubscribe/{subscription.unsubscribe_token}/"
        snapshot_url = (
            f"{settings.SITE_URL}/community/snapshots/{snapshot.key}"
            f"?subscription={subscription.unsubscribe_token}"
        )

        return {
            "snapshot": snapshot,
            "subscription": subscription,
            "chapters_data": chapters_data,
            "users_data": users_data,
            "issues_data": issues_data,
            "prs_data": prs_data,
            "releases_data": releases_data,
            "projects_data": projects_data,
            "projects_extra": projects_extra,
            "posts_data": posts_data,
            "events_data": events_data,
            "entity_sections": entity_sections,
            "entities_extra": entities_extra,
            "site_url": settings.SITE_URL,
            "unsubscribe_url": unsubscribe_url,
            "snapshot_url": snapshot_url,
        }

    def _get_project_content(self, snapshot, project, preferences, limit=MIN_ITEMS_PER_SECTION):
        """Get issues, PRs, releases for a project from the snapshot.

        Args:
            snapshot: The Snapshot instance.
            project: A Project instance.
            preferences: Dict of content type to boolean.
            limit: Maximum number of items per content type.

        Returns:
            List of content dicts with type, items, total.

        """
        repositories = project.repositories.all()
        if not repositories.exists():
            return []

        content = []
        for attr, content_type in (
            ("issues", "issues"),
            ("pull_requests", "pull_requests"),
            ("releases", "releases"),
        ):
            if not preferences.get(attr, True):
                continue
            qs = getattr(snapshot, attr).filter(repository__in=repositories).order_by("created_at")
            total = qs.count()
            if total > 0:
                content.append(
                    {
                        "type": content_type,
                        "items": list(qs[:limit]),
                        "rows": self._chunk_rows(list(qs[:limit])),
                        "total": total,
                        "extra": max(0, total - limit),
                    }
                )

        return content

    def _get_entity_content(self, snapshot, entity, rows_limit=MIN_ITEMS_PER_SECTION):
        """Fetch issues, pull requests, and releases for an entity from snapshot.

        Items are chunked into rows of ITEMS_PER_ROW for side-by-side display.

        Args:
            snapshot: The Snapshot instance.
            entity: A Project, Chapter, or Committee instance.
            rows_limit: Maximum number of rows per content type.

        Returns:
            List of content dicts. Empty list if no content found.

        """
        repositories = self._get_repositories(entity)
        if not repositories:
            return []

        items_limit = rows_limit * ITEMS_PER_ROW
        content = []
        for attr, content_type in (
            ("issues", "issues"),
            ("pull_requests", "pull_requests"),
            ("releases", "releases"),
        ):
            qs = getattr(snapshot, attr).filter(repository__in=repositories).order_by("created_at")
            total = qs.count()
            if total > 0:
                content.append(
                    {
                        "type": content_type,
                        "rows": self._chunk_rows(list(qs[:items_limit])),
                        "total": total,
                        "extra": max(0, total - items_limit),
                    }
                )

        return content

    @staticmethod
    def _get_repositories(entity):
        """Return repositories for a project, chapter, or committee.

        Projects use the M2M `repositories` field.
        Chapters and committees use the single `owasp_repository` FK.

        Args:
            entity: A Project, Chapter, or Committee instance.

        Returns:
            A queryset or list of Repository instances.

        """
        if hasattr(entity, "repositories"):
            return entity.repositories.all()
        repo = getattr(entity, "owasp_repository", None)
        if repo:
            return [repo]
        return []


@job("ai")
def send_digest_email(snapshot_id: int, subscription_id: int):
    """Send a single snapshot digest email. Called by the RQ worker.

    This is the RQ job function enqueued by owasp_send_snapshot_emails.
    Performs an idempotency check before sending to handle retries safely.

    Args:
        snapshot_id: The primary key of the Snapshot to send.
        subscription_id: The primary key of the SnapshotSubscription to send to.

    """
    try:
        snapshot = Snapshot.objects.get(id=snapshot_id)
        subscription = SnapshotSubscription.objects.get(id=subscription_id)
    except (Snapshot.DoesNotExist, SnapshotSubscription.DoesNotExist):
        logger.warning(
            "send_digest_email: snapshot %s or subscription %s not found.",
            snapshot_id,
            subscription_id,
        )
        return

    if not subscription.is_active:
        logger.info("Subscription %s is inactive, skipping.", subscription_id)
        return

    if EmailLog.is_duplicate(snapshot=snapshot, snapshot_subscription=subscription):
        logger.info("Email already sent for snapshot %s, skipping.", snapshot.key)
        return

    try:
        digest = SnapshotDigestService().generate(snapshot, subscription)

        has_content = (
            digest.get("chapters_data")
            or digest.get("users_data")
            or digest.get("issues_data")
            or digest.get("prs_data")
            or digest.get("releases_data")
            or digest.get("projects_data")
            or digest["entity_sections"]
            or digest.get("posts_data")
            or digest.get("events_data")
        )
        if not has_content:
            logger.info("No content for snapshot %s, skipping email.", snapshot.key)
            return

        html_body = render_to_string(SNAPSHOT_TEMPLATE_HTML, digest)
        plain_body = render_to_string(SNAPSHOT_TEMPLATE_TXT, digest)

        headers = {
            "List-Unsubscribe": f"<{digest['unsubscribe_url']}>",
            "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
        }

        email_service = get_email_service()
        is_sent = email_service.send(
            to=subscription.user.email,
            subject=f"OWASP Snapshot | {subscription.name} | {snapshot.title}",
            html_body=html_body,
            plain_body=plain_body,
            headers=headers,
        )

        if is_sent:
            EmailLog.mark_sent(snapshot=snapshot, snapshot_subscription=subscription)
            logger.info("Sent digest for snapshot %s.", snapshot.key)
        else:
            EmailLog.mark_failed(
                snapshot=snapshot,
                snapshot_subscription=subscription,
                error_message="Failed to send email.",
            )

    except Exception as exc:
        logger.exception("Failed to send digest for snapshot %s.", snapshot.key)
        EmailLog.mark_failed(
            snapshot=snapshot,
            snapshot_subscription=subscription,
            error_message=str(exc),
        )
