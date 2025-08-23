"""Chapter admin configuration."""

from django.contrib import admin

from apps.owasp.models.chapter import Chapter

from .mixins import EntityMemberInline, GenericEntityAdminMixin


class ChapterAdmin(admin.ModelAdmin, GenericEntityAdminMixin):
    """Admin for Chapter model."""

    autocomplete_fields = ("owasp_repository",)
    inlines = (EntityMemberInline,)
    list_display = (
        "name",
        "created_at",
        "updated_at",
        "region",
        "custom_field_owasp_url",
        "custom_field_github_urls",
    )
    list_filter = (
        "is_active",
        "is_leaders_policy_compliant",
        "country",
        "region",
    )
    search_fields = (
        "name",
        "key",
    )


admin.site.register(Chapter, ChapterAdmin)
