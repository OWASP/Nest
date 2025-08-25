"""Admin configuration for the EntityChannel model."""

from django.contrib import admin, messages

from apps.slack.models import EntityChannel


@admin.action(description="Mark selected EntityChannels as reviewed")
def mark_as_reviewed(_modeladmin, request, queryset):
    """Admin action to mark selected EntityChannels as reviewed."""
    messages.success(
        request,
        f"Marked {queryset.update(is_reviewed=True)} EntityChannel(s) as reviewed.",
    )


@admin.register(EntityChannel)
class EntityChannelAdmin(admin.ModelAdmin):
    """Admin interface for the EntityChannel model."""

    actions = (mark_as_reviewed,)
    list_display = (
        "entity",
        "channel",
        "is_default",
        "is_reviewed",
        "platform",
    )
    list_filter = (
        "is_default",
        "is_reviewed",
        "platform",
        "entity_type",
        "channel_type",
    )
    search_fields = ("channel_id", "entity_id")
