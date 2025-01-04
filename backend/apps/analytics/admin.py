"""Analytics app admin."""

from django.contrib import admin

from apps.analytics.models.usersearchquery import UserSearchQuery


@admin.register(UserSearchQuery)
class AnalyticsAdmin(admin.ModelAdmin):
    list_display = ("query", "source", "category", "timestamp")
    list_filter = ("source", "category", "timestamp")
    search_fields = ("query", "user_id", "session_id")
    ordering = ("-timestamp",)
    readonly_fields = ("timestamp",)
