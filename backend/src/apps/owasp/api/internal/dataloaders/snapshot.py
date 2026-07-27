"""DataLoaders for snapshots."""

from django.db.models import F, Window
from django.db.models.functions import RowNumber
from strawberry.dataloader import DataLoader

from apps.common.api.internal.dataloaders.utils import get_results_by_keys
from apps.github.models.issue import Issue
from apps.github.models.release import Release
from apps.github.models.user import User
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.project import Project

CHAPTERS_BY_SNAPSHOT_ID = "chapters_by_snapshot_id"
ISSUES_BY_SNAPSHOT_ID = "issues_by_snapshot_id"
PROJECTS_BY_SNAPSHOT_ID = "projects_by_snapshot_id"
RELEASES_BY_SNAPSHOT_ID = "releases_by_snapshot_id"
USERS_BY_SNAPSHOT_ID = "users_by_snapshot_id"

RECENT_ISSUES_LIMIT = 100


async def load_chapters_by_snapshot_id(snapshot_ids: list[int]) -> list[list[Chapter]]:
    """Batch-load new chapters for the given snapshot IDs in a single query."""
    chapters = (
        Chapter.objects.filter(snapshots__in=snapshot_ids)
        .annotate(snapshot_id=F("snapshots__pk"))
        .order_by("-created_at")
    )

    return await get_results_by_keys(chapters, snapshot_ids, key_field="snapshot_id")


async def load_issues_by_snapshot_id(snapshot_ids: list[int]) -> list[list[Issue]]:
    """Batch-load new issues for the given snapshot IDs in a single query."""
    issues = (
        Issue.objects.filter(snapshots__in=snapshot_ids)
        .annotate(snapshot_id=F("snapshots__pk"))
        .annotate(
            row_number=Window(
                expression=RowNumber(),
                partition_by=[F("snapshot_id")],
                order_by=F("created_at").desc(),
            ),
        )
        .filter(row_number__lte=RECENT_ISSUES_LIMIT)
        .order_by("snapshot_id", "-created_at")
    )

    return await get_results_by_keys(issues, snapshot_ids, key_field="snapshot_id")


async def load_projects_by_snapshot_id(snapshot_ids: list[int]) -> list[list[Project]]:
    """Batch-load new projects for the given snapshot IDs in a single query."""
    projects = (
        Project.objects.filter(snapshots__in=snapshot_ids)
        .annotate(snapshot_id=F("snapshots__pk"))
        .order_by("-created_at")
    )

    return await get_results_by_keys(projects, snapshot_ids, key_field="snapshot_id")


async def load_releases_by_snapshot_id(snapshot_ids: list[int]) -> list[list[Release]]:
    """Batch-load new releases for the given snapshot IDs in a single query."""
    releases = (
        Release.objects.filter(snapshots__in=snapshot_ids)
        .annotate(snapshot_id=F("snapshots__pk"))
        .order_by("-published_at")
    )

    return await get_results_by_keys(releases, snapshot_ids, key_field="snapshot_id")


async def load_users_by_snapshot_id(snapshot_ids: list[int]) -> list[list[User]]:
    """Batch-load new users for the given snapshot IDs in a single query."""
    users = (
        User.objects.filter(snapshots__in=snapshot_ids)
        .annotate(snapshot_id=F("snapshots__pk"))
        .order_by("-created_at")
    )

    return await get_results_by_keys(users, snapshot_ids, key_field="snapshot_id")


def get_snapshot_loaders() -> dict[str, object]:
    """Return a mapping of per-request DataLoader instances."""
    return {
        CHAPTERS_BY_SNAPSHOT_ID: DataLoader[int, list[Chapter]](
            load_fn=load_chapters_by_snapshot_id,
        ),
        ISSUES_BY_SNAPSHOT_ID: DataLoader[int, list[Issue]](
            load_fn=load_issues_by_snapshot_id,
        ),
        PROJECTS_BY_SNAPSHOT_ID: DataLoader[int, list[Project]](
            load_fn=load_projects_by_snapshot_id,
        ),
        RELEASES_BY_SNAPSHOT_ID: DataLoader[int, list[Release]](
            load_fn=load_releases_by_snapshot_id,
        ),
        USERS_BY_SNAPSHOT_ID: DataLoader[int, list[User]](
            load_fn=load_users_by_snapshot_id,
        ),
    }
