"""A command to create chunks of OWASP event data for RAG."""

from django.db.models import QuerySet

from apps.ai.common.base.chunk_command import BaseChunkCommand
from apps.ai.common.extractors.event import extract_event_content
from apps.owasp.models.event import Event


class Command(BaseChunkCommand):
    key_field_name = "key"
    model_class = Event

    def extract_content(self, entity: Event) -> tuple[str, str]:
        """Extract content from the event."""
        return extract_event_content(entity)

    def get_base_queryset(self) -> QuerySet:
        """Return the base queryset with ordering."""
        return super().get_base_queryset()

    def get_default_queryset(self) -> QuerySet:
        """Return upcoming events by default instead of is_active filter."""
        return Event.upcoming_events()
