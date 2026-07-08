"""GitHub app Organization model admin."""

from django.contrib import admin

from apps.github.models.organization import Organization


class OrganizationAdmin(admin.ModelAdmin):
    """Admin for Organization model."""

    list_display = (
        "title",
        "created_at",
        "updated_at",
        "followers_count",
    )
    list_filter = ("is_owasp_related_organization",)
    search_fields = (
        "login",
        "name",
    )


admin.site.register(Organization, OrganizationAdmin)
