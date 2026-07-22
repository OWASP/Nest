"""Admin registration for EntitySubscription model."""

from django.contrib import admin

from apps.owasp.models.entity_subscription import EntitySubscription
from apps.owasp.models.entity_subscription_preference import EntitySubscriptionPreference


def get_preference_inline(entity_field: str, entity_name: str) -> type[admin.StackedInline]:
    """Create an inline class for a specific entity preference."""

    class BasePreferenceInline(admin.StackedInline):
        model = EntitySubscriptionPreference
        verbose_name = f"{entity_name} Preference"
        verbose_name_plural = f"{entity_name} Preferences"
        extra = 0
        fields = (entity_field, "include_issues", "include_pull_requests", "include_releases")
        autocomplete_fields = (entity_field,)

        def get_queryset(self, request):
            """Filter to only show preferences for this entity type."""
            return super().get_queryset(request).filter(**{f"{entity_field}__isnull": False})

    return BasePreferenceInline


ProjectPreferenceInline = get_preference_inline("project", "Project")
ChapterPreferenceInline = get_preference_inline("chapter", "Chapter")
CommitteePreferenceInline = get_preference_inline("committee", "Committee")


class EntitySubscriptionAdmin(admin.ModelAdmin):
    """Admin for EntitySubscription model."""

    list_display = ("user", "name", "frequency", "is_active", "created_at", "updated_at")
    list_filter = ("frequency", "is_active", "created_at")
    search_fields = ("user__email", "user__username", "name")
    raw_id_fields = ("user",)
    readonly_fields = ("unsubscribe_token", "created_at", "updated_at")
    inlines = [ProjectPreferenceInline, ChapterPreferenceInline, CommitteePreferenceInline]

    fieldsets = (
        (None, {"fields": ("user", "name", "frequency", "is_active")}),
        (
            "System",
            {
                "fields": ("unsubscribe_token", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


admin.site.register(EntitySubscription, EntitySubscriptionAdmin)
