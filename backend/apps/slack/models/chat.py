"""Chat model for storing conversation context."""

from django.db import models
from django.utils import timezone

from apps.common.models import TimestampedModel
from apps.slack.models.member import Member
from apps.slack.models.workspace import Workspace


class Chat(TimestampedModel):
    """Store chat conversation context for DMs."""

    context = models.TextField(blank=True)
    created_at = models.DateTimeField(verbose_name="Created at", default=timezone.now)
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="chats")
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="chats")

    class Meta:
        db_table = "slack_chat"
        unique_together = [["user", "workspace"]]
        ordering = ["-created_at"]

    def __str__(self):
        """Return a concise, human-readable identifier for this chat."""
        return f"Chat with {self.user.real_name or self.user.username} in {self.workspace.name}"

    @staticmethod
    def update_data(user: Member, workspace: Workspace, *, save: bool = True) -> "Chat":
        """Update or create chat data for a user in a workspace.

        Args:
            user: Member instance to associate with the chat.
            workspace: Workspace instance to associate with the chat.
            save: Whether to save the chat to the database.

        Returns:
            Updated or created Chat instance.

        """
        try:
            chat = Chat.objects.get(user=user, workspace=workspace)
        except Chat.DoesNotExist:
            chat = Chat(user=user, workspace=workspace, is_active=True)

        if save:
            chat.save()

        return chat

    def add_to_context(self, user_message: str, bot_response: str | None = None) -> None:
        """Add messages to the conversation context.

        Args:
            user_message: The user's message to add to context.
            bot_response: The bot's response to add to context.

        """
        if not self.context:
            self.context = ""

        self.context += f"User: {user_message}\n"

        if bot_response:
            self.context += f"Bot: {bot_response}\n"

        self.save(update_fields=["context"])

    def get_context(self, limit_exchanges: int | None = None) -> str:
        """Get the conversation context.

        Args:
            limit_exchanges: Optional limit on number of exchanges to return.

        Returns:
            The conversation context, potentially limited to recent exchanges.

        """
        if not self.context:
            return ""

        if limit_exchanges is None:
            return self.context

        lines = self.context.strip().split("\n")
        if len(lines) <= limit_exchanges * 2:
            return self.context

        return "\n".join(lines[-(limit_exchanges * 2) :])
