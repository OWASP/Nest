"""AI app admin."""

from django.contrib import admin

from apps.ai.models.chunk import Chunk
from apps.ai.models.context import Context
from apps.ai.models.semantic_cache import SemanticCache


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


class SemanticCacheAdmin(admin.ModelAdmin):
    """Admin for SemanticCache model."""

    list_display = (
        "confidence",
        "id",
        "intent",
        "nest_created_at",
        "query_text",
    )
    list_filter = ("intent",)
    search_fields = ("query_text", "response_text")


admin.site.register(Chunk, ChunkAdmin)
admin.site.register(Context, ContextAdmin)
admin.site.register(SemanticCache, SemanticCacheAdmin)
