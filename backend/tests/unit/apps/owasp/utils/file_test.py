"""Tests for OWASP app file utilities."""

import io
from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from pypdf import PdfReader, PdfWriter

from apps.owasp.utils.file import (
    IMAGE_CONTENT_TYPE_MAP,
    IMAGE_EXTENSIONS,
    PDF_CONTENT_TYPE,
    PDF_EXTENSION,
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
    exif = image.getexif()
    exif[271] = "TestCamera"
    image.save(output, format="JPEG", exif=exif)
    content = output.getvalue()

    file = SimpleUploadedFile(
        name="test_exif.jpg",
        content=content,
        content_type="image/jpeg",
    )
    return file, content


def _create_jpeg_with_orientation():
    """Create a 10x5 JPEG image with EXIF Orientation = 6 (requires 90 CW rotation)."""
    image = Image.new("RGB", (10, 5), color="blue")
    output = io.BytesIO()
    exif = image.getexif()
    exif[0x0112] = 6  # Orientation tag
    image.save(output, format="JPEG", exif=exif)
    content = output.getvalue()
    return SimpleUploadedFile(
        name="test_orientation.jpg",
        content=content,
        content_type="image/jpeg",
    )


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


def _create_test_pdf_with_xmp():
    """Create a test PDF file containing an XMP /Metadata stream."""
    xmp_xml = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b'<x:xmpmeta xmlns:x="adobe:ns:meta/">'
        b'<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
        b'<rdf:Description xmlns:dc="http://purl.org/dc/elements/1.1/">'
        b"<dc:creator>XMP Test Author</dc:creator>"
        b"</rdf:Description>"
        b"</rdf:RDF>"
        b"</x:xmpmeta>"
    )
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.add_metadata({"/Author": "Test Author"})
    writer.xmp_metadata = xmp_xml

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

    @pytest.mark.parametrize("ext", sorted(IMAGE_EXTENSIONS))
    def test_dispatches_to_image_handler_for_image_extensions(self, ext):
        mock_file = MagicMock()
        mock_file.name = f"test.{ext}"

        with patch(
            "apps.owasp.utils.file._strip_image_metadata", return_value=mock_file
        ) as mock_strip:
            result = strip_file_metadata(mock_file)

        mock_strip.assert_called_once_with(mock_file, ext)
        assert result == mock_file

    @pytest.mark.parametrize("ext", [PDF_EXTENSION])
    def test_dispatches_to_pdf_handler_for_pdf_extensions(self, ext):
        mock_file = MagicMock()
        mock_file.name = f"test.{ext}"

        with patch(
            "apps.owasp.utils.file._strip_pdf_metadata", return_value=mock_file
        ) as mock_strip:
            result = strip_file_metadata(mock_file)

        mock_strip.assert_called_once_with(mock_file)
        assert result == mock_file

    def test_raises_error_for_unsupported_extension(self):
        mock_file = MagicMock()
        mock_file.name = "test.txt"

        with pytest.raises(
            ValidationError, match=r"Unsupported file type for metadata stripping: \.txt"
        ):
            strip_file_metadata(mock_file)

    def test_handles_uppercase_extension(self):
        mock_file = MagicMock()
        mock_file.name = "test.JPEG"

        with patch(
            "apps.owasp.utils.file._strip_image_metadata", return_value=mock_file
        ) as mock_strip:
            strip_file_metadata(mock_file)

        mock_strip.assert_called_once_with(mock_file, ".jpeg")

    def test_handles_mixed_case_extension(self):
        mock_file = MagicMock()
        mock_file.name = "test.Pdf"

        with patch(
            "apps.owasp.utils.file._strip_pdf_metadata", return_value=mock_file
        ) as mock_strip:
            strip_file_metadata(mock_file)

        mock_strip.assert_called_once_with(mock_file)

    def test_corrupt_file_raises_validation_error(self):
        mock_file = SimpleUploadedFile(
            name="corrupt.jpg",
            content=b"not an image",
            content_type="image/jpeg",
        )
        with pytest.raises(ValidationError, match="Invalid or corrupt image"):
            strip_file_metadata(mock_file)


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

        result_image = Image.open(io.BytesIO(result.read()))
        assert not result_image.getexif()

    def test_corrupt_image_raises_validation_error(self):
        mock_file = SimpleUploadedFile(
            name="corrupt.jpg",
            content=b"not an image file data",
            content_type="image/jpeg",
        )
        with pytest.raises(ValidationError, match="Invalid or corrupt image"):
            _strip_image_metadata(mock_file, ".jpg")

    def test_exif_transpose_preserves_orientation(self):
        mock_file = _create_jpeg_with_orientation()
        result = _strip_image_metadata(mock_file, ".jpg")

        result_image = Image.open(io.BytesIO(result.read()))
        assert result_image.size == (5, 10)
        assert result_image.getexif().get(0x0112) is None


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

    def test_strips_xmp_metadata_stream(self):
        mock_file = _create_test_pdf_with_xmp()

        result = _strip_pdf_metadata(mock_file)

        cleaned_bytes = result.read()
        reader = PdfReader(io.BytesIO(cleaned_bytes))
        assert reader.xmp_metadata is None
        assert b"/Metadata" not in cleaned_bytes

    def test_corrupt_pdf_raises_validation_error(self):
        mock_file = SimpleUploadedFile(
            name="corrupt.pdf",
            content=b"not a pdf file data",
            content_type="application/pdf",
        )
        with pytest.raises(ValidationError, match="Invalid or corrupt PDF"):
            _strip_pdf_metadata(mock_file)
