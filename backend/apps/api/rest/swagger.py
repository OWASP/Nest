"""Custom Swagger UI renderer with theme support for OWASP Nest."""

from django.shortcuts import render
from ninja.openapi.docs import Swagger


class ThemedSwagger(Swagger):
    """Custom Swagger renderer with OWASP Nest theme support."""

    def render_page(self, request, api, template_name=None):
        """Render the Swagger UI page with custom theme support."""
        # Get the current path and replace /docs with /openapi.json
        current_path = request.path.rstrip("/")
        if current_path.endswith("/docs"):
            openapi_path = current_path[:-5] + "/openapi.json"
        else:
            # Fallback: construct from base path
            openapi_path = current_path.rsplit("/", 1)[0] + "/openapi.json"

        context = {
            "title": api.title,
            "description": api.description or "API Documentation",
            "swagger_url": request.build_absolute_uri(openapi_path),
            "persist_authorization": self.settings.get("persistAuthorization", True),
        }

        return render(
            request,
            template_name or "ninja/swagger.html",
            context,
        )
