import pytest
import fitz
from app.services.resume_parser import ResumeParserService
from app.utils.exceptions import InvalidFileError


def test_parse_valid_pdf(sample_pdf_bytes):
    text, meta = ResumeParserService.extract_text(sample_pdf_bytes, ".pdf")
    assert "Alice Developer" in text
    assert "FastAPI" in text
    assert meta["format"] == "pdf"
    assert meta["page_count"] == 1


def test_parse_valid_docx(sample_docx_bytes):
    text, meta = ResumeParserService.extract_text(sample_docx_bytes, ".docx")
    assert "Bob Engineer" in text
    assert "Kubernetes" in text
    assert meta["format"] == "docx"
    assert "AWS Certified Solutions Architect" in text  # table content check


def test_parse_empty_pdf():
    doc = fitz.open()
    doc.new_page()
    empty_bytes = doc.write()
    doc.close()

    with pytest.raises(InvalidFileError) as exc_info:
        ResumeParserService.extract_text(empty_bytes, ".pdf")
    assert "empty" in str(exc_info.value).lower() or "usable text" in str(exc_info.value).lower()


def test_parse_corrupted_file():
    corrupted_bytes = b"%PDF-1.4\nCorrupted content without valid xref structure 12345678"
    with pytest.raises(InvalidFileError):
        ResumeParserService.extract_text(corrupted_bytes, ".pdf")


def test_parse_unsupported_format():
    with pytest.raises(InvalidFileError) as exc:
        ResumeParserService.extract_text(b"some content", ".txt")
    assert "Unsupported" in str(exc.value)
