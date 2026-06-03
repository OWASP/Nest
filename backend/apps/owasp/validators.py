"""OWASP app validators."""

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.template.defaultfilters import filesizeformat

EVIDENCE_ALLOWED_CONTENT_TYPES = [
    "application/msword",
    "application/pdf",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "image/jpeg",
    "image/png",
    "image/webp",
    "text/csv",
]

EVIDENCE_ALLOWED_EXTENSIONS = [
    "csv",
    "doc",
    "docx",
    "jpeg",
    "jpg",
    "pdf",
    "png",
    "webp",
    "xls",
    "xlsx",
]

EVIDENCE_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

validate_evidence_extension = FileExtensionValidator(
    allowed_extensions=EVIDENCE_ALLOWED_EXTENSIONS,
)


def validate_evidence_content_type(file):
    """Validate the content type of an uploaded evidence file.

    Args:
        file: The uploaded file object to validate.

    Raises:
        ValidationError: If the file content type is not allowed.

    """
    content_type = getattr(file, "content_type", None)
    if content_type and content_type not in EVIDENCE_ALLOWED_CONTENT_TYPES:
        msg = f"File content type '{content_type}' is not supported."
        raise ValidationError(msg)


def validate_evidence_file_size(file):
    """Validate the file size of an uploaded evidence file.

    Args:
        file: The uploaded file object to validate.

    Raises:
        ValidationError: If the file exceeds the maximum allowed size.

    """
    if file.size > EVIDENCE_MAX_FILE_SIZE:
        msg = (
            f"File size exceeds the maximum allowed size of "
            f"{filesizeformat(EVIDENCE_MAX_FILE_SIZE)}. "
            f"Uploaded file size: {filesizeformat(file.size)}."
        )
        raise ValidationError(msg)
