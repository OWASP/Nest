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

NEW_CHAPTERS_BY_SNAPSHOT_ID = "new_chapters_by_snapshot_id"
NEW_ISSUES_BY_SNAPSHOT_ID = "new_issues_by_snapshot_id"
NEW_PROJECTS_BY_SNAPSHOT_ID = "new_projects_by_snapshot_id"
NEW_RELEASES_BY_SNAPSHOT_ID = "new_releases_by_snapshot_id"
NEW_USERS_BY_SNAPSHOT_ID = "new_users_by_snapshot_id"

RECENT_ISSUES_LIMIT = 100


async def load_new_chapters_by_snapshot_id(snapshot_ids: list[int]) -> list[list[Chapter]]:
    """Batch-load new chapters for the given snapshot IDs in a single query."""
    chapters = (
        Chapter.objects.filter(snapshots__in=snapshot_ids)
        .annotate(snapshot_id=F("snapshots__pk"))
        .order_by("-created_at")
    )

    return await get_results_by_keys(chapters, snapshot_ids, key_field="snapshot_id")


async def load_new_issues_by_snapshot_id(snapshot_ids: list[int]) -> list[list[Issue]]:
    """Batch-load new issues for the given snapshot IDs in a single query."""
    issues = (
        Issue.objects.filter(snapshots__in=snapshot_ids)
        .annotate(
            snapshot_id=F("snapshots__pk"),
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


async def load_new_projects_by_snapshot_id(snapshot_ids: list[int]) -> list[list[Project]]:
    """Batch-load new projects for the given snapshot IDs in a single query."""
    projects = (
        Project.objects.filter(snapshots__in=snapshot_ids)
        .annotate(snapshot_id=F("snapshots__pk"))
        .order_by("-created_at")
    )

    return await get_results_by_keys(projects, snapshot_ids, key_field="snapshot_id")


async def load_new_releases_by_snapshot_id(snapshot_ids: list[int]) -> list[list[Release]]:
    """Batch-load new releases for the given snapshot IDs in a single query."""
    releases = (
        Release.objects.filter(snapshots__in=snapshot_ids)
        .annotate(snapshot_id=F("snapshots__pk"))
        .order_by("-published_at")
    )

    return await get_results_by_keys(releases, snapshot_ids, key_field="snapshot_id")


async def load_new_users_by_snapshot_id(snapshot_ids: list[int]) -> list[list[User]]:
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
        NEW_CHAPTERS_BY_SNAPSHOT_ID: DataLoader[int, list[Chapter]](
            load_fn=load_new_chapters_by_snapshot_id,
        ),
        NEW_ISSUES_BY_SNAPSHOT_ID: DataLoader[int, list[Issue]](
            load_fn=load_new_issues_by_snapshot_id,
        ),
        NEW_PROJECTS_BY_SNAPSHOT_ID: DataLoader[int, list[Project]](
            load_fn=load_new_projects_by_snapshot_id,
        ),
        NEW_RELEASES_BY_SNAPSHOT_ID: DataLoader[int, list[Release]](
            load_fn=load_new_releases_by_snapshot_id,
        ),
        NEW_USERS_BY_SNAPSHOT_ID: DataLoader[int, list[User]](
            load_fn=load_new_users_by_snapshot_id,
        ),
    }
