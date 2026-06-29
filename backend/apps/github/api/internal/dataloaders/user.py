"""DataLoaders for users."""

from django.db.models import Count
from strawberry.dataloader import DataLoader

from apps.common.api.internal.dataloaders.utils import get_result_by_keys, get_results_by_keys
from apps.github.models.user import User
from apps.nest.models.badge import Badge
from apps.nest.models.user_badge import UserBadge

USER_BADGES_BY_USER_ID_LOADER = "user_badges_by_user_id"
USER_ISSUES_COUNT_LOADER = "user_issues_count"
USER_RELEASES_COUNT_LOADER = "user_releases_count"


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


async def load_user_issues_count(user_ids: list[int]) -> list[int]:
    """Batch-load issues count for the given user IDs in a single query."""
    users = User.objects.filter(pk__in=user_ids).annotate(items_count=Count("created_issues"))
    return [
        result or 0
        for result in await get_result_by_keys(
            users, user_ids, key_field="pk", value_field="items_count"
        )
    ]


async def load_user_releases_count(user_ids: list[int]) -> list[int]:
    """Batch-load releases count for the given user IDs in a single query."""
    users = User.objects.filter(pk__in=user_ids).annotate(items_count=Count("created_releases"))
    return [
        result or 0
        for result in await get_result_by_keys(
            users, user_ids, key_field="pk", value_field="items_count"
        )
    ]


def get_user_loaders() -> dict[str, DataLoader[int, int] | DataLoader[int, list[Badge]]]:
    """Return a mapping of per-request DataLoader instances."""
    return {
        USER_BADGES_BY_USER_ID_LOADER: DataLoader[int, list[Badge]](
            load_fn=load_user_badges_by_user_id,
        ),
        USER_ISSUES_COUNT_LOADER: DataLoader[int, int](
            load_fn=load_user_issues_count,
        ),
        USER_RELEASES_COUNT_LOADER: DataLoader[int, int](
            load_fn=load_user_releases_count,
        ),
    }
