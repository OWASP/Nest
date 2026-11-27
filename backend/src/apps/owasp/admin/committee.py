"""Committee admin configuration."""

from django.contrib import admin

from apps.owasp.admin.mixins import (
    EntityChannelInline,
    EntityMemberInline,
    GenericEntityAdminMixin,
)
from apps.owasp.models.committee import Committee


class CommitteeAdmin(admin.ModelAdmin, GenericEntityAdminMixin):
    """Admin for Committee model."""

    autocomplete_fields = ("owasp_repository",)
    exclude = (
        "leaders",
        "suggested_leaders",
    )
    inlines = (EntityMemberInline, EntityChannelInline)
    search_fields = ("name",)


admin.site.register(Committee, CommitteeAdmin)
