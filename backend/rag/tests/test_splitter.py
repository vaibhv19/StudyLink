from django.test import SimpleTestCase
from unittest.mock import patch, MagicMock
from vault.services import PDFIngestionService

class PDFSplitterTests(SimpleTestCase):
    @patch('vault.services.PdfReader')
    def test_extract_and_split_pdf_success(self, mock_pdf_reader):
        # Setup mock reader and pages
        mock_reader_instance = MagicMock()
        
        # Page 1 text: repeat a word to reach ~1200 characters
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Hello World! " * 100
        
        # Page 2 text: simple small text
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "This is page 2 text content."
        
        mock_reader_instance.pages = [mock_page1, mock_page2]
        mock_pdf_reader.return_value = mock_reader_instance

        # Execute splitter
        chunks = PDFIngestionService.extract_and_split_pdf("dummy_stream")

        # Assertions
        # Page 1 should split into at least 2 chunks (size 1000, overlap 200)
        self.assertTrue(len(chunks) >= 2)
        self.assertEqual(chunks[0]['page_number'], 1)
        self.assertTrue(len(chunks[0]['content']) <= 1000)
        self.assertEqual(chunks[-1]['page_number'], 2)
        self.assertEqual(chunks[-1]['content'], "This is page 2 text content.")

    @patch('vault.services.PdfReader')
    def test_extract_and_split_pdf_empty_text(self, mock_pdf_reader):
        mock_reader_instance = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = ""  # Empty text (scanned PDF)
        
        mock_reader_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader_instance

        chunks = PDFIngestionService.extract_and_split_pdf("dummy_stream")
        
        # Assertions
        self.assertEqual(chunks, [])
