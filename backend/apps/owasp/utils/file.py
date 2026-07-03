"""OWASP app file utilities."""

from __future__ import annotations

import io
import logging
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile, UploadedFile
from PIL import Image, ImageOps, UnidentifiedImageError
from pypdf import PdfWriter
from pypdf.errors import PdfReadError, PyPdfError

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = frozenset({".jpeg", ".jpg", ".png", ".webp"})
PDF_EXTENSION = ".pdf"

IMAGE_FORMAT_MAP = {
    ".jpeg": "JPEG",
    ".jpg": "JPEG",
    ".png": "PNG",
    ".webp": "WEBP",
}

IMAGE_CONTENT_TYPE_MAP = {
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}

PDF_CONTENT_TYPE = "application/pdf"


def strip_file_metadata(file: UploadedFile | None) -> UploadedFile | None:
    """Strip EXIF/XMP metadata from an uploaded file.

    Dispatches to the appropriate handler based on file extension.

    Args:
        file: An uploaded file object with `name`, `read()`, and `seek()`.

    Returns:
        A new SimpleUploadedFile with metadata stripped, or the original
        file unchanged if the extension is not supported.

    """
    if not file:
        return file

    try:
        ext = Path(file.name).suffix.lower()

        if ext in IMAGE_EXTENSIONS:
            return _strip_image_metadata(file, ext)

        if ext == PDF_EXTENSION:
            return _strip_pdf_metadata(file)
    except ValidationError:
        raise
    except Exception as e:
        logger.exception("Unexpected error in strip_file_metadata")
        msg = "Invalid or corrupt file."
        raise ValidationError(msg) from e

    return file


def _strip_image_metadata(file: UploadedFile, ext: str) -> SimpleUploadedFile:
    """Strip EXIF/XMP metadata from an image file.

    Opens the image with Pillow and re-saves it without metadata.
    Pillow's save() naturally drops EXIF/XMP data when the exif
    parameter is not explicitly passed.

    Args:
        file: An uploaded image file object.
        ext: The lowercase file extension (e.g. "jpeg", "png").

    Returns:
        A new SimpleUploadedFile containing the cleaned image.

    """
    try:
        file.seek(0)
        with Image.open(file) as image:
            transposed_image = ImageOps.exif_transpose(image)
            output = io.BytesIO()
            image_format = IMAGE_FORMAT_MAP[ext]
            transposed_image.save(output, format=image_format)
            cleaned_bytes = output.getvalue()
    except (UnidentifiedImageError, OSError, ValueError) as e:
        logger.warning("Failed to strip image metadata: %s", e)
        msg = "Invalid or corrupt image."
        raise ValidationError(msg) from e
    except Exception as e:
        logger.exception("Unexpected error stripping image metadata")
        msg = "Invalid or corrupt image."
        raise ValidationError(msg) from e

    content_type = IMAGE_CONTENT_TYPE_MAP[ext]
    return SimpleUploadedFile(
        name=file.name,
        content=cleaned_bytes,
        content_type=content_type,
    )


def _strip_pdf_metadata(file: UploadedFile) -> SimpleUploadedFile:
    """Strip metadata from a PDF file.

    Uses pypdf to read and rewrite the PDF, removing the /Info
    dictionary and /Metadata XMP stream from the output.

    Args:
        file: An uploaded PDF file object.

    Returns:
        A new SimpleUploadedFile containing the cleaned PDF.

    """
    try:
        file.seek(0)
        writer = PdfWriter(clone_from=file)
        writer.metadata = {}
        writer.xmp_metadata = None

        output = io.BytesIO()
        writer.write(output)
        cleaned_bytes = output.getvalue()
    except (PyPdfError, PdfReadError, ValueError, KeyError) as e:
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
