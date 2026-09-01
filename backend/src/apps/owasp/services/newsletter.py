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

MAX_ITEMS_PER_SECTION = 1


class SnapshotDigestService:
    """Generate personalized snapshot digest content.

    Produces both:
    1. Global sections — filtered by the 8 content toggles.
    2. Entity sections — per subscribed project/chapter/committee,
       showing issues, pull requests, and releases from the snapshot.
    """

    def generate(self, snapshot, subscription):
        """Return filtered content based on subscriber preferences.

        Args:
            snapshot: The Snapshot containing community data.
            subscription: The SnapshotSubscription with toggles and M2M entities.

        Returns:
            Dict with snapshot metadata, sections list, and entity sections.

        """
        preferences = subscription.content_preferences

        # Chapters section
        chapters_data = None
        if preferences.get("chapters"):
            items = list(snapshot.chapters.order_by("created_at")[:MAX_ITEMS_PER_SECTION])
            total = snapshot.chapters.count()
            if items:
                chapters_data = {
                    "items": items,
                    "total": total,
                    "extra": max(0, total - MAX_ITEMS_PER_SECTION),
                }

        # Users section
        users_data = None
        if preferences.get("users"):
            items = list(snapshot.users.order_by("created_at")[:MAX_ITEMS_PER_SECTION])
            total = snapshot.users.count()
            if items:
                users_data = {
                    "items": items,
                    "total": total,
                    "extra": max(0, total - MAX_ITEMS_PER_SECTION),
                }

        # Issues section
        issues_data = None
        if preferences.get("issues"):
            items = list(snapshot.issues.order_by("created_at")[:MAX_ITEMS_PER_SECTION])
            total = snapshot.issues.count()
            if items:
                issues_data = {
                    "items": items,
                    "total": total,
                    "extra": max(0, total - MAX_ITEMS_PER_SECTION),
                }

        # Pull Requests section
        prs_data = None
        if preferences.get("pull_requests"):
            items = list(snapshot.pull_requests.order_by("created_at")[:MAX_ITEMS_PER_SECTION])
            total = snapshot.pull_requests.count()
            if items:
                prs_data = {
                    "items": items,
                    "total": total,
                    "extra": max(0, total - MAX_ITEMS_PER_SECTION),
                }

        # Releases section
        releases_data = None
        if preferences.get("releases"):
            items = list(snapshot.releases.order_by("created_at")[:MAX_ITEMS_PER_SECTION])
            total = snapshot.releases.count()
            if items:
                releases_data = {
                    "items": items,
                    "total": total,
                    "extra": max(0, total - MAX_ITEMS_PER_SECTION),
                }

        # Project sections — one section per project with issues/PRs/releases
        projects_data = []
        projects_extra = 0
        if any(preferences.get(k) for k in ("projects", "issues", "pull_requests", "releases")):
            total_projects = snapshot.projects.count()
            projects_extra = max(0, total_projects - MAX_ITEMS_PER_SECTION)
            for project in snapshot.projects.all()[:MAX_ITEMS_PER_SECTION]:
                content = self._get_project_content(snapshot, project, preferences)
                if content:
                    projects_data.append(
                        {
                            "project": project,
                            "content": content,
                        }
                    )

        # Posts
        posts_data = None
        if preferences.get("posts"):
            items = list(snapshot.posts.order_by("published_at")[:MAX_ITEMS_PER_SECTION])
            total = snapshot.posts.count()
            if items:
                posts_data = {
                    "items": items,
                    "total": total,
                    "extra": max(0, total - MAX_ITEMS_PER_SECTION),
                }

        # Events
        events_data = None
        if preferences.get("events"):
            items = list(snapshot.events.order_by("start_date")[:MAX_ITEMS_PER_SECTION])
            total = snapshot.events.count()
            if items:
                events_data = {
                    "items": items,
                    "total": total,
                    "extra": max(0, total - MAX_ITEMS_PER_SECTION),
                }

        # Entity sections (subscribed projects/chapters/committees)
        entity_sections = []
        for entity_type, m2m_field in (
            ("project", "subscribed_projects"),
            ("chapter", "subscribed_chapters"),
            ("committee", "subscribed_committees"),
        ):
            for entity in getattr(subscription, m2m_field).all():
                content = self._get_entity_content(snapshot, entity)
                if content:
                    entity_sections.append(
                        {
                            "entity": entity,
                            "entity_type": entity_type,
                            "content": content,
                        }
                    )

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
            "site_url": settings.SITE_URL,
            "unsubscribe_url": unsubscribe_url,
            "snapshot_url": snapshot_url,
        }

    def _get_project_content(self, snapshot, project, preferences):
        """Get issues, PRs, releases for a project from the snapshot.

        Args:
            snapshot: The Snapshot instance.
            project: A Project instance.
            preferences: Dict of content type to boolean.

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
                        "items": list(qs[:MAX_ITEMS_PER_SECTION]),
                        "total": total,
                        "extra": max(0, total - MAX_ITEMS_PER_SECTION),
                    }
                )

        return content

    def _get_entity_content(self, snapshot, entity):
        """Fetch issues, pull requests, and releases for an entity from snapshot.

        Args:
            snapshot: The Snapshot instance.
            entity: A Project, Chapter, or Committee instance.

        Returns:
            List of content dicts. Empty list if no content found.

        """
        repositories = self._get_repositories(entity)
        if not repositories:
            return []

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
                        "items": list(qs[:MAX_ITEMS_PER_SECTION]),
                        "total": total,
                        "extra": max(0, total - MAX_ITEMS_PER_SECTION),
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

    # Double-check idempotency in case of RQ retry
    if EmailLog.is_duplicate(snapshot=snapshot, snapshot_subscription=subscription):
        logger.info("Email already sent for snapshot %s, skipping.", snapshot.key)
        return

    try:
        digest = SnapshotDigestService().generate(snapshot, subscription)

        # Skip if there's nothing to send
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
