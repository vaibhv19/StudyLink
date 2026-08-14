import random
import requests
import redis
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task(bind=True, name='vault.tasks.process_pdf_document_task', max_retries=3)
def process_pdf_document_task(self, document_id):
    logger.info("Task vault.tasks.process_pdf_document_task started for document_id: %s", document_id)
    try:
        # Task Skeleton ONLY - no actual processing in this phase
        if document_id == 'simulate_error':
            raise requests.exceptions.RequestException("Simulated connection error")
            
    except (requests.exceptions.RequestException, redis.exceptions.ConnectionError) as e:
        logger.warning(
            "Connection error in process_pdf_document_task. Retrying (attempt %s/%s)... Error: %s",
            self.request.retries + 1, self.max_retries, str(e)
        )
        countdown = 2 ** self.request.retries + random.uniform(1, 5)
        raise self.retry(exc=e, countdown=countdown)
        
    logger.info("Task vault.tasks.process_pdf_document_task completed for document_id: %s", document_id)
    return f"Processed document {document_id}"
