import os
import sys
# Disable C-extension for protobuf on Python 3.14 to avoid metaclass tp_new TypeError
sys.modules['google._upb._message'] = None
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

from django.test import TestCase, override_settings
from unittest.mock import patch, MagicMock
import requests
import redis
import uuid
from celery.exceptions import Retry

from vault.tasks import process_pdf_document_task
from market.tasks import dispatch_marketplace_alerts_task

@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class CeleryIntegrationTests(TestCase):
    @patch('vault.tasks.Resource.objects.get')
    def test_process_pdf_document_task_success(self, mock_get):
        dummy_uuid = str(uuid.uuid4())
        mock_resource = MagicMock()
        mock_resource.id = dummy_uuid
        mock_resource.status = 'PROCESSING'
        mock_resource.file_path.open.return_value.__enter__.return_value = MagicMock()
        mock_get.return_value = mock_resource
        
        with patch('vault.tasks.PDFIngestionService.extract_and_split_pdf', return_value=[]):
            result = process_pdf_document_task.delay(dummy_uuid)
            self.assertEqual(result.get(), f"Resource {dummy_uuid} is UNSEARCHABLE")

    def test_dispatch_marketplace_alerts_task_success(self):
        # Execute the task eagerly using .delay()
        result = dispatch_marketplace_alerts_task.delay("listing-456")
        self.assertEqual(result.get(), "Alerts dispatched for listing listing-456")

    @patch('vault.tasks.Resource.objects.get')
    @patch('celery.app.task.Task.retry')
    def test_process_pdf_document_task_retry(self, mock_retry, mock_get):
        dummy_uuid = str(uuid.uuid4())
        mock_get.side_effect = requests.exceptions.RequestException("Simulated connection error")
        mock_retry.side_effect = Retry("Simulated Retry", None)
        
        with self.assertRaises(Retry):
            process_pdf_document_task(dummy_uuid)
            
        mock_retry.assert_called_once()
        args, kwargs = mock_retry.call_args
        self.assertIsInstance(kwargs['exc'], requests.exceptions.RequestException)
        self.assertTrue(kwargs['countdown'] > 0)

    @patch('celery.app.task.Task.retry')
    def test_dispatch_marketplace_alerts_task_retry(self, mock_retry):
        mock_retry.side_effect = Retry("Simulated Retry", None)
        
        # When simulate_error is passed, it should trigger retry
        with self.assertRaises(Retry):
            dispatch_marketplace_alerts_task("simulate_error")
            
        mock_retry.assert_called_once()
        args, kwargs = mock_retry.call_args
        self.assertIsInstance(kwargs['exc'], redis.exceptions.ConnectionError)
        self.assertTrue(kwargs['countdown'] > 0)
