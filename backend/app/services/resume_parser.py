import io
import re
from typing import Tuple
import fitz  # PyMuPDF
from docx import Document
from app.utils.exceptions import InvalidFileError


class ResumeParserService:
    """Extracts plain text and page metadata from PDF and DOCX documents."""

    @staticmethod
    def extract_text(file_bytes: bytes, file_type: str) -> Tuple[str, dict]:
        """
        Parses text from raw file bytes.
        Returns:
            Tuple of (extracted_text, metadata_dict)
        Raises:
            InvalidFileError if document is corrupted, password-protected, or image-only.
        """
        clean_ext = file_type.lower().strip()
        if not clean_ext.startswith("."):
            clean_ext = f".{clean_ext}"

        if clean_ext == ".pdf":
            return ResumeParserService._extract_pdf(file_bytes)
        elif clean_ext == ".docx":
            return ResumeParserService._extract_docx(file_bytes)
        else:
            raise InvalidFileError(f"Unsupported format '{file_type}'. Supported: .pdf, .docx")

    @staticmethod
    def _extract_pdf(file_bytes: bytes) -> Tuple[str, dict]:
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
        except Exception as e:
            raise InvalidFileError(f"Failed to open PDF document: {str(e)}")

        if doc.is_encrypted:
            raise InvalidFileError("The PDF document is password-protected or encrypted.")

        total_pages = len(doc)
        if total_pages == 0:
            raise InvalidFileError("The PDF document has 0 pages.")

        page_texts = []
        has_images = False

        for page_num in range(total_pages):
            page = doc.load_page(page_num)
            text = page.get_text()
            if text:
                page_texts.append(text)
            if len(page.get_images()) > 0:
                has_images = True

        full_text = "\n".join(page_texts).strip()
        normalized_text = ResumeParserService._clean_text(full_text)

        # Scanned or image-only detection
        if len(normalized_text) < 30:
            if has_images:
                raise InvalidFileError(
                    "The uploaded PDF appears to be a scanned image or photo without selectable text. "
                    "Please provide a text-searchable PDF or a Word (.docx) document."
                )
            else:
                raise InvalidFileError("The uploaded PDF does not contain any usable text.")

        metadata = {
            "page_count": total_pages,
            "format": "pdf",
            "character_count": len(normalized_text),
            "word_count": len(normalized_text.split())
        }

        return normalized_text, metadata

    @staticmethod
    def _extract_docx(file_bytes: bytes) -> Tuple[str, dict]:
        try:
            doc = Document(io.BytesIO(file_bytes))
        except Exception as e:
            raise InvalidFileError(f"Failed to read DOCX file: {str(e)}")

        paragraphs = []
        for p in doc.paragraphs:
            txt = p.text.strip()
            if txt:
                paragraphs.append(txt)

        # Also extract table text
        for table in doc.tables:
            for row in table.rows:
                row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_cells:
                    paragraphs.append(" | ".join(row_cells))

        full_text = "\n".join(paragraphs).strip()
        normalized_text = ResumeParserService._clean_text(full_text)

        if len(normalized_text) < 20:
            raise InvalidFileError("The uploaded DOCX document contains insufficient or empty text.")

        metadata = {
            "paragraph_count": len(doc.paragraphs),
            "format": "docx",
            "character_count": len(normalized_text),
            "word_count": len(normalized_text.split())
        }

        return normalized_text, metadata

    @staticmethod
    def _clean_text(text: str) -> str:
        # Normalize non-breaking spaces and strange unicode
        text = text.replace('\xa0', ' ').replace('\r\n', '\n').replace('\r', '\n')
        # Replace 3 or more consecutive newlines with 2
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
