from django.db import transaction
from django.core.exceptions import ValidationError
from rest_framework.exceptions import PermissionDenied, APIException
from rest_framework import status
from market.models import Listing, ListingRequest, ListingStatusHistory

class ConflictError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Conflict'
    default_code = 'conflict'

def accept_request(owner, request_id):
    with transaction.atomic():
        try:
            request_obj = ListingRequest.objects.select_related('listing').get(id=request_id)
        except ListingRequest.DoesNotExist:
            raise ValidationError("Listing request not found.")

        # Lock parent listing row using pessimistic locking
        try:
            listing = Listing.objects.select_for_update().get(id=request_obj.listing_id)
        except Listing.DoesNotExist:
            raise ValidationError("Listing not found.")

        # Verify that owner is the owner of the listing
        if listing.owner != owner:
            raise PermissionDenied("You do not have permission to accept requests for this listing.")

        # Recheck current listing status while holding the lock
        if listing.status != 'AVAILABLE':
            raise ConflictError("This listing is already requested or given away.")

        old_status = listing.status
        listing.status = 'REQUESTED'
        listing.save(update_fields=['status'])

        request_obj.status = 'ACCEPTED'
        request_obj.save(update_fields=['status'])

        # Reject all other pending requests
        listing.requests.filter(status='PENDING').exclude(id=request_obj.id).update(status='REJECTED')

        # Write ListingStatusHistory record
        ListingStatusHistory.objects.create(
            listing=listing,
            from_status=old_status,
            to_status='REQUESTED',
            changed_by=owner,
            reason="Request accepted"
        )

        return request_obj
