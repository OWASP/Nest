from django.contrib import admin
from ..models import EntityChannel

@admin.action(description="Mark selected EntityChannels as reviewed")
def mark_as_reviewed(_modeladmin, request, queryset):
    updated = queryset.update(is_reviewed=True)
    # Provide feedback in the admin UI
    request._messages.add(
        level=20,
        message=f"Marked {updated} EntityChannel(s) as reviewed.",
    )

@admin.register(EntityChannel)
class EntityChannelAdmin(admin.ModelAdmin):
    list_display = ("entity", "conversation", "is_main_channel", "is_reviewed", "kind")
    list_filter = ("is_main_channel", "is_reviewed", "kind", "content_type")
    search_fields = ("object_id", "conversation__name")
    actions = [mark_as_reviewed]
