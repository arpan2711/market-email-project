"""Pull text out of a PDF so it can go into the RAG store.

Just wraps pypdf - most saved articles are text-layer PDFs (printed from a
browser, downloaded from a news site), so no OCR needed here. A scanned
image PDF won't extract anything useful; that'd need something heavier like
pytesseract, not worth it for this project.
"""
from __future__ import annotations

from pypdf import PdfReader


def extract_pdf_text(file) -> str:
    reader = PdfReader(file)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()
