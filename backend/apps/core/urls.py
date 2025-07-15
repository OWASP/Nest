"""URL configuration for sitemap endpoints in the core app."""

from django.urls import path

from .sitemaps import (
    ChapterSitemap,
    CommitteeSitemap,
    ProjectSitemap,
    StaticSitemap,
    UserSitemap,
    cached_sitemap_view,
)

sitemaps = {
    "static": StaticSitemap,
    "projects": ProjectSitemap,
    "chapters": ChapterSitemap,
    "committees": CommitteeSitemap,
    "users": UserSitemap,
}

urlpatterns = [
    path("sitemap.xml", cached_sitemap_view(sitemaps=sitemaps), name="sitemap-index"),
    path(
        "sitemap/static.xml",
        cached_sitemap_view(sitemaps={"static": StaticSitemap}),
        name="sitemap-static",
    ),
    path(
        "sitemap/projects.xml",
        cached_sitemap_view(sitemaps={"projects": ProjectSitemap}),
        name="sitemap-projects",
    ),
    path(
        "sitemap/chapters.xml",
        cached_sitemap_view(sitemaps={"chapters": ChapterSitemap}),
        name="sitemap-chapters",
    ),
    path(
        "sitemap/committees.xml",
        cached_sitemap_view(sitemaps={"committees": CommitteeSitemap}),
        name="sitemap-committees",
    ),
    path(
        "sitemap/users.xml",
        cached_sitemap_view(sitemaps={"users": UserSitemap}),
        name="sitemap-users",
    ),
]
