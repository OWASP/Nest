"""Custom Swagger UI renderer with theme support for OWASP Nest."""

from django.shortcuts import render
from ninja.openapi.docs import Swagger


class ThemedSwagger(Swagger):
    """Custom Swagger renderer with OWASP Nest theme support."""

    def render_page(self, request, api, template_name=None):
        """Render the Swagger UI page with custom theme support."""
        context = {
            "title": api.title,
            "description": api.description or "API Documentation",
            "swagger_url": request.build_absolute_uri(api.urls_namespace + "openapi.json"),
            "persist_authorization": self.settings.get("persistAuthorization", True),
        }

        return render(
            request,
            template_name or "ninja/swagger.html",
            context,
        )
