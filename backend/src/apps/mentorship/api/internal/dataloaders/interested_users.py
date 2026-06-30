"""DataLoaders for interested users."""

from strawberry.dataloader import DataLoader

from apps.common.api.internal.dataloaders.utils import get_results_by_keys
from apps.github.models.user import User
from apps.mentorship.models.issue_user_interest import IssueUserInterest

INTERESTED_USERS_BY_ISSUE_ID_LOADER = "interested_users_by_issue_id"


async def load_interested_users_by_issue_id(issue_ids: list[int]) -> list[list[User]]:
    """Batch-load interested users for the given issue IDs in a single query."""
    interests = (
        IssueUserInterest.objects.select_related("user__owasp_profile")
        .filter(issue_id__in=issue_ids)
        .order_by("user__login")
    )
    return await get_results_by_keys(
        interests, issue_ids, key_field="issue_id", value_field="user"
    )


def get_interested_users_loaders() -> dict[str, DataLoader[int, list[User]]]:
    """Return a mapping of per-request DataLoader instances."""
    return {
        INTERESTED_USERS_BY_ISSUE_ID_LOADER: DataLoader[int, list[User]](
            load_fn=load_interested_users_by_issue_id,
        ),
    }
