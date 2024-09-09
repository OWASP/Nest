"""OWASP Nest URL configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from apps.github.api.urls import router as github_router
from apps.owasp.api import search_project
from apps.owasp.api.urls import router as owasp_router
from apps.owasp.views import home_page, search_issues

router = routers.DefaultRouter()
router.registry.extend(github_router.registry)
router.registry.extend(owasp_router.registry)

urlpatterns = [
    path("api/v1/", include(router.urls)),
    path("api/v1/search/", search_project),
    path("projects/contribute", search_issues),
    path("", home_page),
    path("a/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
