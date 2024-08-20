"""Repository app admin."""

from django.contrib import admin

from apps.github.models import Repository

admin.site.register(Repository)
