import csv
from datetime import datetime, timezone
from io import StringIO
from unittest.mock import Mock, patch

import botocore
import pytest
from django.conf import settings
from rest_framework import status

from apps.feedback.api.feedback import FeedbackViewSet


@pytest.fixture()
def feedback_viewset():
    return FeedbackViewSet()


@pytest.fixture()
def valid_feedback_data():
    return {
        "name": "John Doe",
        "email": "john@example.com",
        "message": "Test feedback",
        "is_anonymous": False,
        "is_nestbot": False,
    }


@pytest.fixture()
def mock_s3_client():
    with patch("boto3.client") as mock_client:
        mock_client.return_value.exceptions.NoSuchKey = botocore.exceptions.ClientError(
            {"Error": {"Code": "NoSuchKey", "Message": "The specified key does not exist."}},
            "GetObject",
        )
        yield mock_client.return_value


class TestFeedbackViewSet:
    def test_create_success(self, feedback_viewset, valid_feedback_data, mock_s3_client):
        """Test successful feedback submission."""
        request = Mock()
        request.data = valid_feedback_data

        mock_s3_client.get_object.return_value = {"Body": Mock(read=lambda: b"")}

        response = feedback_viewset.create(request)

        assert response.status_code == status.HTTP_201_CREATED

        mock_s3_client.put_object.assert_called_once()
        put_call_kwargs = mock_s3_client.put_object.call_args[1]
        assert put_call_kwargs["Bucket"] == settings.AWS_STORAGE_BUCKET_NAME
        assert put_call_kwargs["Key"] == "feedbacks.tsv"
        assert "Body" in put_call_kwargs
        assert put_call_kwargs["ContentType"] == "text/tab-separated-values"

    def test_create_validation_error(self, feedback_viewset, valid_feedback_data, mock_s3_client):
        """Test feedback submission with validation error."""
        request = Mock()
        request.data = valid_feedback_data

        mock_s3_client.get_object.side_effect = botocore.exceptions.ClientError(
            {"Error": {"Code": "ValidationError", "Message": "Invalid credentials"}}, "GetObject"
        )

        response = feedback_viewset.create(request)

        assert response.status_code == status.HTTP_201_CREATED

    def test_write_feedback_to_tsv(self, feedback_viewset, valid_feedback_data):
        """Test writing feedback data to TSV format."""
        output = StringIO()
        writer = csv.writer(output, delimiter="\t")

        current_time = datetime(2025, 1, 22, 10, 45, 34, 567884, tzinfo=timezone.utc)
        with patch("django.utils.timezone.now", return_value=current_time):
            feedback_viewset.write_feedback_to_tsv(writer, valid_feedback_data)

        output.seek(0)
        written_data = output.getvalue().strip().split("\t")
        assert written_data[0] == valid_feedback_data["name"]
        assert written_data[1] == valid_feedback_data["email"]
        assert written_data[2] == valid_feedback_data["message"]
        assert written_data[3] == str(valid_feedback_data["is_anonymous"])
        assert written_data[4] == str(valid_feedback_data["is_nestbot"])

    @patch("boto3.client")
    def test_get_s3_client(self, mock_boto3, feedback_viewset):
        """Test S3 client initialization."""
        feedback_viewset.get_s3_client()

        mock_boto3.assert_called_once_with(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
