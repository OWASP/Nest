"""Feedback API endpoint for handling feedback submissions."""

import csv
import logging
from io import StringIO

import boto3
from django.conf import settings
from rest_framework import serializers, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.owasp.models.feedback import Feedback

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # This ensures logs go to stdout/stderr
    ],
)
logger = logging.getLogger(__name__)


class FeedbackSerializer(serializers.ModelSerializer):
    """Serializer for Feedback model."""

    class Meta:
        model = Feedback
        fields = "__all__"


class FeedbackViewSet(viewsets.ModelViewSet):
    """ViewSet for handling feedback."""

    permission_classes = [AllowAny]
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    def post(self, request):
        """Handle POST request for feedback submission."""
        logger.info("Processing new feedback submission")
        serializer = FeedbackSerializer(data=request.data)

        if serializer.is_valid():
            try:
                # Initialize S3 client
                logger.debug("Initializing S3 client")
                s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_S3_REGION_NAME,
                )

                logger.debug("Received feedback data: %s", serializer.validated_data)
                logger.info(
                    "AWS Configuration - Bucket: %s, Region: %s",
                    settings.AWS_STORAGE_BUCKET_NAME,
                    settings.AWS_S3_REGION_NAME,
                )

                # Try to get existing file
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
                    logger.info("No existing TSV file found, creating new one")
                    output = StringIO()
                    writer = csv.writer(output, delimiter="\t")
                    writer.writerow(
                        ["Name", "Email", "Message", "isAnonymous", "isNestbot", "created_at"]
                    )
                else:
                    writer = csv.writer(output, delimiter="\t")

                # Write new feedback to the TSV file
                writer.writerow(
                    [
                        serializer.validated_data["name"],
                        serializer.validated_data["email"],
                        serializer.validated_data["message"],
                        serializer.validated_data["is_anonymous"],
                        serializer.validated_data["is_nestbot"],
                        serializer.validated_data["created_at"],
                    ]
                )

                # Upload the updated TSV file back to S3
                s3_client.put_object(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                    Key=tsv_key,
                    Body=output.getvalue(),
                    ContentType="text/tab-separated-values",
                )
                logger.info("Feedback successfully saved to %s", tsv_key)

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception:
                logger.exception("Error processing feedback submission")
                return Response(
                    {"error": "An error occurred while processing feedback"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            logger.warning("Invalid feedback data received: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
