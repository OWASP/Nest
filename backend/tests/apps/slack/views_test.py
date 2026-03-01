from django.test import RequestFactory


class TestViews:
    """Tests for the Slack views."""

    def test_slack_request_handler_works(self, mocker):
        """Tests that the view correctly calls the SlackRequestHandler."""
        mock_slack_request_handler = mocker.patch("slack_bolt.adapter.django.SlackRequestHandler")

        mock_handler_instance = mock_slack_request_handler.return_value
        mock_handler_instance.handle.return_value = "mock_http_response"

        from apps.slack.views import slack_request_handler  # noqa: PLC0415

        request = RequestFactory().post("/slack/events/")
        response = slack_request_handler(request)

        mock_handler_instance.handle.assert_called_once_with(request)
        assert response == "mock_http_response"
