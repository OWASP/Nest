from django.contrib import admin

from apps.owasp.models.chapter import Chapter

from .mixins import GenericEntityAdminMixin, LeaderAdminMixin


class ChapterAdmin(admin.ModelAdmin, GenericEntityAdminMixin, LeaderAdminMixin):
    """Admin for Chapter model."""

    autocomplete_fields = ("owasp_repository",)
    filter_horizontal = LeaderAdminMixin.filter_horizontal
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
    search_fields = ("name", "key")


admin.site.register(Chapter, ChapterAdmin)
