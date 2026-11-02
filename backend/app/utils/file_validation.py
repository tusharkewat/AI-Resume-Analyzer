import os
import re
from fastapi import UploadFile
from app.config import settings
from app.utils.exceptions import InvalidFileError

# Magic bytes
PDF_MAGIC = b"%PDF-"
DOCX_MAGIC = b"PK\x03\x04"


def sanitize_filename(filename: str) -> str:
    """Sanitizes filename to prevent directory traversal and invalid chars."""
    basename = os.path.basename(filename)
    clean_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', basename)
    if not clean_name or clean_name.startswith('.'):
        clean_name = f"upload_{clean_name}"
    return clean_name


async def validate_uploaded_file(file: UploadFile) -> bytes:
    """
    Validates uploaded resume file:
    - Non-empty filename
    - Allowed extension (.pdf, .docx)
    - File size <= MAX_FILE_SIZE_BYTES and > 0
    - File magic bytes match extension
    Returns raw file bytes.
    """
    if not file.filename:
        raise InvalidFileError("Uploaded file must have a filename.")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise InvalidFileError(f"Unsupported file type '{ext}'. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}")

    # Read content to validate size and magic bytes
    content = await file.read()
    file_size = len(content)

    if file_size == 0:
        raise InvalidFileError("The uploaded file is empty.")

    if file_size > settings.MAX_FILE_SIZE_BYTES:
        raise InvalidFileError(f"File size exceeds limit of {settings.MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB.")

    # Validate magic bytes
    if ext == ".pdf":
        if not content.startswith(PDF_MAGIC):
            raise InvalidFileError("Invalid PDF file: corrupted or incorrect format.")
    elif ext == ".docx":
        if not content.startswith(DOCX_MAGIC):
            raise InvalidFileError("Invalid DOCX file: corrupted or incorrect format.")

    # Reset file cursor for any future reads if needed
    await file.seek(0)
    return content
