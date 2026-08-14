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

def cancel_request(user, request_id):
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

        # Check authorization: user must be listing owner or the requester
        is_owner = (listing.owner == user)
        is_requester = (request_obj.requester == user)

        if not is_owner and not is_requester:
            raise PermissionDenied("You do not have permission to cancel this request.")

        old_status = listing.status
        old_request_status = request_obj.status

        # Revert listing status back to AVAILABLE if this request was the accepted one
        listing_status_changed = False
        if old_request_status == 'ACCEPTED':
            listing.status = 'AVAILABLE'
            listing.save(update_fields=['status'])
            listing_status_changed = True

        # Update request status
        if is_owner:
            request_obj.status = 'REJECTED'
        else:
            request_obj.status = 'WITHDRAWN'
        request_obj.save(update_fields=['status'])

        # Write ListingStatusHistory record if listing status reverted
        if listing_status_changed:
            reason = "Request cancelled by owner" if is_owner else "Request withdrawn by requester"
            ListingStatusHistory.objects.create(
                listing=listing,
                from_status=old_status,
                to_status='AVAILABLE',
                changed_by=user,
                reason=reason
            )

        return request_obj

