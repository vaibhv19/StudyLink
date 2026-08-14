from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task(name='market.tasks.dispatch_marketplace_alerts_task')
def dispatch_marketplace_alerts_task(listing_id):
    logger.info("Task market.tasks.dispatch_marketplace_alerts_task started for listing_id: %s", listing_id)
    # Skeleton implementation for Phase 06
    logger.info("Task market.tasks.dispatch_marketplace_alerts_task completed for listing_id: %s", listing_id)
    return f"Alerts dispatched for listing {listing_id}"
