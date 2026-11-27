"""A command to update context for Slack message data."""

from django.db.models import QuerySet

from apps.ai.common.base.context_command import BaseContextCommand
from apps.slack.models.message import Message


class Command(BaseContextCommand):
    key_field_name = "slack_message_id"
    model_class = Message

    def extract_content(self, entity: Message) -> tuple[str, str]:
        """Extract content from the message."""
        return entity.cleaned_text or "", ""

    def get_default_queryset(self) -> QuerySet:
        """Return all messages by default since Message model doesn't have is_active field."""
        return self.get_base_queryset()

    def source_name(self) -> str:
        return "slack_message"
