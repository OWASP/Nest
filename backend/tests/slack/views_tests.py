from django.test import TestCase, RequestFactory
from unittest.mock import patch, MagicMock
from apps.slack.views import slack_request_handler

from slack_bolt.adapter.django import SlackRequestHandler
from apps.slack.apps import SlackConfig


class SlackRequestHandlerTests(TestCase):
    def setUp(self):
        # Set up a request factory for simulating HTTP requests
        self.factory = RequestFactory()

    @patch("slack.views.slack_handler")
    def test_slack_request_handler_valid_request(self, mock_slack_handler):
        """Test slack_request_handler with a valid request."""
        # Mock Slack handler's response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"OK"
        mock_slack_handler.handle.return_value = mock_response

        # Create a mock request
        request = self.factory.post("/slack/events/", {"type": "event_callback"})

        # Call the slack_request_handler function
        response = slack_request_handler(request)

        # Assert that the Slack handler was called
        mock_slack_handler.handle.assert_called_once_with(request)

        # Assert the response matches the mock response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")

    @patch("slack.views.slack_handler")
    def test_slack_request_handler_invalid_request(self, mock_slack_handler):
        """Test slack_request_handler with an invalid request."""
        # Mock Slack handler's response for invalid input
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.content = b"Bad Request"
        mock_slack_handler.handle.return_value = mock_response

        # Create a mock invalid request
        request = self.factory.post("/slack/events/", {"invalid": "data"})

        # Call the slack_request_handler function
        response = slack_request_handler(request)

        # Assert that the Slack handler was called
        mock_slack_handler.handle.assert_called_once_with(request)

        # Assert the response matches the mock response
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b"Bad Request")

    @patch("slack.views.slack_handler")
    def test_slack_request_handler_exception_handling(self, mock_slack_handler):
        """Test slack_request_handler when an exception occurs."""
        # Simulate an exception being raised by the handler
        mock_slack_handler.handle.side_effect = Exception("Something went wrong")

        # Create a mock request
        request = self.factory.post("/slack/events/", {"type": "event_callback"})

        # Call the slack_request_handler function
        with self.assertRaises(Exception) as context:
            slack_request_handler(request)

        # Assert that the exception message is correct
        self.assertEqual(str(context.exception), "Something went wrong")
