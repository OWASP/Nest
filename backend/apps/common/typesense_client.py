"""Typesense client configuration and schema definition."""

import typesense
from django.conf import settings


class Typesense:
    """Typesense client."""

    @staticmethod
    def get_client():
        """Return an instance of typesense client."""
        return typesense.Client(
            {
                "api_key": settings.TYPESENSE_API_KEY,
                "nodes": [
                    {
                        "host": settings.TYPESENSE_HOST,
                        "port": settings.TYPESENSE_PORT,
                        "protocol": "http",
                    }
                ],
                "connection_timeout_seconds": 5,
            }
        )
