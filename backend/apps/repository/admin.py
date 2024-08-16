"""Repository app admin."""

from django.contrib import admin

from apps.repository.models import Repository

admin.site.register(Repository)
