from django.contrib import admin

from apps.owasp.models.committee import Committee

from .mixins import GenericEntityAdminMixin, LeaderAdminMixin


class CommitteeAdmin(admin.ModelAdmin, GenericEntityAdminMixin, LeaderAdminMixin):
    """Admin for Committee model."""

    autocomplete_fields = (
        "leaders",
        "owasp_repository",
    )
    filter_horizontal = LeaderAdminMixin.filter_horizontal
    search_fields = ("name",)


admin.site.register(Committee, CommitteeAdmin)
