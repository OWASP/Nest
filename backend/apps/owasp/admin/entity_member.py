"""EntityMember admin configuration."""

from django.contrib import admin

from apps.owasp.models.entity_member import EntityMember


class EntityMemberAdmin(admin.ModelAdmin):
    """Admin for EntityMember records (generic link to any OWASP entity)."""

    autocomplete_fields = ("member",)
    fields = (
        "entity_type",
        "entity_id",
        "member",
        "kind",
        "order",
        "is_reviewed",
        "description",
    )
    list_display = (
        "member",
        "kind",
        "is_reviewed",
        "order",
    )
    list_filter = (
        "kind",
        "is_reviewed",
    )
    search_fields = (
        "member__login",
        "member__name",
        "description",
        "entity_id",
    )


admin.site.register(EntityMember, EntityMemberAdmin)
