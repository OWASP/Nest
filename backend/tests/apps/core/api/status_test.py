import json

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse
from requests.status_codes import codes


class TestStatusEndpoint:
    """Test suite for the status endpoint."""

    @pytest.fixture(autouse=True)
    def setup_client(self):
        self.client = Client()
        self.url = reverse("get_status")

    def test_status_endpoint_valid_request(self):
        """Test a valid GET request to the status endpoint."""
        response = self.client.get(self.url)

        assert response.status_code == codes.ok
        response_data = json.loads(response.content)

        assert response_data == {"version": settings.RELEASE_VERSION}

    @pytest.mark.parametrize("invalid_method", ["post", "put", "delete", "patch"])
    def test_status_endpoint_invalid_method(self, invalid_method):
        """Test that methods other than GET are not allowed."""
        response = getattr(self.client, invalid_method)(self.url)

        assert response.status_code == codes.not_allowed
