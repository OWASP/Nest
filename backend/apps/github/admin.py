"""Repository app admin."""

from django.contrib import admin

from apps.github.models import Organization, Release, Repository, User


class RepositoryAdmin(admin.ModelAdmin):
    list_filter = ("has_funding_yml", "is_funding_policy_compliant")


admin.site.register(Organization)
admin.site.register(Release)
admin.site.register(Repository, RepositoryAdmin)
admin.site.register(User)
