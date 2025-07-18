"""Sitemap view base class."""

from django.contrib.sitemaps import Sitemap


class BaseSitemap(Sitemap):
    """Base sitemap class."""

    change_frequency = "weekly"
    limit = 50000
    prefix = ""
    protocol = "https"

    STATIC_ROUTES = (
        {"path": "/chapters", "changefreq": "weekly", "priority": 0.8},
        {"path": "/committees", "changefreq": "monthly", "priority": 0.8},
        {"path": "/contribute", "changefreq": "daily", "priority": 0.6},
        {"path": "/members", "changefreq": "daily", "priority": 0.7},
        {"path": "/projects", "changefreq": "weekly", "priority": 0.9},
    )

    def get_static_priority(self, path):
        """Get the priority for a static route based on its path."""
        for route in self.STATIC_ROUTES:
            if route["path"] == path:
                return route["priority"]

        return 0.7  # Fallback priority.

    def changefreq(self, obj):
        """Return the change frequency for an object."""
        return self.change_frequency

    def items(self):
        """Return list of items for sitemap generation."""
        return []

    def lastmod(self, obj):
        """Return the last modification date for an object."""
        return obj.updated_at or obj.created_at

    def location(self, obj):
        """Return the URL path for an object."""
        return f"{self.prefix}/{obj.nest_key}"

    def priority(self, obj):
        """Return the priority score for an object."""
        return self.get_static_priority(self.prefix)
