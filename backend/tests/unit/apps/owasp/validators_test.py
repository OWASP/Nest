"""Tests for OWASP app validators."""

from unittest.mock import MagicMock

import pytest
from django.core.exceptions import ValidationError

from apps.owasp.validators import (
    EVIDENCE_ALLOWED_EXTENSIONS,
    EVIDENCE_MAX_FILE_SIZE,
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
