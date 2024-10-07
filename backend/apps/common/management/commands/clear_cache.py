"""A command to clear cached data."""

from django.core.cache import cache
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Clear cached data."

    def handle(self, *_args, **options):
        cache.clear()
