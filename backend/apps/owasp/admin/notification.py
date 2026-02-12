"""Admin registration for notification models."""

from django.contrib import admin

from apps.owasp.models.notification import Notification, Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin for Subscription model."""

    list_display = ("user", "content_type", "object_id", "created_at")
    list_filter = ("content_type", "created_at")
    search_fields = ("user__email", "user__username")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin for Notification model."""

    list_display = ("recipient", "type", "title", "is_read", "created_at")
    list_filter = ("type", "is_read", "created_at")
    search_fields = ("recipient__email", "recipient__username", "title", "message")
    readonly_fields = ("created_at",)
