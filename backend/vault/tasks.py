import os
import sys
# Disable C-extension for protobuf on Python 3.14 to avoid metaclass tp_new TypeError
sys.modules['google._upb._message'] = None
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

import random
import requests
import redis
import logging
from celery import shared_task
from django.db import transaction
from google.api_core.exceptions import GoogleAPIError

from vault.models import Resource, ResourceChunk
from vault.services import PDFIngestionService
from rag.client import GeminiClient

logger = logging.getLogger(__name__)

@shared_task(bind=True, name='vault.tasks.process_pdf_document_task', max_retries=3)
def process_pdf_document_task(self, resource_id):
    logger.info("Task vault.tasks.process_pdf_document_task started for resource_id: %s", resource_id)
    
    try:
        try:
            resource = Resource.objects.get(id=resource_id)
        except Resource.DoesNotExist:
            logger.error("Resource %s does not exist", resource_id)
            return f"Resource {resource_id} does not exist"
            
        resource.status = 'PROCESSING'
        resource.save()
        
        # Open PDF from storage stream
        with resource.file_path.open('rb') as f:
            chunks = PDFIngestionService.extract_and_split_pdf(f)
            
        if not chunks:
            resource.status = 'UNSEARCHABLE'
            resource.save()
            logger.info("Resource %s contains no extractable text, status set to UNSEARCHABLE", resource_id)
            return f"Resource {resource_id} is UNSEARCHABLE"
            
        chunk_instances = []
        for chunk in chunks:
            # Query Gemini embeddings
            embedding = GeminiClient.get_embedding(chunk['content'])
            
            chunk_instances.append(ResourceChunk(
                resource=resource,
                content=chunk['content'],
                page_number=chunk['page_number'],
                embedding=embedding
            ))
            
        # Atomic transactional save
        with transaction.atomic():
            ResourceChunk.objects.filter(resource=resource).delete()
            ResourceChunk.objects.bulk_create(chunk_instances)
            
            resource.status = 'READY'
            resource.save()
            
        logger.info("Resource %s processed successfully, created %d chunks, status set to READY", resource_id, len(chunk_instances))
        return f"Resource {resource_id} processed successfully: {len(chunk_instances)} chunks created"
        
    except Exception as e:
        logger.exception("Error processing resource %s: %s", resource_id, str(e))
        # Attempt to set to FAILED if resource was resolved
        try:
            resource_obj = Resource.objects.get(id=resource_id)
            resource_obj.status = 'FAILED'
            resource_obj.save()
        except Exception as save_err:
            logger.error("Failed to update status to FAILED for resource %s: %s", resource_id, str(save_err))
            
        # Retry policies wrapper for connection/network/API limit failures
        if isinstance(e, (requests.exceptions.RequestException, redis.exceptions.ConnectionError, GoogleAPIError)):
            countdown = 2 ** self.request.retries + random.uniform(1, 5)
            raise self.retry(exc=e, countdown=countdown)
            
        raise e
