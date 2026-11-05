"""GitHub app Release model admin."""

from django.contrib import admin

from apps.github.models.release import Release


class ReleaseAdmin(admin.ModelAdmin):
    """Admin for Release model."""

    autocomplete_fields = (
        "author",
        "repository",
    )
    search_fields = (
        "node_id",
        "repository__name",
    )


admin.site.register(Release, ReleaseAdmin)
