"""Handle feedback submission, saving to local DB and uploading to S3."""

import csv
import logging
from datetime import datetime, timezone
from io import StringIO

import boto3
from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],  # Ensures logs go to stdout/stderr
)
logger = logging.getLogger(__name__)


class FeedbackViewSet(viewsets.ModelViewSet):
    """ViewSet for handling feedback."""

    permission_classes = [AllowAny]

    def create(self, request):
        """Handle POST request for feedback submission."""
        logger.info("Processing new feedback submission")
        try:
            feedback_data = request.data
            logger.debug("Received feedback data: %s", feedback_data)

            # Initialize S3 client
            s3_client = self._get_s3_client()

            # Get or create the TSV file
            output, writer = self._get_or_create_tsv(s3_client)

            # Write new feedback data
            self._write_feedback_to_tsv(writer, feedback_data)

            # Upload the updated TSV file back to S3
            self._upload_tsv_to_s3(s3_client, output)

            logger.info("Feedback successfully saved to %s", "feedbacks.tsv")

            return Response(status=status.HTTP_201_CREATED)
        except Exception:
            logger.exception("Error processing feedback submission: %s")
            return Response(
                {"error": "An error occurred while processing feedback"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _get_s3_client(self):
        """Initialize and returns the S3 client."""
        logger.debug("Initializing S3 client")
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
            logger.debug("Attempting to read existing TSV file: %s", tsv_key)
            response = s3_client.get_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=tsv_key,
            )
            existing_content = response["Body"].read().decode("utf-8")
            output = StringIO(existing_content)
            logger.debug("Successfully read existing TSV file")
        except s3_client.exceptions.NoSuchKey:
            logger.info("No existing TSV file found, creating a new one")
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
        logger.debug("New feedback data written to TSV")

    def _upload_tsv_to_s3(self, s3_client, output):
        """Upload the updated TSV file back to S3."""
        s3_client.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key="feedbacks.tsv",
            Body=output.getvalue(),
            ContentType="text/tab-separated-values",
        )
        logger.debug("TSV file uploaded to S3 successfully")
