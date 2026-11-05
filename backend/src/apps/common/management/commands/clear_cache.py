"""A command to clear OWASP Nest cached data."""

from django.core.cache import cache
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Clear OWASP Nest cached data."

    def handle(self, *_args, **options) -> None:
        """Clear data from cache."""
        cache.clear()
