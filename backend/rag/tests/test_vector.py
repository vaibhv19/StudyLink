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
from rag.search import VectorSearchService, RAGAnswerService

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
        self.assertEqual(list(chunks[0].embedding), [0.1] * 768)

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


class VectorSearchTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="search@studylink.com", password="password123")
        self.subject = Subject.objects.create(name="Mathematics", slug="math")
        self.course = Course.objects.create(subject=self.subject, name="Calculus I", code="MATH101")
        
        # Resource A (Target)
        self.resource_a = Resource.objects.create(
            uploader=self.user,
            title="Calculus Notes A",
            file_path="resources/math_a.pdf",
            subject=self.subject,
            course=self.course,
            status='READY'
        )
        # Resource B (Boundary/Other)
        self.resource_b = Resource.objects.create(
            uploader=self.user,
            title="Calculus Notes B",
            file_path="resources/math_b.pdf",
            subject=self.subject,
            course=self.course,
            status='READY'
        )

        # Insert 6 chunks for Resource A with varying similarities
        # Use orthogonal direction components to vary cosine distance
        self.chunk_a1 = ResourceChunk.objects.create(
            resource=self.resource_a,
            content="Derivative represents instantaneous rate of change.",
            page_number=1,
            embedding=[1.0] + [0.0] * 767  # Cosine Dist = 0.0 (exact match)
        )
        self.chunk_a2 = ResourceChunk.objects.create(
            resource=self.resource_a,
            content="Integral represents area under the curve.",
            page_number=2,
            embedding=[0.9, 0.1] + [0.0] * 766  # Cosine Dist = 0.006
        )
        self.chunk_a3 = ResourceChunk.objects.create(
            resource=self.resource_a,
            content="Limits describe function behavior near a point.",
            page_number=3,
            embedding=[0.8, 0.2] + [0.0] * 766  # Cosine Dist = 0.0299
        )
        self.chunk_a4 = ResourceChunk.objects.create(
            resource=self.resource_a,
            content="Continuity requires limit equals function value.",
            page_number=4,
            embedding=[0.7, 0.3] + [0.0] * 766  # Cosine Dist = 0.0808
        )
        self.chunk_a5 = ResourceChunk.objects.create(
            resource=self.resource_a,
            content="Mean value theorem guarantees tangent parallel to secant.",
            page_number=5,
            embedding=[0.6, 0.4] + [0.0] * 766  # Cosine Dist = 0.168
        )
        self.chunk_a6 = ResourceChunk.objects.create(
            resource=self.resource_a,
            content="Chain rule for composite function derivatives.",
            page_number=6,
            embedding=[0.1, 0.9] + [0.0] * 766  # Cosine Dist = 0.889 (very far)
        )

        # Insert 1 chunk for Resource B with exact matching embedding
        self.chunk_b = ResourceChunk.objects.create(
            resource=self.resource_b,
            content="Resource B content with same match.",
            page_number=1,
            embedding=[1.0] + [0.0] * 767
        )

    def test_similarity_search_scoping_and_ordering(self):
        query_embedding = [1.0] + [0.0] * 767

        # Execute similarity search on Resource A
        results = VectorSearchService.similarity_search(self.resource_a.id, query_embedding)

        # 1. Enforces Cap: Returns exactly 5 matching chunks (ignoring the 6th farthest one)
        self.assertEqual(len(results), 5)

        # 2. Scope boundary: None of the chunks from Resource B are returned
        for chunk, dist in results:
            self.assertEqual(chunk.resource_id, self.resource_a.id)
            self.assertNotEqual(chunk.id, self.chunk_b.id)

        # 3. Order constraint: Ordered ascending by cosine distance (highest similarity first)
        self.assertEqual(results[0][0].id, self.chunk_a1.id)
        self.assertEqual(results[1][0].id, self.chunk_a2.id)
        self.assertEqual(results[2][0].id, self.chunk_a3.id)
        self.assertEqual(results[3][0].id, self.chunk_a4.id)
        self.assertEqual(results[4][0].id, self.chunk_a5.id)

        # 4. Valid distances
        self.assertAlmostEqual(results[0][1], 0.0) # Exact match distance is 0
        self.assertTrue(results[4][1] > results[0][1])

    @patch('rag.search.GeminiClient.generate_answer')
    @patch('rag.search.GeminiClient.get_embedding')
    def test_answer_query_cutoff_triggers_rejection(self, mock_get_embedding, mock_generate_answer):
        # Mock query vector to have very low similarity (< 0.65 similarity, i.e., > 0.35 distance)
        mock_get_embedding.return_value = [0.0, 0.0, 1.0] + [0.0] * 765

        response = RAGAnswerService.answer_query(self.resource_a.id, "What is Calculus?")

        # Assert fallback is triggered
        self.assertEqual(response['answer'], "I couldn't find any relevant information in this specific document to answer that.")
        self.assertEqual(response['citations'], [])
        
        # Verify LLM generation is bypassed
        mock_generate_answer.assert_not_called()

    @patch('rag.search.GeminiClient.generate_answer')
    @patch('rag.search.GeminiClient.get_embedding')
    def test_answer_query_strong_match_calls_llm(self, mock_get_embedding, mock_generate_answer):
        # Mock query vector to have exact match
        mock_get_embedding.return_value = [1.0] + [0.0] * 767
        mock_generate_answer.return_value = "Derivatives measure rate of change [Page 1]."

        response = RAGAnswerService.answer_query(self.resource_a.id, "What is derivative?")

        # Assert LLM was called and cited answer returned
        self.assertEqual(response['answer'], "Derivatives measure rate of change [Page 1].")
        self.assertEqual(response['citations'], [1, 2, 3, 4, 5])
        mock_generate_answer.assert_called_once()
