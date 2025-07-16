"""URL configuration for sitemap endpoints in the sitemaps app."""

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
    "chapters": ChapterSitemap,
    "committees": CommitteeSitemap,
    "projects": ProjectSitemap,
    "static": StaticSitemap,
    "users": UserSitemap,
}

urlpatterns = [
    path(
        "sitemap.xml",
        cached_sitemap_view(sitemaps=sitemaps),
        name="sitemap-index",
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
        "sitemap/projects.xml",
        cached_sitemap_view(sitemaps={"projects": ProjectSitemap}),
        name="sitemap-projects",
    ),
    path(
        "sitemap/static.xml",
        cached_sitemap_view(sitemaps={"static": StaticSitemap}),
        name="sitemap-static",
    ),
    path(
        "sitemap/users.xml",
        cached_sitemap_view(sitemaps={"users": UserSitemap}),
        name="sitemap-users",
    ),
]
