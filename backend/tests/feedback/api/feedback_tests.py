import json
from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class FeedbackViewSetTests(APITestCase):
    def setUp(self):
        self.url = reverse("feedback-list")
        self.valid_payload = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "message": "This is a feedback message.",
            "is_anonymous": False,
            "is_nestbot": False,
        }
        self.invalid_payload = {
            "name": "",
            "email": "invalid-email",
            "message": "",
            "is_anonymous": False,
            "is_nestbot": False,
        }

    @patch("apps.feedback.api.feedback.FeedbackViewSet._get_s3_client")
    def test_create_feedback_valid_payload(self, mock_get_s3_client):
        mock_s3_client = mock_get_s3_client.return_value
        mock_s3_client.get_object.side_effect = mock_s3_client.exceptions.NoSuchKey

        response = self.client.post(
            self.url, data=json.dumps(self.valid_payload), content_type="application/json"
        )

        assert response.status_code == status.HTTP_201_CREATED
        mock_get_s3_client.assert_called_once()
        mock_s3_client.put_object.assert_called_once()

    @patch("apps.feedback.api.feedback.FeedbackViewSet._get_s3_client")
    def test_create_feedback_invalid_payload(self, mock_get_s3_client):
        response = self.client.post(
            self.url, data=json.dumps(self.invalid_payload), content_type="application/json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        mock_get_s3_client.assert_not_called()

    @patch("apps.feedback.api.feedback.FeedbackViewSet._get_s3_client")
    def test_create_feedback_anonymous(self, mock_get_s3_client):
        payload = self.valid_payload.copy()
        payload["is_anonymous"] = True
        payload["email"] = ""

        mock_s3_client = mock_get_s3_client.return_value
        mock_s3_client.get_object.side_effect = mock_s3_client.exceptions.NoSuchKey

        response = self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json"
        )

        assert response.status_code == status.HTTP_201_CREATED
        mock_get_s3_client.assert_called_once()
        mock_s3_client.put_object.assert_called_once()
