"""Django admin configuration for Certificate model."""

from django.contrib import admin

from apps.owasp.models.crp.certificate import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    """Admin for Certificate model."""

    autocomplete_fields = ("recipient", "issuer", "project", "chapter")
    list_display = (
        "id",
        "recipient",
        "title",
        "project",
        "chapter",
        "issuer",
        "tier",
        "score",
        "issued_at",
        "is_revoked",
    )
    list_filter = ("tier", "is_revoked", "issued_at")
    search_fields = (
        "recipient__login",
        "recipient__name",
        "issuer__login",
        "title",
        "id",
    )
    readonly_fields = ("id", "issued_at", "nest_created_at", "nest_updated_at")

    fieldsets = (
        (
            "Certificate Information",
            {
                "fields": (
                    "id",
                    "recipient",
                    "issuer",
                    "title",
                    "message",
                    "project",
                    "chapter",
                    "tier",
                    "score",
                    "issued_at",
                ),
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
