import os
import sys
# Disable C-extension for protobuf on Python 3.14 to avoid metaclass tp_new TypeError
sys.modules['google._upb._message'] = None
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

from django.test import SimpleTestCase
from unittest.mock import patch, MagicMock
from google.api_core.exceptions import ResourceExhausted
from rag.client import GeminiClient

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
