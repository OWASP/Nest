"""DataLoaders for users."""

from strawberry.dataloader import DataLoader

from apps.common.api.internal.dataloaders.utils import get_results_by_keys
from apps.nest.models.badge import Badge
from apps.nest.models.user_badge import UserBadge

USER_BADGES_BY_USER_ID_LOADER = "user_badges_by_user_id"


async def load_user_badges_by_user_id(user_ids: list[int]) -> list[list[Badge]]:
    """Batch-load badges for the given user IDs in a single query."""
    user_badges = (
        UserBadge.objects.select_related("badge")
        .filter(user_id__in=user_ids, is_active=True)
        .order_by(
            "badge__weight",
            "badge__name",
        )
    )
    return await get_results_by_keys(
        user_badges, user_ids, key_field="user_id", value_field="badge"
    )


def get_user_loaders() -> dict[str, DataLoader[int, list[Badge]]]:
    """Return a mapping of per-request DataLoader instances."""
    return {
        USER_BADGES_BY_USER_ID_LOADER: DataLoader[int, list[Badge]](
            load_fn=load_user_badges_by_user_id,
        ),
    }
