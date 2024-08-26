"""Repository app admin."""

from django.contrib import admin

from apps.github.models import Organization, Release, Repository, User


class RepositoryAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        "organization",
        "owner",
    )
    list_display = (
        "title",
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
        "is_owasp_repository",
        "is_owasp_site_repository",
    )
    search_fields = ("name",)


class OrganizationAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "followers_count",
        "created_at",
        "updated_at",
    )
    search_fields = ("name",)


class ReleaseAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        "author",
        "repository",
    )
    search_fields = ("node_id", "repository__name")


class UserAdmin(admin.ModelAdmin):
    search_fields = ("name",)


admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Release, ReleaseAdmin)
admin.site.register(Repository, RepositoryAdmin)
admin.site.register(User, UserAdmin)
