"""AI app admin."""

from django.contrib import admin

from apps.ai.models.chunk import Chunk
from apps.ai.models.context import Context


class ChunkAdmin(admin.ModelAdmin):
    """Admin for Chunk model."""

    list_display = (
        "id",
        "text",
        "context",
    )
    list_filter = ("context__entity_type",)
    search_fields = ("text",)


class ContextAdmin(admin.ModelAdmin):
    """Admin for Context model."""

    list_display = (
        "id",
        "content",
        "entity_type",
        "entity_id",
        "source",
    )
    list_filter = ("entity_type", "source")
    search_fields = ("content", "source")


admin.site.register(Chunk, ChunkAdmin)
admin.site.register(Context, ContextAdmin)
