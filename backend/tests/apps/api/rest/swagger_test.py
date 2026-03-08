"""Tests for custom Swagger UI renderer with theme support."""

from unittest.mock import MagicMock, Mock, patch

import pytest
from django.test import RequestFactory

from apps.api.rest.swagger import ThemedSwagger


class TestThemedSwagger:
    """Test cases for ThemedSwagger class."""

    @pytest.fixture
    def themed_swagger(self):
        """Pytest fixture to provide an instance of ThemedSwagger."""
        return ThemedSwagger(settings={"persistAuthorization": True})

    @pytest.fixture
    def mock_api(self):
        """Pytest fixture to provide a mock NinjaAPI instance."""
        api = Mock()
        api.title = "OWASP Nest"
        api.description = "Open Worldwide Application Security Project API"
        api.urls_namespace = "/api/v0/"
        return api

    @pytest.fixture
    def request_factory(self):
        """Pytest fixture to provide a Django RequestFactory."""
        return RequestFactory()

    def test_themed_swagger_initialization(self, themed_swagger):
        """Test that ThemedSwagger initializes with correct settings."""
        assert themed_swagger.settings.get("persistAuthorization") is True

    def test_render_page_default_template(
        self, themed_swagger, mock_api, request_factory
    ):
        """Test render_page with default template."""
        request = request_factory.get("/api/v0/docs")

        with patch("apps.api.rest.swagger.render") as mock_render:
            mock_render.return_value = MagicMock()
            themed_swagger.render_page(request, mock_api)

            # Verify render was called once
            assert mock_render.call_count == 1

            # Get the call arguments
            call_args = mock_render.call_args
            assert call_args[0][0] == request
            assert call_args[0][1] == "ninja/swagger.html"

            # Verify context contains required keys
            context = call_args[0][2]
            assert "title" in context
            assert "description" in context
            assert "swagger_url" in context
            assert "persist_authorization" in context
            assert context["title"] == "OWASP Nest"
            assert (
                context["description"]
                == "Open Worldwide Application Security Project API"
            )
            assert context["persist_authorization"] is True

    def test_render_page_custom_template(
        self, themed_swagger, mock_api, request_factory
    ):
        """Test render_page with custom template."""
        request = request_factory.get("/api/v0/docs")

        with patch("apps.api.rest.swagger.render") as mock_render:
            mock_render.return_value = MagicMock()
            themed_swagger.render_page(
                request, mock_api, template_name="custom/swagger.html"
            )

            # Verify custom template was used
            call_args = mock_render.call_args
            assert call_args[0][1] == "custom/swagger.html"

    def test_render_page_missing_description(
        self, themed_swagger, mock_api, request_factory
    ):
        """Test render_page when API description is None."""
        request = request_factory.get("/api/v0/docs")
        mock_api.description = None

        with patch("apps.api.rest.swagger.render") as mock_render:
            mock_render.return_value = MagicMock()
            themed_swagger.render_page(request, mock_api)

            # Verify default description is used
            context = mock_render.call_args[0][2]
            assert context["description"] == "API Documentation"

    def test_render_page_builds_correct_url(
        self, themed_swagger, mock_api, request_factory
    ):
        """Test that render_page builds correct OpenAPI URL."""
        request = request_factory.get("/api/v0/docs")

        with patch("apps.api.rest.swagger.render") as mock_render:
            mock_render.return_value = MagicMock()
            themed_swagger.render_page(request, mock_api)

            # Verify swagger_url is constructed correctly
            context = mock_render.call_args[0][2]
            assert "/api/v0/openapi.json" in context["swagger_url"]

    def test_render_page_persist_authorization_false(self, mock_api, request_factory):
        """Test render_page when persistAuthorization is False."""
        themed_swagger = ThemedSwagger(settings={"persistAuthorization": False})
        request = request_factory.get("/api/v0/docs")

        with patch("apps.api.rest.swagger.render") as mock_render:
            mock_render.return_value = MagicMock()
            themed_swagger.render_page(request, mock_api)

            # Verify persistAuthorization is False in context
            context = mock_render.call_args[0][2]
            assert context["persist_authorization"] is False

    def test_render_page_no_persist_authorization_setting(
        self, mock_api, request_factory
    ):
        """Test render_page when persistAuthorization setting is not provided."""
        themed_swagger = ThemedSwagger(settings={})
        request = request_factory.get("/api/v0/docs")

        with patch("apps.api.rest.swagger.render") as mock_render:
            mock_render.return_value = MagicMock()
            themed_swagger.render_page(request, mock_api)

            # Verify persistAuthorization defaults to True
            context = mock_render.call_args[0][2]
            assert context["persist_authorization"] is True
