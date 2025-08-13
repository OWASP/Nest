"""Badge admin configuration."""

from django.contrib import admin

from apps.nest.models.badge import Badge


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    """Admin for Badge model."""

    list_display = ("name", "description", "weight", "css_class")
    list_filter = ("weight",)
    search_fields = ("name", "description")
    ordering = ("weight", "name")
