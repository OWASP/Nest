"""DataLoader for interested users per issue."""

from strawberry.dataloader import DataLoader

from apps.common.api.internal.dataloaders.utils import get_results_by_keys
from apps.github.models.user import User
from apps.mentorship.models.issue_user_interest import IssueUserInterest


async def load_interested_users(issue_ids: list[int]) -> list[list[User]]:
    """Batch-load interested users for the given issue IDs in a single query."""
    interests = (
        IssueUserInterest.objects.select_related("user__owasp_profile")
        .filter(issue_id__in=issue_ids)
        .order_by("user__login")
    )
    return await get_results_by_keys(
        interests, issue_ids, key_field="issue_id", value_field="user"
    )


def get_interested_users_loader() -> DataLoader:
    """Return a per-request DataLoader instance."""
    return DataLoader(load_fn=load_interested_users)
