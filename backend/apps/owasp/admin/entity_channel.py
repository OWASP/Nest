"""Admin configuration for the EntityChannel model."""

from django.contrib import admin, messages
from django.contrib.contenttypes.models import ContentType

from apps.owasp.models import EntityChannel
from apps.slack.models import Conversation


@admin.action(description="Mark selected EntityChannels as reviewed")
def mark_as_reviewed(_modeladmin, request, queryset):
    """Mark selected EntityChannels as reviewed.

    Args:
        _modeladmin (EntityChannelAdmin): The admin instance.
        request (HttpRequest): The current admin request.
        queryset (QuerySet): Selected EntityChannel instances.

    """
    messages.success(
        request,
        f"Marked {queryset.update(is_reviewed=True)} EntityChannel(s) as reviewed.",
    )


@admin.register(EntityChannel)
class EntityChannelAdmin(admin.ModelAdmin):
    """Admin interface for the EntityChannel model."""

    actions = (mark_as_reviewed,)
    fields = (
        "entity_type",
        "entity_id",
        "channel_type",
        "channel_id",
        "platform",
        "is_default",
        "is_active",
        "is_reviewed",
    )
    list_display = (
        "entity_type",
        "entity_id",
        "channel_type",
        "channel_search_display",
        "channel_id",
        "platform",
        "is_default",
        "is_active",
        "is_reviewed",
    )
    list_filter = (
        "entity_type",
        "channel_type",
        "platform",
        "is_default",
        "is_active",
        "is_reviewed",
    )
    ordering = (
        "entity_type",
        "entity_id",
        "platform",
        "channel_id",
    )
    search_fields = (
        "entity_id",
        "channel_id",
    )

    def channel_search_display(self, obj):
        """Return the channel name for the selected EntityChannel."""
        if obj.channel_id and obj.channel_type:
            try:
                if obj.channel_type.model == "conversation":
                    conversation = Conversation.objects.get(id=obj.channel_id)
                    return f"#{conversation.name}"
            except Conversation.DoesNotExist:
                return f"Channel {obj.channel_id} (not found)"
        return "-"

    channel_search_display.short_description = "Channel Name"

    def get_form(self, request, obj=None, **kwargs):
        """Return the form for EntityChannel with preset conversation content type.

        Args:
            request (HttpRequest): The current admin request.
            obj (EntityChannel, optional): The instance being edited.
            **kwargs: Additional keyword arguments.

        Returns:
            Form: The form class with conversation_content_type_id preset.

        """
        form = super().get_form(request, obj, **kwargs)
        form.conversation_content_type_id = ContentType.objects.get_for_model(Conversation).id

        return form
