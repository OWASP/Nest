"""Repository app admin."""

from django.contrib import admin

from apps.github.models import Organization, Release, Repository, User


class RepositoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "stars_count",
        "forks_count",
        "commits_count",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "has_funding_yml",
        "is_funding_policy_compliant",
        "is_empty",
        "is_owasp_site_repository",
    )
    search_fields = ("name",)


admin.site.register(Organization)
admin.site.register(Release)
admin.site.register(Repository, RepositoryAdmin)
admin.site.register(User)
