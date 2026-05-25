"""Django admin configuration for Certificate model."""

from django.contrib import admin

from apps.recognition.models.certificate import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    """Admin for Certificate model."""

    autocomplete_fields = ("github_user",)
    list_display = ("id", "github_user", "tier", "score_at_issue", "issued_at", "is_revoked")
    list_filter = ("tier", "is_revoked", "issued_at")
    search_fields = ("github_user__login", "github_user__name", "id")
    readonly_fields = ("id", "issued_at", "nest_created_at", "nest_updated_at")

    fieldsets = (
        (
            "Certificate Information",
            {
                "fields": ("id", "github_user", "tier", "score_at_issue", "issued_at"),
            },
        ),
        (
            "Status",
            {
                "fields": ("is_revoked",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("nest_created_at", "nest_updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
