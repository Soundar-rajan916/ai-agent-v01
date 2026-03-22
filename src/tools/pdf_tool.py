"""
PDF Parser Tool
Extracts text from uploaded PDF files using pdfplumber
"""
import io
import pdfplumber
from fastapi import UploadFile, HTTPException


async def extract_text_from_pdf(file: UploadFile) -> str:
    """
    Extract text content from an uploaded PDF file.

    Args:
        file: UploadFile object from FastAPI

    Returns:
        str: Extracted text from the PDF

    Raises:
        HTTPException: If PDF is invalid or cannot be processed
    """
    try:
        # Read file content
        contents = await file.read()

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="Empty file uploaded"
            )

        # Validate PDF signature (PDF files start with %PDF)
        if not contents.startswith(b'%PDF'):
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF file. File does not have PDF signature."
            )

        # Extract text using pdfplumber
        text_parts = []
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            if len(pdf.pages) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="PDF has no pages"
                )

            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

        # Combine all pages
        full_text = "\n\n".join(text_parts)

        if not full_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF. The file may be image-based or corrupted."
            )

        # Clean up the text
        cleaned_text = clean_extracted_text(full_text)

        return cleaned_text

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF: {str(e)}"
        )


def clean_extracted_text(text: str) -> str:
    """
    Clean and normalize extracted text.

    Args:
        text: Raw extracted text

    Returns:
        str: Cleaned text
    """
    # Remove excessive whitespace
    lines = text.split('\n')
    cleaned_lines = []

    for line in lines:
        # Strip whitespace from each line
        stripped = line.strip()
        # Skip empty lines but keep single empty lines for structure
        if stripped or (cleaned_lines and cleaned_lines[-1]):
            cleaned_lines.append(stripped)

    return '\n'.join(cleaned_lines)
