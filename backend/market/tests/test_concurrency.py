import threading
import queue
from django.db import connection
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITransactionTestCase
from market.models import Listing, ListingRequest

User = get_user_model()

class ConcurrencyTests(APITransactionTestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.edu',
            password='StrongPassword123!',
            full_name='Owner'
        )
        self.buyer1 = User.objects.create_user(
            email='buyer1@example.edu',
            password='StrongPassword123!',
            full_name='Buyer 1'
        )
        self.buyer2 = User.objects.create_user(
            email='buyer2@example.edu',
            password='StrongPassword123!',
            full_name='Buyer 2'
        )
        self.listing = Listing.objects.create(
            owner=self.owner,
            title='Textbook',
            status='AVAILABLE',
            photo_url='listings/book.jpg',
            pickup_area='Campus',
            condition='New',
            is_active=True
        )
        self.req1 = ListingRequest.objects.create(listing=self.listing, requester=self.buyer1, status='PENDING')
        self.req2 = ListingRequest.objects.create(listing=self.listing, requester=self.buyer2, status='PENDING')

    def test_concurrent_accept_requests(self):
        if connection.vendor == 'sqlite':
            self.skipTest("SQLite does not support row-level pessimistic locks (SELECT FOR UPDATE) under concurrent threads.")

        accept_url1 = reverse('request-accept', kwargs={'id': self.req1.id})
        accept_url2 = reverse('request-accept', kwargs={'id': self.req2.id})

        results = queue.Queue()

        def make_request(url, user):
            from rest_framework.test import APIClient
            client = APIClient()
            client.force_authenticate(user=user)
            try:
                response = client.post(url)
                results.put(response)
            except Exception as e:
                results.put(e)

        # Start two threads representing concurrent accept requests
        t1 = threading.Thread(target=make_request, args=(accept_url1, self.owner))
        t2 = threading.Thread(target=make_request, args=(accept_url2, self.owner))

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        # Gather responses
        responses = []
        while not results.empty():
            responses.append(results.get())

        # Verify that exactly one accepted transition succeeded (200 OK)
        successes = [r for r in responses if hasattr(r, 'status_code') and r.status_code == status.HTTP_200_OK]
        conflicts = [r for r in responses if hasattr(r, 'status_code') and r.status_code == status.HTTP_409_CONFLICT]
        failures = [r for r in responses if not hasattr(r, 'status_code') or r.status_code not in [200, 409]]

        # Exactly one acceptance must succeed
        self.assertEqual(len(successes), 1)
        
        # Verify final database state is consistent
        self.listing.refresh_from_db()
        self.req1.refresh_from_db()
        self.req2.refresh_from_db()
        
        self.assertEqual(self.listing.status, 'REQUESTED')
        
        # Verify that the requests have the correct status (one accepted, one rejected)
        accepted_reqs = [r for r in [self.req1, self.req2] if r.status == 'ACCEPTED']
        rejected_reqs = [r for r in [self.req1, self.req2] if r.status == 'REJECTED']
        
        self.assertEqual(len(accepted_reqs), 1)
        self.assertEqual(len(rejected_reqs), 1)
