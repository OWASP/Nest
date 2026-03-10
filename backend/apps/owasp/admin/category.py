"""Project Category admin configuration."""

from django.contrib import admin

from apps.owasp.models.category import ProjectCategory


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    """Admin for Project Category model."""

    list_display = (
        "name",
        "level",
        "full_path",
        "is_active",
        "nest_created_at",
        "nest_updated_at",
    )
    list_filter = (
        "is_active",
        "parent",
        "nest_created_at",
        "nest_updated_at",
    )
    ordering = ("name",)
    readonly_fields = (
        "full_path",
        "level",
        "nest_created_at",
        "nest_updated_at",
    )
    search_fields = (
        "name",
        "slug",
        "description",
    )
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "slug",
                    "description",
                )
            },
        ),
        (
            "Hierarchy",
            {
                "fields": (
                    "parent",
                    "level",
                    "full_path",
                )
            },
        ),
        (
            "Status",
            {
                "fields": ("is_active",)
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "nest_created_at",
                    "nest_updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def get_readonly_fields(self, request, obj=None):
        """Get readonly fields."""
        readonly = list(self.readonly_fields)
        if obj:  # Editing an existing object
            readonly.append("slug")
        return readonly
