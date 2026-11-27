"""Tests for Status API."""

import json
from http import HTTPStatus
from unittest.mock import patch

import pytest
from django.conf import settings
from django.test import RequestFactory

from apps.core.api.internal.status import get_status


class TestGetStatusFunction:
    """Tests for the get_status API function."""

    @pytest.fixture(autouse=True)
    def setup_client(self):
        """Set up Django RequestFactory for tests."""
        self.factory = RequestFactory()

    def test_get_status_with_release_version(self):
        """Test get_status function when RELEASE_VERSION is set."""
        with patch.object(settings, "RELEASE_VERSION", "1.2.3"):
            response = get_status(self.factory.get("/"))

        assert response.status_code == HTTPStatus.OK
        data = json.loads(response.content)
        assert data["version"] == "1.2.3"

    def test_get_status_returns_unknown_when_no_version(self):
        """Test get_status function returns env name when RELEASE_VERSION is not set."""
        with (
            patch.object(settings, "ENVIRONMENT", "test"),
            patch.object(settings, "RELEASE_VERSION", None),
        ):
            response = get_status(self.factory.get("/"))

        assert response.status_code == HTTPStatus.OK
        data = json.loads(response.content)
        assert data["version"] == "test"
