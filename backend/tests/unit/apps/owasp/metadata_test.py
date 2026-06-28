"""Tests for OWASP app file metadata stripping utilities."""

import io
import struct
from unittest.mock import MagicMock, patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from pypdf import PdfReader, PdfWriter

from apps.owasp.metadata import (
    IMAGE_CONTENT_TYPE_MAP,
    IMAGE_EXTENSIONS,
    PDF_CONTENT_TYPE,
    PDF_EXTENSIONS,
    _strip_image_metadata,
    _strip_pdf_metadata,
    strip_file_metadata,
)


def _create_test_image_simple(fmt="JPEG", ext=".jpg"):
    """Create a simple test image file without external EXIF libraries."""
    image = Image.new("RGB", (10, 10), color="red")
    output = io.BytesIO()
    image.save(output, format=fmt)
    content = output.getvalue()

    return SimpleUploadedFile(
        name=f"test_image.{ext.lstrip('.')}",
        content=content,
        content_type=IMAGE_CONTENT_TYPE_MAP[ext],
    )


def _create_jpeg_with_exif():
    """Create a JPEG with EXIF data embedded via Pillow."""
    image = Image.new("RGB", (10, 10), color="blue")
    output = io.BytesIO()
    image.save(output, format="JPEG")
    jpeg_bytes = output.getvalue()

    # Build a minimal EXIF APP1 segment with a Make tag.
    byte_order = b"MM"
    ifd_entry_count = 1
    tag_make = 0x010F
    tag_type_ascii = 2
    make_value = b"TestCamera\x00"
    make_length = len(make_value)
    ifd_offset = 8
    value_offset = ifd_offset + 2 + 12 + 4

    exif_body = bytearray()
    exif_body += byte_order
    exif_body += struct.pack(">H", 0x002A)
    exif_body += struct.pack(">I", ifd_offset)
    exif_body += struct.pack(">H", ifd_entry_count)
    exif_body += struct.pack(">HHI", tag_make, tag_type_ascii, make_length)
    exif_body += struct.pack(">I", value_offset)
    exif_body += struct.pack(">I", 0)
    exif_body += make_value

    app1_marker = b"\xff\xe1"
    app1_length = len(exif_body) + 2 + 6
    app1_header = app1_marker + struct.pack(">H", app1_length) + b"Exif\x00\x00"

    soi = jpeg_bytes[:2]
    rest = jpeg_bytes[2:]
    modified_jpeg = soi + app1_header + exif_body + rest

    file = SimpleUploadedFile(
        name="test_exif.jpg",
        content=modified_jpeg,
        content_type="image/jpeg",
    )
    return file, modified_jpeg


def _create_test_pdf(*, with_metadata=True):
    """Create a test PDF file with optional metadata."""
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)

    if with_metadata:
        writer.add_metadata(
            {
                "/Author": "Test Author",
                "/Creator": "Test Creator",
                "/Producer": "Test Producer",
                "/Title": "Test Title",
            }
        )

    output = io.BytesIO()
    writer.write(output)
    content = output.getvalue()

    return SimpleUploadedFile(
        name="test_document.pdf",
        content=content,
        content_type=PDF_CONTENT_TYPE,
    )


class TestStripFileMetadata:
    """Tests for strip_file_metadata dispatch function."""

    def test_returns_none_for_none_input(self):
        result = strip_file_metadata(None)

        assert result is None

    def test_returns_empty_string_for_empty_input(self):
        result = strip_file_metadata("")

        assert result == ""

    @pytest.mark.parametrize("ext", sorted(IMAGE_EXTENSIONS))
    def test_dispatches_to_image_handler_for_image_extensions(self, ext):
        mock_file = MagicMock()
        mock_file.name = f"test.{ext}"

        with patch(
            "apps.owasp.metadata._strip_image_metadata", return_value=mock_file
        ) as mock_strip:
            result = strip_file_metadata(mock_file)

        mock_strip.assert_called_once_with(mock_file, ext)
        assert result == mock_file

    @pytest.mark.parametrize("ext", sorted(PDF_EXTENSIONS))
    def test_dispatches_to_pdf_handler_for_pdf_extensions(self, ext):
        mock_file = MagicMock()
        mock_file.name = f"test.{ext}"

        with patch(
            "apps.owasp.metadata._strip_pdf_metadata", return_value=mock_file
        ) as mock_strip:
            result = strip_file_metadata(mock_file)

        mock_strip.assert_called_once_with(mock_file)
        assert result == mock_file

    def test_returns_file_unchanged_for_unsupported_extension(self):
        mock_file = MagicMock()
        mock_file.name = "test.txt"

        result = strip_file_metadata(mock_file)

        assert result is mock_file

    def test_handles_uppercase_extension(self):
        mock_file = MagicMock()
        mock_file.name = "test.JPEG"

        with patch(
            "apps.owasp.metadata._strip_image_metadata", return_value=mock_file
        ) as mock_strip:
            strip_file_metadata(mock_file)

        mock_strip.assert_called_once_with(mock_file, ".jpeg")

    def test_handles_mixed_case_extension(self):
        mock_file = MagicMock()
        mock_file.name = "test.Pdf"

        with patch(
            "apps.owasp.metadata._strip_pdf_metadata", return_value=mock_file
        ) as mock_strip:
            strip_file_metadata(mock_file)

        mock_strip.assert_called_once_with(mock_file)


class TestStripImageMetadata:
    """Tests for _strip_image_metadata."""

    @pytest.mark.parametrize(
        ("fmt", "ext"),
        [
            ("JPEG", ".jpeg"),
            ("JPEG", ".jpg"),
            ("PNG", ".png"),
            ("WEBP", ".webp"),
        ],
    )
    def test_strips_metadata_and_preserves_image_content(self, fmt, ext):
        mock_file = _create_test_image_simple(fmt=fmt, ext=ext)

        result = _strip_image_metadata(mock_file, ext)

        result_image = Image.open(io.BytesIO(result.read()))
        assert result_image.size == (10, 10)
        assert result_image.mode == "RGB"

    @pytest.mark.parametrize(
        ("fmt", "ext"),
        [
            ("JPEG", ".jpeg"),
            ("JPEG", ".jpg"),
            ("PNG", ".png"),
            ("WEBP", ".webp"),
        ],
    )
    def test_preserves_file_name(self, fmt, ext):
        mock_file = _create_test_image_simple(fmt=fmt, ext=ext)

        result = _strip_image_metadata(mock_file, ext)

        assert result.name == f"test_image.{ext.lstrip('.')}"

    @pytest.mark.parametrize(
        ("fmt", "ext"),
        [
            ("JPEG", ".jpeg"),
            ("JPEG", ".jpg"),
            ("PNG", ".png"),
            ("WEBP", ".webp"),
        ],
    )
    def test_sets_correct_content_type(self, fmt, ext):
        mock_file = _create_test_image_simple(fmt=fmt, ext=ext)

        result = _strip_image_metadata(mock_file, ext)

        assert result.content_type == IMAGE_CONTENT_TYPE_MAP[ext]

    def test_result_has_valid_size(self):
        mock_file = _create_test_image_simple(fmt="JPEG", ext=".jpg")

        result = _strip_image_metadata(mock_file, ".jpg")

        assert result.size > 0

    def test_strips_exif_data_from_jpeg(self):
        mock_file, original_bytes = _create_jpeg_with_exif()

        assert b"TestCamera" in original_bytes

        result = _strip_image_metadata(mock_file, ".jpg")

        assert b"TestCamera" not in result.read()


class TestStripPdfMetadata:
    """Tests for _strip_pdf_metadata."""

    def test_strips_metadata_from_pdf(self):
        mock_file = _create_test_pdf(with_metadata=True)

        result = _strip_pdf_metadata(mock_file)

        reader = PdfReader(io.BytesIO(result.read()))
        metadata = reader.metadata
        assert not metadata.get("/Author")
        assert not metadata.get("/Title")

    def test_preserves_page_count(self):
        mock_file = _create_test_pdf(with_metadata=True)

        result = _strip_pdf_metadata(mock_file)

        reader = PdfReader(io.BytesIO(result.read()))
        assert len(reader.pages) == 1

    def test_preserves_file_name(self):
        mock_file = _create_test_pdf()

        result = _strip_pdf_metadata(mock_file)

        assert result.name == "test_document.pdf"

    def test_sets_correct_content_type(self):
        mock_file = _create_test_pdf()

        result = _strip_pdf_metadata(mock_file)

        assert result.content_type == PDF_CONTENT_TYPE

    def test_result_has_valid_size(self):
        mock_file = _create_test_pdf()

        result = _strip_pdf_metadata(mock_file)

        assert result.size > 0

    def test_handles_pdf_without_metadata(self):
        mock_file = _create_test_pdf(with_metadata=False)

        result = _strip_pdf_metadata(mock_file)

        assert result.size > 0
        assert result.name == "test_document.pdf"

    def test_producer_and_creator_are_cleared(self):
        mock_file = _create_test_pdf(with_metadata=True)

        result = _strip_pdf_metadata(mock_file)

        reader = PdfReader(io.BytesIO(result.read()))
        metadata = reader.metadata
        assert not metadata.get("/Producer")
        assert not metadata.get("/Creator")
