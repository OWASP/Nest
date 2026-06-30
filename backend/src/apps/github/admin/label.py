"""GitHub app Label model admin."""

from django.contrib import admin

from apps.github.models.label import Label


class LabelAdmin(admin.ModelAdmin):
    """Admin for Label model."""

    search_fields = ("name", "description")


admin.site.register(Label, LabelAdmin)
