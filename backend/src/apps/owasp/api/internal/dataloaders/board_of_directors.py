"""DataLoaders for Board of Directors."""

from asgiref.sync import sync_to_async
from django.contrib.contenttypes.models import ContentType
from strawberry.dataloader import DataLoader

from apps.common.api.internal.dataloaders.utils import get_results_by_keys
from apps.owasp.models.board_of_directors import BoardOfDirectors
from apps.owasp.models.entity_member import EntityMember

CANDIDATES_BY_BOARD_ID_LOADER = "candidates_by_board_id"
MEMBERS_BY_BOARD_ID_LOADER = "members_by_board_id"


async def load_candidates_by_board_id(board_ids: list[int]) -> list[list[EntityMember]]:
    """Batch-load candidates for the given board of directors IDs in a single query."""
    board_content_type = await sync_to_async(ContentType.objects.get_for_model)(BoardOfDirectors)
    candidates = (
        EntityMember.objects.select_related("member")
        .filter(
            entity_type=board_content_type,
            entity_id__in=board_ids,
            role=EntityMember.Role.CANDIDATE,
            is_active=True,
            is_reviewed=True,
        )
        .order_by("member_name")
    )
    return await get_results_by_keys(candidates, board_ids, key_field="entity_id")


async def load_members_by_board_id(board_ids: list[int]) -> list[list[EntityMember]]:
    """Batch-load members for the given board of directors IDs in a single query."""
    board_content_type = await sync_to_async(ContentType.objects.get_for_model)(BoardOfDirectors)
    members = (
        EntityMember.objects.select_related("member")
        .filter(
            entity_type=board_content_type,
            entity_id__in=board_ids,
            role=EntityMember.Role.MEMBER,
            is_active=True,
            is_reviewed=True,
        )
        .order_by("member_name")
    )
    return await get_results_by_keys(members, board_ids, key_field="entity_id")


def get_board_of_directors_loaders() -> dict[str, DataLoader[int, list[EntityMember]]]:
    """Return a mapping of per-request DataLoader instances."""
    return {
        CANDIDATES_BY_BOARD_ID_LOADER: DataLoader[int, list[EntityMember]](
            load_fn=load_candidates_by_board_id,
        ),
        MEMBERS_BY_BOARD_ID_LOADER: DataLoader[int, list[EntityMember]](
            load_fn=load_members_by_board_id,
        ),
    }
