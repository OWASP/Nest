"""OWASP app award admin."""

from django.contrib import admin

from apps.owasp.models.award import Award


@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    """Award admin."""

    list_display = ("name", "category", "year", "user", "is_reviewed", "created_at")
    list_filter = ("category", "year", "is_reviewed", "created_at")
    search_fields = ("name", "category", "user__name", "user__login")
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("user",)
