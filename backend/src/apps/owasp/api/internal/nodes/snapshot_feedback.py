"""OWASP snapshot feedback GraphQL node."""

import strawberry
import strawberry_django

from apps.owasp.models.snapshot_feedback import SnapshotFeedback


@strawberry_django.type(
    SnapshotFeedback,
    fields=[
        "comment",
        "created_at",
        "rating",
        "updated_at",
    ],
)
class SnapshotFeedbackNode(strawberry.relay.Node):
    """Snapshot feedback node."""

    @strawberry_django.field(select_related=["user__github_user"])
    def avatar_url(self, root: SnapshotFeedback) -> str:
        """Resolve the GitHub avatar URL of the feedback author, if linked."""
        github_user = root.user.github_user
        return github_user.avatar_url if github_user else ""

    @strawberry_django.field(select_related=["user__github_user"])
    def login(self, root: SnapshotFeedback) -> str:
        """Resolve the GitHub login of the feedback author, if linked."""
        github_user = root.user.github_user
        return github_user.login if github_user else ""

    @strawberry_django.field(select_related=["user"])
    def username(self, root: SnapshotFeedback) -> str:
        """Resolve the username of the feedback author."""
        return root.user.username
