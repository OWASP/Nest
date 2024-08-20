"""Repository app admin."""

from django.contrib import admin

from apps.github.models import Organization, Repository, User

admin.site.register(Organization)
admin.site.register(Repository)
admin.site.register(User)
