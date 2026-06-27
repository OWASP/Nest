"""Dataloaders for Admin."""

from strawberry.dataloader import DataLoader

from apps.common.api.internal.dataloaders.utils import get_m2m_results_by_keys
from apps.mentorship.models.admin import Admin

ADMINS_BY_PROGRAM_ID_LOADER = "admins_by_program_id"


async def load_admins_by_program_id(program_ids: list[int]) -> list[list[Admin]]:
    """Batch-load admins for the given program IDs in a single query."""
    admins = (
        Admin.objects.select_related("github_user")
        .filter(admin_programs__in=program_ids)
        .prefetch_related("admin_programs")
        .order_by("github_user__login")
    )
    return await get_m2m_results_by_keys(admins, program_ids, "admin_programs", "pk")


def get_admin_loaders() -> dict[str, DataLoader[int, list[Admin]]]:
    """Return a mapping of per-request DataLoader instances."""
    return {
        ADMINS_BY_PROGRAM_ID_LOADER: DataLoader[int, list[Admin]](
            load_fn=load_admins_by_program_id,
        ),
    }
