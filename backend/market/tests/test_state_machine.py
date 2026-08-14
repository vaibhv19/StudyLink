from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from market.models import Listing, ListingRequest, ListingStatusHistory

User = get_user_model()

class StateMachineTests(APITestCase):
    def setUp(self):
        # Create users
        self.owner = User.objects.create_user(
            email='owner@example.edu',
            password='StrongPassword123!',
            full_name='Listing Owner'
        )
        self.buyer1 = User.objects.create_user(
            email='buyer1@example.edu',
            password='StrongPassword123!',
            full_name='Buyer One'
        )
        self.buyer2 = User.objects.create_user(
            email='buyer2@example.edu',
            password='StrongPassword123!',
            full_name='Buyer Two'
        )
        self.third_party = User.objects.create_user(
            email='other@example.edu',
            password='StrongPassword123!',
            full_name='Third Party User'
        )

        # Create listing
        self.listing = Listing.objects.create(
            owner=self.owner,
            title='Quark Physics Lab Manual',
            status='AVAILABLE',
            photo_url='listings/manual.jpg',
            pickup_area='Physics Dept Lab 4',
            condition='New',
            is_active=True
        )

        # URLs
        self.request_url = reverse('request-item', kwargs={'id': self.listing.id})
        self.complete_url = reverse('listing-complete', kwargs={'id': self.listing.id})
        self.history_url = reverse('listing-history', kwargs={'id': self.listing.id})

    def test_request_item_rules(self):
        # 1. Owner cannot request their own listing
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.request_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # 2. Buyer can request item
        self.client.force_authenticate(user=self.buyer1)
        response = self.client.post(self.request_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ListingRequest.objects.count(), 1)
        self.assertEqual(ListingRequest.objects.first().status, 'PENDING')

        # 3. Duplicate request is rejected
        response = self.client.post(self.request_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accept_request_state_transition(self):
        # Create requests
        req1 = ListingRequest.objects.create(listing=self.listing, requester=self.buyer1, status='PENDING')
        req2 = ListingRequest.objects.create(listing=self.listing, requester=self.buyer2, status='PENDING')

        accept_url = reverse('request-accept', kwargs={'id': req1.id})

        # 1. Non-owner cannot accept request
        self.client.force_authenticate(user=self.buyer1)
        response = self.client.post(accept_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 2. Owner accepts request successfully
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(accept_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check states
        self.listing.refresh_from_db()
        req1.refresh_from_db()
        req2.refresh_from_db()

        self.assertEqual(self.listing.status, 'REQUESTED')
        self.assertEqual(req1.status, 'ACCEPTED')
        self.assertEqual(req2.status, 'REJECTED')

        # Check status history record created
        self.assertEqual(ListingStatusHistory.objects.count(), 1)
        history = ListingStatusHistory.objects.first()
        self.assertEqual(history.from_status, 'AVAILABLE')
        self.assertEqual(history.to_status, 'REQUESTED')
        self.assertEqual(history.changed_by, self.owner)

    def test_cancel_request_by_owner(self):
        req = ListingRequest.objects.create(listing=self.listing, requester=self.buyer1, status='ACCEPTED')
        self.listing.status = 'REQUESTED'
        self.listing.save()

        cancel_url = reverse('request-cancel', kwargs={'id': req.id})

        # 1. Non-related user cannot cancel
        self.client.force_authenticate(user=self.third_party)
        response = self.client.post(cancel_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 2. Owner cancels -> status is REJECTED and listing becomes AVAILABLE
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(cancel_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.listing.refresh_from_db()
        req.refresh_from_db()
        self.assertEqual(self.listing.status, 'AVAILABLE')
        self.assertEqual(req.status, 'REJECTED')

        # Verify audit history
        history = ListingStatusHistory.objects.filter(to_status='AVAILABLE').first()
        self.assertIsNotNone(history)
        self.assertEqual(history.changed_by, self.owner)

    def test_cancel_request_by_requester(self):
        req = ListingRequest.objects.create(listing=self.listing, requester=self.buyer1, status='ACCEPTED')
        self.listing.status = 'REQUESTED'
        self.listing.save()

        cancel_url = reverse('request-cancel', kwargs={'id': req.id})

        # Requester cancels -> status is WITHDRAWN and listing becomes AVAILABLE
        self.client.force_authenticate(user=self.buyer1)
        response = self.client.post(cancel_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.listing.refresh_from_db()
        req.refresh_from_db()
        self.assertEqual(self.listing.status, 'AVAILABLE')
        self.assertEqual(req.status, 'WITHDRAWN')

        # Verify audit history
        history = ListingStatusHistory.objects.filter(to_status='AVAILABLE').first()
        self.assertIsNotNone(history)
        self.assertEqual(history.changed_by, self.buyer1)

    def test_complete_handoff(self):
        # Setup accepted request state
        req = ListingRequest.objects.create(listing=self.listing, requester=self.buyer1, status='ACCEPTED')
        self.listing.status = 'REQUESTED'
        self.listing.save()

        # 1. Non-owner cannot complete handoff
        self.client.force_authenticate(user=self.buyer1)
        response = self.client.post(self.complete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 2. Owner completes handoff
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.complete_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.listing.refresh_from_db()
        self.assertEqual(self.listing.status, 'GIVEN_AWAY')

        # Check status history
        history = ListingStatusHistory.objects.filter(to_status='GIVEN_AWAY').first()
        self.assertIsNotNone(history)
        self.assertEqual(history.changed_by, self.owner)

    def test_history_api_permissions(self):
        # 1. Guest/non-owner is forbidden
        self.client.force_authenticate(user=self.buyer1)
        response = self.client.get(self.history_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 2. Owner can view history
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.history_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
