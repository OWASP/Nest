"""DataLoaders for entity channels."""

from asgiref.sync import sync_to_async
from django.contrib.contenttypes.models import ContentType
from django.db.models import OuterRef, Subquery
from strawberry.dataloader import DataLoader

from apps.common.api.internal.dataloaders.utils import get_result_by_keys
from apps.owasp.models.entity_channel import EntityChannel
from apps.slack.models.conversation import Conversation

EXTERNAL_ID_BY_ENTITY_CHANNEL_ID_LOADER = "external_id_by_entity_channel_id"
NAME_BY_ENTITY_CHANNEL_ID_LOADER = "name_by_entity_channel_id"


async def _load_channel_field_by_entity_channel_id(
    entity_channel_ids: list[int], field: str
) -> list[str | None]:
    """Batch-load a channel field for the given entity channel IDs in a single query."""
    conversation_content_type = await sync_to_async(ContentType.objects.get_for_model)(
        Conversation
    )
    channels = EntityChannel.objects.filter(
        pk__in=entity_channel_ids,
        channel_type=conversation_content_type,
    ).annotate(
        value=Subquery(
            Conversation.objects.filter(pk=OuterRef("channel_id")).values(field),
        ),
    )
    return await get_result_by_keys(
        channels, entity_channel_ids, key_field="pk", value_field="value"
    )


async def load_external_id_by_entity_channel_id(
    entity_channel_ids: list[int],
) -> list[str | None]:
    """Batch-load external channel IDs for the given entity channel IDs in a single query."""
    return await _load_channel_field_by_entity_channel_id(entity_channel_ids, "slack_channel_id")


async def load_name_by_entity_channel_id(
    entity_channel_ids: list[int],
) -> list[str | None]:
    """Batch-load channel names for the given entity channel IDs in a single query."""
    return await _load_channel_field_by_entity_channel_id(entity_channel_ids, "name")


def get_entity_channel_loaders() -> dict[str, DataLoader[int, str | None]]:
    """Return a mapping of per-request DataLoader instances."""
    return {
        EXTERNAL_ID_BY_ENTITY_CHANNEL_ID_LOADER: DataLoader[int, str | None](
            load_fn=load_external_id_by_entity_channel_id,
        ),
        NAME_BY_ENTITY_CHANNEL_ID_LOADER: DataLoader[int, str | None](
            load_fn=load_name_by_entity_channel_id,
        ),
    }
