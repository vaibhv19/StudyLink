import uuid
from django.db import models
from django.conf import settings


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        NEW_REQUEST = 'NEW_REQUEST', 'New Request'
        REQUEST_ACCEPTED = 'REQUEST_ACCEPTED', 'Request Accepted'
        REQUEST_CANCELED = 'REQUEST_CANCELED', 'Request Canceled'
        ITEM_CLAIMED = 'ITEM_CLAIMED', 'Item Claimed'
        UPVOTE_RECEIVED = 'UPVOTE_RECEIVED', 'Upvote Received'
        NEW_COMMENT = 'NEW_COMMENT', 'New Comment'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        db_index=True
    )
    type = models.CharField(
        max_length=50,
        choices=NotificationType.choices
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['recipient', 'created_at']),
        ]

    def __str__(self):
        return f"Notification({self.recipient.email} - {self.type} - {self.title})"
