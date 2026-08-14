import uuid
from django.db import models
from django.conf import settings
from core.models import Subject, Course
from market.storage import ListingStorage

class Listing(models.Model):
    STATUS_CHOICES = (
        ('AVAILABLE', 'Available'),
        ('REQUESTED', 'Requested'),
        ('GIVEN_AWAY', 'Given Away'),
    )
    
    CONDITION_CHOICES = (
        ('New', 'New'),
        ('Used - Good', 'Used - Good'),
        ('Used - Fair', 'Used - Fair'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listings"
    )
    title = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='AVAILABLE',
        db_index=True
    )
    photo_url = models.FileField(storage=ListingStorage())
    pickup_area = models.TextField()
    condition = models.CharField(
        max_length=50,
        choices=CONDITION_CHOICES
    )
    is_active = models.BooleanField(default=True, db_index=True)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="listings"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="listings"
    )

    class Meta:
        indexes = [
            models.Index(fields=['status', 'is_active']),
        ]

    def __str__(self):
        return self.title

class ListingRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('WITHDRAWN', 'Withdrawn'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="requests"
    )
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_requests"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('listing', 'requester')

    def __str__(self):
        return f"Request by {self.requester.email} for {self.listing.title}"

class ListingStatusHistory(models.Model):
    id = models.BigAutoField(primary_key=True)
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="status_history"
    )
    from_status = models.CharField(max_length=20)
    to_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )
    reason = models.TextField(null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.listing.title}: {self.from_status} -> {self.to_status}"
