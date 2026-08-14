from django.db import transaction
from django.core.exceptions import ValidationError
from rest_framework.exceptions import PermissionDenied, APIException
from rest_framework import status
from market.models import Listing, ListingRequest, ListingStatusHistory
from notifications.tasks import send_notification_task

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

        # Collect other active/pending requester IDs before updating their status
        other_requester_ids = list(
            listing.requests.filter(status='PENDING')
            .exclude(id=request_obj.id)
            .values_list('requester_id', flat=True)
        )

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

        # Trigger notification to the selected recipient
        recipient_id = str(request_obj.requester_id)
        listing_title = listing.title
        pickup_area = listing.pickup_area or "Not specified"
        transaction.on_commit(lambda: send_notification_task.delay(
            recipient_id,
            'REQUEST_ACCEPTED',
            f"Request accepted for {listing_title}",
            f"Your request for '{listing_title}' was accepted! Pickup area: {pickup_area}."
        ))

        # Trigger notifications to other active requesters
        for other_id in other_requester_ids:
            other_id_str = str(other_id)
            transaction.on_commit(lambda oid=other_id_str: send_notification_task.delay(
                oid,
                'ITEM_CLAIMED',
                f"Item no longer available: {listing_title}",
                f"The item '{listing_title}' is no longer available as another request was accepted."
            ))

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

        # Trigger notification tasks
        listing_title = listing.title
        if is_owner:
            req_user_id = str(request_obj.requester_id)
            transaction.on_commit(lambda: send_notification_task.delay(
                req_user_id,
                'REQUEST_CANCELED',
                f"Request declined for {listing_title}",
                f"Your request for '{listing_title}' was declined by the owner."
            ))
        else:
            if old_request_status == 'ACCEPTED':
                owner_id = str(listing.owner_id)
                user_name = user.full_name or user.email
                transaction.on_commit(lambda: send_notification_task.delay(
                    owner_id,
                    'REQUEST_CANCELED',
                    f"Request withdrawn for {listing_title}",
                    f"{user_name} has withdrawn their accepted request for '{listing_title}'."
                ))

        return request_obj

def complete_handoff(owner, listing_id):
    with transaction.atomic():
        try:
            listing = Listing.objects.select_for_update().get(id=listing_id)
        except Listing.DoesNotExist:
            raise ValidationError("Listing not found.")

        # Verify ownership
        if listing.owner != owner:
            raise PermissionDenied("You do not have permission to modify this listing.")

        # Ensure listing is in a valid pre-terminal state
        if listing.status not in ['AVAILABLE', 'REQUESTED']:
            raise ValidationError("This listing cannot be marked as given away in its current state.")

        # Find accepted requester before completing handoff
        accepted_req = listing.requests.filter(status='ACCEPTED').first()

        old_status = listing.status
        listing.status = 'GIVEN_AWAY'
        listing.save(update_fields=['status'])

        # Write ListingStatusHistory record
        ListingStatusHistory.objects.create(
            listing=listing,
            from_status=old_status,
            to_status='GIVEN_AWAY',
            changed_by=owner,
            reason="Handoff completed"
        )

        # Notify accepted recipient
        if accepted_req:
            rec_id = str(accepted_req.requester_id)
            listing_title = listing.title
            transaction.on_commit(lambda: send_notification_task.delay(
                rec_id,
                'ITEM_CLAIMED',
                f"Handoff completed for {listing_title}",
                f"The handoff for '{listing_title}' has been completed."
            ))

        return listing


