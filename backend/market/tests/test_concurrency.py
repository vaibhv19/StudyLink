import threading
import queue
from unittest.mock import patch
from django.db import connection
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITransactionTestCase, APIClient
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
        self.buyer3 = User.objects.create_user(
            email='buyer3@example.edu',
            password='StrongPassword123!',
            full_name='Buyer 3'
        )
        self.listing = Listing.objects.create(
            owner=self.owner,
            title='Calculus Textbook 8th Edition',
            status='AVAILABLE',
            photo_url='listings/book.jpg',
            pickup_area='Campus Library Lobby',
            condition='Used - Good',
            is_active=True
        )
        self.req1 = ListingRequest.objects.create(listing=self.listing, requester=self.buyer1, status='PENDING')
        self.req2 = ListingRequest.objects.create(listing=self.listing, requester=self.buyer2, status='PENDING')
        self.req3 = ListingRequest.objects.create(listing=self.listing, requester=self.buyer3, status='PENDING')

    @patch('market.services.send_notification_task.delay')
    def test_concurrent_accept_requests(self, mock_notify):
        """
        Verify that multiple concurrent threads attempting to accept different requests
        for the same listing result in exactly ONE successful 200 OK acceptance,
        while competing acceptance attempts are rejected with 409 Conflict.
        """
        if connection.vendor == 'sqlite':
            self.skipTest("SQLite does not support row-level pessimistic locks (SELECT FOR UPDATE) under concurrent threads.")

        accept_url1 = reverse('request-accept', kwargs={'id': self.req1.id})
        accept_url2 = reverse('request-accept', kwargs={'id': self.req2.id})
        accept_url3 = reverse('request-accept', kwargs={'id': self.req3.id})

        results = queue.Queue()

        def make_request(url, user):
            client = APIClient()
            client.force_authenticate(user=user)
            try:
                response = client.post(url)
                results.put(response)
            except Exception as e:
                results.put(e)

        # Start concurrent threads representing simultaneous acceptance attempts
        t1 = threading.Thread(target=make_request, args=(accept_url1, self.owner))
        t2 = threading.Thread(target=make_request, args=(accept_url2, self.owner))
        t3 = threading.Thread(target=make_request, args=(accept_url3, self.owner))

        t1.start()
        t2.start()
        t3.start()

        t1.join()
        t2.join()
        t3.join()

        # Gather responses
        responses = []
        while not results.empty():
            responses.append(results.get())

        # Verify that exactly one accepted transition succeeded (200 OK)
        successes = [r for r in responses if hasattr(r, 'status_code') and r.status_code == status.HTTP_200_OK]
        conflicts = [r for r in responses if hasattr(r, 'status_code') and r.status_code == status.HTTP_409_CONFLICT]

        # Exactly one acceptance must succeed
        self.assertEqual(len(successes), 1)
        # Remaining competing requests must receive HTTP 409 Conflict
        self.assertEqual(len(conflicts), 2)
        
        # Verify final database state is consistent
        self.listing.refresh_from_db()
        self.req1.refresh_from_db()
        self.req2.refresh_from_db()
        self.req3.refresh_from_db()
        
        self.assertEqual(self.listing.status, 'REQUESTED')
        
        # Verify that the requests have the correct status (one accepted, others rejected)
        all_reqs = [self.req1, self.req2, self.req3]
        accepted_reqs = [r for r in all_reqs if r.status == 'ACCEPTED']
        rejected_reqs = [r for r in all_reqs if r.status == 'REJECTED']
        
        self.assertEqual(len(accepted_reqs), 1)
        self.assertEqual(len(rejected_reqs), 2)

    @patch('market.services.send_notification_task.delay')
    def test_second_accept_attempt_returns_409_conflict(self, mock_notify):
        """
        Verify that attempting to accept a second request after the first has been accepted
        strictly returns HTTP 409 Conflict.
        """
        client = APIClient()
        client.force_authenticate(user=self.owner)

        accept_url1 = reverse('request-accept', kwargs={'id': self.req1.id})
        accept_url2 = reverse('request-accept', kwargs={'id': self.req2.id})

        # First acceptance succeeds
        res1 = client.post(accept_url1)
        self.assertEqual(res1.status_code, status.HTTP_200_OK)

        # Second acceptance on now-REQUESTED listing must return 409 Conflict
        res2 = client.post(accept_url2)
        self.assertEqual(res2.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(res2.data.get('code'), 'conflict')
        self.assertIn("already requested or given away", res2.data.get('message', ''))
