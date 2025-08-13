"""A command to update context for Slack message data."""

from django.db.models import Model, QuerySet

from apps.ai.common.base.context_command import BaseContextCommand
from apps.slack.models.message import Message


class Command(BaseContextCommand):
    def add_arguments(self, parser):
        """Override to use different default batch size for messages."""
        parser.add_argument(
            "--message-key",
            type=str,
            help="Process only the message with this key",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Process all the messages",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100,
            help="Number of messages to process in each batch",
        )

    def entity_name(self) -> str:
        return "message"

    def entity_name_plural(self) -> str:
        return "messages"

    def extract_content(self, entity: Message) -> tuple[str, str]:
        """Extract content from the message."""
        return entity.cleaned_text or "", ""

    def get_default_queryset(self) -> QuerySet:
        """Return all messages by default since Message model doesn't have is_active field."""
        return self.get_base_queryset()

    def key_field_name(self) -> str:
        return "slack_message_id"

    def model_class(self) -> type[Model]:
        return Message

    def source_name(self) -> str:
        return "slack_message"
