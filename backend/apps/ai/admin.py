"""AI app admin."""

from django.contrib import admin

from apps.ai.models.chunk import Chunk
from apps.ai.models.context import Context


class ContextAdmin(admin.ModelAdmin):
    """Admin for Context model."""

    list_display = (
        "id",
        "generated_text",
        "content_type",
        "object_id",
        "source",
    )
    search_fields = ("generated_text", "source")
    list_filter = ("content_type", "source")


class ChunkAdmin(admin.ModelAdmin):
    """Admin for Chunk model."""

    list_display = (
        "id",
        "text",
        "context",
    )
    search_fields = ("text",)
    list_filter = ("context__content_type",)


admin.site.register(Context, ContextAdmin)
admin.site.register(Chunk, ChunkAdmin)
