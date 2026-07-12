"""OWASP app file utilities."""

from __future__ import annotations

import io
import logging
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile, UploadedFile
from PIL import Image, ImageOps
from pypdf import PdfWriter
from pypdf.errors import PyPdfError

logger = logging.getLogger(__name__)

IMAGE_CONTENT_TYPE_MAP = {
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}
IMAGE_EXTENSIONS = frozenset({".jpeg", ".jpg", ".png", ".webp"})
IMAGE_FORMAT_MAP = {
    ".jpeg": "JPEG",
    ".jpg": "JPEG",
    ".png": "PNG",
    ".webp": "WEBP",
}

PDF_CONTENT_TYPE = "application/pdf"
PDF_EXTENSION = ".pdf"


def strip_file_metadata(file: UploadedFile | None) -> UploadedFile | None:
    """Strip EXIF/XMP metadata from an uploaded file.

    Args:
        file (UploadedFile, optional): An uploaded file object.

    Returns:
        UploadedFile, optional: A new SimpleUploadedFile with metadata stripped.

    Raises:
        ValidationError: If the file is invalid, corrupt, or has an unsupported extension.

    """
    if not file:
        return file

    ext = Path(file.name).suffix.lower()

    if ext in IMAGE_EXTENSIONS:
        return _strip_image_metadata(file, ext)

    if ext == PDF_EXTENSION:
        return _strip_pdf_metadata(file)

    msg = f"Unsupported file type for metadata stripping: {ext}"
    raise ValidationError(msg)


def _strip_image_metadata(file: UploadedFile, ext: str) -> SimpleUploadedFile:
    """Strip EXIF/XMP metadata from an image file.

    Opens the image with Pillow and re-saves it without metadata.
    Pillow's save() naturally drops EXIF/XMP data when the exif
    parameter is not explicitly passed.

    Args:
        file (UploadedFile): An uploaded image file object.
        ext (str): The lowercase file extension (e.g. ".jpeg", ".png").

    Returns:
        SimpleUploadedFile: A new file object containing the cleaned image.

    Raises:
        ValidationError: If the image is invalid or corrupt.

    """
    try:
        file.seek(0)
        with Image.open(file) as image:
            output = io.BytesIO()
            ImageOps.exif_transpose(image).save(output, format=IMAGE_FORMAT_MAP[ext])
            cleaned_bytes = output.getvalue()
    except (OSError, ValueError) as e:
        logger.warning("Failed to strip image metadata: %s", e)
        msg = "Invalid or corrupt image."
        raise ValidationError(msg) from e
    except Exception as e:
        logger.exception("Unexpected error stripping image metadata")
        msg = "Invalid or corrupt image."
        raise ValidationError(msg) from e

    return SimpleUploadedFile(
        name=file.name,
        content=cleaned_bytes,
        content_type=IMAGE_CONTENT_TYPE_MAP[ext],
    )


def _strip_pdf_metadata(file: UploadedFile) -> SimpleUploadedFile:
    """Strip metadata from a PDF file.

    Uses pypdf to read and rewrite the PDF, removing the /Info
    dictionary and /Metadata XMP stream from the output.

    Args:
        file (UploadedFile): An uploaded PDF file object.

    Returns:
        SimpleUploadedFile: A new cleaned PDF file object.

    Raises:
        ValidationError: If the PDF is invalid or corrupt.

    """
    try:
        file.seek(0)
        writer = PdfWriter(clone_from=file)
        writer.metadata = {}
        writer.xmp_metadata = None

        output = io.BytesIO()
        writer.write(output)
        cleaned_bytes = output.getvalue()
    except (PyPdfError, ValueError, KeyError) as e:
        logger.warning("Failed to strip PDF metadata: %s", e)
        msg = "Invalid or corrupt PDF."
        raise ValidationError(msg) from e
    except Exception as e:
        logger.exception("Unexpected error stripping PDF metadata")
        msg = "Invalid or corrupt PDF."
        raise ValidationError(msg) from e

    return SimpleUploadedFile(
        name=file.name,
        content=cleaned_bytes,
        content_type=PDF_CONTENT_TYPE,
    )
