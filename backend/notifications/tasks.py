from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from notifications.models import Notification

logger = get_task_logger(__name__)
User = get_user_model()


def send_notification_sync(recipient_id, notification_type, title, message):
    """
    Synchronously resolves recipient and writes a Notification database record.
    Executed in-process within transaction.on_commit hooks for v1.
    """
    logger.info(
        "Sending notification: recipient_id=%s, type=%s, title=%s",
        recipient_id, notification_type, title
    )
    try:
        try:
            recipient = User.objects.get(id=recipient_id)
        except ObjectDoesNotExist:
            logger.error("Recipient user with id %s does not exist. Aborting notification.", recipient_id)
            return None

        notification = Notification.objects.create(
            recipient=recipient,
            type=notification_type,
            title=title,
            message=message
        )
        logger.info(
            "Notification %s created successfully for recipient %s (type=%s)",
            notification.id, recipient.email, notification_type
        )
        return str(notification.id)
    except Exception as e:
        logger.exception("Error creating notification for recipient %s: %s", recipient_id, str(e))
        return None


@shared_task(bind=True, name='notifications.tasks.send_notification_task', max_retries=3)
def send_notification_task(self, recipient_id, notification_type, title, message):
    """
    Celery task wrapper around send_notification_sync for v2 async compatibility.
    """
    return send_notification_sync(recipient_id, notification_type, title, message)

