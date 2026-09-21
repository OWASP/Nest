"""OWASP snapshot GraphQL node."""

import strawberry
import strawberry_django
from django.db.models import Avg
from strawberry.types import Info

from apps.common.utils import normalize_limit
from apps.github.api.internal.nodes.issue import MERGED_PULL_REQUESTS_PREFETCH, IssueNode
from apps.github.api.internal.nodes.pull_request import PullRequestNode
from apps.github.api.internal.nodes.release import ReleaseNode
from apps.github.api.internal.nodes.user import UserNode
from apps.owasp.api.internal.nodes.chapter import ChapterNode
from apps.owasp.api.internal.nodes.event import EventNode
from apps.owasp.api.internal.nodes.post import PostNode
from apps.owasp.api.internal.nodes.project import ProjectNode
from apps.owasp.api.internal.nodes.snapshot_feedback import SnapshotFeedbackNode
from apps.owasp.models.snapshot import Snapshot

MAX_LIMIT = 1000
RATING_PRECISION = 2


@strawberry_django.type(
    Snapshot,
    fields=[
        "created_at",
        "end_at",
        "start_at",
        "title",
    ],
)
class SnapshotNode(strawberry.relay.Node):
    """Snapshot node."""

    @staticmethod
    def _slice_related(queryset, limit: int, offset: int):
        """Paginate related items."""
        if (normalized_limit := normalize_limit(limit, MAX_LIMIT)) is None:
            return []
        normalized_offset = max(0, offset)
        return list(queryset[normalized_offset : normalized_offset + normalized_limit])

    chapters: list[ChapterNode] = strawberry_django.field(prefetch_related=["chapters"])

    @strawberry_django.field
    def key(self, root: Snapshot) -> str:
        """Resolve key."""
        return root.key

    @strawberry_django.field
    def average_rating(self, root: Snapshot) -> float:
        """Resolve the average community rating, or 0 when there is no feedback yet."""
        average = getattr(root, "_average_rating", None)
        if average is None:
            average = root.feedback.aggregate(average=Avg("rating"))["average"]
        return round(average, RATING_PRECISION) if average is not None else 0.0

    @strawberry_django.field
    def feedback_count(self, root: Snapshot) -> int:
        """Resolve the number of feedback entries."""
        count = getattr(root, "_feedback_count", None)
        return count if count is not None else root.feedback.count()

    @strawberry_django.field(prefetch_related=["feedback"])
    def feedback(
        self, root: Snapshot, limit: int = 10, offset: int = 0
    ) -> list[SnapshotFeedbackNode]:
        """Resolve feedback entries, most recent first."""
        queryset = root.feedback.select_related("user__github_user").order_by("-created_at")
        return SnapshotNode._slice_related(queryset, limit, offset)

    @strawberry_django.field
    def my_feedback(self, root: Snapshot, info: Info) -> SnapshotFeedbackNode | None:
        """Resolve the current user's own feedback, if any."""
        user = info.context.request.user
        if not user.is_authenticated:
            return None
        return root.feedback.filter(user=user).first()

    @strawberry_django.field(prefetch_related=["events"])
    def events(self, root: Snapshot, limit: int = 100, offset: int = 0) -> list[EventNode]:
        """Resolve events."""
        return SnapshotNode._slice_related(root.events.order_by("-start_date"), limit, offset)

    @strawberry_django.field(prefetch_related=["issues"])
    def issues(
        self,
        root: Snapshot,
        limit: int = 6,
        offset: int = 0,
        repository_names: list[str] | None = None,
    ) -> list[IssueNode]:
        """Resolve issues."""
        queryset = root.issues.prefetch_related(MERGED_PULL_REQUESTS_PREFETCH).order_by(
            "-created_at"
        )
        if repository_names is not None:
            queryset = queryset.filter(repository__name__in=repository_names)
        return SnapshotNode._slice_related(queryset, limit, offset)

    @strawberry_django.field(prefetch_related=["posts"])
    def posts(self, root: Snapshot, limit: int = 100, offset: int = 0) -> list[PostNode]:
        """Resolve posts."""
        return SnapshotNode._slice_related(root.posts.order_by("-published_at"), limit, offset)

    @strawberry_django.field(prefetch_related=["projects"])
    def projects(self, root: Snapshot) -> list[ProjectNode]:
        """Resolve projects."""
        return root.projects.order_by("-created_at")

    @strawberry_django.field(prefetch_related=["pull_requests"])
    def pull_requests(
        self,
        root: Snapshot,
        limit: int = 6,
        offset: int = 0,
        repository_names: list[str] | None = None,
    ) -> list[PullRequestNode]:
        """Resolve pull requests."""
        queryset = root.pull_requests.order_by("-created_at")
        if repository_names is not None:
            queryset = queryset.filter(repository__name__in=repository_names)
        return SnapshotNode._slice_related(queryset, limit, offset)

    @strawberry_django.field(prefetch_related=["releases"])
    def releases(self, root: Snapshot) -> list[ReleaseNode]:
        """Resolve releases."""
        return root.releases.order_by("-published_at")

    @strawberry_django.field(prefetch_related=["users"])
    def users(self, root: Snapshot, limit: int = 100, offset: int = 0) -> list[UserNode]:
        """Resolve users."""
        return SnapshotNode._slice_related(root.users.order_by("-created_at"), limit, offset)
