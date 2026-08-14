import uuid
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from core.models import Subject, Course
from vault.models import Resource, ResourceChunk

User = get_user_model()

class ChatAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="student@university.edu",
            password="StrongPassword123!",
            full_name="Alice"
        )
        self.client.force_authenticate(user=self.user)

        self.subject = Subject.objects.create(name="Computer Science", slug="cs")
        self.course = Course.objects.create(
            name="Data Structures",
            code="CS101",
            subject=self.subject
        )

        self.ready_resource = Resource.objects.create(
            uploader=self.user,
            title="Data Structures Lecture 1",
            subject=self.subject,
            course=self.course,
            status='READY',
            file_path='resources/sample.pdf'
        )

        self.processing_resource = Resource.objects.create(
            uploader=self.user,
            title="Data Structures Lecture 2",
            subject=self.subject,
            course=self.course,
            status='PROCESSING',
            file_path='resources/sample2.pdf'
        )

        self.failed_resource = Resource.objects.create(
            uploader=self.user,
            title="Data Structures Lecture 3",
            subject=self.subject,
            course=self.course,
            status='FAILED',
            file_path='resources/sample3.pdf'
        )

        # Create chunks for ready_resource
        ResourceChunk.objects.create(
            resource=self.ready_resource,
            content="Binary Search has O(log n) time complexity.",
            page_number=1,
            embedding=[1.0] + [0.0] * 767
        )

        self.url = reverse('chat-query')

    def test_unauthenticated_request_rejected(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url, {
            "resource_id": str(self.ready_resource.id),
            "query": "What is binary search?"
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_query_parameter(self):
        response = self.client.post(self.url, {
            "resource_id": str(self.ready_resource.id)
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 'invalid_request')
        self.assertIn('query', response.data['fields'])

    def test_missing_resource_id(self):
        response = self.client.post(self.url, {
            "query": "What is binary search?"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 'invalid_request')
        self.assertIn('resource_id', response.data['fields'])

    def test_non_existent_resource(self):
        random_uuid = str(uuid.uuid4())
        response = self.client.post(self.url, {
            "resource_id": random_uuid,
            "query": "What is binary search?"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('resource_id', response.data['fields'])

    def test_resource_not_ready_rejected(self):
        # Processing resource
        response = self.client.post(self.url, {
            "resource_id": str(self.processing_resource.id),
            "query": "What is binary search?"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('resource_id', response.data['fields'])

        # Failed resource
        response = self.client.post(self.url, {
            "resource_id": str(self.failed_resource.id),
            "query": "What is binary search?"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('resource_id', response.data['fields'])

    @patch('rag.search.GeminiClient.generate_answer')
    @patch('rag.search.GeminiClient.get_embedding')
    def test_successful_query_returns_answer_and_citations(self, mock_get_embedding, mock_generate_answer):
        mock_get_embedding.return_value = [1.0] + [0.0] * 767
        mock_generate_answer.return_value = "Binary search runs in O(log n) time [Page 1]."

        response = self.client.post(self.url, {
            "resource_id": str(self.ready_resource.id),
            "query": "What is the time complexity of Binary Search?"
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['answer'], "Binary search runs in O(log n) time [Page 1].")
        self.assertEqual(response.data['citations'], [1])
        self.assertEqual(len(response.data['sources']), 1)
        self.assertEqual(response.data['sources'][0]['page_number'], 1)
        self.assertEqual(response.data['sources'][0]['excerpt'], "Binary Search has O(log n) time complexity.")
        self.assertAlmostEqual(response.data['sources'][0]['similarity_score'], 1.0)

    @patch('rag.search.GeminiClient.generate_answer')
    @patch('rag.search.GeminiClient.get_embedding')
    def test_low_similarity_triggers_fallback_refusal(self, mock_get_embedding, mock_generate_answer):
        # Orthogonal embedding -> similarity 0.0 (< 0.65)
        mock_get_embedding.return_value = [0.0] * 768

        response = self.client.post(self.url, {
            "resource_id": str(self.ready_resource.id),
            "query": "What is photosynthesis?"
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['answer'], "I couldn't find any relevant information in this specific document to answer that.")
        self.assertEqual(response.data['citations'], [])
        self.assertEqual(response.data['sources'], [])
        mock_generate_answer.assert_not_called()
