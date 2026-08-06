"""Admin registration for EntitySubscription model."""

from django.contrib import admin

from apps.owasp.models.entity_subscription import EntitySubscription


class EntitySubscriptionAdmin(admin.ModelAdmin):
    """Admin for EntitySubscription model."""

    list_display = ("user", "get_entity", "frequency", "is_active", "created_at")
    list_filter = ("frequency", "is_active", "created_at")
    list_select_related = ("chapter", "committee", "project", "user")
    search_fields = ("user__email", "user__username")
    raw_id_fields = ("user",)
    autocomplete_fields = ("chapter", "committee", "project")
    readonly_fields = ("unsubscribe_token", "created_at", "updated_at")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user",
                    "frequency",
                    "is_active",
                    "chapter",
                    "committee",
                    "project",
                ),
            },
        ),
        (
            "System",
            {
                "fields": ("unsubscribe_token", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description="Entity")
    def get_entity(self, obj):
        """Return the subscribed entity name."""
        return obj.entity or "—"


admin.site.register(EntitySubscription, EntitySubscriptionAdmin)
