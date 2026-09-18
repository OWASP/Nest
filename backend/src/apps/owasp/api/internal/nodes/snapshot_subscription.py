"""OWASP snapshot subscription GraphQL node."""

import strawberry
import strawberry_django

from apps.github.api.internal.nodes.issue import MERGED_PULL_REQUESTS_PREFETCH, IssueNode
from apps.github.api.internal.nodes.pull_request import PullRequestNode
from apps.github.api.internal.nodes.release import ReleaseNode
from apps.owasp.models.snapshot import Snapshot
from apps.owasp.models.snapshot_subscription import SnapshotSubscription

ENTITY_ITEMS_LIMIT = 6


@strawberry.type
class SubscribedEntityNode:
    """Subscribed entity node."""

    id: int
    key: str
    name: str
    repository_names: list[str] = strawberry.field(default_factory=list)


@strawberry.type
class EntitySectionNode:
    """Entity section with grouped PRs, Issues, and Releases."""

    entity_key: str
    entity_name: str
    entity_type: str
    pull_requests: list[PullRequestNode]
    issues: list[IssueNode]
    releases: list[ReleaseNode]


@strawberry_django.type(
    SnapshotSubscription,
    fields=[
        "name",
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
        "created_at",
        "updated_at",
    ],
)
class SnapshotSubscriptionNode(strawberry.relay.Node):
    """Snapshot subscription node."""

    @strawberry_django.field(prefetch_related=["projects__repositories"])
    def projects(self, root: SnapshotSubscription) -> list[SubscribedEntityNode]:
        """Resolve subscribed projects with id, key, name, and repository names."""
        return [
            SubscribedEntityNode(
                id=p.pk,
                key=p.key,
                name=p.name,
                repository_names=[r.name for r in p.repositories.all()],
            )
            for p in root.projects.all()
        ]

    @strawberry_django.field(prefetch_related=["chapters"])
    def chapters(self, root: SnapshotSubscription) -> list[SubscribedEntityNode]:
        """Resolve subscribed chapters with id, key, and name."""
        return [SubscribedEntityNode(id=c.pk, key=c.key, name=c.name) for c in root.chapters.all()]

    @strawberry_django.field(prefetch_related=["committees"])
    def committees(self, root: SnapshotSubscription) -> list[SubscribedEntityNode]:
        """Resolve subscribed committees with id, key, and name."""
        return [
            SubscribedEntityNode(id=c.pk, key=c.key, name=c.name) for c in root.committees.all()
        ]

    @strawberry_django.field(
        prefetch_related=[
            "projects__repositories",
            "chapters__owasp_repository",
            "committees__owasp_repository",
        ]
    )
    def entity_sections(
        self, root: SnapshotSubscription, snapshot_key: str
    ) -> list[EntitySectionNode]:
        """Resolve entity-specific PRs, Issues, and Releases grouped by entity.

        Args:
            root: The SnapshotSubscription instance.
            snapshot_key: The snapshot key to fetch entity data from.

        Returns:
            List of EntitySectionNode, one per subscribed entity.

        """
        try:
            snapshot = Snapshot.objects.get(
                key=snapshot_key,
                status=Snapshot.Status.COMPLETED,
            )
        except Snapshot.DoesNotExist:
            return []

        entities = []
        for p in root.projects.all():
            repo_names = [r.name for r in p.repositories.all()]
            entities.append(("Project", p.key, p.name, repo_names))

        entities.extend(
            (
                "Chapter",
                c.key,
                c.name,
                [c.owasp_repository.name] if c.owasp_repository else [],
            )
            for c in root.chapters.all()
        )

        entities.extend(
            (
                "Committee",
                c.key,
                c.name,
                [c.owasp_repository.name] if c.owasp_repository else [],
            )
            for c in root.committees.all()
        )

        if not entities:
            return []

        sections = []
        for entity_type, key, name, repo_names in entities:
            prs = list(
                snapshot.pull_requests.filter(repository__name__in=repo_names)
                .order_by("-created_at")
                .prefetch_related("author", "repository__organization")[:ENTITY_ITEMS_LIMIT]
            )
            issues = list(
                snapshot.issues.filter(repository__name__in=repo_names)
                .order_by("-created_at")
                .prefetch_related(
                    MERGED_PULL_REQUESTS_PREFETCH, "author", "repository__organization"
                )[:ENTITY_ITEMS_LIMIT]
            )
            releases = list(
                snapshot.releases.filter(repository__name__in=repo_names)
                .order_by("-published_at")
                .prefetch_related("author", "repository__organization", "repository__project_set")
            )

            if not prs and not issues and not releases:
                continue

            sections.append(
                EntitySectionNode(
                    entity_key=key,
                    entity_name=name,
                    entity_type=entity_type,
                    pull_requests=prs,
                    issues=issues,
                    releases=releases,
                )
            )

        return sections
