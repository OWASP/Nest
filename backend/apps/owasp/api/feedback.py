"""Handle feedback submission, saving to local DB and uploading to S3."""

import csv
from datetime import datetime, timezone
from io import StringIO

import boto3
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


class FeedbackViewSet(viewsets.ModelViewSet):
    """ViewSet for handling feedback."""

    permission_classes = [AllowAny]

    def create(self, request):
        """Handle POST request for feedback submission."""
        try:
            feedback_data = request.data

            # Initialize S3 client
            s3_client = self._get_s3_client()

            # Get or create the TSV file
            output, writer = self._get_or_create_tsv(s3_client)

            # Write new feedback data
            self._write_feedback_to_tsv(writer, feedback_data)

            # Upload the updated TSV file back to S3
            self._upload_tsv_to_s3(s3_client, output)

            return Response(status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def _get_s3_client(self):
        """Initialize and returns the S3 client."""
        return boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

    def _get_or_create_tsv(self, s3_client):
        """Get the existing TSV file or creates a new one if it doesn't exist."""
        tsv_key = "feedbacks.tsv"
        try:
            response = s3_client.get_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=tsv_key,
            )
            existing_content = response["Body"].read().decode("utf-8")
            output = StringIO(existing_content)
        except s3_client.exceptions.NoSuchKey:
            output = StringIO()
            writer = csv.writer(output, delimiter="\t")
            writer.writerow(
                ["Name", "Email", "Message", "is_anonymous", "is_nestbot", "created_at"]
            )
        else:
            writer = csv.writer(output, delimiter="\t")

        return output, writer

    def _write_feedback_to_tsv(self, writer, feedback_data):
        """Write the new feedback data to the TSV file."""
        writer.writerow(
            [
                feedback_data["name"],
                feedback_data["email"],
                feedback_data["message"],
                feedback_data["is_anonymous"],
                feedback_data["is_nestbot"],
                datetime.now(timezone.utc).isoformat(),
            ]
        )

    def _upload_tsv_to_s3(self, s3_client, output):
        """Upload the updated TSV file back to S3."""
        s3_client.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key="feedbacks.tsv",
            Body=output.getvalue(),
            ContentType="text/tab-separated-values",
        )
