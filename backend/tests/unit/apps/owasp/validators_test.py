"""Tests for OWASP app validators."""

from unittest.mock import MagicMock

import pytest
from django.core.exceptions import ValidationError

from apps.owasp.validators import (
    EVIDENCE_ALLOWED_CONTENT_TYPES,
    EVIDENCE_ALLOWED_EXTENSIONS,
    EVIDENCE_MAX_FILE_SIZE,
    validate_evidence_content_type,
    validate_evidence_extension,
    validate_evidence_file_size,
)


class TestValidateEvidenceExtension:
    """Tests for validate_evidence_extension."""

    @pytest.mark.parametrize("extension", EVIDENCE_ALLOWED_EXTENSIONS)
    def test_allowed_extension_passes(self, extension):
        """Test that allowed file extensions pass validation."""
        mock_file = MagicMock()
        mock_file.name = f"evidence.{extension}"
        validate_evidence_extension(mock_file)

    @pytest.mark.parametrize(
        "filename",
        [
            "evidence.exe",
            "evidence.gif",
            "evidence.txt",
            "evidence.zip",
            "evidence.tar.gz",
            "evidence",
            "evidence.py",
            "evidence.js",
            "evidence.html",
            "evidence.svg",
        ],
    )
    def test_disallowed_extension_raises_error(self, filename):
        """Test that disallowed file extensions raise ValidationError."""
        mock_file = MagicMock()
        mock_file.name = filename
        with pytest.raises(ValidationError):
            validate_evidence_extension(mock_file)


class TestValidateEvidenceFileSize:
    """Tests for validate_evidence_file_size."""

    def test_file_within_size_limit_passes(self):
        """Test that a file within the size limit passes validation."""
        mock_file = MagicMock()
        mock_file.size = EVIDENCE_MAX_FILE_SIZE - 1
        validate_evidence_file_size(mock_file)

    def test_file_at_size_limit_passes(self):
        """Test that a file at exactly the size limit passes validation."""
        mock_file = MagicMock()
        mock_file.size = EVIDENCE_MAX_FILE_SIZE
        validate_evidence_file_size(mock_file)

    def test_file_exceeds_size_limit_raises_error(self):
        """Test that a file exceeding the size limit raises ValidationError."""
        mock_file = MagicMock()
        mock_file.size = EVIDENCE_MAX_FILE_SIZE + 1
        with pytest.raises(ValidationError):
            validate_evidence_file_size(mock_file)


class TestValidateEvidenceContentType:
    """Tests for validate_evidence_content_type."""

    @pytest.mark.parametrize("content_type", EVIDENCE_ALLOWED_CONTENT_TYPES)
    def test_allowed_content_type_passes(self, content_type):
        """Test that allowed content types pass validation."""
        mock_file = MagicMock()
        mock_file.content_type = content_type
        validate_evidence_content_type(mock_file)

    @pytest.mark.parametrize(
        "content_type",
        [
            "image/gif",
            "text/plain",
            "application/octet-stream",
            "application/x-msdownload",
            "image/svg+xml",
            "text/html",
            "application/zip",
            "application/x-rar-compressed",
        ],
    )
    def test_disallowed_content_type_raises_error(self, content_type):
        """Test that disallowed content types raise ValidationError."""
        mock_file = MagicMock()
        mock_file.content_type = content_type
        with pytest.raises(ValidationError):
            validate_evidence_content_type(mock_file)

    def test_missing_content_type_passes(self):
        """Test that a file without content_type (e.g. FieldFile) passes validation."""
        mock_file = MagicMock(spec=[])
        del mock_file.content_type
        validate_evidence_content_type(mock_file)

    def test_none_content_type_passes(self):
        """Test that a file with None content_type passes validation."""
        mock_file = MagicMock()
        mock_file.content_type = None
        validate_evidence_content_type(mock_file)
