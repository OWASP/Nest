from unittest.mock import MagicMock, patch

import pytest
from django.test import RequestFactory

from apps.slack.views import slack_request_handler

success_status_code = 200
server_request_code = 500
bad_request_code = 400


@pytest.fixture()
def factory():
    """Fixture for Django's RequestFactory."""
    return RequestFactory()


@patch("apps.slack.views.slack_handler.handle")
def test_valid_slack_request(mock_handle, factory):
    """Test handling of a valid Slack request."""
    mock_response = MagicMock()
    mock_response.status_code = success_status_code
    mock_response.content = b"Success"
    mock_handle.return_value = mock_response

    request = factory.post("/slack/events", {"key": "value"}, content_type="application/json")

    response = slack_request_handler(request)

    assert response.status_code == success_status_code
    assert response.content == b"Success"
    mock_handle.assert_called_once_with(request)


@patch("apps.slack.views.slack_handler.handle")
def test_invalid_slack_request(mock_handle, factory):
    """Test handling of an invalid Slack request."""
    mock_handle.side_effect = Exception("Invalid Request")

    request = factory.post("/slack/events", {"key": "value"}, content_type="application/json")

    response = slack_request_handler(request)

    assert response.status_code == server_request_code
    mock_handle.assert_called_once_with(request)


@patch("apps.slack.views.slack_handler.handle")
def test_empty_request_body(mock_handle, factory):
    """Test handling of a request with an empty body."""
    mock_response = MagicMock()
    mock_response.status_code = bad_request_code
    mock_response.content = b"Bad Request"
    mock_handle.return_value = mock_response

    request = factory.post("/slack/events", {}, content_type="application/json")

    response = slack_request_handler(request)

    assert response.status_code == bad_request_code
    assert response.content == b"Bad Request"
    mock_handle.assert_called_once_with(request)
