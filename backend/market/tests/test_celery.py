from django.test import TestCase, override_settings
from unittest.mock import patch
import requests
import redis
from celery.exceptions import Retry

from vault.tasks import process_pdf_document_task
from market.tasks import dispatch_marketplace_alerts_task

@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class CeleryIntegrationTests(TestCase):
    def test_process_pdf_document_task_success(self):
        # Execute the task eagerly using .delay()
        result = process_pdf_document_task.delay("doc-123")
        self.assertEqual(result.get(), "Processed document doc-123")

    def test_dispatch_marketplace_alerts_task_success(self):
        # Execute the task eagerly using .delay()
        result = dispatch_marketplace_alerts_task.delay("listing-456")
        self.assertEqual(result.get(), "Alerts dispatched for listing listing-456")

    @patch('vault.tasks.process_pdf_document_task.retry')
    def test_process_pdf_document_task_retry(self, mock_retry):
        # Mock retry to raise Celery's internal Retry exception
        mock_retry.side_effect = Retry("Simulated Retry", None)
        
        # When simulate_error is passed, it should trigger retry
        with self.assertRaises(Retry):
            process_pdf_document_task("simulate_error")
            
        mock_retry.assert_called_once()
        # Verify that exc argument is passed as a RequestException
        args, kwargs = mock_retry.call_args
        self.assertIsInstance(kwargs['exc'], requests.exceptions.RequestException)
        self.assertTrue(kwargs['countdown'] > 0)

    @patch('market.tasks.dispatch_marketplace_alerts_task.retry')
    def test_dispatch_marketplace_alerts_task_retry(self, mock_retry):
        # Mock retry to raise Celery's internal Retry exception
        mock_retry.side_effect = Retry("Simulated Retry", None)
        
        # When simulate_error is passed, it should trigger retry
        with self.assertRaises(Retry):
            dispatch_marketplace_alerts_task("simulate_error")
            
        mock_retry.assert_called_once()
        # Verify that exc argument is passed as a ConnectionError
        args, kwargs = mock_retry.call_args
        self.assertIsInstance(kwargs['exc'], redis.exceptions.ConnectionError)
        self.assertTrue(kwargs['countdown'] > 0)
