import os
import sys
# Disable C-extension for protobuf on Python 3.14 to avoid metaclass tp_new TypeError
sys.modules['google._upb._message'] = None
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

from django.test import TestCase, SimpleTestCase, override_settings
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from google.api_core.exceptions import ResourceExhausted

from vault.models import Resource, ResourceChunk, Subject, Course
from vault.tasks import process_pdf_document_task
from rag.client import GeminiClient

User = get_user_model()

class GeminiClientTests(SimpleTestCase):
    @patch('google.generativeai.embed_content')
    def test_get_embedding_success(self, mock_embed):
        # Configure mock to return 768-dimensional vector
        mock_embed.return_value = {'embedding': [0.05] * 768}

        emb = GeminiClient.get_embedding("Test document content")

        self.assertEqual(len(emb), 768)
        self.assertEqual(emb[0], 0.05)
        mock_embed.assert_called_once_with(
            model="models/text-embedding-004",
            content="Test document content",
            task_type="retrieval_document"
        )

    @patch('google.generativeai.embed_content')
    def test_get_embedding_quota_exception(self, mock_embed):
        # Configure mock to raise a ResourceExhausted quota/rate-limit exception
        mock_embed.side_effect = ResourceExhausted("API rate limit exceeded")

        with self.assertRaises(ResourceExhausted):
            GeminiClient.get_embedding("Test document content")


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class CeleryIngestionTaskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@studylink.com", password="password123")
        self.subject = Subject.objects.create(name="Computer Science", slug="computer-science")
        self.course = Course.objects.create(subject=self.subject, name="Intro to Programming", code="CS101")
        self.resource = Resource.objects.create(
            uploader=self.user,
            title="Lecture Notes",
            file_path="resources/dummy.pdf",
            subject=self.subject,
            course=self.course,
            status='PROCESSING'
        )

    @patch('vault.tasks.GeminiClient.get_embedding')
    @patch('vault.services.PdfReader')
    @patch('django.core.files.storage.Storage.open')
    def test_process_pdf_document_task_success(self, mock_storage_open, mock_pdf_reader, mock_get_embedding):
        # Setup mocks
        mock_storage_open.return_value = MagicMock()
        
        mock_reader_instance = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "This is some PDF text to split."
        mock_reader_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader_instance

        mock_get_embedding.return_value = [0.1] * 768

        # Execute Celery task synchronously
        process_pdf_document_task(self.resource.id)

        # Assert status updated to READY
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.status, 'READY')

        # Assert chunks persisted in DB
        chunks = ResourceChunk.objects.filter(resource=self.resource)
        self.assertEqual(chunks.count(), 1)
        self.assertEqual(chunks[0].content, "This is some PDF text to split.")
        self.assertEqual(chunks[0].page_number, 1)
        self.assertEqual(chunks[0].embedding, [0.1] * 768)

    @patch('vault.services.PdfReader')
    @patch('django.core.files.storage.Storage.open')
    def test_process_pdf_document_task_unsearchable(self, mock_storage_open, mock_pdf_reader):
        mock_storage_open.return_value = MagicMock()
        
        mock_reader_instance = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = ""  # No text
        mock_reader_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader_instance

        # Execute task
        process_pdf_document_task(self.resource.id)

        # Assert status updated to UNSEARCHABLE and no chunks stored
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.status, 'UNSEARCHABLE')
        self.assertEqual(ResourceChunk.objects.filter(resource=self.resource).count(), 0)

    @patch('django.core.files.storage.Storage.open')
    def test_process_pdf_document_task_failed(self, mock_storage_open):
        # Setup file open to raise an exception
        mock_storage_open.side_effect = Exception("Storage connection timeout")

        # Execute task and expect error to raise
        with self.assertRaises(Exception):
            process_pdf_document_task(self.resource.id)

        # Assert status updated to FAILED
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.status, 'FAILED')
