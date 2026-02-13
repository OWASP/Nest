"""Image extraction orchestration for Slack messages."""

import io
import logging
from datetime import UTC, datetime, timedelta

import requests
from django_rq import job
from PIL import Image
from requests.exceptions import RequestException

from apps.ai.common.constants import QUEUE_RESPONSE_TIME_MINUTES
from apps.common.open_ai import OpenAi
from apps.slack.models import Message
from apps.slack.services.message_auto_reply import generate_ai_reply_if_unanswered

logger = logging.getLogger(__name__)

MAX_IMAGES_PER_MESSAGE = 3
SUPPORTED_IMAGE_TYPES = ("image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp")
MAX_IMAGE_SIZE_MB = 20

# OpenAI supported formats
OPENAI_SUPPORTED_FORMATS = {"PNG", "JPEG", "GIF", "WEBP"}
# Map PIL formats to MIME types
FORMAT_TO_MIME = {
    "PNG": "image/png",
    "JPEG": "image/jpeg",
    "JPG": "image/jpeg",
    "GIF": "image/gif",
    "WEBP": "image/webp",
}


def is_valid_image_file(file_data: dict) -> bool:
    """Check if file is a valid image for extraction.

    Args:
        file_data: Dictionary containing file metadata from Slack

    Returns:
        True if file is valid for extraction, False otherwise

    """
    mimetype = file_data.get("mimetype", "")
    size_bytes = file_data.get("size", 0)

    if mimetype not in SUPPORTED_IMAGE_TYPES:
        logger.debug("Skipping non-image file: %s", mimetype)
        return False

    size_mb = size_bytes / (1024 * 1024)
    if size_mb > MAX_IMAGE_SIZE_MB:
        logger.warning(
            "Image %s too large: %.2fMB (max: %sMB)",
            file_data.get("id"),
            size_mb,
            MAX_IMAGE_SIZE_MB,
        )
        return False

    return True


def download_slack_image(url: str, bot_token: str) -> bytes | None:
    """Download image from Slack using bot token authentication.

    Args:
        url: Slack file URL (url_private or url_private_download)
        bot_token: Slack bot token for authentication

    Returns:
        Image bytes if successful, None if download fails

    """
    try:
        headers = {"Authorization": f"Bearer {bot_token}"}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except RequestException:
        logger.exception("Failed to download image from %s", url)
        return None
    else:
        return response.content


def validate_and_get_image_format(image_data: bytes) -> str | None:
    """Validate image and return MIME type if supported by OpenAI.

    Args:
        image_data: Raw image bytes

    Returns:
        MIME type string if valid, None if unsupported or invalid

    """
    try:
        img = Image.open(io.BytesIO(image_data))
        img.verify()  # Verify it's actually a valid image

        # Re-open after verify (verify() closes the file)
        img = Image.open(io.BytesIO(image_data))
        image_format = img.format

        if not image_format:
            logger.warning("Could not detect image format from data")
            return None

        # Check if format is supported by OpenAI
        if image_format.upper() not in OPENAI_SUPPORTED_FORMATS:
            logger.warning(
                "Unsupported image format: %s (supported: %s)",
                image_format,
                ", ".join(OPENAI_SUPPORTED_FORMATS),
            )
            return None

        # Return proper MIME type
        mime_type = FORMAT_TO_MIME.get(image_format.upper())
        if not mime_type:
            logger.warning("No MIME type mapping for format: %s", image_format)
            return None

    except (OSError, ValueError) as e:
        logger.warning("Failed to validate image: %s", e)
        return None
    except Exception:
        logger.exception("Unexpected error validating image")
        return None
    else:
        logger.debug("Detected valid image format: %s -> %s", image_format, mime_type)
        return mime_type


def extract_text_from_image(image_data: bytes) -> str:
    """Extract text from image using GPT-4o Vision API.

    Args:
        image_data: Raw image bytes

    Returns:
        Extracted text from the image

    Raises:
        ValueError: If image format is invalid or unsupported

    """
    # Validate image format first
    mime_type = validate_and_get_image_format(image_data)
    if not mime_type:
        msg = (
            "Invalid or unsupported image format. "
            f"Supported formats: {', '.join(OPENAI_SUPPORTED_FORMATS)}"
        )
        raise ValueError(msg)

    # Use the OpenAi class with vision support
    open_ai = OpenAi(model="gpt-4o", max_tokens=1000, temperature=0.0)

    prompt = (
        "Extract all text from this image. "
        "If there's code, preserve formatting. "
        "If it's a screenshot of an error, include the full error message. "
        "If it's a diagram or chart, describe the key information."
        "Return only the extracted text without any preamble."
    )

    result = (
        open_ai.set_prompt("You are a helpful assistant that extracts text from images.")
        .set_input(prompt)
        .set_image(image_data, mime_type)
        .complete()
    )

    # Handle None response
    if result is None:
        logger.warning("OpenAI returned None content for image extraction")
        return ""

    return result.strip()


@job("ai")
def extract_images_then_maybe_reply(message_id: int, image_files: list[dict]) -> None:
    """Extract text from images, store results, then queue AI reply.

    Args:
        message_id: Primary key of the Slack message
        image_files: List of file metadata dictionaries from Slack

    """
    import django_rq

    try:
        message = Message.objects.get(pk=message_id)
    except Message.DoesNotExist:
        logger.error("Message %s not found for image extraction", message_id)  # noqa: TRY400
        return

    logger.info("Extracting text from %s images for message %s", len(image_files), message_id)

    bot_token = message.conversation.workspace.bot_token
    if not bot_token or bot_token == "None":  # noqa: S105
        logger.error("No bot token available")
        django_rq.get_queue("ai").enqueue_in(
            timedelta(minutes=QUEUE_RESPONSE_TIME_MINUTES),
            generate_ai_reply_if_unanswered,
            message_id,
        )
        return

    extractions = []
    for idx, file_data in enumerate(image_files[:MAX_IMAGES_PER_MESSAGE]):
        file_id = file_data.get("id")
        file_name = file_data.get("name", f"image_{idx + 1}")

        extraction_result = {
            "file_id": file_id,
            "file_name": file_name,
            "timestamp": datetime.now(UTC).isoformat(),
            "model": "gpt-4o",
        }

        try:
            image_url = file_data.get("url_private_download") or file_data.get("url_private")
            if not image_url:
                extraction_result.update({"status": "failed", "error": "No image URL found"})
                extractions.append(extraction_result)
                continue

            image_data = download_slack_image(image_url, bot_token)
            if not image_data:
                extraction_result.update({"status": "failed", "error": "Failed to download image"})
                extractions.append(extraction_result)
                continue

            extracted_text = extract_text_from_image(image_data)

            extraction_result.update(
                {
                    "status": "success",
                    "extracted_text": extracted_text,
                    "size_bytes": len(image_data),
                }
            )

            logger.info(
                "Successfully extracted text from %s (%s chars)", file_name, len(extracted_text)
            )

        except ValueError as e:
            # Image format validation error from ai service
            logger.warning("Invalid image format for %s: %s", file_name, e)
            extraction_result.update({"status": "failed", "error": f"Invalid image format: {e}"})

        except Exception:
            logger.exception("Failed to extract text from %s", file_name)
            extraction_result.update({"status": "failed", "error": "Extraction failed"})

        extractions.append(extraction_result)

    if "image_extractions" not in message.raw_data:
        message.raw_data["image_extractions"] = []
    message.raw_data["image_extractions"].extend(extractions)
    message.save(update_fields=["raw_data"])

    success_count = sum(1 for e in extractions if e.get("status") == "success")
    logger.info("Completed image extraction: %s/%s successful", success_count, len(extractions))

    django_rq.get_queue("ai").enqueue_in(
        timedelta(minutes=QUEUE_RESPONSE_TIME_MINUTES),
        generate_ai_reply_if_unanswered,
        message_id,
    )
