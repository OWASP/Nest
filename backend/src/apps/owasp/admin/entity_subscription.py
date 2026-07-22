"""Admin registration for EntitySubscription model."""

from django.contrib import admin

from apps.owasp.models.entity_subscription import EntitySubscription
from apps.owasp.models.entity_subscription_preference import EntitySubscriptionPreference


class ProjectPreferenceInline(admin.StackedInline):
    """Inline for project entity preferences."""

    model = EntitySubscriptionPreference
    verbose_name = "Project Preference"
    verbose_name_plural = "Project Preferences"
    extra = 0
    fields = ("project", "include_issues", "include_pull_requests", "include_releases")
    autocomplete_fields = ("project",)

    def get_queryset(self, request):
        """Filter to only show project preferences."""
        return super().get_queryset(request).filter(project__isnull=False)


class ChapterPreferenceInline(admin.StackedInline):
    """Inline for chapter entity preferences."""

    model = EntitySubscriptionPreference
    verbose_name = "Chapter Preference"
    verbose_name_plural = "Chapter Preferences"
    extra = 0
    fields = ("chapter", "include_issues", "include_pull_requests", "include_releases")
    autocomplete_fields = ("chapter",)

    def get_queryset(self, request):
        """Filter to only show chapter preferences."""
        return super().get_queryset(request).filter(chapter__isnull=False)


class CommitteePreferenceInline(admin.StackedInline):
    """Inline for committee entity preferences."""

    model = EntitySubscriptionPreference
    verbose_name = "Committee Preference"
    verbose_name_plural = "Committee Preferences"
    extra = 0
    fields = ("committee", "include_issues", "include_pull_requests", "include_releases")
    autocomplete_fields = ("committee",)

    def get_queryset(self, request):
        """Filter to only show committee preferences."""
        return super().get_queryset(request).filter(committee__isnull=False)


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
