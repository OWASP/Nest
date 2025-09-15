"""Committee admin configuration."""

from django.contrib import admin

from apps.owasp.models.committee import Committee

from .mixins import EntityMemberInline, GenericEntityAdminMixin


class CommitteeAdmin(admin.ModelAdmin, GenericEntityAdminMixin):
    """Admin for Committee model."""

    autocomplete_fields = ("owasp_repository",)
    exclude = (
        "leaders",
        "suggested_leaders",
    )
    inlines = (EntityMemberInline,)
    search_fields = ("name",)


admin.site.register(Committee, CommitteeAdmin)
