"""A command to update context for OWASP event data."""

from django.db.models import Model, QuerySet

from apps.ai.common.base import BaseContextCommand
from apps.ai.common.extractors.event import extract_event_content
from apps.owasp.models.event import Event


class Command(BaseContextCommand):
    @property
    def model_class(self) -> type[Model]:
        return Event

    @property
    def entity_name(self) -> str:
        return "event"

    @property
    def entity_name_plural(self) -> str:
        return "events"

    @property
    def key_field_name(self) -> str:
        return "key"

    def get_default_queryset(self) -> QuerySet:
        """Return upcoming events by default instead of is_active filter."""
        return Event.upcoming_events()

    def get_base_queryset(self) -> QuerySet:
        """Return the base queryset with ordering."""
        return super().get_base_queryset()

    def extract_content(self, entity: Event) -> tuple[str, str]:
        """Extract content from the event."""
        return extract_event_content(entity)
