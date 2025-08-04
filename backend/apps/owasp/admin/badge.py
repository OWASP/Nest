"""Admin configuration for the Badge model in the OWASP app."""

from django.contrib import admin

from apps.owasp.models.badge import Badge


class BadgeAdmin(admin.ModelAdmin):
    """Admin for Badge model."""

    list_display = (
        "name",
        "description",
        "weight",
        "css_class",
        "nest_created_at",
        "nest_updated_at",
    )
    search_fields = ("name", "description", "css_class")
    list_filter = ("weight",)
    ordering = ("weight", "name")
    fieldsets = (
        ("Basic Information", {"fields": ("name", "description", "weight")}),
        ("Display Settings", {"fields": ("css_class",)}),
        ("Timestamps", {"fields": ("nest_created_at", "nest_updated_at")}),
    )


admin.site.register(Badge, BadgeAdmin)
