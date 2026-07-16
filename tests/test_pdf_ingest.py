from unittest.mock import MagicMock, patch

import pdf_ingest


def test_extract_pdf_text_joins_pages():
    page1 = MagicMock()
    page1.extract_text.return_value = "First page text."
    page2 = MagicMock()
    page2.extract_text.return_value = "Second page text."

    fake_reader = MagicMock()
    fake_reader.pages = [page1, page2]

    with patch("pdf_ingest.PdfReader", return_value=fake_reader):
        text = pdf_ingest.extract_pdf_text("fake.pdf")

    assert text == "First page text.\nSecond page text."


def test_extract_pdf_text_handles_pages_with_no_text():
    page1 = MagicMock()
    page1.extract_text.return_value = None

    fake_reader = MagicMock()
    fake_reader.pages = [page1]

    with patch("pdf_ingest.PdfReader", return_value=fake_reader):
        text = pdf_ingest.extract_pdf_text("fake.pdf")

    assert text == ""
