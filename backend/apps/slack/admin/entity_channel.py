"""Admin configuration for the EntityChannel model."""

from django.contrib import admin, messages

from apps.slack.models import EntityChannel


@admin.action(description="Mark selected EntityChannels as reviewed")
def mark_as_reviewed(_modeladmin, request, queryset):
    """Admin action to mark selected EntityChannels as reviewed."""
    updated = queryset.update(is_reviewed=True)
    # Provide feedback in the admin UI
    messages.success(request, f"Marked {updated} EntityChannel(s) as reviewed.")


@admin.register(EntityChannel)
class EntityChannelAdmin(admin.ModelAdmin):
    """Admin interface for the EntityChannel model."""

    list_display = ("entity", "conversation", "is_main_channel", "is_reviewed", "kind")
    list_filter = ("is_main_channel", "is_reviewed", "kind", "content_type")
    search_fields = ("object_id", "conversation__name")
    actions = [mark_as_reviewed]
