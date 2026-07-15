import fitz  # PyMuPDF
import logging
import os

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path: str) -> str:
    """
    Reads a PDF file safely and returns all text sorted by natural reading order.
    Returns an empty string if reading fails.
    """
    # 1. Edge Case: Check if file actually exists
    if not os.path.exists(file_path):
        logger.error(f"PDF file not found at path: {file_path}")
        return ""

    text_content = []

    try:
        # 2. Use 'with' context manager - isse crash hone par bhi file handle automatic close ho jata hai
        with fitz.open(file_path) as document:
            for page in document:
                # 3. 'sort=True' ka use: Yeh text ko natural top-to-bottom, left-to-right order mein arrange karta hai.
                # Yeh multi-column resumes ke liye bohot zaroori hai.
                page_text = page.get_text("text", sort=True)
                if page_text:
                    text_content.append(page_text)

        # 4. Saare pages ka text clean tarike se join karo
        return "\n".join(text_content).strip()

    except Exception as e:
        logger.error(f"Error while extracting text from PDF ({file_path}): {e}")
        return ""