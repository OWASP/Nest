"""Unit tests for Slack views."""

from unittest.mock import MagicMock, patch

import pytest
from django.http import HttpResponse
from django.test import RequestFactory

with (
    patch("apps.slack.apps.SlackConfig.app") as mock_app,
    patch("slack_bolt.adapter.django.SlackRequestHandler") as MockSlackRequestHandler,
):
    mock_handler = MagicMock()
    mock_handler.handle.return_value = HttpResponse(status=200)
    MockSlackRequestHandler.return_value = mock_handler
    from apps.slack.views import slack_handler, slack_request_handler

slack_events_endpoint = "/slack/events"


class TestSlackViews:
    """Test suite for Slack views."""

    @pytest.fixture
    def request_factory(self):
        """Request factory fixture."""
        return RequestFactory()

    def test_slack_handler_exists(self):
        """Test that slack_handler is initialized correctly."""
        assert slack_handler is not None

    def test_slack_request_handler_is_csrf_exempt(self):
        """Test that the slack_request_handler is csrf_exempt."""
        assert getattr(slack_request_handler, "csrf_exempt", False) is True

    def test_slack_request_handler_calls_handler(self, request_factory):
        """Test that slack_request_handler calls the handler correctly."""
        with patch("apps.slack.views.slack_handler") as mocked_handler:
            mocked_handler.handle.return_value = HttpResponse(status=200)
            request = request_factory.post(
                slack_events_endpoint, data="{}", content_type="application/json"
            )
            response = slack_request_handler(request)
            mocked_handler.handle.assert_called_once_with(request)
            assert response == mocked_handler.handle.return_value

    def test_slack_request_handler_with_different_request_types(self, request_factory):
        """Test slack_request_handler with different HTTP methods."""
        with patch("apps.slack.views.slack_handler") as mocked_handler:
            mocked_handler.handle.return_value = HttpResponse(status=200)
            get_request = request_factory.get(slack_events_endpoint)
            slack_request_handler(get_request)
            mocked_handler.handle.assert_called_with(get_request)
            mocked_handler.handle.reset_mock()
            put_request = request_factory.put(
                slack_events_endpoint, data="{}", content_type="application/json"
            )
            slack_request_handler(put_request)
            mocked_handler.handle.assert_called_with(put_request)
