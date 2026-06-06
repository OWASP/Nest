"""OWASP app validators."""

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.template.defaultfilters import filesizeformat

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
