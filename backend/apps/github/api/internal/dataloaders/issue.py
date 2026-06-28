"""Dataloaders for issues."""

from strawberry.dataloader import DataLoader

from apps.common.api.internal.dataloaders.utils import get_results_by_keys
from apps.github.models.issue import Issue

RECENT_ISSUES_LIMIT = 5
ISSUES_BY_REPOSITORY_ID_LOADER = "issues_by_repository_id"


async def load_issues_by_repository_id(repository_ids: list[int]) -> list[list[Issue]]:
    """Batch-load recent issues for the given repository IDs."""
    issues = Issue.objects.filter(repository_id__in=repository_ids).order_by(
        "repository_id", "-created_at"
    )

    results: list[list[Issue]] = await get_results_by_keys(
        issues, repository_ids, key_field="repository_id"
    )

    return [group[:RECENT_ISSUES_LIMIT] for group in results]


def get_issue_loaders() -> dict[str, DataLoader[int, list[Issue]]]:
    """Return a mapping of per-request DataLoader instances."""
    return {
        ISSUES_BY_REPOSITORY_ID_LOADER: DataLoader[int, list[Issue]](
            load_fn=load_issues_by_repository_id,
        ),
    }
