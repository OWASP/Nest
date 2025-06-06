import json
from unittest.mock import Mock

import pytest
import requests
from django.conf import settings

from apps.core.api.status import status_view


class TestStatusEndpoint:
    """
    Test suite for the status endpoint.
    """

    def test_status_endpoint_valid_request(self):
        """
        Test a valid GET request to the status endpoint.
        """
        mock_request = Mock()
        mock_request.method = "GET"
        expected_version = settings.RELEASE_VERSION
        expected_result = {"version": expected_version}

        response = status_view(mock_request)
        response_data = json.loads(response.content)

        assert response.status_code == requests.codes.ok
        assert response_data == expected_result

    @pytest.mark.parametrize("invalid_method", ["POST", "PUT", "DELETE", "PATCH"])
    def test_status_endpoint_invalid_method(self, invalid_method):
        """
        Test that methods other than GET are not allowed.
        """
        mock_request = Mock()
        mock_request.method = invalid_method

        response = status_view(mock_request)
        response_data = json.loads(response.content)

        assert response.status_code == requests.codes.method_not_allowed
        assert response_data["error"] == f"Method {invalid_method} is not allowed"