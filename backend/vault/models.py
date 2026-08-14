import uuid
from django.db import models
from django.conf import settings
from core.models import Subject, Course
from vault.storage import ResourceStorage

class Resource(models.Model):
    STATUS_CHOICES = (
        ('PROCESSING', 'Processing'),
        ('READY', 'Ready'),
        ('FAILED', 'Failed'),
        ('UNSEARCHABLE', 'Unsearchable'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uploaded_resources"
    )
    title = models.CharField(max_length=255)
    file_path = models.FileField(storage=ResourceStorage())
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PROCESSING'
    )
    is_active = models.BooleanField(default=True)
    upvote_count = models.IntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['subject']),
            models.Index(fields=['course']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.title

class ResourceUpvote(models.Model):
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name="upvotes"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('resource', 'user')

class DoubtBoardComment(models.Model):
    id = models.AutoField(primary_key=True)
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies"
    )
    content = models.TextField()
    is_solved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.email} on {self.resource.title}"
