"""Django admin configuration for Certificate model."""

from django.contrib import admin

from apps.owasp.models.crp.certificate import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    """Admin for Certificate model."""

    autocomplete_fields = ("chapter", "issuer", "project", "recipient")
    list_display = (
        "chapter",
        "id",
        "is_revoked",
        "issued_at",
        "issuer",
        "project",
        "recipient",
        "score",
        "tier",
        "title",
    )
    list_filter = ("is_revoked", "issued_at", "tier")
    list_display_links = ("id",)
    search_fields = (
        "chapter__key",
        "chapter__name",
        "id",
        "issuer__login",
        "issuer__name",
        "project__key",
        "project__name",
        "recipient__login",
        "recipient__name",
        "title",
    )
    readonly_fields = ("id", "issued_at", "nest_created_at", "nest_updated_at")

    fieldsets = (
        (
            "Certificate Information",
            {
                "fields": (
                    "chapter",
                    "id",
                    "issued_at",
                    "issuer",
                    "message",
                    "project",
                    "recipient",
                    "score",
                    "tier",
                    "title",
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
