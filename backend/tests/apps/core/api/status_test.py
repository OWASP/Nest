import json
from http import HTTPStatus
from unittest.mock import patch

import pytest
from django.test import RequestFactory

from apps.core.api.status import status_view


class TestStatusView:
    @pytest.fixture(autouse=True)
    def setup_client(self):
        self.factory = RequestFactory()

    def test_status_view_success(self):
        """Test status view returns successful response."""
        request = self.factory.get("/status/")
        
        with patch("django.conf.settings.RELEASE_VERSION", "1.0.0"):
            response = status_view(request)

        assert response.status_code == HTTPStatus.OK
        assert response["Content-Type"] == "application/json"
        
        data = json.loads(response.content)
        assert data["status"] == "ok"
        assert data["version"] == "1.0.0"

    def test_status_view_no_version(self):
        """Test status view when no version is configured."""
        request = self.factory.get("/status/")
        
        response = status_view(request)

        assert response.status_code == HTTPStatus.OK
        assert response["Content-Type"] == "application/json"
        
        data = json.loads(response.content)
        assert data["status"] == "ok"
        assert "version" in data  # Just check version key exists

    def test_status_view_response_structure(self):
        """Test the response structure is correct."""
        request = self.factory.get("/status/")
        
        response = status_view(request)
        data = json.loads(response.content)
        
        assert isinstance(data, dict)
        assert len(data) == 2
        assert "status" in data
        assert "version" in data
