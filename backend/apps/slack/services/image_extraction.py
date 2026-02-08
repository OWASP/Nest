"""Image extraction service for Slack messages."""

import base64
import logging
from datetime import UTC, datetime, timedelta

import openai
import requests
from django.conf import settings
from django_rq import job
from requests.exceptions import RequestException

from apps.ai.common.constants import QUEUE_RESPONSE_TIME_MINUTES
from apps.slack.models import Message
from apps.slack.services.message_auto_reply import generate_ai_reply_if_unanswered

logger = logging.getLogger(__name__)

MAX_IMAGES_PER_MESSAGE = 3
SUPPORTED_IMAGE_TYPES = ("image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp")
MAX_IMAGE_SIZE_MB = 20


def is_valid_image_file(file_data: dict) -> bool:
    """Check if file is a valid image for extraction."""
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
    """Download image from Slack."""
    try:
        headers = {"Authorization": f"Bearer {bot_token}"}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except RequestException:
        logger.exception("Failed to download image from %s", url)
        return None
    else:
        return response.content


def extract_text_from_image(image_data: bytes) -> str:
    """Extract text from image using GPT-4o."""
    api_key = settings.OPEN_AI_SECRET_KEY
    if not api_key:
        msg = "DJANGO_OPEN_AI_SECRET_KEY not set"
        raise ValueError(msg)

    client = openai.OpenAI(api_key=api_key)
    base64_image = base64.b64encode(image_data).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Extract all text from this image. "
                            "If there's code, preserve formatting. "
                            "If it's a screenshot of an error, include the full error message. "
                            "If it's a diagram or chart, describe the key information. "
                            "Return only the extracted text without any preamble."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
        max_tokens=1000,
        temperature=0.0,
    )

    return response.choices[0].message.content.strip()


@job("ai")
def extract_images_then_maybe_reply(message_id: int, image_files: list[dict]) -> None:
    """Extract text from images, store results, then queue AI reply."""
    import django_rq

    try:
        message = Message.objects.get(pk=message_id)
    except Message.DoesNotExist:
        logger.exception("Message %s not found for image extraction", message_id)
        return

    logger.info("Extracting text from %s images for message %s", len(image_files), message_id)

    bot_token = settings.SLACK_BOT_TOKEN
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

        except openai.OpenAIError:
            logger.exception("OpenAI API error for %s", file_name)
            extraction_result.update({"status": "failed", "error": "OpenAI API error"})

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
