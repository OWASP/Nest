from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from ..models import EntityChannel

@admin.action(description="Mark selected EntityChannels as reviewed")
def mark_as_reviewed(modeladmin, request, queryset):
    queryset.update(is_reviewed=True)

@admin.register(EntityChannel)
class EntityChannelAdmin(admin.ModelAdmin):
    list_display = ("entity", "conversation", "is_main_channel", "is_reviewed", "kind")
    list_filter = ("is_main_channel", "is_reviewed", "kind", "content_type")
    search_fields = ("object_id", "conversation__name")
    actions = [mark_as_reviewed]
